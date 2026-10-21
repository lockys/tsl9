param([switch]$Cpp,[string]$Firmware,[string]$ProofRoot)
$ErrorActionPreference='Stop'
$irqRoot=$PSScriptRoot
$irqRepo=(Resolve-Path (Join-Path $irqRoot '..\..')).Path
$irqMapPath=Join-Path $irqRoot 'source-map.json'
$irqMap=Get-Content -LiteralPath $irqMapPath -Raw | ConvertFrom-Json
if($irqMap.schema -ne 'ID2966-irq-frame-readable-model-source-v1'){throw 'Exact frame-model source scope required'}
if(-not $Firmware){
    foreach($irqCandidate in @('firmware-downloads\legacy-options-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin','exports\TSL-firmware-options-22-BINs-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin')){
        $irqFile=Join-Path $irqRepo $irqCandidate
        if(Test-Path -LiteralPath $irqFile){$Firmware=$irqFile;break}
    }
}
if(-not $Firmware -or (Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant() -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'){throw 'Original ID2966 identity required'}
$irqRaw=[IO.File]::ReadAllBytes($Firmware)
if($irqMap.source_bytes -ne $irqRaw.Length -or $irqMap.source_ranges.Count -ne 2){throw 'Two exact original frame bodies required'}
foreach($irqRange in $irqMap.source_ranges){
    $irqSlice=[byte[]]::new($irqRange.bytes)
    [Array]::Copy($irqRaw,([int]$irqRange.address-32768),$irqSlice,0,$irqSlice.Length)
    if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($irqSlice)).ToLowerInvariant() -ne $irqRange.sha256){throw 'Original frame bytes changed'}
}
if(-not $ProofRoot){
    foreach($irqCandidate in @('apk-analysis\tsl9-v4160-entry-irq-contract-2026-10-21','analysis\v4160-entry-irq-contract-2026-10-21')){
        $irqFile=Join-Path $irqRepo $irqCandidate
        if(Test-Path -LiteralPath $irqFile){$ProofRoot=$irqFile;break}
    }
}
if(-not $ProofRoot){throw 'Retained source-proof directory required'}
$irqProofPins=@{}
$irqSealPath=Join-Path $ProofRoot $irqMap.proof_seal
if((Get-FileHash -LiteralPath $irqSealPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $irqMap.proof_seal_sha256){throw 'Exact independent original IRQ proof required'}
$irqSeal=Get-Content -LiteralPath $irqSealPath -Raw | ConvertFrom-Json
if(-not $irqSeal.passed){throw 'Completed independent source proof required'}
$irqScope=[IO.Path]::GetFullPath((Split-Path -Parent $irqSealPath))+[IO.Path]::DirectorySeparatorChar
foreach($irqMember in $irqSeal.members){
    $irqFile=[IO.Path]::GetFullPath((Join-Path $irqScope $irqMember.path))
    if(-not $irqFile.StartsWith($irqScope,[StringComparison]::OrdinalIgnoreCase) -or (Get-Item -LiteralPath $irqFile).Length -ne $irqMember.bytes -or (Get-FileHash -LiteralPath $irqFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne $irqMember.sha256){throw 'Actual sealed source-proof member required'}
    $irqProofPins[$irqFile]=$irqMember.sha256
}
$irqFrameMapPath=Join-Path $ProofRoot $irqMap.frame_map
if((Get-FileHash -LiteralPath $irqFrameMapPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $irqMap.frame_map_sha256){throw 'Exact source-derived29-register map required'}
$irqProofPins[$irqSealPath]=$irqMap.proof_seal_sha256
$irqNames=@('src\irq_frames.c','src\irq_frames.h','tests\test_irq_frames.c','verify.ps1','source-map.json','README.md')
$irqPins=@{}
foreach($irqName in $irqNames){$irqPins[$irqName]=(Get-FileHash -LiteralPath (Join-Path $irqRoot $irqName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$irqVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $irqVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $irqVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$irqVersion=(Get-Content -LiteralPath (Join-Path $irqVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$irqCompiler=Join-Path $irqVs ('VC\Tools\MSVC\'+$irqVersion+'\bin\Hostx64\x64\cl.exe')
$irqMode=if($Cpp){'cpp'}else{'c'}
$irqBuild=Join-Path $irqRoot ('build\'+[Guid]::NewGuid().ToString('N')+'-'+$irqMode)
New-Item -ItemType Directory -Path $irqBuild | Out-Null
$irqExe=Join-Path $irqBuild 'host-frame-tests.exe'
$irqFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $irqRoot 'src')),('/Fo'+$irqBuild+'\'))
$irqFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $irqCompiler @irqFlags (Join-Path $irqRoot 'src\irq_frames.c') (Join-Path $irqRoot 'tests\test_irq_frames.c') ('/Fe'+$irqExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Own host frame compilation failed'}
$irqOutput=& $irqExe
if($LASTEXITCODE -ne 0){throw 'Own host frame behavior failed'}
$irqTests=$irqOutput | ConvertFrom-Json
if(-not $irqTests.passed -or $irqTests.groups -ne 16){throw 'Complete finite frame behavior evidence required'}
foreach($irqName in $irqNames){if($irqPins[$irqName] -ne (Get-FileHash -LiteralPath (Join-Path $irqRoot $irqName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source changed during verification'}}
foreach($irqFile in $irqProofPins.Keys){if($irqProofPins[$irqFile] -ne (Get-FileHash -LiteralPath $irqFile -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source proof changed during verification'}}
$irqReceipt=@{schema='ID2966-irq-frame-host-model-verification-v1';passed=$true;mode=$irqMode;tests=$irqTests;source_sha256=$irqPins;proof_sha256=$irqProofPins;firmware_sha256=$irqMap.firmware_sha256;executable=$irqExe;executable_sha256=(Get-FileHash -LiteralPath $irqExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$irqCompiler;compiler_sha256=(Get-FileHash -LiteralPath $irqCompiler -Algorithm SHA256).Hash.ToLowerInvariant();original_executed=$false;CPU_stepper=$false;emulation=$false;network=$false;hardware=$false;native_BIN=$false;physical_IRQ_ABI_proved=$false;OTA_ready=$false}
$irqReceipt | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $irqBuild 'verification.json') -Encoding utf8
Write-Output ('FRAME_RESULT '+($irqReceipt|ConvertTo-Json -Depth 10 -Compress))
