param([switch]$Cpp,[string]$Carrier,[string]$Tail,[string]$ProofRoot,[string]$Runtime)
$ErrorActionPreference='Stop'
$riRoot=$PSScriptRoot
$riRepo=(Resolve-Path (Join-Path $riRoot '../..')).Path
if(-not $ProofRoot){foreach($riName in @('apk-analysis/tsl9-resident-entry-reference-2026-10-21/source','analysis/resident-entry-reference-2026-10-21/source')){$riPath=Join-Path $riRepo $riName;if(Test-Path -LiteralPath $riPath){$ProofRoot=$riPath;break}}}
if(-not $Carrier){foreach($riName in @('apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin','analysis/resident-entry-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin')){$riPath=Join-Path $riRepo $riName;if(Test-Path -LiteralPath $riPath){$Carrier=$riPath;break}}}
if(-not $Tail){foreach($riName in @('apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-0006EAA4-0006EB2C.bin','analysis/resident-entry-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-0006EAA4-0006EB2C.bin')){$riPath=Join-Path $riRepo $riName;if(Test-Path -LiteralPath $riPath){$Tail=$riPath;break}}}
if(-not $Runtime){foreach($riName in @('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')){$riPath=Join-Path $riRepo $riName;if(Test-Path -LiteralPath $riPath){$Runtime=$riPath;break}}}
if(-not $Carrier -or -not $Tail -or -not $ProofRoot -or -not $Runtime){throw 'Exact candidate segments, source proof and Runtime required'}
$riMap=Get-Content -LiteralPath (Join-Path $riRoot 'source-map.json') -Raw | ConvertFrom-Json
$riInputs=@{};$riInputs[$Carrier]=$riMap.carrier_sha256;$riInputs[$Tail]=$riMap.tail_sha256;$riInputs[$Runtime]=$riMap.runtime_sha256
if((Get-Item -LiteralPath $Carrier).Length -ne $riMap.carrier_bytes -or (Get-Item -LiteralPath $Tail).Length -ne $riMap.tail_bytes){throw 'Exact segment sizes'}
$riSealPath=Join-Path $ProofRoot 'final-audit.json';$riInputs[$riSealPath]=$riMap.source_seal_sha256
if((Get-FileHash -LiteralPath $riSealPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $riMap.source_seal_sha256){throw 'Exact source seal required'}
$riSeal=Get-Content -LiteralPath $riSealPath -Raw | ConvertFrom-Json
if(-not $riSeal.passed -or -not $riSeal.sealed){throw 'Completed selected source required'}
$riContained=[IO.Path]::GetFullPath($ProofRoot)+[IO.Path]::DirectorySeparatorChar
foreach($riMember in $riSeal.members){$riPath=[IO.Path]::GetFullPath((Join-Path $ProofRoot $riMember.path));if(-not $riPath.StartsWith($riContained,[StringComparison]::OrdinalIgnoreCase) -or (Get-Item -LiteralPath $riPath).Length -ne $riMember.bytes){throw 'Contained proof member'};$riInputs[$riPath]=$riMember.sha256}
foreach($riProperty in $riMap.reset_inputs.PSObject.Properties){$riInputs[(Join-Path $riRepo $riProperty.Name)]=$riProperty.Value}
foreach($riPath in $riInputs.Keys){if((Get-FileHash -LiteralPath $riPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $riInputs[$riPath]){throw 'Source/reference/dependency changed'}}
$riNames=@('src/resident_entry.c','src/resident_entry.h','src/reset_entry_bridge.c','src/reset_entry_bridge.h','tests/test_resident_entry.c','tests/run-tests.ps1','verify.ps1','source-map.json','README.md')
$riPins=@{};foreach($riName in $riNames){$riPins[$riName]=(Get-FileHash -LiteralPath (Join-Path $riRoot $riName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$riPython=$env:TSL9_PYTHON
$riPythonPrefix=@()
if(-not $riPython){
    $riPythonCommand=Get-Command python -CommandType Application -ErrorAction SilentlyContinue
    if($riPythonCommand){$riPython=$riPythonCommand.Source}else{
        $riPythonCommand=Get-Command py -CommandType Application -ErrorAction SilentlyContinue
        if(-not $riPythonCommand){throw 'Set TSL9_PYTHON to a Python 3 executable, or add python/py to PATH.'}
        $riPython=$riPythonCommand.Source
        $riPythonPrefix=@('-3')
    }
}
$riProofText=& $riPython @riPythonPrefix -X utf8 -B (Join-Path $ProofRoot 'inspect-source.py') --check --carrier $Carrier --source-root $ProofRoot
if($LASTEXITCODE -ne 0){throw 'Resident entry raw source replay failed'}
$riProof=$riProofText | ConvertFrom-Json
if(-not $riProof.passed -or $riProof.body_bytes -ne 230 -or $riProof.body_instructions -ne 66 -or $riProof.header_bytes -ne 4 -or $riProof.raw_operand_mutation_rejections -ne 35){throw 'Complete selected source required'}
$riTestText=& (Join-Path $riRoot 'tests/run-tests.ps1') -Cpp:$Cpp
$riBuild=$riTestText | ConvertFrom-Json
if(-not $riBuild.passed -or $riBuild.tests.groups -ne 5 -or $riBuild.tests.checks -ne 121496){throw 'Complete current entry suite required'}
foreach($riName in $riNames){if($riPins[$riName] -ne (Get-FileHash -LiteralPath (Join-Path $riRoot $riName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Model changed during verification'}}
foreach($riPath in $riInputs.Keys){if($riInputs[$riPath] -ne (Get-FileHash -LiteralPath $riPath -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Evidence changed during verification'}}
$riReceipt=@{schema='TSL9-resident-entry-reference-host-verification-v1';passed=$true;mode=$riBuild.mode;tests=$riBuild.tests;source_sha256=$riPins;input_sha256=$riInputs;original_source=$riProof;executable=$riBuild.executable;executable_sha256=$riBuild.executable_sha256;compiler=$riBuild.compiler;compiler_sha256=$riBuild.compiler_sha256;original_executed=$false;ISA_emulation=$false;network=$false;hardware=$false;reference_candidate_only=$true;holes_filled=$false;native_BIN=$false;OTA_ready=$false;original_ABI_proved=$false}
$riReceiptPath=Join-Path (Split-Path -Parent $riBuild.executable) 'verification.json'
$riReceipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $riReceiptPath -Encoding utf8
Write-Output ('RESIDENT_ENTRY_RESULT '+(@{passed=$true;mode=$riBuild.mode;tests=$riBuild.tests;receipt=$riReceiptPath;hardware=$false;OTA_ready=$false}|ConvertTo-Json -Depth 8 -Compress))
