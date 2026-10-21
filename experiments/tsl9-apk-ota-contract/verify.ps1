param([switch]$Cpp,[switch]$ExpectRed,[string]$Apk,[string]$Python)
$ErrorActionPreference='Stop'
$caseRoot=$PSScriptRoot
$caseVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $caseVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $caseVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$caseVersion=(Get-Content -LiteralPath (Join-Path $caseVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$caseCompiler=Join-Path $caseVs ('VC\Tools\MSVC\'+$caseVersion+'\bin\Hostx64\x64\cl.exe')
$caseMode=if($Cpp){'cpp'}else{'c'}
$caseBuild=Join-Path $caseRoot ('build\'+[Guid]::NewGuid().ToString('N')+'-'+$caseMode)
New-Item -ItemType Directory -Path $caseBuild | Out-Null
if(-not $Python){
    $caseBundledPython='C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
    if(Test-Path -LiteralPath $caseBundledPython){$Python=$caseBundledPython}else{$Python=(Get-Command python -ErrorAction Stop).Source}
}
$caseSourceArgs=@('-X','utf8','-B',(Join-Path $caseRoot 'verify-source.py'))
if($Apk){$caseSourceArgs+=@('--apk',$Apk)}
$caseSourceOutput=& $Python @caseSourceArgs
if($LASTEXITCODE -ne 0){throw 'Original APK/source-chain verification failed'}
$caseSource=$caseSourceOutput | ConvertFrom-Json
if(-not $caseSource.passed -or -not $caseSource.source_chain_verified){throw 'Source receipt missing'}
$caseSourceOutput | Set-Content -LiteralPath (Join-Path $caseBuild 'source-verification.json') -Encoding utf8
$caseInputs=@('src\apk_ota.h','src\apk_ota.c','tests\test_apk_ota.c','verify.ps1','verify-source.py','source-map.json','README.md')
$casePins=@{}
foreach($caseName in $caseInputs){$casePins[$caseName]=(Get-FileHash -LiteralPath (Join-Path $caseRoot $caseName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$caseExe=Join-Path $caseBuild 'apk-receive-tests.exe'
$caseFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $caseRoot 'src')),('/Fo'+$caseBuild+'\'))
$caseFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $caseCompiler @caseFlags (Join-Path $caseRoot 'src\apk_ota.c') (Join-Path $caseRoot 'tests\test_apk_ota.c') ('/Fe'+$caseExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Host C/C++ compilation failed'}
$caseOutput=& $caseExe 2>&1
$caseExit=$LASTEXITCODE
$caseOutput | Set-Content -LiteralPath (Join-Path $caseBuild 'host-test.log') -Encoding utf8
if($ExpectRed){if($caseExit -ne 1 -or "$caseOutput" -notmatch 'ak_verify\(page,1,page,sizeof\(page\)\)==AK_YES'){throw 'Expected initial missing-prefix-acceptance test failure not observed'}}
elseif($caseExit -ne 0){throw ('Host tests failed: '+$caseOutput)}
foreach($caseName in $caseInputs){if($casePins[$caseName] -ne (Get-FileHash -LiteralPath (Join-Path $caseRoot $caseName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source changed during run'}}
$caseReceipt=@{passed=(!$ExpectRed);expected_red=([bool]$ExpectRed);mode=$caseMode;exit_code=$caseExit;output="$caseOutput";source_sha256=$casePins;source_chain_sha256=(Get-FileHash -LiteralPath (Join-Path $caseBuild 'source-verification.json') -Algorithm SHA256).Hash.ToLowerInvariant();source_chain_verified=$true;executable_sha256=(Get-FileHash -LiteralPath $caseExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler_sha256=(Get-FileHash -LiteralPath $caseCompiler -Algorithm SHA256).Hash.ToLowerInvariant();original_executed=$false;emulation=$false;hardware=$false;network=$false;native_BIN=$false;OTA_ready=$false}
$caseReceipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $caseBuild 'verification.json') -Encoding utf8
Write-Output ('APK_CONTRACT_RESULT '+(@{receipt=(Join-Path $caseBuild 'verification.json');expected_red=([bool]$ExpectRed);mode=$caseMode;exit_code=$caseExit}|ConvertTo-Json -Compress))
