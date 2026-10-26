param(
    [Parameter(Mandatory)][string]$Serial,
    [string]$AdbPath,
    [string]$Version = '0.7.4-test'
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '../scripts/android-tools.ps1')
$AdbPath = Resolve-AndroidAdb $PSScriptRoot $AdbPath
if ($Serial -notmatch '^emulator-[0-9]+$') { throw 'This synthetic DocumentsUI test is restricted to an emulator. Never run it during hardware OTA.' }
$workspace = Split-Path -Parent $PSScriptRoot
$outputDir = Join-Path $workspace ("artifacts/tsl9-updater/documents-smoke-" + $Version.Replace('-test',''))
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
trap {
    [ordered]@{status='failed';date_utc=[DateTime]::UtcNow.ToString('o');reason=$_.Exception.Message;physical_bluetooth_or_firmware_tested=$false} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputDir 'result.json') -Encoding utf8
    throw
}
function Invoke-TestAdb([string[]]$AdbArguments, [int]$TimeoutSeconds = 30) {
    $start = [System.Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $AdbPath
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    foreach ($arg in (@('-s', $Serial) + $AdbArguments)) { $start.ArgumentList.Add($arg) }
    $process = [System.Diagnostics.Process]::Start($start)
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        $process.Kill($true)
        throw "Local ADB command timed out after $TimeoutSeconds seconds."
    }
    $result = $stdout.GetAwaiter().GetResult()
    $errorText = $stderr.GetAwaiter().GetResult()
    if ($process.ExitCode -ne 0) { throw "Local ADB failed: $errorText $result" }
    $process.Dispose()
    return $result
}
$apk = Join-Path $workspace "artifacts/tsl9-updater/TSL9-Updater-$Version.apk"
$testApk = Join-Path $PSScriptRoot 'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'
[ordered]@{status='running'; date_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputDir 'result.json') -Encoding utf8
Invoke-TestAdb -AdbArguments @('wait-for-device') -TimeoutSeconds 30 | Out-Null
Invoke-TestAdb -AdbArguments @('install', '-r', $apk) | Write-Output
Invoke-TestAdb -AdbArguments @('install', '-r', $testApk) | Write-Output
try {
    $run = Invoke-TestAdb -AdbArguments @('shell', 'am', 'instrument', '-w', '-e', 'documents', 'true', 'dev.tsl9.morphe.test.test/dev.tsl9.morphe.SmokeInstrumentation') -TimeoutSeconds 180
} catch {
    Invoke-TestAdb -AdbArguments @('shell', 'am', 'force-stop', 'dev.tsl9.morphe.test') | Out-Null
    throw
}
Set-Content -LiteralPath (Join-Path $outputDir 'instrumentation.txt') -Value $run -Encoding utf8
Write-Output $run
if ($run -notmatch 'result=PASS ([0-9]+) Android') { throw 'DocumentsUI instrumentation did not pass.' }
$androidAssertions = [int]$Matches[1]
$names = [regex]::Matches($run, 'documentFile=(tsl9-smoke-(?:hardware|debug)-[0-9]+\.(?:jsonl|txt))') | ForEach-Object { $_.Groups[1].Value }
if ($names.Count -ne 2) { throw 'Expected two actual document export receipts.' }
foreach ($name in $names) {
    $destination = if ($name -match '-hardware-') { 'hardware-export.jsonl' } else { 'debug-export.txt' }
    Invoke-TestAdb -AdbArguments @('pull', "/sdcard/Download/$name", (Join-Path $outputDir $destination)) | Write-Output
}
$hardware = Get-Content -Raw -LiteralPath (Join-Path $outputDir 'hardware-export.jsonl')
$debug = Get-Content -Raw -LiteralPath (Join-Path $outputDir 'debug-export.txt')
$rows = @($hardware -split '\r?\n' | Where-Object { $_ } | ForEach-Object { $_ | ConvertFrom-Json })
if ($rows[0].schema -ne 'tsl9-hardware-log-v1' -or $hardware -notmatch 'SYNTH_TEMP=31') { throw 'Exported hardware JSONL content mismatch.' }
if ($hardware -match 'synthetic-android-secret') { throw 'Synthetic hardware secret was not redacted.' }
if ($debug -notmatch 'SMOKE local-ui-check no BLE' -or $debug -notmatch 'BIN validated') { throw 'Exported phone debug content mismatch.' }
if ($debug -match 'synthetic-android-secret') { throw 'Synthetic secret leaked to phone debug.' }
$evidence = [ordered]@{
    status = 'passed'
    date_utc = [DateTime]::UtcNow.ToString('o')
    apk_sha256 = (Get-FileHash -LiteralPath $apk -Algorithm SHA256).Hash.ToLowerInvariant()
    android_assertions = $androidAssertions
    actual_export_content_assertions = 4
    real_documents_provider = $true
    synthetic_input_bytes = 1031
    synthetic_input_padding_bytes = 1017
    hardware_rows = $rows[0].records
    hardware_export_sha256 = (Get-FileHash -LiteralPath (Join-Path $outputDir 'hardware-export.jsonl') -Algorithm SHA256).Hash.ToLowerInvariant()
    debug_export_sha256 = (Get-FileHash -LiteralPath (Join-Path $outputDir 'debug-export.txt') -Algorithm SHA256).Hash.ToLowerInvariant()
    physical_bluetooth_or_firmware_tested = $false
}
$evidence | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputDir 'result.json') -Encoding utf8
Write-Output "PASS $androidAssertions Android assertions + 4 actual exported-file checks; synthetic only, no physical BLE."
