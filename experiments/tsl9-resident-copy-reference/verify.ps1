param([switch]$Cpp,[string]$Carrier,[string]$ProofRoot,[string]$Firmware)
$ErrorActionPreference='Stop'
$rpRoot=$PSScriptRoot
$rpRepo=(Resolve-Path (Join-Path $rpRoot '../..')).Path
if(-not $ProofRoot){
    foreach($rpName in @('apk-analysis/tsl9-resident-copy-reference-2026-10-21/source','analysis/resident-copy-reference-2026-10-21/source')){
        $rpPath=Join-Path $rpRepo $rpName;if(Test-Path -LiteralPath $rpPath){$ProofRoot=$rpPath;break}
    }
}
if(-not $Carrier){
    foreach($rpName in @('apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin','analysis/resident-copy-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin')){
        $rpPath=Join-Path $rpRepo $rpName;if(Test-Path -LiteralPath $rpPath){$Carrier=$rpPath;break}
    }
}
if(-not $Firmware){
    foreach($rpName in @('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin')){
        $rpPath=Join-Path $rpRepo $rpName;if(Test-Path -LiteralPath $rpPath){$Firmware=$rpPath;break}
    }
}
if(-not $ProofRoot -or -not $Carrier -or -not $Firmware){throw 'Exact reference carrier, proof and selected BOOT required'}
$rpMap=Get-Content -LiteralPath (Join-Path $rpRoot 'source-map.json') -Raw | ConvertFrom-Json
$rpInputs=@{};$rpInputs[$Carrier]=$rpMap.carrier_sha256;$rpInputs[$Firmware]=$rpMap.bridge_firmware_sha256
if((Get-Item -LiteralPath $Carrier).Length -ne $rpMap.carrier_bytes){throw 'Reference carrier size'}
$rpSealPath=Join-Path $ProofRoot 'final-audit.json';$rpInputs[$rpSealPath]=$rpMap.source_seal_sha256
if((Get-FileHash -LiteralPath $rpSealPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $rpMap.source_seal_sha256){throw 'Exact source seal required'}
$rpSeal=Get-Content -LiteralPath $rpSealPath -Raw | ConvertFrom-Json
if(-not $rpSeal.passed -or -not $rpSeal.sealed){throw 'Completed selected reference source required'}
$rpContained=[IO.Path]::GetFullPath($ProofRoot)+[IO.Path]::DirectorySeparatorChar
foreach($rpMember in $rpSeal.members){
    $rpPath=[IO.Path]::GetFullPath((Join-Path $ProofRoot $rpMember.path))
    if(-not $rpPath.StartsWith($rpContained,[StringComparison]::OrdinalIgnoreCase) -or (Get-Item -LiteralPath $rpPath).Length -ne $rpMember.bytes){throw 'Contained source member'}
    $rpInputs[$rpPath]=$rpMember.sha256
}
foreach($rpProperty in $rpMap.bridge_inputs.PSObject.Properties){$rpInputs[(Join-Path $rpRepo $rpProperty.Name)]=$rpProperty.Value}
foreach($rpPath in $rpInputs.Keys){if((Get-FileHash -LiteralPath $rpPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $rpInputs[$rpPath]){throw 'Source/reference/dependency changed'}}
$rpNames=@('src/reference_copy.c','src/reference_copy.h','tests/test_reference_copy.c','tests/run-tests.ps1','verify.ps1','source-map.json','README.md')
$rpPins=@{};foreach($rpName in $rpNames){$rpPins[$rpName]=(Get-FileHash -LiteralPath (Join-Path $rpRoot $rpName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$rpPython='C:/Users/locky/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe'
$rpProofText=& $rpPython -X utf8 -B (Join-Path $ProofRoot 'inspect-source.py') --check --carrier $Carrier --source-root $ProofRoot
if($LASTEXITCODE -ne 0){throw 'Reference source replay failed'}
$rpProof=$rpProofText | ConvertFrom-Json
if(-not $rpProof.passed -or $rpProof.helper_bytes -ne 58 -or $rpProof.helper_instructions -ne 18 -or $rpProof.raw_operand_mutation_rejections -ne 23){throw 'Complete selected source required'}
$rpTestText=& (Join-Path $rpRoot 'tests/run-tests.ps1') -Cpp:$Cpp
$rpBuild=$rpTestText | ConvertFrom-Json
if(-not $rpBuild.passed -or $rpBuild.tests.groups -ne 5 -or $rpBuild.tests.checks -ne 772){throw 'Complete current suite required'}
foreach($rpName in $rpNames){if($rpPins[$rpName] -ne (Get-FileHash -LiteralPath (Join-Path $rpRoot $rpName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Model changed during verification'}}
foreach($rpPath in $rpInputs.Keys){if($rpInputs[$rpPath] -ne (Get-FileHash -LiteralPath $rpPath -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Evidence changed during verification'}}
$rpReceipt=@{schema='TSL9-reference-copy-host-verification-v1';passed=$true;mode=$rpBuild.mode;tests=$rpBuild.tests;source_sha256=$rpPins;input_sha256=$rpInputs;original_source=$rpProof;executable=$rpBuild.executable;executable_sha256=$rpBuild.executable_sha256;compiler=$rpBuild.compiler;compiler_sha256=$rpBuild.compiler_sha256;original_executed=$false;ISA_emulation=$false;network=$false;hardware=$false;real_UID_used=$false;reference_candidate_only=$true;native_BIN=$false;OTA_ready=$false;original_ABI_proved=$false}
$rpReceiptPath=Join-Path (Split-Path -Parent $rpBuild.executable) 'verification.json'
$rpReceipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $rpReceiptPath -Encoding utf8
Write-Output ('REFERENCE_COPY_RESULT '+(@{passed=$true;mode=$rpBuild.mode;tests=$rpBuild.tests;receipt=$rpReceiptPath;hardware=$false;OTA_ready=$false}|ConvertTo-Json -Depth 8 -Compress))
