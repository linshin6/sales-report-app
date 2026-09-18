import os
import sys
import zipfile
import subprocess
import shutil
import datetime
import re
import glob

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW_DIR = os.path.join(ROOT_DIR, 'android', 'app', 'src', 'main', 'assets', 'www')
BASE_APK = os.path.join(ROOT_DIR, 'BaoCaoDoanhSo_TeamCamGiang.apk')
TEMP_UNSIGNED = os.path.join(ROOT_DIR, 'temp_unsigned.apk')
OUT_DIR = os.path.join(ROOT_DIR, 'out_apk')
TOOLS_DIR = os.path.join(ROOT_DIR, 'tools')
SIGNER_JAR = os.path.join(TOOLS_DIR, 'uber-apk-signer.jar')
APKTOOL_JAR = os.path.join(TOOLS_DIR, 'apktool.jar')
APK_SRC_DIR = os.path.join(TOOLS_DIR, 'apk_src')
JAVA_EXE = os.path.join(TOOLS_DIR, 'jre', 'bin', 'java.exe')
R8_JAR = os.path.join(TOOLS_DIR, 'r8.jar')
ANDROID_JAR = os.path.join(ROOT_DIR, 'android-33.jar')
LIBS_DIR = os.path.join(TOOLS_DIR, 'android_libs')
STRIPPED_BASE_DEX = os.path.join(TOOLS_DIR, 'stripped_base.dex')

BUILD_DIR = os.path.join(ROOT_DIR, 'build')
OUT_CLASSES = os.path.join(BUILD_DIR, 'classes')
OUT_DEX_DIR = os.path.join(BUILD_DIR, 'final_dex')
FINAL_CLASSES_DEX = os.path.join(OUT_DEX_DIR, 'classes.dex')

def get_javac_path():
    candidates = [
        r"C:\Users\giang\.antigravity-ide\extensions\redhat.java-1.56.0-win32-x64\jre\21.0.12.1-win32-x86_64\bin\javac.exe",
        shutil.which("javac")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    # Scan extension dir
    ext_dir = os.path.expanduser(r"~\.antigravity-ide\extensions")
    if os.path.exists(ext_dir):
        for root, dirs, files in os.walk(ext_dir):
            if "javac.exe" in files:
                return os.path.join(root, "javac.exe")
    return None

def sync_and_stamp_assets():
    now_str = datetime.datetime.now().strftime("%H:%M - %d/%m/%Y")
    
    # Doc thong tin version tu version.json
    version_json_path = os.path.join(ROOT_DIR, 'version.json')
    v_code = 11
    v_name = "1.1.0"
    if os.path.exists(version_json_path):
        try:
            import json
            with open(version_json_path, 'r', encoding='utf-8') as f:
                v_data = json.load(f)
                v_code = v_data.get('latestVersionCode', 11)
                v_name = v_data.get('latestVersionName', '1.1.0')
        except Exception as e:
            print(f"Warn: {e}")

    print(f"[*] Tu dong dong dau: Phien ban v{v_name} (Code {v_code}) - Ngay gio: {now_str}")
    
    # 1. Cap nhat thoi gian va phien ban vao index.html goc
    index_path = os.path.join(ROOT_DIR, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = re.sub(r'versionName:\s*"[^"]*"', f'versionName: "v{v_name}"', content)
        new_content = re.sub(r'versionCode:\s*\d+', f'versionCode: {v_code}', new_content)
        new_content = re.sub(r'buildDate:\s*"[^"]*"', f'buildDate: "{now_str}"', new_content)
        new_content = re.sub(r'<strong id="headerAppVersion"[^>]*>[^<]*</strong>', f'<strong id="headerAppVersion" style="color:#0f766e;">v{v_name}</strong>', new_content)
        new_content = re.sub(r'<strong id="footerAppVersion"[^>]*>[^<]*</strong>', f'<strong id="footerAppVersion" style="color:#0f766e;">v{v_name}</strong>', new_content)
        new_content = re.sub(r'<strong id="footerAppBuildDate"[^>]*>[^<]*</strong>', f'<strong id="footerAppBuildDate" style="color:#0f766e;">{now_str}</strong>', new_content)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    # 2. Dong bo sang assets/www/
    os.makedirs(WWW_DIR, exist_ok=True)
    for fname in ['index.html', 'view.html', 'master_data.js', 'version.json']:
        src = os.path.join(ROOT_DIR, fname)
        dst = os.path.join(WWW_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    # 3. Dong bo sang tools/apk_src/ (neu co) de apktool dong goi truc tiep
    if os.path.exists(APK_SRC_DIR):
        apk_www = os.path.join(APK_SRC_DIR, 'assets', 'www')
        os.makedirs(apk_www, exist_ok=True)
        for fname in ['index.html', 'view.html', 'master_data.js', 'version.json']:
            src = os.path.join(ROOT_DIR, fname)
            dst = os.path.join(apk_www, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)

        # Cap nhat versionCode va versionName trong apktool.yml
        yml_path = os.path.join(APK_SRC_DIR, 'apktool.yml')
        if os.path.exists(yml_path):
            with open(yml_path, 'r', encoding='utf-8') as f:
                yml_c = f.read()
            yml_c = re.sub(r'versionCode:.*', f'versionCode: {v_code}', yml_c)
            yml_c = re.sub(r'versionName:.*', f'versionName: {v_name}', yml_c)
            with open(yml_path, 'w', encoding='utf-8') as f:
                f.write(yml_c)

    return v_code, v_name

def compile_java_and_build_dex():
    print("1. Bien dich ma nguon Java native (MainActivity, AppUpdateManager)...")
    javac_path = get_javac_path()
    if not javac_path:
        print("[!] Canh bao: Khong tim thay javac.exe. Bo qua bien dich Java, su dung classes.dex hien tai.")
        return False

    if not os.path.exists(STRIPPED_BASE_DEX) or not os.path.exists(R8_JAR):
        print("[!] Canh bao: Thieu stripped_base.dex hoac r8.jar. Bo qua bien dich DEX.")
        return False

    if os.path.exists(OUT_CLASSES):
        shutil.rmtree(OUT_CLASSES)
    os.makedirs(OUT_CLASSES, exist_ok=True)

    jar_files = [ANDROID_JAR] + glob.glob(os.path.join(LIBS_DIR, "*.jar"))
    classpath = ";".join(jar_files)
    java_srcs = glob.glob(os.path.join(ROOT_DIR, "android", "app", "src", "main", "java", "com", "salesreport", "app", "*.java"))

    javac_cmd = [
        javac_path,
        "-cp", classpath,
        "-d", OUT_CLASSES,
        "-source", "1.8",
        "-target", "1.8",
        "-encoding", "UTF-8"
    ] + java_srcs

    res = subprocess.run(javac_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[X] Loi bien dich Java:\n", res.stderr or res.stdout)
        return False

    print("   -> Bien dich Java thanh cong!")

    print("2. Gop bytecode DEX bang Google D8...")
    if os.path.exists(OUT_DEX_DIR):
        shutil.rmtree(OUT_DEX_DIR)
    os.makedirs(OUT_DEX_DIR, exist_ok=True)

    class_files = []
    for root, dirs, files in os.walk(OUT_CLASSES):
        for file in files:
            if file.endswith('.class'):
                class_files.append(os.path.join(root, file))

    d8_cmd = [
        JAVA_EXE, '-cp', R8_JAR, 'com.android.tools.r8.D8',
        '--min-api', '26',
        '--lib', ANDROID_JAR,
        '--output', OUT_DEX_DIR
    ]
    for jar in glob.glob(os.path.join(LIBS_DIR, '*.jar')):
        d8_cmd.extend(['--lib', jar])

    d8_cmd.append(STRIPPED_BASE_DEX)
    d8_cmd.extend(class_files)

    res_d8 = subprocess.run(d8_cmd, capture_output=True, text=True)
    if res_d8.returncode != 0 or not os.path.exists(FINAL_CLASSES_DEX):
        print("[X] Loi D8 merge:\n", res_d8.stderr or res_d8.stdout)
        return False

    print(f"   -> D8 merge thanh cong: classes.dex ({os.path.getsize(FINAL_CLASSES_DEX):,} bytes)")
    return True

def main():
    print("=== DANG DONG GOI VA CAP NHAT APK (FULL NATIVE + WEB ASSETS) ===")
    if not os.path.exists(JAVA_EXE) or not os.path.exists(SIGNER_JAR):
        print(f"Error: Java or Signer tool not found in {TOOLS_DIR}")
        sys.exit(1)

    v_code, v_name = sync_and_stamp_assets()
    has_new_dex = compile_java_and_build_dex()

    if os.path.exists(TEMP_UNSIGNED):
        os.remove(TEMP_UNSIGNED)

    # 3. Su dung Apktool neu co san thu muc nguon apk_src de dam bao Manifest co REQUEST_INSTALL_PACKAGES
    use_apktool = os.path.exists(APKTOOL_JAR) and os.path.exists(APK_SRC_DIR)
    
    if use_apktool:
        print("3. Dong goi APK bang Apktool (Tich hop REQUEST_INSTALL_PACKAGES & Version v" + str(v_name) + ")...")
        if has_new_dex and os.path.exists(FINAL_CLASSES_DEX):
            shutil.copy2(FINAL_CLASSES_DEX, os.path.join(APK_SRC_DIR, 'classes.dex'))

        apktool_cmd = [JAVA_EXE, '-jar', APKTOOL_JAR, 'b', APK_SRC_DIR, '-o', TEMP_UNSIGNED]
        res_apktool = subprocess.run(apktool_cmd, capture_output=True, text=True)
        if res_apktool.returncode != 0 or not os.path.exists(TEMP_UNSIGNED):
            print("[!] Apktool build loi, chuyen sang phuong phap zipfile fallback:\n", res_apktool.stderr or res_apktool.stdout)
            use_apktool = False

    if not use_apktool:
        print("3. (Fallback) Dong goi bang ZipFile...")
        if not os.path.exists(BASE_APK):
            print(f"Error: Base APK not found at {BASE_APK}")
            sys.exit(1)

        with zipfile.ZipFile(BASE_APK, 'r') as zin, zipfile.ZipFile(TEMP_UNSIGNED, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename.startswith('META-INF/'):
                    continue
                if item.filename == 'classes.dex' and has_new_dex and os.path.exists(FINAL_CLASSES_DEX):
                    with open(FINAL_CLASSES_DEX, 'rb') as f:
                        zout.writestr(item, f.read())
                    continue
                if item.filename.startswith('assets/www/'):
                    rel_name = item.filename[len('assets/www/'):]
                    local_path = os.path.join(WWW_DIR, rel_name)
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            zout.writestr(item, f.read())
                        continue
                zout.writestr(item, zin.read(item.filename))

    print("4. Ky so (ZipAlign & APK Signature Scheme v2/v3)...")
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)

    cmd = [
        JAVA_EXE, '-jar', SIGNER_JAR,
        '-a', TEMP_UNSIGNED,
        '-o', OUT_DIR,
        '--allowResign'
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Signer Error:\n", res.stderr or res.stdout)
        sys.exit(1)

    signed_name = 'temp_unsigned-aligned-debugSigned.apk'
    signed_path = os.path.join(OUT_DIR, signed_name)
    if not os.path.exists(signed_path):
        print("Error: Signed APK not generated.")
        sys.exit(1)

    print("5. Cap nhat file APK dau ra duy nhat...")
    apk1 = os.path.join(ROOT_DIR, 'BaoCaoDoanhSo_TeamCamGiang.apk')
    shutil.copy2(signed_path, apk1)

    apk2 = os.path.join(ROOT_DIR, 'BaoCaoThucDat.apk')
    shutil.copy2(signed_path, apk2)

    # Clean up
    if os.path.exists(TEMP_UNSIGNED):
        os.remove(TEMP_UNSIGNED)
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)

    print("========================================================")
    print(f" DA CAP NHAT THANH CONG FILE APK MOI NHAT (v{v_name} - Code {v_code}):")
    print(" -> BaoCaoDoanhSo_TeamCamGiang.apk")
    print(" -> BaoCaoThucDat.apk")
    print("========================================================")

if __name__ == '__main__':
    main()
