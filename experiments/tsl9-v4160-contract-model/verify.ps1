param([switch]$Cpp,[string]$Firmware)
$ErrorActionPreference='Stop'
$contractRoot=$PSScriptRoot
$contractRepo=(Resolve-Path (Join-Path $contractRoot '..\..')).Path
if(-not $Firmware){
    foreach($candidate in @('firmware-downloads\legacy-options-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin','exports\TSL-firmware-options-22-BINs-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin')){
        $contractCandidate=Join-Path $contractRepo $candidate
        if(Test-Path -LiteralPath $contractCandidate){$Firmware=$contractCandidate;break}
    }
}
if(-not $Firmware -or (Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant() -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'){throw 'ID2966 original firmware identity required'}
$contractMap=Get-Content -LiteralPath (Join-Path $contractRoot 'source-map.json') -Raw | ConvertFrom-Json
$contractRaw=[IO.File]::ReadAllBytes($Firmware)
if($contractMap.firmware_sha256 -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' -or $contractMap.source_base -ne 32768 -or $contractMap.source_bytes -ne $contractRaw.Length){throw 'Source map identity'}
if($contractMap.original_functions.Count -ne 6){throw 'Six source ranges required'}
foreach($contractRange in $contractMap.original_functions){
    $contractSlice=[byte[]]::new($contractRange.bytes)
    [Array]::Copy($contractRaw,([int]$contractRange.address-32768),$contractSlice,0,$contractSlice.Length)
    $contractDigest=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($contractSlice)).ToLowerInvariant()
    if($contractDigest -ne $contractRange.sha256){throw 'Original function range drift'}
}
$contractVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $contractVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $contractVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$contractVersion=(Get-Content -LiteralPath (Join-Path $contractVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$contractCompiler=Join-Path $contractVs ('VC\Tools\MSVC\'+$contractVersion+'\bin\Hostx64\x64\cl.exe')
$contractMode=if($Cpp){'cpp'}else{'c'}
$contractBuild=Join-Path $contractRoot ('build\'+[Guid]::NewGuid().ToString('N')+'-'+$contractMode)
New-Item -ItemType Directory -Path $contractBuild | Out-Null
$contractSources=@('src\flash_contract.c','src\flash_contract.h','tests\test_flash_contract.c','verify.ps1','source-map.json','README.md')
$contractPins=@{}
foreach($contractName in $contractSources){$contractPins[$contractName]=(Get-FileHash -LiteralPath (Join-Path $contractRoot $contractName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$contractExe=Join-Path $contractBuild 'host-contract-tests.exe'
$contractFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $contractRoot 'src')),('/Fo'+$contractBuild+'\'))
$contractFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $contractCompiler @contractFlags (Join-Path $contractRoot 'src\flash_contract.c') (Join-Path $contractRoot 'tests\test_flash_contract.c') ('/Fe'+$contractExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Host C/C++ compilation failed'}
$contractOutput=& $contractExe
if($LASTEXITCODE -ne 0){throw 'Host behavior tests failed'}
$contractResult=$contractOutput | ConvertFrom-Json
if(-not $contractResult.passed){throw 'Host behavior receipt missing'}
foreach($contractName in $contractSources){if($contractPins[$contractName] -ne (Get-FileHash -LiteralPath (Join-Path $contractRoot $contractName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source changed during verification'}}
$contractReceipt=@{passed=$true;mode=$contractMode;tests=$contractResult;source_sha256=$contractPins;executable=$contractExe;executable_sha256=(Get-FileHash -LiteralPath $contractExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$contractCompiler;compiler_sha256=(Get-FileHash -LiteralPath $contractCompiler -Algorithm SHA256).Hash.ToLowerInvariant();firmware_sha256=(Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant();original_executed=$false;emulation=$false;network=$false;hardware=$false;native_bin=$false;OTA_ready=$false}
$contractReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $contractBuild 'verification.json') -Encoding utf8
Write-Output ('CONTRACT_RESULT '+($contractReceipt|ConvertTo-Json -Depth 8 -Compress))
