@echo off
set "JAVA_HOME=C:\Users\PT COMPUTER\.jdks\ms-21.0.9"
set "PATH=%JAVA_HOME%\bin;%PATH%"
set "ANDROID_HOME=C:\Users\PT COMPUTER\AppData\Local\Android\Sdk"
call "C:\Users\PT COMPUTER\.gradle\wrapper\dists\gradle-8.13-bin\5xuhj0ry160q40clulazy9h7d\gradle-8.13\bin\gradle.bat" assembleRelease
