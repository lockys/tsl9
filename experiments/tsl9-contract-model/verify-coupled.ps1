param([switch]$Cpp)
$ErrorActionPreference='Stop'
$coupledRoot=$PSScriptRoot
$coupledRepo=(Resolve-Path (Join-Path $coupledRoot '..\..')).Path
$coupledRuntime=Join-Path $coupledRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$coupledBoot=Join-Path $coupledRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $coupledRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $coupledBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'BOOT identity mismatch'}
$coupledVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $coupledVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $coupledVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$coupledVersion=(Get-Content -LiteralPath (Join-Path $coupledVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$coupledCl=Join-Path $coupledVs ('VC\Tools\MSVC\'+$coupledVersion+'\bin\Hostx64\x64\cl.exe')
$coupledMode=if($Cpp){'coupled-cpp'}else{'coupled-c'}
$coupledBuild=Join-Path $coupledRoot ('build\'+$coupledMode)
New-Item -ItemType Directory -Path $coupledBuild -Force | Out-Null
$coupledFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $coupledRoot 'src')),('/Fo'+$coupledBuild+'\'))
$coupledFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$coupledExe=Join-Path $coupledBuild ('test-coupled-'+[Guid]::NewGuid().ToString('N')+'.exe')
$coupledSources=@('model.c','feature.c','boot_ram.c','general_ble.c','general_helpers.c','dnd_actions.c','boot_startup.c','rom_candidate.c','rom_kernel.c','ram_bridge.c','native_callbacks.c','general_deep.c','report_packet.c','general_reports.c','flash_page.c','spi_can.c','can_receive.c') | ForEach-Object {Join-Path $coupledRoot ('src\'+$_)}
. (Join-Path $coupledRoot 'build-evidence.ps1')
$coupledGuardInputs=@('src/model.c','src/tsl9_contract.h','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','tests/test_coupled.c','verify-coupled.ps1','build-evidence.ps1')
$coupledBefore=Get-ModelBuildInputHashes -ModelRoot $coupledRoot -Sources $coupledGuardInputs
& $coupledCl @coupledFlags @coupledSources (Join-Path $coupledRoot 'tests\test_coupled.c') ('/Fe'+$coupledExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Coupled model compilation failed'}
. (Join-Path $coupledRoot 'build-evidence.ps1')
Write-ModelBuildEvidence -ModelRoot $coupledRoot -Compiler $coupledCl -Executable $coupledExe -Mode $coupledMode -Sources $coupledGuardInputs -Before $coupledBefore
& $coupledExe $coupledRuntime $coupledBoot
exit $LASTEXITCODE
