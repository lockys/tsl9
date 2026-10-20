param([switch]$Cpp)
$ErrorActionPreference='Stop'
$systemRoot=$PSScriptRoot
$systemRepo=(Resolve-Path (Join-Path $systemRoot '..\..')).Path
$systemRuntime=Join-Path $systemRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$systemBoot=Join-Path $systemRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $systemRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $systemBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Server BOOT identity mismatch'}
$systemVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $systemVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $systemVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$systemVersion=(Get-Content -LiteralPath (Join-Path $systemVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$systemCl=Join-Path $systemVs ('VC\Tools\MSVC\'+$systemVersion+'\bin\Hostx64\x64\cl.exe')
$systemMode=if($Cpp){'system-bridge-cpp'}else{'system-bridge-c'}
$systemBuild=Join-Path $systemRoot ('build\'+$systemMode)
New-Item -ItemType Directory -Path $systemBuild -Force | Out-Null
$systemFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $systemRoot 'src')),('/Fo'+$systemBuild+'\'))
$systemFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$systemExe=Join-Path $systemBuild ('test-system-'+[Guid]::NewGuid().ToString('N')+'.exe')
$systemNames=@('model','feature','boot_ram','general_ble','general_helpers','dnd_actions','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','report_packet','general_reports','flash_page','spi_can','can_receive')
$systemSources=$systemNames | ForEach-Object {Join-Path $systemRoot ('src\'+$_+'.c')}
. (Join-Path $systemRoot 'build-evidence.ps1')
$systemGuardInputs=@('src/model.c','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','src/tsl9_contract.h','tests/test_system_bridge.c','verify-system-bridge.ps1','build-evidence.ps1','tests/test_coupled.c')
$systemBefore=Get-ModelBuildInputHashes -ModelRoot $systemRoot -Sources $systemGuardInputs
& $systemCl @systemFlags @systemSources (Join-Path $systemRoot 'tests\test_system_bridge.c') ('/Fe'+$systemExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'System adapter compilation failed'}
. (Join-Path $systemRoot 'build-evidence.ps1')
$systemManifest=@('src/tsl9_contract.h','tests/test_coupled.c','tests/test_system_bridge.c','verify-system-bridge.ps1','build-evidence.ps1')
foreach($systemName in $systemNames){$systemManifest+='src/'+$systemName+'.c';if($systemName -ne 'model'){$systemManifest+='src/'+$systemName+'.h'}}
Write-ModelBuildEvidence -ModelRoot $systemRoot -Compiler $systemCl -Executable $systemExe -Mode $systemMode -Sources $systemGuardInputs -Before $systemBefore
& $systemExe $systemRuntime $systemBoot
exit $LASTEXITCODE
