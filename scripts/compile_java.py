import os
import glob
import subprocess
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAVAC = r"C:\Users\giang\.antigravity-ide\extensions\redhat.java-1.56.0-win32-x64\jre\21.0.12.1-win32-x86_64\bin\javac.exe"
ANDROID_JAR = os.path.join(ROOT_DIR, "android-33.jar")
LIBS_DIR = os.path.join(ROOT_DIR, "tools", "android_libs")
OUT_CLASSES = os.path.join(ROOT_DIR, "build", "classes")

os.makedirs(OUT_CLASSES, exist_ok=True)

jar_files = [ANDROID_JAR] + glob.glob(os.path.join(LIBS_DIR, "*.jar"))
classpath = ";".join(jar_files)

java_srcs = glob.glob(os.path.join(ROOT_DIR, "android", "app", "src", "main", "java", "com", "salesreport", "app", "*.java"))
print("Compiling sources:", java_srcs)

cmd = [
    JAVAC,
    "-cp", classpath,
    "-d", OUT_CLASSES,
    "-source", "1.8",
    "-target", "1.8",
    "-encoding", "UTF-8"
] + java_srcs

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Compilation failed:")
    print(res.stderr or res.stdout)
else:
    print("SUCCESS: Java classes compiled successfully!")
    print("Output files:", os.listdir(os.path.join(OUT_CLASSES, "com", "salesreport", "app")))
