param([switch]$Cpp,[string]$Firmware,[string]$ProofRoot,[string]$LegacyRoot)
$ErrorActionPreference='Stop'
$bcRoot=$PSScriptRoot
$bcRepo=(Resolve-Path (Join-Path $bcRoot '..\..')).Path
if(-not $Firmware){
    foreach($bcName in @('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin')){
        $bcPath=Join-Path $bcRepo $bcName
        if(Test-Path -LiteralPath $bcPath){$Firmware=$bcPath;break}
    }
}
if(-not $ProofRoot){
    foreach($bcName in @('apk-analysis/tsl9-boot2580-command-adapter-2026-10-21/source','analysis/boot2580-command-adapter-2026-10-21/source')){
        $bcPath=Join-Path $bcRepo $bcName
        if(Test-Path -LiteralPath $bcPath){$ProofRoot=$bcPath;break}
    }
}
if(-not $LegacyRoot){$LegacyRoot=Join-Path $bcRepo 'experiments/tsl9-contract-model'}
if(-not $Firmware -or -not $ProofRoot){throw 'Exact selected BOOT and retained source proof required'}
$bcMap=Get-Content -LiteralPath (Join-Path $bcRoot 'source-map.json') -Raw | ConvertFrom-Json
$bcInputs=@{}
$bcInputs[$Firmware]=$bcMap.firmware_sha256
if((Get-Item -LiteralPath $Firmware).Length -ne $bcMap.firmware_bytes){throw 'Original BOOT size'}
$bcSealPath=Join-Path $ProofRoot 'final-audit.json'
if((Get-FileHash -LiteralPath $bcSealPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $bcMap.source_seal_sha256){throw 'Selected raw source seal'}
$bcInputs[$bcSealPath]=$bcMap.source_seal_sha256
$bcSeal=Get-Content -LiteralPath $bcSealPath -Raw | ConvertFrom-Json
if(-not $bcSeal.passed -or -not $bcSeal.sealed){throw 'Completed source evidence required'}
$bcContained=[IO.Path]::GetFullPath($ProofRoot)+[IO.Path]::DirectorySeparatorChar
foreach($bcMember in $bcSeal.members){
    $bcPath=[IO.Path]::GetFullPath((Join-Path $ProofRoot $bcMember.path))
    if(-not $bcPath.StartsWith($bcContained,[StringComparison]::OrdinalIgnoreCase) -or (Get-Item -LiteralPath $bcPath).Length -ne $bcMember.bytes){throw 'Contained original proof member'}
    $bcInputs[$bcPath]=$bcMember.sha256
}
foreach($bcProperty in $bcMap.legacy_inputs.PSObject.Properties){$bcInputs[(Join-Path $LegacyRoot $bcProperty.Name)]=$bcProperty.Value}
foreach($bcPath in $bcInputs.Keys){if((Get-FileHash -LiteralPath $bcPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $bcInputs[$bcPath]){throw 'Original input changed'}}
$bcNames=@('src/boot_command.c','src/boot_command.h','src/boot_fp_bridge.c','src/boot_fp_bridge.h','tests/test_boot_command.c','verify.ps1','source-map.json','README.md')
$bcPins=@{}
foreach($bcName in $bcNames){$bcPins[$bcName]=(Get-FileHash -LiteralPath (Join-Path $bcRoot $bcName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$bcPython=$env:TSL9_PYTHON
$bcPythonPrefix=@()
if(-not $bcPython){
    $bcPythonCommand=Get-Command python -CommandType Application -ErrorAction SilentlyContinue
    if($bcPythonCommand){$bcPython=$bcPythonCommand.Source}else{
        $bcPythonCommand=Get-Command py -CommandType Application -ErrorAction SilentlyContinue
        if(-not $bcPythonCommand){throw 'Set TSL9_PYTHON to a Python 3 executable, or add python/py to PATH.'}
        $bcPython=$bcPythonCommand.Source
        $bcPythonPrefix=@('-3')
    }
}
$bcProofText=& $bcPython @bcPythonPrefix -X utf8 -B (Join-Path $ProofRoot 'inspect-source.py') --check --firmware $Firmware --source-root $ProofRoot
if($LASTEXITCODE -ne 0){throw 'Actual original selected BOOT source replay failed'}
$bcProof=$bcProofText | ConvertFrom-Json
if(-not $bcProof.passed -or $bcProof.body_bytes -ne 414 -or $bcProof.instructions -ne 144 -or $bcProof.raw_mutation_rejections -ne 18){throw 'Complete selected command source required'}
$bcVs='C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools'
Import-Module (Join-Path $bcVs 'Common7/Tools/Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $bcVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$bcVersion=(Get-Content -LiteralPath (Join-Path $bcVs 'VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$bcCompiler=Join-Path $bcVs ('VC/Tools/MSVC/'+$bcVersion+'/bin/Hostx64/x64/cl.exe')
$bcMode=if($Cpp){'cpp'}else{'c'}
$bcBuild=Join-Path $bcRoot ('build/'+[guid]::NewGuid().ToString('N')+'-'+$bcMode)
New-Item -ItemType Directory -Path $bcBuild | Out-Null
$bcExe=Join-Path $bcBuild 'host-boot-command-tests.exe'
$bcFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $bcRoot 'src')),('/I'+(Join-Path $LegacyRoot 'src')),('/Fo'+$bcBuild+'/'))
$bcFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$bcLog=& $bcCompiler @bcFlags (Join-Path $bcRoot 'src/boot_command.c') (Join-Path $bcRoot 'src/boot_fp_bridge.c') (Join-Path $LegacyRoot 'src/flash_page.c') (Join-Path $bcRoot 'tests/test_boot_command.c') ('/Fe'+$bcExe) /link /INCREMENTAL:NO 2>&1
$bcLog | Set-Content -LiteralPath (Join-Path $bcBuild 'compiler.log') -Encoding utf8
if($LASTEXITCODE -ne 0){throw ('Own host command compilation failed: '+($bcLog -join [Environment]::NewLine))}
$bcOutput=& $bcExe
if($LASTEXITCODE -ne 0){throw 'Own host command behavior failed'}
$bcTests=$bcOutput | ConvertFrom-Json
if(-not $bcTests.passed -or $bcTests.groups -ne 11 -or $bcTests.checks -ne 5515){throw 'Complete current behavior suite required'}
foreach($bcName in $bcNames){if($bcPins[$bcName] -ne (Get-FileHash -LiteralPath (Join-Path $bcRoot $bcName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source changed during verification'}}
foreach($bcPath in $bcInputs.Keys){if($bcInputs[$bcPath] -ne (Get-FileHash -LiteralPath $bcPath -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Original input changed during verification'}}
$bcReceipt=@{schema='BOOT2580-numeric-live-host-verification-v1';passed=$true;mode=$bcMode;tests=$bcTests;source_sha256=$bcPins;input_sha256=$bcInputs;original_source=$bcProof;executable=$bcExe;executable_sha256=(Get-FileHash -LiteralPath $bcExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$bcCompiler;compiler_sha256=(Get-FileHash -LiteralPath $bcCompiler -Algorithm SHA256).Hash.ToLowerInvariant();original_executed=$false;ISA_emulation=$false;network=$false;hardware=$false;OTA_ready=$false;native_BIN=$false;original_ABI_proved=$false}
$bcReceipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $bcBuild 'verification.json') -Encoding utf8
Write-Output ('BOOT_COMMAND_RESULT '+(@{passed=$true;mode=$bcMode;groups=$bcTests.groups;checks=$bcTests.checks;receipt=(Join-Path $bcBuild 'verification.json');hardware=$false;OTA_ready=$false}|ConvertTo-Json -Compress))
