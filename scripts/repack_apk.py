import os
import sys
import zipfile
import subprocess
import shutil
import datetime
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW_DIR = os.path.join(ROOT_DIR, 'android', 'app', 'src', 'main', 'assets', 'www')
BASE_APK = os.path.join(ROOT_DIR, 'BaoCaoDoanhSo_TeamCamGiang.apk')
TEMP_UNSIGNED = os.path.join(ROOT_DIR, 'temp_unsigned.apk')
OUT_DIR = os.path.join(ROOT_DIR, 'out_apk')
TOOLS_DIR = os.path.join(ROOT_DIR, 'tools')
SIGNER_JAR = os.path.join(TOOLS_DIR, 'uber-apk-signer.jar')
JAVA_EXE = os.path.join(TOOLS_DIR, 'jre', 'bin', 'java.exe')

def sync_and_stamp_assets():
    now_str = datetime.datetime.now().strftime("%H:%M - %d/%m/%Y")
    print(f"[*] Tu dong dong dau ngay gio cap nhat: {now_str}")
    
    # 1. Cap nhat thoi gian vao index.html goc
    index_path = os.path.join(ROOT_DIR, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Thay the buildDate trong APP_METADATA va footer
        new_content = re.sub(r'buildDate:\s*"[^"]*"', f'buildDate: "{now_str}"', content)
        new_content = re.sub(r'<strong id="footerAppBuildDate"[^>]*>[^<]*</strong>', f'<strong id="footerAppBuildDate" style="color:#0f766e;">{now_str}</strong>', new_content)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    # 2. Dong bo sang assets/www/
    os.makedirs(WWW_DIR, exist_ok=True)
    for fname in ['index.html', 'view.html', 'master_data.js']:
        src = os.path.join(ROOT_DIR, fname)
        dst = os.path.join(WWW_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)

def main():
    print("=== DANG DONG GOI VA CAP NHAT APK (PORTABLE SIGNER) ===")
    if not os.path.exists(BASE_APK):
        print(f"Error: Base APK not found at {BASE_APK}")
        sys.exit(1)
        
    if not os.path.exists(JAVA_EXE) or not os.path.exists(SIGNER_JAR):
        print(f"Error: Java or Signer tool not found in {TOOLS_DIR}")
        sys.exit(1)

    sync_and_stamp_assets()

    print("1. Dong goi ma nguon web moi nhat vao APK...")
    with zipfile.ZipFile(BASE_APK, 'r') as zin, zipfile.ZipFile(TEMP_UNSIGNED, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename.startswith('META-INF/'):
                continue
            if item.filename.startswith('assets/www/'):
                rel_name = item.filename[len('assets/www/'):]
                local_path = os.path.join(WWW_DIR, rel_name)
                if os.path.exists(local_path):
                    with open(local_path, 'rb') as f:
                        zout.writestr(item, f.read())
                    continue
            zout.writestr(item, zin.read(item.filename))

    print("2. Ky so (ZipAlign & APK Signature Scheme v2/v3)...")
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

    print("3. Cap nhat file APK dau ra duy nhat...")
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
    print(" DA CAP NHAT THANH CONG FILE APK MOI NHAT:")
    print(" -> BaoCaoDoanhSo_TeamCamGiang.apk")
    print("========================================================")

if __name__ == '__main__':
    main()
