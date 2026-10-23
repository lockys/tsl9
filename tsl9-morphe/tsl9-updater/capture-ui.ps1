param(
    [Parameter(Mandatory)][string]$Serial,
    [string]$AdbPath,
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '../artifacts/ui-screenshots'),
    [switch]$AdditionalStatesOnly
)
$ErrorActionPreference = 'Stop'
if ($Serial -notmatch '^emulator-[0-9]+$') { throw 'Screenshots use a local synthetic emulator only.' }
. (Join-Path $PSScriptRoot '../scripts/android-tools.ps1')
$AdbPath = Resolve-AndroidAdb $PSScriptRoot $AdbPath
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
function Invoke-CaptureAdb([string[]]$Arguments, [int]$Timeout = 45) {
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $AdbPath; $start.UseShellExecute = $false; $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true; $start.RedirectStandardError = $true
    foreach ($arg in @('-s', $Serial) + $Arguments) { $start.ArgumentList.Add($arg) }
    $process = [Diagnostics.Process]::Start($start)
    $stdout = $process.StandardOutput.ReadToEndAsync(); $stderr = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit($Timeout * 1000)) { $process.Kill($true); throw 'Screenshot command timed out.' }
    $result = $stdout.GetAwaiter().GetResult(); $errorText = $stderr.GetAwaiter().GetResult(); $code = $process.ExitCode; $process.Dispose()
    if ($code) { throw "Screenshot command failed: $errorText $result" }
    return $result
}
function Read-Layout {
    Invoke-CaptureAdb @('shell','uiautomator','dump','/sdcard/tsl9-layout.xml') | Out-Null
    return [xml](Invoke-CaptureAdb @('shell','cat','/sdcard/tsl9-layout.xml'))
}
function Select-Tab([string]$Label) {
    $tree = Read-Layout
    $node = @($tree.SelectNodes('//node') | Where-Object { ($_.text -eq $Label -or $_.'content-desc' -eq $Label) -and $_.clickable -eq 'true' }) | Select-Object -Last 1
    if (-not $node -or $node.bounds -notmatch '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') { throw "Missing tab: $Label" }
    $x = [int](([int]$Matches[1] + [int]$Matches[3]) / 2); $y = [int](([int]$Matches[2] + [int]$Matches[4]) / 2)
    Invoke-CaptureAdb @('shell','input','tap',"$x","$y") | Out-Null
    Read-Layout | Out-Null
}
function Save-Screenshot([string]$Name) {
    Invoke-CaptureAdb @('shell','screencap','-p','/sdcard/tsl9-screenshot.png') | Out-Null
    Invoke-CaptureAdb @('pull','/sdcard/tsl9-screenshot.png',(Join-Path $OutputDirectory "$Name.png")) | Out-Null
    Write-Output "Captured $Name.png"
}
Invoke-CaptureAdb @('wait-for-device') 30 | Out-Null
$oldFont=$null; $oldRotation=$null; $oldAutoRotation=$null
if ($AdditionalStatesOnly) {
    $oldFont=(Invoke-CaptureAdb @('shell','settings','get','system','font_scale')).Trim()
    $oldRotation=(Invoke-CaptureAdb @('shell','settings','get','system','user_rotation')).Trim()
    $oldAutoRotation=(Invoke-CaptureAdb @('shell','settings','get','system','accelerometer_rotation')).Trim()
}
$run = Invoke-CaptureAdb @('shell','am','instrument','-w','-e','locale','zh-Hant','dev.tsl9.morphe.test.test/dev.tsl9.morphe.SmokeInstrumentation') 120
if ($run -notmatch 'result=PASS') { throw $run }
try {
    Invoke-CaptureAdb @('shell','am','start','-W','-n','dev.tsl9.morphe.test/dev.tsl9.morphe.MainActivity') | Out-Null
    $deadline = [DateTime]::UtcNow.AddSeconds(25)
    do {
        $tree = Read-Layout
        $ready = @($tree.SelectNodes('//node') | Where-Object { $_.'content-desc' -eq 'TSL9 硬體工具' }).Count -gt 0
    } while (-not $ready -and [DateTime]::UtcNow -lt $deadline)
    if (-not $ready) { throw 'Actual App UI did not become visible before screenshot.' }
    if (-not $AdditionalStatesOnly) {
        Select-Tab '藍芽／更新'; Save-Screenshot 'tools-portrait'
        Select-Tab '汽車控制'; Save-Screenshot 'car-portrait'
        Select-Tab '即時資料'; Save-Screenshot 'live-portrait'
    } else {
        Invoke-CaptureAdb @('shell','settings','put','system','accelerometer_rotation','0') | Out-Null
        Select-Tab '汽車控制'
        Invoke-CaptureAdb @('shell','settings','put','system','user_rotation','1') | Out-Null
        Read-Layout | Out-Null; Save-Screenshot 'car-landscape'
        Invoke-CaptureAdb @('shell','settings','put','system','user_rotation','0') | Out-Null
        Invoke-CaptureAdb @('shell','settings','put','system','font_scale','2.0') | Out-Null
        Read-Layout | Out-Null; Select-Tab '汽車控制'; Save-Screenshot 'car-font-200'
        Select-Tab '即時資料'; Save-Screenshot 'live-font-200'
        Invoke-CaptureAdb @('shell','am','force-stop','dev.tsl9.morphe.test') | Out-Null
        $largeRun=Invoke-CaptureAdb @('shell','am','instrument','-w','-e','locale','en','dev.tsl9.morphe.test.test/dev.tsl9.morphe.SmokeInstrumentation') 120
        if ($largeRun -notmatch 'result=PASS') { throw $largeRun }
        Write-Output "200% text $largeRun"
        Invoke-CaptureAdb @('shell','am','start','-W','-n','dev.tsl9.morphe.test/dev.tsl9.morphe.MainActivity') | Out-Null
        Read-Layout | Out-Null; Select-Tab 'Car controls'; Save-Screenshot 'car-en-font-200'
    }
} finally {
    if ($null -ne $oldFont) {
        Invoke-CaptureAdb @('shell','settings','put','system','font_scale',$oldFont) | Out-Null
        Invoke-CaptureAdb @('shell','settings','put','system','user_rotation',$oldRotation) | Out-Null
        Invoke-CaptureAdb @('shell','settings','put','system','accelerometer_rotation',$oldAutoRotation) | Out-Null
    }
    Invoke-CaptureAdb @('shell','am','force-stop','dev.tsl9.morphe.test') | Out-Null
}
