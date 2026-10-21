param([switch]$Cpp,[string]$Firmware)
$ErrorActionPreference='Stop'
$ingressRoot=$PSScriptRoot
$ingressRepo=(Resolve-Path (Join-Path $ingressRoot '..\..')).Path
if(-not $Firmware){
    foreach($candidate in @('firmware-downloads\legacy-options-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin','exports\TSL-firmware-options-22-BINs-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin')){
        $ingressCandidate=Join-Path $ingressRepo $candidate
        if(Test-Path -LiteralPath $ingressCandidate){$Firmware=$ingressCandidate;break}
    }
}
if(-not $Firmware -or (Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant() -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'){throw 'Original ID2966 identity required'}
$ingressMap=Get-Content -LiteralPath (Join-Path $ingressRoot 'source-map.json') -Raw | ConvertFrom-Json
$ingressRaw=[IO.File]::ReadAllBytes($Firmware)
if($ingressMap.firmware_sha256 -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' -or $ingressMap.source_base -ne 32768 -or $ingressMap.source_bytes -ne $ingressRaw.Length -or $ingressMap.original_functions.Count -ne 1){throw 'Original source-map scope'}
foreach($ingressRange in $ingressMap.original_functions){
    $ingressSlice=[byte[]]::new($ingressRange.bytes)
    [Array]::Copy($ingressRaw,([int]$ingressRange.address-32768),$ingressSlice,0,$ingressSlice.Length)
    if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($ingressSlice)).ToLowerInvariant() -ne $ingressRange.sha256){throw 'Original callback source changed'}
}
$ingressVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $ingressVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $ingressVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$ingressVersion=(Get-Content -LiteralPath (Join-Path $ingressVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$ingressCompiler=Join-Path $ingressVs ('VC\Tools\MSVC\'+$ingressVersion+'\bin\Hostx64\x64\cl.exe')
$ingressMode=if($Cpp){'cpp'}else{'c'}
$ingressBuild=Join-Path $ingressRoot ('build\'+[Guid]::NewGuid().ToString('N')+'-'+$ingressMode)
New-Item -ItemType Directory -Path $ingressBuild | Out-Null
$ingressNames=@('src\gatt_ingress.c','src\gatt_ingress.h','tests\test_gatt_ingress.c','verify.ps1','source-map.json','README.md')
$ingressPins=@{}
foreach($ingressName in $ingressNames){$ingressPins[$ingressName]=(Get-FileHash -LiteralPath (Join-Path $ingressRoot $ingressName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$ingressExe=Join-Path $ingressBuild 'host-ingress-tests.exe'
$ingressFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $ingressRoot 'src')),('/Fo'+$ingressBuild+'\'))
$ingressFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $ingressCompiler @ingressFlags (Join-Path $ingressRoot 'src\gatt_ingress.c') (Join-Path $ingressRoot 'tests\test_gatt_ingress.c') ('/Fe'+$ingressExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Host ingress compilation failed'}
$ingressOutput=& $ingressExe
if($LASTEXITCODE -ne 0){throw 'Host ingress behavior failed'}
$ingressTests=$ingressOutput | ConvertFrom-Json
if(-not $ingressTests.passed){throw 'Host ingress result missing'}
foreach($ingressName in $ingressNames){if($ingressPins[$ingressName] -ne (Get-FileHash -LiteralPath (Join-Path $ingressRoot $ingressName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Inputs changed during verification'}}
$ingressReceipt=@{passed=$true;mode=$ingressMode;tests=$ingressTests;source_sha256=$ingressPins;executable=$ingressExe;executable_sha256=(Get-FileHash -LiteralPath $ingressExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$ingressCompiler;compiler_sha256=(Get-FileHash -LiteralPath $ingressCompiler -Algorithm SHA256).Hash.ToLowerInvariant();firmware_sha256=(Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant();original_executed=$false;emulation=$false;network=$false;hardware=$false;native_bin=$false;OTA_ready=$false}
$ingressReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $ingressBuild 'verification.json') -Encoding utf8
Write-Output ('INGRESS_RESULT '+($ingressReceipt|ConvertTo-Json -Depth 8 -Compress))
