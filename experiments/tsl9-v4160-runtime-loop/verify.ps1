param([switch]$Cpp,[string]$Firmware,[string]$ProofRoot)
$ErrorActionPreference='Stop'
$mlRoot=$PSScriptRoot
$mlRepo=(Resolve-Path (Join-Path $mlRoot '../..')).Path
if(-not $ProofRoot){foreach($mlName in @('apk-analysis/tsl9-v4160-runtime-loop-2026-10-21/source','analysis/v4160-runtime-loop-2026-10-21/source')){$mlPath=Join-Path $mlRepo $mlName;if(Test-Path -LiteralPath $mlPath){$ProofRoot=$mlPath;break}}}
if(-not $Firmware){foreach($mlName in @('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')){$mlPath=Join-Path $mlRepo $mlName;if(Test-Path -LiteralPath $mlPath){$Firmware=$mlPath;break}}}
if(-not $Firmware -or -not $ProofRoot){throw 'Exact Runtime and sealed source proof required'}
$mlMap=Get-Content -LiteralPath (Join-Path $mlRoot 'source-map.json') -Raw | ConvertFrom-Json
$mlInputs=@{};$mlInputs[$Firmware]=$mlMap.runtime_sha256
if((Get-Item -LiteralPath $Firmware).Length -ne $mlMap.runtime_bytes){throw 'Exact Runtime size required'}
$mlSealPath=Join-Path $ProofRoot 'final-audit.json';$mlInputs[$mlSealPath]=$mlMap.source_seal_sha256
if((Get-FileHash -LiteralPath $mlSealPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mlMap.source_seal_sha256){throw 'Exact completed source seal required'}
$mlSeal=Get-Content -LiteralPath $mlSealPath -Raw | ConvertFrom-Json
if(-not $mlSeal.passed -or -not $mlSeal.sealed){throw 'Completed source proof required'}
$mlContained=[IO.Path]::GetFullPath($ProofRoot)+[IO.Path]::DirectorySeparatorChar
foreach($mlMember in $mlSeal.members){$mlPath=[IO.Path]::GetFullPath((Join-Path $ProofRoot $mlMember.path));if(-not $mlPath.StartsWith($mlContained,[StringComparison]::OrdinalIgnoreCase) -or (Get-Item -LiteralPath $mlPath).Length -ne $mlMember.bytes){throw 'Contained proof member'};$mlInputs[$mlPath]=$mlMember.sha256}
foreach($mlProperty in $mlMap.dependency_inputs.PSObject.Properties){$mlInputs[(Join-Path $mlRepo $mlProperty.Name)]=$mlProperty.Value}
foreach($mlPath in $mlInputs.Keys){if((Get-FileHash -LiteralPath $mlPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mlInputs[$mlPath]){throw 'Source/reference/dependency changed'}}
$mlNames=@('src/runtime_loop.c','src/runtime_loop.h','tests/test_runtime_loop.c','tests/run-tests.ps1','verify.ps1','source-map.json','README.md')
$mlPins=@{};foreach($mlName in $mlNames){$mlPins[$mlName]=(Get-FileHash -LiteralPath (Join-Path $mlRoot $mlName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$mlPython='C:/Users/locky/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe'
$mlProofText=& $mlPython -X utf8 -B (Join-Path $ProofRoot 'inspect-source.py') --check --firmware $Firmware --source-root $ProofRoot
if($LASTEXITCODE -ne 0){throw 'Runtime-loop raw source replay failed'}
$mlProof=$mlProofText | ConvertFrom-Json
if(-not $mlProof.passed -or $mlProof.bytes -ne $mlMap.body_bytes -or $mlProof.instructions -ne $mlMap.body_instructions -or $mlProof.raw_operand_mutation_rejections -ne $mlMap.raw_operand_mutation_rejections){throw 'Complete selected source proof required'}
$mlTestText=& (Join-Path $mlRoot 'tests/run-tests.ps1') -Cpp:$Cpp
$mlBuild=$mlTestText | ConvertFrom-Json
if(-not $mlBuild.passed -or $mlBuild.tests.groups -ne $mlMap.expected_tests.groups -or $mlBuild.tests.checks -ne $mlMap.expected_tests.checks){throw 'Complete current runtime-loop suite required'}
foreach($mlName in $mlNames){if($mlPins[$mlName] -ne (Get-FileHash -LiteralPath (Join-Path $mlRoot $mlName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Model changed during verification'}}
foreach($mlPath in $mlInputs.Keys){if($mlInputs[$mlPath] -ne (Get-FileHash -LiteralPath $mlPath -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Evidence changed during verification'}}
$mlReceipt=@{schema='TSL9-v4160-runtime-loop-host-verification-v1';passed=$true;mode=$mlBuild.mode;tests=$mlBuild.tests;source_sha256=$mlPins;input_sha256=$mlInputs;original_source=$mlProof;executable=$mlBuild.executable;executable_sha256=$mlBuild.executable_sha256;compiler=$mlBuild.compiler;compiler_sha256=$mlBuild.compiler_sha256;original_executed=$false;ISA_emulation=$false;network=$false;hardware=$false;native_BIN=$false;OTA_ready=$false;original_ABI_proved=$false}
$mlReceiptPath=Join-Path (Split-Path -Parent $mlBuild.executable) 'verification.json'
$mlReceipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $mlReceiptPath -Encoding utf8
Write-Output ('RUNTIME_LOOP_RESULT '+(@{passed=$true;mode=$mlBuild.mode;tests=$mlBuild.tests;receipt=$mlReceiptPath;hardware=$false;OTA_ready=$false}|ConvertTo-Json -Depth 8 -Compress))
