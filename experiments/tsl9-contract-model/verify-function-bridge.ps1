param([switch]$Cpp)
$ErrorActionPreference='Stop'
$functionRoot=$PSScriptRoot
$functionRepo=(Resolve-Path (Join-Path $functionRoot '..\..')).Path
$functionRuntime=Join-Path $functionRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$functionBoot=Join-Path $functionRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $functionRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $functionBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Server BOOT identity mismatch'}
$functionVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $functionVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $functionVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$functionVersion=(Get-Content -LiteralPath (Join-Path $functionVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$functionCl=Join-Path $functionVs ('VC\Tools\MSVC\'+$functionVersion+'\bin\Hostx64\x64\cl.exe')
$functionMode=if($Cpp){'function-bridge-cpp'}else{'function-bridge-c'}
$functionBuild=Join-Path $functionRoot ('build\'+$functionMode)
New-Item -ItemType Directory -Path $functionBuild -Force | Out-Null
$functionFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $functionRoot 'src')),('/Fo'+$functionBuild+'\'))
$functionFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$functionExe=Join-Path $functionBuild ('test-function-'+[Guid]::NewGuid().ToString('N')+'.exe')
$functionNames=@('model','feature','boot_ram','general_ble','general_helpers','dnd_actions','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','report_packet','general_reports','flash_page','spi_can','can_receive')
$functionSources=$functionNames | ForEach-Object {Join-Path $functionRoot ('src\'+$_+'.c')}
. (Join-Path $functionRoot 'build-evidence.ps1')
$functionGuardInputs=@('src/model.c','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','src/tsl9_contract.h','tests/test_function_bridge.c','verify-function-bridge.ps1','build-evidence.ps1','tests/test_coupled.c')
$functionBefore=Get-ModelBuildInputHashes -ModelRoot $functionRoot -Sources $functionGuardInputs
& $functionCl @functionFlags @functionSources (Join-Path $functionRoot 'tests\test_function_bridge.c') ('/Fe'+$functionExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Function adapter compilation failed'}
. (Join-Path $functionRoot 'build-evidence.ps1')
$functionManifest=@('src/tsl9_contract.h','tests/test_coupled.c','tests/test_function_bridge.c','verify-function-bridge.ps1','build-evidence.ps1')
foreach($functionName in $functionNames){$functionManifest+='src/'+$functionName+'.c';if($functionName -ne 'model'){$functionManifest+='src/'+$functionName+'.h'}}
Write-ModelBuildEvidence -ModelRoot $functionRoot -Compiler $functionCl -Executable $functionExe -Mode $functionMode -Sources $functionGuardInputs -Before $functionBefore
& $functionExe $functionRuntime $functionBoot
exit $LASTEXITCODE
