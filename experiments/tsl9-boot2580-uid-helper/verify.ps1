param([switch]$Cpp,[string]$Firmware,[string]$ProofRoot,[string]$CommandRoot)
$ErrorActionPreference='Stop'
$ubRoot=$PSScriptRoot
$ubRepo=(Resolve-Path (Join-Path $ubRoot '..\..')).Path
if(-not $Firmware){
    foreach($ubName in @('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin')){
        $ubPath=Join-Path $ubRepo $ubName
        if(Test-Path -LiteralPath $ubPath){$Firmware=$ubPath;break}
    }
}
if(-not $ProofRoot){
    foreach($ubName in @('apk-analysis/tsl9-boot2580-uid-helper-2026-10-21/source','analysis/boot2580-uid-helper-2026-10-21/source')){
        $ubPath=Join-Path $ubRepo $ubName
        if(Test-Path -LiteralPath $ubPath){$ProofRoot=$ubPath;break}
    }
}
if(-not $CommandRoot){$CommandRoot=Join-Path $ubRepo 'experiments/tsl9-boot2580-command-adapter'}
if(-not $Firmware -or -not $ProofRoot){throw 'Exact selected BOOT and source proof required'}
$ubMap=Get-Content -LiteralPath (Join-Path $ubRoot 'source-map.json') -Raw | ConvertFrom-Json
if((Get-Item -LiteralPath $Firmware).Length -ne $ubMap.firmware_bytes){throw 'Original BOOT size'}
$ubInputs=@{};$ubInputs[$Firmware]=$ubMap.firmware_sha256
$ubSealPath=Join-Path $ProofRoot 'final-audit.json'
if((Get-FileHash -LiteralPath $ubSealPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ubMap.source_seal_sha256){throw 'Exact helper source seal'}
$ubInputs[$ubSealPath]=$ubMap.source_seal_sha256
$ubSeal=Get-Content -LiteralPath $ubSealPath -Raw | ConvertFrom-Json
if(-not $ubSeal.passed -or -not $ubSeal.sealed){throw 'Completed helper evidence required'}
$ubContained=[IO.Path]::GetFullPath($ProofRoot)+[IO.Path]::DirectorySeparatorChar
foreach($ubMember in $ubSeal.members){
    $ubPath=[IO.Path]::GetFullPath((Join-Path $ProofRoot $ubMember.path))
    if(-not $ubPath.StartsWith($ubContained,[StringComparison]::OrdinalIgnoreCase) -or (Get-Item -LiteralPath $ubPath).Length -ne $ubMember.bytes){throw 'Contained source proof member'}
    $ubInputs[$ubPath]=$ubMember.sha256
}
foreach($ubProperty in $ubMap.command_inputs.PSObject.Properties){$ubInputs[(Join-Path $CommandRoot $ubProperty.Name)]=$ubProperty.Value}
foreach($ubPath in $ubInputs.Keys){if((Get-FileHash -LiteralPath $ubPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ubInputs[$ubPath]){throw 'Original helper input changed'}}
$ubNames=@('src/uid_helper.c','src/uid_helper.h','tests/test_uid_helper.c','verify.ps1','source-map.json','README.md')
$ubPins=@{}
foreach($ubName in $ubNames){$ubPins[$ubName]=(Get-FileHash -LiteralPath (Join-Path $ubRoot $ubName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$ubPython=$env:TSL9_PYTHON
$ubPythonPrefix=@()
if(-not $ubPython){
    $ubPythonCommand=Get-Command python -CommandType Application -ErrorAction SilentlyContinue
    if($ubPythonCommand){$ubPython=$ubPythonCommand.Source}else{
        $ubPythonCommand=Get-Command py -CommandType Application -ErrorAction SilentlyContinue
        if(-not $ubPythonCommand){throw 'Set TSL9_PYTHON to a Python 3 executable, or add python/py to PATH.'}
        $ubPython=$ubPythonCommand.Source
        $ubPythonPrefix=@('-3')
    }
}
$ubProofText=& $ubPython @ubPythonPrefix -X utf8 -B (Join-Path $ProofRoot 'inspect-source.py') --check --firmware $Firmware --source-root $ProofRoot
if($LASTEXITCODE -ne 0){throw 'Original helper source replay failed'}
$ubProof=$ubProofText | ConvertFrom-Json
if(-not $ubProof.passed -or $ubProof.bytes -ne 122 -or $ubProof.instructions -ne 48 -or $ubProof.raw_mutation_rejections -ne 24){throw 'Complete selected UID helper source required'}
$ubVs='C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools'
Import-Module (Join-Path $ubVs 'Common7/Tools/Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $ubVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$ubVersion=(Get-Content -LiteralPath (Join-Path $ubVs 'VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$ubCompiler=Join-Path $ubVs ('VC/Tools/MSVC/'+$ubVersion+'/bin/Hostx64/x64/cl.exe')
$ubMode=if($Cpp){'cpp'}else{'c'}
$ubBuild=Join-Path $ubRoot ('build/'+[guid]::NewGuid().ToString('N')+'-'+$ubMode)
New-Item -ItemType Directory -Path $ubBuild | Out-Null
$ubExe=Join-Path $ubBuild 'host-uid-helper-tests.exe'
$ubFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $ubRoot 'src')),('/I'+(Join-Path $CommandRoot 'src')),('/Fo'+$ubBuild+'/'))
$ubFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$ubLog=& $ubCompiler @ubFlags (Join-Path $ubRoot 'src/uid_helper.c') (Join-Path $ubRoot 'tests/test_uid_helper.c') ('/Fe'+$ubExe) /link /INCREMENTAL:NO 2>&1
$ubLog | Set-Content -LiteralPath (Join-Path $ubBuild 'compiler.log') -Encoding utf8
if($LASTEXITCODE -ne 0){throw ('Own helper compilation failed: '+($ubLog -join [Environment]::NewLine))}
$ubOutput=& $ubExe
if($LASTEXITCODE -ne 0){throw 'Own helper behavior failed'}
$ubTests=$ubOutput | ConvertFrom-Json
if(-not $ubTests.passed -or $ubTests.groups -ne 6 -or $ubTests.checks -ne 817){throw 'Complete current helper suite required'}
foreach($ubName in $ubNames){if($ubPins[$ubName] -ne (Get-FileHash -LiteralPath (Join-Path $ubRoot $ubName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Helper source changed during verification'}}
foreach($ubPath in $ubInputs.Keys){if($ubInputs[$ubPath] -ne (Get-FileHash -LiteralPath $ubPath -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Helper evidence changed during verification'}}
$ubReceipt=@{schema='BOOT2580-uid-helper-host-verification-v1';passed=$true;mode=$ubMode;tests=$ubTests;source_sha256=$ubPins;input_sha256=$ubInputs;original_source=$ubProof;executable=$ubExe;executable_sha256=(Get-FileHash -LiteralPath $ubExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$ubCompiler;compiler_sha256=(Get-FileHash -LiteralPath $ubCompiler -Algorithm SHA256).Hash.ToLowerInvariant();original_executed=$false;ISA_emulation=$false;real_UID_used=$false;network=$false;hardware=$false;OTA_ready=$false;native_BIN=$false;original_ABI_proved=$false}
$ubReceipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $ubBuild 'verification.json') -Encoding utf8
Write-Output ('UID_HELPER_RESULT '+(@{passed=$true;mode=$ubMode;groups=$ubTests.groups;checks=$ubTests.checks;receipt=(Join-Path $ubBuild 'verification.json');hardware=$false;OTA_ready=$false}|ConvertTo-Json -Compress))
