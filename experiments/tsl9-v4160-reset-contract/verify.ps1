param([switch]$Cpp,[string]$Firmware)
$ErrorActionPreference='Stop'
$resetRoot=$PSScriptRoot
$resetRepo=(Resolve-Path (Join-Path $resetRoot '..\..')).Path
if(-not $Firmware){
    foreach($candidate in @('firmware-downloads\legacy-options-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin','exports\TSL-firmware-options-22-BINs-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin')){
        $resetCandidate=Join-Path $resetRepo $candidate
        if(Test-Path -LiteralPath $resetCandidate){$Firmware=$resetCandidate;break}
    }
}
if(-not $Firmware -or (Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant() -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'){throw 'Original ID2966 identity required'}
$resetMap=Get-Content -LiteralPath (Join-Path $resetRoot 'source-map.json') -Raw | ConvertFrom-Json
$resetRaw=[IO.File]::ReadAllBytes($Firmware)
if($resetMap.firmware_sha256 -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' -or $resetMap.source_base -ne 32768 -or $resetMap.source_bytes -ne $resetRaw.Length -or $resetMap.source_ranges.Count -ne 2){throw 'Original source-map scope'}
foreach($resetRange in $resetMap.source_ranges){
    $resetSlice=[byte[]]::new($resetRange.bytes)
    [Array]::Copy($resetRaw,([int]$resetRange.address-32768),$resetSlice,0,$resetSlice.Length)
    if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($resetSlice)).ToLowerInvariant() -ne $resetRange.sha256){throw 'Original reset source changed'}
}
$resetVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $resetVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $resetVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$resetVersion=(Get-Content -LiteralPath (Join-Path $resetVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$resetCompiler=Join-Path $resetVs ('VC\Tools\MSVC\'+$resetVersion+'\bin\Hostx64\x64\cl.exe')
$resetMode=if($Cpp){'cpp'}else{'c'}
$resetBuild=Join-Path $resetRoot ('build\'+[Guid]::NewGuid().ToString('N')+'-'+$resetMode)
New-Item -ItemType Directory -Path $resetBuild | Out-Null
$resetNames=@('src\reset_contract.c','src\reset_contract.h','tests\test_reset_contract.c','verify.ps1','source-map.json','README.md')
$resetPins=@{}
foreach($resetName in $resetNames){$resetPins[$resetName]=(Get-FileHash -LiteralPath (Join-Path $resetRoot $resetName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$resetExe=Join-Path $resetBuild 'host-reset-tests.exe'
$resetFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $resetRoot 'src')),('/Fo'+$resetBuild+'\'))
$resetFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $resetCompiler @resetFlags (Join-Path $resetRoot 'src\reset_contract.c') (Join-Path $resetRoot 'tests\test_reset_contract.c') ('/Fe'+$resetExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Host reset compilation failed'}
$resetOutput=& $resetExe
if($LASTEXITCODE -ne 0){throw 'Host reset behavior failed'}
$resetTests=$resetOutput | ConvertFrom-Json
if(-not $resetTests.passed){throw 'Host reset result missing'}
foreach($resetName in $resetNames){if($resetPins[$resetName] -ne (Get-FileHash -LiteralPath (Join-Path $resetRoot $resetName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Inputs changed during verification'}}
$resetReceipt=@{passed=$true;mode=$resetMode;tests=$resetTests;source_sha256=$resetPins;executable=$resetExe;executable_sha256=(Get-FileHash -LiteralPath $resetExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$resetCompiler;compiler_sha256=(Get-FileHash -LiteralPath $resetCompiler -Algorithm SHA256).Hash.ToLowerInvariant();firmware_sha256=(Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant();original_executed=$false;emulation=$false;network=$false;hardware=$false;native_bin=$false;OTA_ready=$false}
$resetReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $resetBuild 'verification.json') -Encoding utf8
Write-Output ('RESET_RESULT '+($resetReceipt|ConvertTo-Json -Depth 8 -Compress))
