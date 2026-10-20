param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeRepo=(Resolve-Path (Join-Path $nativeRoot '..\..')).Path
$nativeRuntime=Join-Path $nativeRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$nativeBoot=Join-Path $nativeRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $nativeRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $nativeBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Server BOOT identity mismatch'}
$nativeVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $nativeVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $nativeVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$nativeVersion=(Get-Content -LiteralPath (Join-Path $nativeVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$nativeCl=Join-Path $nativeVs ('VC\Tools\MSVC\'+$nativeVersion+'\bin\Hostx64\x64\cl.exe')
$nativeMode=if($Cpp){'native-bridge-cpp'}else{'native-bridge-c'}
$nativeBuild=Join-Path $nativeRoot ('build\'+$nativeMode)
New-Item -ItemType Directory -Path $nativeBuild -Force | Out-Null
$nativeFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $nativeRoot 'src')),('/Fo'+$nativeBuild+'\'))
$nativeFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$nativeExe=Join-Path $nativeBuild ('test-native-'+[Guid]::NewGuid().ToString('N')+'.exe')
$nativeNames=@('model','feature','boot_ram','general_ble','general_helpers','dnd_actions','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','report_packet','general_reports','flash_page','spi_can','can_receive')
$nativeSources=$nativeNames | ForEach-Object {Join-Path $nativeRoot ('src\'+$_+'.c')}
. (Join-Path $nativeRoot 'build-evidence.ps1')
$nativeGuardInputs=@('src/model.c','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','src/tsl9_contract.h','tests/test_native_bridge.c','verify-native-bridge.ps1','build-evidence.ps1','tests/test_coupled.c')
$nativeBefore=Get-ModelBuildInputHashes -ModelRoot $nativeRoot -Sources $nativeGuardInputs
& $nativeCl @nativeFlags @nativeSources (Join-Path $nativeRoot 'tests\test_native_bridge.c') ('/Fe'+$nativeExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Native adapter compilation failed'}
. (Join-Path $nativeRoot 'build-evidence.ps1')
$nativeManifest=@('src/tsl9_contract.h','tests/test_coupled.c','tests/test_native_bridge.c','verify-native-bridge.ps1','build-evidence.ps1')
foreach($nativeName in $nativeNames){$nativeManifest+='src/'+$nativeName+'.c';if($nativeName -ne 'model'){$nativeManifest+='src/'+$nativeName+'.h'}}
Write-ModelBuildEvidence -ModelRoot $nativeRoot -Compiler $nativeCl -Executable $nativeExe -Mode $nativeMode -Sources $nativeGuardInputs -Before $nativeBefore
& $nativeExe $nativeRuntime $nativeBoot
exit $LASTEXITCODE
