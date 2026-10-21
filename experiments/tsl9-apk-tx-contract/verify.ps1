param([switch]$Cpp,[string]$Apk,[string]$ProofRoot,[string]$RxRoot)
$ErrorActionPreference='Stop'
$txRoot=$PSScriptRoot
$txRepo=(Resolve-Path (Join-Path $txRoot '..\..')).Path
if(-not $Apk){
    foreach($txCandidate in @('publish-tsl9/artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk','artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk')){
        $txPath=Join-Path $txRepo $txCandidate
        if(Test-Path -LiteralPath $txPath){$Apk=$txPath;break}
    }
}
if(-not $ProofRoot){
    foreach($txCandidate in @('apk-analysis/tsl9-v4160-ota-handoff-2026-10-21','analysis/v4160-ota-handoff-2026-10-21')){
        $txPath=Join-Path $txRepo $txCandidate
        if(Test-Path -LiteralPath $txPath){$ProofRoot=$txPath;break}
    }
}
if(-not $RxRoot){$RxRoot=Join-Path $txRepo 'experiments/tsl9-apk-ota-contract'}
if(-not $Apk -or -not $ProofRoot){throw 'Exact APK and sealed source proof required'}
$txNames=@('src/apk_tx.c','src/apk_tx.h','tests/test_apk_tx.c','verify.ps1','verify-source.py','source-map.json','README.md')
$txPins=@{}
foreach($txName in $txNames){$txPins[$txName]=(Get-FileHash -LiteralPath (Join-Path $txRoot $txName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$txPython='C:/Users/locky/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe'
$txProofText=& $txPython -X utf8 -B (Join-Path $txRoot 'verify-source.py') --apk $Apk --proof-root $ProofRoot --rx-root $RxRoot
if($LASTEXITCODE -ne 0){throw 'Actual original APK source check failed'}
$txProof=$txProofText | ConvertFrom-Json
if(-not $txProof.passed -or $txProof.sender_sections -ne 21 -or $txProof.receiver_sections -ne 6){throw 'Exact sender/receiver proof required'}
$txMap=Get-Content -LiteralPath (Join-Path $txRoot 'source-map.json') -Raw | ConvertFrom-Json
$txExtra=@{}
foreach($txProperty in $txMap.receive_inputs.PSObject.Properties){$txExtra[(Join-Path $RxRoot $txProperty.Name)]=$txProperty.Value}
$txExtra[$Apk]=$txMap.apk_sha256
foreach($txProperty in $txProof.sealed_inputs.PSObject.Properties){$txExtra[$txProperty.Name]=$txProperty.Value}
$txVs='C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools'
Import-Module (Join-Path $txVs 'Common7/Tools/Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $txVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$txVersion=(Get-Content -LiteralPath (Join-Path $txVs 'VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$txCompiler=Join-Path $txVs ('VC/Tools/MSVC/'+$txVersion+'/bin/Hostx64/x64/cl.exe')
$txMode=if($Cpp){'cpp'}else{'c'}
$txBuild=Join-Path $txRoot ('build/'+[guid]::NewGuid().ToString('N')+'-'+$txMode)
New-Item -ItemType Directory -Path $txBuild | Out-Null
$txExe=Join-Path $txBuild 'host-sender-tests.exe'
$txFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $txRoot 'src')),('/I'+(Join-Path $RxRoot 'src')),('/Fo'+$txBuild+'/'))
$txFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$txLog=& $txCompiler @txFlags (Join-Path $txRoot 'src/apk_tx.c') (Join-Path $txRoot 'tests/test_apk_tx.c') (Join-Path $RxRoot 'src/apk_ota.c') ('/Fe'+$txExe) /link /INCREMENTAL:NO 2>&1
$txLog | Set-Content -LiteralPath (Join-Path $txBuild 'compiler.log') -Encoding utf8
if($LASTEXITCODE -ne 0){throw ('Own host sender compilation failed: '+($txLog -join [Environment]::NewLine))}
$txOutput=& $txExe
if($LASTEXITCODE -ne 0){throw 'Own host sender behavior failed'}
$txTests=$txOutput | ConvertFrom-Json
if(-not $txTests.passed -or $txTests.groups -ne 15){throw 'Full sender behavior evidence required'}
foreach($txName in $txNames){if($txPins[$txName] -ne (Get-FileHash -LiteralPath (Join-Path $txRoot $txName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source changed during verification'}}
foreach($txPath in $txExtra.Keys){if($txExtra[$txPath] -ne (Get-FileHash -LiteralPath $txPath -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source evidence changed during verification'}}
$txReceipt=@{schema='APK127-readable-shared-sender-host-v1';passed=$true;mode=$txMode;tests=$txTests;source_sha256=$txPins;proof=$txProof;input_sha256=$txExtra;executable=$txExe;executable_sha256=(Get-FileHash -LiteralPath $txExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$txCompiler;compiler_sha256=(Get-FileHash -LiteralPath $txCompiler -Algorithm SHA256).Hash.ToLowerInvariant();original_executed=$false;target_execution=$false;network=$false;BLE=$false;hardware=$false;native_BIN=$false;OTA_ready=$false}
$txReceipt | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath (Join-Path $txBuild 'verification.json') -Encoding utf8
Write-Output ('SENDER_RESULT '+(@{passed=$true;mode=$txMode;groups=$txTests.groups;checks=$txTests.checks;receipt=(Join-Path $txBuild 'verification.json');hardware=$false;OTA_ready=$false}|ConvertTo-Json -Compress))
