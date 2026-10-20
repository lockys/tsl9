param([switch]$Cpp,[switch]$Baseline)
$ErrorActionPreference='Stop'
$observerRoot=$PSScriptRoot
$observerRepo=(Resolve-Path (Join-Path $observerRoot '..\..')).Path
$observerRuntime=Join-Path $observerRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$observerBoot=Join-Path $observerRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $observerRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $observerBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Server BOOT identity mismatch'}
$observerVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $observerVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $observerVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$observerVersion=(Get-Content -LiteralPath (Join-Path $observerVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$observerCl=Join-Path $observerVs ('VC\Tools\MSVC\'+$observerVersion+'\bin\Hostx64\x64\cl.exe')
$observerMode=if($Cpp){'observer-integration-cpp'}else{'observer-integration-c'}
if($Baseline){$observerMode+='-baseline'}
$observerBuild=Join-Path $observerRoot ('build\'+$observerMode)
New-Item -ItemType Directory -Path $observerBuild -Force | Out-Null
$observerFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $observerRoot 'src')),('/Fo'+$observerBuild+'\'))
$observerFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$observerExe=Join-Path $observerBuild ('test-observer-'+[Guid]::NewGuid().ToString('N')+'.exe')
$observerNames=@('model','feature','boot_ram','general_ble','general_helpers','dnd_actions','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','report_packet','general_reports','flash_page','spi_can','can_receive')
$observerSources=$observerNames | ForEach-Object {Join-Path $observerRoot ('src\'+$_+'.c')}
. (Join-Path $observerRoot 'build-evidence.ps1')
$observerGuardInputs=@('src/model.c','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','src/tsl9_contract.h','tests/test_observer_integration.c','verify-observer-integration.ps1','build-evidence.ps1','tests/test_coupled.c')
if($Baseline){
 $observerPrior=Join-Path $observerRepo 'apk-analysis\tsl9-function-hardware\eighteenth-round\integration\prior'
 $observerPriorC=Join-Path $observerPrior 'can_receive.c'
 $observerPriorH=Join-Path $observerPrior 'can_receive.h'
 $observerPriorParent=Join-Path $observerPrior 'ram_bridge.c'
 if((Get-FileHash -LiteralPath $observerPriorParent -Algorithm SHA256).Hash.ToLowerInvariant() -ne '94f039df1219adc93f3cb311ba45967d08d303c377a0394378be436a8ba47edc'){throw 'Baseline parent identity mismatch'}
 if((Get-FileHash -LiteralPath $observerPriorC -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'cf14a4489889d33643df59f73b77d4766faebcc1816b806ac0d5852f0dcb5bc9'){throw 'Baseline C identity mismatch'}
 if((Get-FileHash -LiteralPath $observerPriorH -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'ba87a1f0c24d699379ff20613db64254da9c0292a2f3ba51b7c95e66895fb8c0'){throw 'Baseline header identity mismatch'}
 $observerSources=@($observerSources | Where-Object { [IO.Path]::GetFileName($_) -ne 'can_receive.c' -and [IO.Path]::GetFileName($_) -ne 'ram_bridge.c' })+@($observerPriorC,$observerPriorParent)
 # Force one matching baseline header across every translation unit.
 $observerFlags+=('/FI'+$observerPriorH)
 $observerGuardInputs=@($observerGuardInputs | Where-Object {$_ -ne 'src/can_receive.c' -and $_ -ne 'src/can_receive.h' -and $_ -ne 'src/ram_bridge.c'})
 $observerGuardInputs+=@('../../apk-analysis/tsl9-function-hardware/eighteenth-round/integration/prior/can_receive.c','../../apk-analysis/tsl9-function-hardware/eighteenth-round/integration/prior/can_receive.h','../../apk-analysis/tsl9-function-hardware/eighteenth-round/integration/prior/ram_bridge.c')
}

$observerBefore=Get-ModelBuildInputHashes -ModelRoot $observerRoot -Sources $observerGuardInputs
& $observerCl @observerFlags @observerSources (Join-Path $observerRoot 'tests\test_observer_integration.c') ('/Fe'+$observerExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Observer integration compilation failed'}
. (Join-Path $observerRoot 'build-evidence.ps1')
$observerManifest=@('src/tsl9_contract.h','tests/test_coupled.c','tests/test_observer_integration.c','verify-observer-integration.ps1','build-evidence.ps1')
foreach($observerName in $observerNames){$observerManifest+='src/'+$observerName+'.c';if($observerName -ne 'model'){$observerManifest+='src/'+$observerName+'.h'}}
Write-ModelBuildEvidence -ModelRoot $observerRoot -Compiler $observerCl -Executable $observerExe -Mode $observerMode -Sources $observerGuardInputs -Before $observerBefore
& $observerExe $observerRuntime $observerBoot
exit $LASTEXITCODE
