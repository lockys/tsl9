param([switch]$Cpp,[switch]$Baseline)
$ErrorActionPreference='Stop'
$gateRoot=$PSScriptRoot
$gateRepo=(Resolve-Path (Join-Path $gateRoot '..\..')).Path
$gateRuntime=Join-Path $gateRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$gateBoot=Join-Path $gateRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $gateRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $gateBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Server BOOT identity mismatch'}
$gateVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $gateVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $gateVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$gateVersion=(Get-Content -LiteralPath (Join-Path $gateVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$gateCl=Join-Path $gateVs ('VC\Tools\MSVC\'+$gateVersion+'\bin\Hostx64\x64\cl.exe')
$gateMode=if($Cpp){'gate-integration-cpp'}else{'gate-integration-c'}
if($Baseline){$gateMode+='-baseline'}
$gateBuild=Join-Path $gateRoot ('build\'+$gateMode)
New-Item -ItemType Directory -Path $gateBuild -Force | Out-Null
$gateFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $gateRoot 'src')),('/Fo'+$gateBuild+'\'))
$gateFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$gateExe=Join-Path $gateBuild ('test-gate-'+[Guid]::NewGuid().ToString('N')+'.exe')
$gateNames=@('model','feature','boot_ram','general_ble','general_helpers','dnd_actions','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','report_packet','general_reports','flash_page','spi_can','can_receive')
$gateSources=$gateNames | ForEach-Object {Join-Path $gateRoot ('src\'+$_+'.c')}
. (Join-Path $gateRoot 'build-evidence.ps1')
$gateGuardInputs=@('src/model.c','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','src/tsl9_contract.h','tests/test_gate_integration.c','verify-gate-integration.ps1','build-evidence.ps1','tests/test_coupled.c')
if($Baseline){
 $gatePrior=Join-Path $gateRepo 'apk-analysis\tsl9-function-hardware\nineteenth-round\integration\prior'
 $gatePriorC=Join-Path $gatePrior 'can_receive.c'
 $gatePriorH=Join-Path $gatePrior 'can_receive.h'
 $gatePriorParent=Join-Path $gatePrior 'ram_bridge.c'
 if((Get-FileHash -LiteralPath $gatePriorParent -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'ef17da4fbfdd825a0afbd961aa2895a8834d0a8ca604656d1cb4b63dbd94ff5d'){throw 'Baseline parent identity mismatch'}
 if((Get-FileHash -LiteralPath $gatePriorC -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'afbfdf00ca171166831580744959608572f22194133325bcfea63f9906383d24'){throw 'Baseline C identity mismatch'}
 if((Get-FileHash -LiteralPath $gatePriorH -Algorithm SHA256).Hash.ToLowerInvariant() -ne '2a98f03d41ea5e5d938964b9171d9f0000c9fdb5233f338c311021606ad331a8'){throw 'Baseline header identity mismatch'}
 $gateSources=@($gateSources | Where-Object { [IO.Path]::GetFileName($_) -ne 'can_receive.c' -and [IO.Path]::GetFileName($_) -ne 'ram_bridge.c' })+@($gatePriorC,$gatePriorParent)
 # Force one matching baseline header across every translation unit.
 $gateFlags+=('/FI'+$gatePriorH)
 $gateGuardInputs=@($gateGuardInputs | Where-Object {$_ -ne 'src/can_receive.c' -and $_ -ne 'src/can_receive.h' -and $_ -ne 'src/ram_bridge.c'})
 $gateGuardInputs+=@('../../apk-analysis/tsl9-function-hardware/nineteenth-round/integration/prior/can_receive.c','../../apk-analysis/tsl9-function-hardware/nineteenth-round/integration/prior/can_receive.h','../../apk-analysis/tsl9-function-hardware/nineteenth-round/integration/prior/ram_bridge.c')
}

$gateBefore=Get-ModelBuildInputHashes -ModelRoot $gateRoot -Sources $gateGuardInputs
& $gateCl @gateFlags @gateSources (Join-Path $gateRoot 'tests\test_gate_integration.c') ('/Fe'+$gateExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Gate integration compilation failed'}
. (Join-Path $gateRoot 'build-evidence.ps1')
$gateManifest=@('src/tsl9_contract.h','tests/test_coupled.c','tests/test_gate_integration.c','verify-gate-integration.ps1','build-evidence.ps1')
foreach($gateName in $gateNames){$gateManifest+='src/'+$gateName+'.c';if($gateName -ne 'model'){$gateManifest+='src/'+$gateName+'.h'}}
Write-ModelBuildEvidence -ModelRoot $gateRoot -Compiler $gateCl -Executable $gateExe -Mode $gateMode -Sources $gateGuardInputs -Before $gateBefore
& $gateExe $gateRuntime $gateBoot
exit $LASTEXITCODE
