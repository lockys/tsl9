param([Parameter(Mandatory)][string]$InputApk)
$ErrorActionPreference = 'Stop'
$InputApk = (Resolve-Path -LiteralPath $InputApk).Path
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $projectRoot
$expected = '10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee'
if ((Get-FileHash -LiteralPath $InputApk -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) {
    throw 'Input APK hash mismatch.'
}
$desktop = Join-Path $projectRoot 'tools\morphe-desktop-1.18.1-all.jar'
if (-not (Test-Path -LiteralPath $desktop)) { throw 'Download the official Morphe Desktop 1.18.1 all.jar into tools first.' }
$compiler = Join-Path $projectRoot 'tools\kotlin-2.4.21\kotlinc\bin\kotlinc.bat'
if (-not (Test-Path -LiteralPath $compiler)) { throw 'Download official Kotlin compiler 2.4.21 into tools first.' }
New-Item -ItemType Directory -Force -Path build,artifacts | Out-Null
$source = Join-Path $projectRoot 'patches\src\main\kotlin\tsl\TextSmokePatch.kt'
& $compiler -no-stdlib -no-reflect -jvm-target 17 -classpath $desktop -d build\tsl-text-smoke.jar $source
if ($LASTEXITCODE -ne 0) { throw 'Kotlin compilation failed.' }
Copy-Item -LiteralPath build\tsl-text-smoke.jar -Destination artifacts\tsl-text-smoke.mpp
& java -jar $desktop list-patches --patches artifacts\tsl-text-smoke.mpp
if ($LASTEXITCODE -ne 0) { throw 'Morphe could not load patch bundle.' }
& java -jar $desktop patch $InputApk -p artifacts\tsl-text-smoke.mpp --unsigned -o artifacts\tsl-text-smoke-unsigned.apk -t build\morphe-temp -r artifacts\morphe-result.json
if ($LASTEXITCODE -ne 0) { throw 'Morphe patch failed.' }
& python scripts\verify-patch.py $InputApk artifacts\tsl-text-smoke-unsigned.apk
if ($LASTEXITCODE -ne 0) { throw 'Independent payload verification failed.' }
