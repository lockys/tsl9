param(
    [Parameter(Mandatory)][string]$Serial,
    [string]$AdbPath,
    [string]$Version='0.7.3-nav-debug',
    [string[]]$Locales=@('en','zh-Hans','zh-Hant','system'),
    [switch]$SkipInstall,
    [switch]$NoScreenshots
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '../scripts/android-tools.ps1')
$AdbPath=Resolve-AndroidAdb $PSScriptRoot $AdbPath
if($Serial -notmatch '^emulator-[0-9]+$'){throw 'Local synthetic UI test accepts emulators only.'}
$workspace=Split-Path -Parent $PSScriptRoot
$outputDir=Join-Path $workspace ("artifacts/tsl9-updater/i18n-smoke-"+$Version.Replace('-test',''))
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
function Invoke-LocalAdb([string[]]$Arguments,[int]$Timeout=60){
    $start=[Diagnostics.ProcessStartInfo]::new();$start.FileName=$AdbPath;$start.UseShellExecute=$false;$start.CreateNoWindow=$true
    $start.RedirectStandardOutput=$true;$start.RedirectStandardError=$true
    foreach($arg in (@('-s',$Serial)+$Arguments)){$start.ArgumentList.Add($arg)}
    $process=[Diagnostics.Process]::Start($start);$stdout=$process.StandardOutput.ReadToEndAsync();$stderr=$process.StandardError.ReadToEndAsync()
    if(-not $process.WaitForExit($Timeout*1000)){$process.Kill($true);throw "Local ADB timed out after $Timeout seconds."}
    $result=$stdout.GetAwaiter().GetResult();$errorText=$stderr.GetAwaiter().GetResult();$exitCode=$process.ExitCode;$process.Dispose()
    if($exitCode -ne 0){throw "Local ADB failed: $errorText $result"}
    return $result
}
$apk=Join-Path $workspace "artifacts/tsl9-updater/TSL9-Updater-$Version.apk"
$testApk=Join-Path $PSScriptRoot 'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'
$results=@()
[ordered]@{status='running';date_utc=[DateTime]::UtcNow.ToString('o');serial=$Serial} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputDir 'result.json') -Encoding utf8
try{
    Invoke-LocalAdb -Arguments @('wait-for-device') -Timeout 30 | Out-Null
    if(-not $SkipInstall){
        Invoke-LocalAdb -Arguments @('install','-r',$apk) | Write-Output
        Invoke-LocalAdb -Arguments @('install','-r',$testApk) | Write-Output
    }
    foreach($locale in $Locales){
        $arguments=@('shell','am','instrument','-w','-e','locale',$locale)
        if($locale -eq 'system'){$arguments+=@('-e','switches','true')}
        $arguments+='dev.tsl9.morphe.test.test/dev.tsl9.morphe.SmokeInstrumentation'
        $run=Invoke-LocalAdb -Arguments $arguments -Timeout 120
        Set-Content -LiteralPath (Join-Path $outputDir "$locale.txt") -Value $run -Encoding utf8
        Write-Output "$locale $run"
        if($run -notmatch 'result=PASS ([0-9]+) Android'){throw "Locale test failed: $locale"}
        $results+=@{locale=$locale;assertions=[int]$Matches[1]}
        if($NoScreenshots){continue}
        Invoke-LocalAdb -Arguments @('shell','am','start','-W','-n','dev.tsl9.morphe.test/dev.tsl9.morphe.MainActivity') | Out-Null
        # A successful cold start may still show the splash on a busy emulator.
        # Capture only after the actual translated App title is visible.
        $deadline=[DateTime]::UtcNow.AddSeconds(25);$drawn=$false
        do{
            Invoke-LocalAdb -Arguments @('shell','uiautomator','dump','/sdcard/tsl9-i18n-ready.xml') | Out-Null
            $layout=Invoke-LocalAdb -Arguments @('shell','cat','/sdcard/tsl9-i18n-ready.xml')
            $drawn=$layout -match 'content-desc="TSL9 (Hardware Tools|硬件工具|硬體工具)"'
            if(-not $drawn){Start-Sleep -Milliseconds 300}
        }while(-not $drawn -and [DateTime]::UtcNow -lt $deadline)
        if(-not $drawn){throw "Translated UI not drawn for screenshot: $locale"}
        $remote="/sdcard/Download/tsl9-i18n-$locale.png"
        Invoke-LocalAdb -Arguments @('shell','screencap','-p',$remote) | Out-Null
        Invoke-LocalAdb -Arguments @('pull',$remote,(Join-Path $outputDir "$locale.png")) | Out-Null
        Invoke-LocalAdb -Arguments @('shell','am','force-stop','dev.tsl9.morphe.test') | Out-Null
    }
    $receipt=[ordered]@{status='passed';date_utc=[DateTime]::UtcNow.ToString('o');serial=$Serial;apk_sha256=(Get-FileHash -LiteralPath $apk -Algorithm SHA256).Hash.ToLower();locales=$results;physical_bluetooth_or_firmware_tested=$false}
}catch{
    try{Invoke-LocalAdb -Arguments @('shell','am','force-stop','dev.tsl9.morphe.test') | Out-Null}catch{}
    $receipt=[ordered]@{status='failed';date_utc=[DateTime]::UtcNow.ToString('o');reason=$_.Exception.Message;completed=$results;physical_bluetooth_or_firmware_tested=$false}
    $receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputDir 'result.json') -Encoding utf8
    throw
}
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputDir 'result.json') -Encoding utf8
Write-Output "PASS receipt: $outputDir/result.json"
