param([switch]$Cpp)
$ErrorActionPreference='Stop'
$currentRoot=$PSScriptRoot
$currentRepo=(Resolve-Path (Join-Path $currentRoot '..\..')).Path
$currentInputs=@{'TSL9-boot-api-payload.bin'='650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb';'TSL9-runtime-api-payload.bin'='32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'}
foreach($currentName in $currentInputs.Keys){if((Get-FileHash -LiteralPath (Join-Path $currentRepo ('apk-analysis\tsl9-server-current\'+$currentName)) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $currentInputs[$currentName]){throw 'Original firmware identity mismatch'}}
$currentVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $currentVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $currentVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$currentVersion=(Get-Content -LiteralPath (Join-Path $currentVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$currentCl=Join-Path $currentVs ('VC\Tools\MSVC\'+$currentVersion+'\bin\Hostx64\x64\cl.exe')
$currentMode=if($Cpp){'current-core-cpp'}else{'current-core-c'}
$currentBuild=Join-Path $currentRoot ('build\'+$currentMode)
New-Item -ItemType Directory -Path $currentBuild -Force | Out-Null
$currentFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $currentRoot 'src')),('/Fo'+$currentBuild+'\'))
$currentFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
# Earlier fixed test-contract.exe remained locked by Windows file scanning.
# Preserve that artifact and produce a uniquely named current compilation.
$currentExe=Join-Path $currentBuild ('test-current-core-'+[Guid]::NewGuid().ToString('N')+'.exe')
& $currentCl @currentFlags (Join-Path $currentRoot 'src\model.c') (Join-Path $currentRoot 'tests\test_contract.c') ('/Fe'+$currentExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Current core compilation failed'}
. (Join-Path $currentRoot 'build-evidence.ps1')
Write-ModelBuildEvidence -ModelRoot $currentRoot -Compiler $currentCl -Executable $currentExe -Mode $currentMode -Sources @('src/model.c','src/tsl9_contract.h','tests/test_contract.c','fixtures/evidence.json','verify-current-core.ps1','build-evidence.ps1')
& $currentExe $currentRepo
exit $LASTEXITCODE
