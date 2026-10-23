param([string]$SdkBuildTools = 'C:\Users\locky\AppData\Local\Android\Sdk\build-tools\35.0.0')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $projectRoot
$sdk = $SdkBuildTools
$keystore = Join-Path $projectRoot 'artifacts\test-only.jks'
# Public Android debug password; this disposable key is for local smoke tests only.
if (-not (Test-Path -LiteralPath $keystore)) {
    & keytool -genkeypair -keystore $keystore -storepass android -keypass android -alias androiddebugkey -dname 'CN=TSL Local Smoke Test' -keyalg RSA -keysize 2048 -validity 3650
    if ($LASTEXITCODE -ne 0) { throw 'Could not create local test key.' }
}
& "$sdk\apksigner.bat" sign --ks $keystore --ks-pass pass:android --key-pass pass:android --ks-key-alias androiddebugkey --out artifacts\tsl-text-smoke.apk artifacts\tsl-text-smoke-unsigned.apk
if ($LASTEXITCODE -ne 0) { throw 'APK signing failed.' }
& "$sdk\apksigner.bat" verify --verbose artifacts\tsl-text-smoke.apk
if ($LASTEXITCODE -ne 0) { throw 'APK signature verification failed.' }
& "$sdk\zipalign.exe" -c 4 artifacts\tsl-text-smoke.apk
if ($LASTEXITCODE -ne 0) { throw 'ZIP alignment verification failed.' }
& python scripts\verify-patch.py 'C:\Users\locky\Downloads\安卓-TSL电子模块-1.2.7.apk' artifacts\tsl-text-smoke.apk
if ($LASTEXITCODE -ne 0) { throw 'Signed APK payload verification failed.' }
