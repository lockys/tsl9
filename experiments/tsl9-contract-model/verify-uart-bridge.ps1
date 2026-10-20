param([switch]$Cpp)
$ErrorActionPreference='Stop'
$uartRoot=$PSScriptRoot
$uartRepo=(Resolve-Path (Join-Path $uartRoot '..\..')).Path
$uartRuntime=Join-Path $uartRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$uartBoot=Join-Path $uartRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $uartRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $uartBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Server BOOT identity mismatch'}
$uartVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $uartVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $uartVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$uartVersion=(Get-Content -LiteralPath (Join-Path $uartVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$uartCl=Join-Path $uartVs ('VC\Tools\MSVC\'+$uartVersion+'\bin\Hostx64\x64\cl.exe')
$uartMode=if($Cpp){'uart-bridge-cpp'}else{'uart-bridge-c'}
$uartBuild=Join-Path $uartRoot ('build\'+$uartMode)
New-Item -ItemType Directory -Path $uartBuild -Force | Out-Null
$uartFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $uartRoot 'src')),('/Fo'+$uartBuild+'\'))
$uartFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$uartExe=Join-Path $uartBuild ('test-uart-'+[Guid]::NewGuid().ToString('N')+'.exe')
$uartNames=@('model','feature','boot_ram','general_ble','general_helpers','dnd_actions','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','report_packet','general_reports','flash_page','spi_can','can_receive')
$uartSources=$uartNames | ForEach-Object {Join-Path $uartRoot ('src\'+$_+'.c')}
. (Join-Path $uartRoot 'build-evidence.ps1')
$uartGuardInputs=@('src/model.c','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','src/tsl9_contract.h','tests/test_uart_bridge.c','verify-uart-bridge.ps1','build-evidence.ps1','tests/test_coupled.c')
$uartBefore=Get-ModelBuildInputHashes -ModelRoot $uartRoot -Sources $uartGuardInputs
& $uartCl @uartFlags @uartSources (Join-Path $uartRoot 'tests\test_uart_bridge.c') ('/Fe'+$uartExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'UART adapter compilation failed'}
. (Join-Path $uartRoot 'build-evidence.ps1')
$uartManifest=@('src/tsl9_contract.h','tests/test_coupled.c','tests/test_uart_bridge.c','verify-uart-bridge.ps1','build-evidence.ps1')
foreach($uartName in $uartNames){$uartManifest+='src/'+$uartName+'.c';if($uartName -ne 'model'){$uartManifest+='src/'+$uartName+'.h'}}
Write-ModelBuildEvidence -ModelRoot $uartRoot -Compiler $uartCl -Executable $uartExe -Mode $uartMode -Sources $uartGuardInputs -Before $uartBefore
& $uartExe $uartRuntime $uartBoot
exit $LASTEXITCODE
