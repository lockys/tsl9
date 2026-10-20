param([switch]$Cpp)
$ErrorActionPreference='Stop'
$bridgeRoot=$PSScriptRoot
$bridgeRepo=(Resolve-Path (Join-Path $bridgeRoot '..\..')).Path
$bridgeInput=Join-Path $bridgeRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $bridgeInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$bridgeVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $bridgeVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $bridgeVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$bridgeVersion=(Get-Content -LiteralPath (Join-Path $bridgeVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$bridgeCl=Join-Path $bridgeVs ('VC\Tools\MSVC\'+$bridgeVersion+'\bin\Hostx64\x64\cl.exe')
$bridgeMode=if($Cpp){'bridge-cpp'}else{'bridge-c'}
$bridgeBuild=Join-Path $bridgeRoot ('build\'+$bridgeMode)
New-Item -ItemType Directory -Path $bridgeBuild -Force | Out-Null
$bridgeFlags=@('/nologo','/W4','/WX','/Od','/Zi','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $bridgeRoot 'src')),('/Fo'+$bridgeBuild+'\'),('/Fd'+(Join-Path $bridgeBuild 'compiler.pdb')))
$bridgeFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
# An earlier executable can remain briefly locked by Windows file scanning.
# Build a new artifact instead of deleting, retrying, or executing a stale one.
$bridgeExe=Join-Path $bridgeBuild ('test-ram-bridge-'+[Guid]::NewGuid().ToString('N')+'.exe')
$bridgeSources=@('model.c','feature.c','boot_ram.c','general_ble.c','general_helpers.c','dnd_actions.c','boot_startup.c','rom_candidate.c','rom_kernel.c','ram_bridge.c','native_callbacks.c','general_deep.c','report_packet.c','general_reports.c','flash_page.c','spi_can.c','can_receive.c') | ForEach-Object {Join-Path $bridgeRoot ('src\'+$_)}
. (Join-Path $bridgeRoot 'build-evidence.ps1')
$bridgeGuardInputs=@('src/model.c','src/tsl9_contract.h','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','tests/test_ram_bridge.c','verify-ram-bridge.ps1','build-evidence.ps1')
$bridgeBefore=Get-ModelBuildInputHashes -ModelRoot $bridgeRoot -Sources $bridgeGuardInputs
& $bridgeCl @bridgeFlags @bridgeSources (Join-Path $bridgeRoot 'tests\test_ram_bridge.c') ('/Fe'+$bridgeExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'RAM bridge compilation failed'}
. (Join-Path $bridgeRoot 'build-evidence.ps1')
Write-ModelBuildEvidence -ModelRoot $bridgeRoot -Compiler $bridgeCl -Executable $bridgeExe -Mode $bridgeMode -Sources $bridgeGuardInputs -Before $bridgeBefore
& $bridgeExe $bridgeInput
exit $LASTEXITCODE
