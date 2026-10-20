param([switch]$Cpp)
$ErrorActionPreference='Stop'
$deepRoot=$PSScriptRoot
$deepRepo=(Resolve-Path (Join-Path $deepRoot '..\..')).Path
$deepRuntime=Join-Path $deepRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$deepBoot=Join-Path $deepRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $deepRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $deepBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Server BOOT identity mismatch'}
$deepVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $deepVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $deepVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$deepVersion=(Get-Content -LiteralPath (Join-Path $deepVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$deepCl=Join-Path $deepVs ('VC\Tools\MSVC\'+$deepVersion+'\bin\Hostx64\x64\cl.exe')
$deepMode=if($Cpp){'deep-bridge-cpp'}else{'deep-bridge-c'}
$deepBuild=Join-Path $deepRoot ('build\'+$deepMode)
New-Item -ItemType Directory -Path $deepBuild -Force | Out-Null
$deepFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $deepRoot 'src')),('/Fo'+$deepBuild+'\'))
$deepFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$deepExe=Join-Path $deepBuild ('test-deep-'+[Guid]::NewGuid().ToString('N')+'.exe')
$deepNames=@('model','feature','boot_ram','general_ble','general_helpers','dnd_actions','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','report_packet','general_reports','flash_page','spi_can','can_receive')
$deepSources=$deepNames | ForEach-Object {Join-Path $deepRoot ('src\'+$_+'.c')}
. (Join-Path $deepRoot 'build-evidence.ps1')
$deepGuardInputs=@('src/model.c','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','src/tsl9_contract.h','tests/test_deep_bridge.c','verify-deep-bridge.ps1','build-evidence.ps1','tests/test_coupled.c')
$deepBefore=Get-ModelBuildInputHashes -ModelRoot $deepRoot -Sources $deepGuardInputs
& $deepCl @deepFlags @deepSources (Join-Path $deepRoot 'tests\test_deep_bridge.c') ('/Fe'+$deepExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Deep adapter compilation failed'}
. (Join-Path $deepRoot 'build-evidence.ps1')
$deepManifest=@('src/tsl9_contract.h','tests/test_coupled.c','tests/test_deep_bridge.c','verify-deep-bridge.ps1','build-evidence.ps1')
foreach($deepName in $deepNames){$deepManifest+='src/'+$deepName+'.c';if($deepName -ne 'model'){$deepManifest+='src/'+$deepName+'.h'}}
Write-ModelBuildEvidence -ModelRoot $deepRoot -Compiler $deepCl -Executable $deepExe -Mode $deepMode -Sources $deepGuardInputs -Before $deepBefore
& $deepExe $deepRuntime $deepBoot
exit $LASTEXITCODE
