param([string]$GradlePath = 'C:\Users\locky\.gradle\wrapper\dists\gradle-8.13-bin\5xuhj0ry160q40clulazy9h7d\gradle-8.13\bin\gradle.bat')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $GradlePath)) { throw 'Specify -GradlePath pointing to Gradle 8.13 or newer compatible with AGP 8.13.0.' }
Push-Location $PSScriptRoot
try {
    & $GradlePath --offline --no-daemon :app:assembleDebug :app:assembleDebugAndroidTest :app:lintDebug
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $builtApk = Join-Path $PSScriptRoot 'app\build\outputs\apk\debug\app-debug.apk'
    $releaseDir = Join-Path $PSScriptRoot '..\artifacts\tsl9-updater'
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
    $deliveryApk = Join-Path $releaseDir 'TSL9-Updater-0.6.1-test.apk'
    Copy-Item -LiteralPath $builtApk -Destination $deliveryApk -Force
    Get-FileHash -LiteralPath $deliveryApk -Algorithm SHA256
} finally { Pop-Location }
