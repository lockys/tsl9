param([switch]$Cpp)
$ErrorActionPreference='Stop'
$generalRoot=$PSScriptRoot
$generalRepo=(Resolve-Path (Join-Path $generalRoot '..\..')).Path
$generalInput=Join-Path $generalRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $generalInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$generalVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $generalVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $generalVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$generalVersion=(Get-Content -LiteralPath (Join-Path $generalVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$generalCl=Join-Path $generalVs ('VC\Tools\MSVC\'+$generalVersion+'\bin\Hostx64\x64\cl.exe')
$generalMode=if($Cpp){'general-cpp'}else{'general-c'}
$generalBuild=Join-Path $generalRoot ('build\'+$generalMode)
New-Item -ItemType Directory -Path $generalBuild -Force | Out-Null
$generalFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $generalRoot 'src')),('/Fo'+$generalBuild+'\'))
$generalFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$generalExe=Join-Path $generalBuild ('test-general-'+[Guid]::NewGuid().ToString('N')+'.exe')
. (Join-Path $generalRoot 'build-evidence.ps1')
$generalGuardInputs=@('src/general_ble.c','src/general_ble.h','src/feature.h','tests/test_general_ble.c','tests/test_reports_counterexample.c','verify-reports-counterexample.ps1','build-evidence.ps1')
$generalBefore=Get-ModelBuildInputHashes -ModelRoot $generalRoot -Sources $generalGuardInputs
& $generalCl @generalFlags (Join-Path $generalRoot 'src\general_ble.c') (Join-Path $generalRoot 'tests\test_reports_counterexample.c') ('/Fe'+$generalExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'General BLE compilation failed'}
. (Join-Path $generalRoot 'build-evidence.ps1')
Write-ModelBuildEvidence -ModelRoot $generalRoot -Compiler $generalCl -Executable $generalExe -Mode 'reports-counterexample' -Sources $generalGuardInputs -Before $generalBefore
& $generalExe $generalInput
exit $LASTEXITCODE
