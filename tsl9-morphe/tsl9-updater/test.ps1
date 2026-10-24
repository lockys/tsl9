param([string]$FactoryPaged, [string]$FactoryRaw, [string]$UserRaw, [string]$OriginalJs, [switch]$SkipOemReference)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$testOutput = Join-Path $projectRoot 'build\core-tests'
New-Item -ItemType Directory -Force -Path $testOutput | Out-Null
$sources = @('UiMessage.java','UiException.java','Protocol.java','FirmwareImage.java','OtaSession.java','HardwareCapture.java','DeviceInfoSnapshot.java','VehicleControls.java','LiveVehicleData.java') | ForEach-Object { Join-Path $projectRoot "app\src\main\java\dev\tsl9\morphe\$_" }
& javac -encoding UTF-8 -d $testOutput @sources (Join-Path $projectRoot 'tests\CoreTests.java') (Join-Path $projectRoot 'tests\HardwareCaptureTests.java') (Join-Path $projectRoot 'tests\OemCompatibilityTests.java') (Join-Path $projectRoot 'tests\DeviceInfoTests.java') (Join-Path $projectRoot 'tests\VehicleControlsTests.java') (Join-Path $projectRoot 'tests\OemBodyCompatibilityTests.java')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (-not $SkipOemReference) {
    if (-not $OriginalJs) { $OriginalJs = Join-Path $projectRoot '../artifacts/firmware-trace/miniapp/app-service.js' }
    if (-not (Test-Path -LiteralPath $OriginalJs)) { throw 'Pass -OriginalJs with the locally extracted OEM source, or explicitly use -SkipOemReference for synthetic-only tests.' }
    $referenceTrace = Join-Path $testOutput 'oem-reference.tsv'
    $oracleArgs = @((Join-Path $projectRoot 'tests/oem-reference.cjs'), $OriginalJs)
    if ($UserRaw) { $oracleArgs += $UserRaw }
    $referenceLines = & node @oracleArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    [System.IO.File]::WriteAllLines($referenceTrace, [string[]]$referenceLines, [System.Text.UTF8Encoding]::new($false))
    $compatArgs = @($referenceTrace)
    if ($UserRaw) { $compatArgs += $UserRaw }
    & java -cp $testOutput dev.tsl9.morphe.OemCompatibilityTests @compatArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $bodyTrace = Join-Path $testOutput 'oem-body-reference.tsv'
    $bodyLines = & node (Join-Path $projectRoot 'tests/oem-body-reference.cjs') $OriginalJs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    [System.IO.File]::WriteAllLines($bodyTrace, [string[]]$bodyLines, [System.Text.UTF8Encoding]::new($false))
    & java -cp $testOutput dev.tsl9.morphe.OemBodyCompatibilityTests $bodyTrace
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else { Write-Output 'SKIP OEM differential tests: synthetic-only mode explicitly selected.' }
$referenceArgs = @()
if ($FactoryPaged -and $FactoryRaw) { $referenceArgs = @($FactoryPaged, $FactoryRaw) }
& java -cp $testOutput dev.tsl9.morphe.CoreTests @referenceArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp $testOutput dev.tsl9.morphe.HardwareCaptureTests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp $testOutput dev.tsl9.morphe.DeviceInfoTests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp $testOutput dev.tsl9.morphe.VehicleControlsTests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& javac -encoding UTF-8 -cp $testOutput -d $testOutput (Join-Path $projectRoot 'tests\LiveVehicleTests.java')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp $testOutput dev.tsl9.morphe.LiveVehicleTests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& javac -encoding UTF-8 -cp $testOutput -d $testOutput (Join-Path $projectRoot 'tests\DirectControlTests.java')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp $testOutput dev.tsl9.morphe.DirectControlTests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& javac -encoding UTF-8 -cp $testOutput -d $testOutput (Join-Path $projectRoot 'tests\PendingControlTests.java')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp $testOutput dev.tsl9.morphe.PendingControlTests
exit $LASTEXITCODE
