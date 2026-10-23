param([string]$GradlePath)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '../scripts/android-tools.ps1')
$GradlePath = Resolve-LocalGradle $GradlePath
$env:ANDROID_HOME = Resolve-AndroidSdk $PSScriptRoot
Push-Location $PSScriptRoot
try {
    & $GradlePath --offline --no-daemon :app:assembleDebug :app:assembleDebugAndroidTest :app:lintDebug
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $builtApk = Join-Path $PSScriptRoot 'app\build\outputs\apk\debug\app-debug.apk'
    $releaseDir = Join-Path $PSScriptRoot '..\artifacts\tsl9-updater'
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
    $deliveryApk = Join-Path $releaseDir 'TSL9-Updater-0.7.1-test.apk'
    Copy-Item -LiteralPath $builtApk -Destination $deliveryApk -Force
    Get-FileHash -LiteralPath $deliveryApk -Algorithm SHA256
} finally { Pop-Location }
