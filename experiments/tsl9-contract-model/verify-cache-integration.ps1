param([switch]$Cpp,[switch]$Baseline)
$ErrorActionPreference='Stop'
$cacheRoot=$PSScriptRoot
$cacheRepo=(Resolve-Path (Join-Path $cacheRoot '..\..')).Path
$cacheRuntime=Join-Path $cacheRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$cacheBoot=Join-Path $cacheRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $cacheRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $cacheBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Server BOOT identity mismatch'}
$cacheVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $cacheVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $cacheVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$cacheVersion=(Get-Content -LiteralPath (Join-Path $cacheVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$cacheCl=Join-Path $cacheVs ('VC\Tools\MSVC\'+$cacheVersion+'\bin\Hostx64\x64\cl.exe')
$cacheMode=if($Cpp){'cache-integration-cpp'}else{'cache-integration-c'}
if($Baseline){$cacheMode+='-baseline'}
$cacheBuild=Join-Path $cacheRoot ('build\'+$cacheMode)
New-Item -ItemType Directory -Path $cacheBuild -Force | Out-Null
$cacheFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $cacheRoot 'src')),('/Fo'+$cacheBuild+'\'))
$cacheFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$cacheExe=Join-Path $cacheBuild ('test-cache-'+[Guid]::NewGuid().ToString('N')+'.exe')
$cacheNames=@('model','feature','boot_ram','general_ble','general_helpers','dnd_actions','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','report_packet','general_reports','flash_page','spi_can','can_receive')
$cacheSources=$cacheNames | ForEach-Object {Join-Path $cacheRoot ('src\'+$_+'.c')}
. (Join-Path $cacheRoot 'build-evidence.ps1')
$cacheGuardInputs=@('src/model.c','src/feature.c','src/feature.h','src/boot_ram.c','src/boot_ram.h','src/general_ble.c','src/general_ble.h','src/general_helpers.c','src/general_helpers.h','src/dnd_actions.c','src/dnd_actions.h','src/boot_startup.c','src/boot_startup.h','src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/ram_bridge.c','src/ram_bridge.h','src/native_callbacks.c','src/native_callbacks.h','src/general_deep.c','src/general_deep.h','src/report_packet.c','src/report_packet.h','src/general_reports.c','src/general_reports.h','src/flash_page.c','src/flash_page.h','src/spi_can.c','src/spi_can.h','src/can_receive.c','src/can_receive.h','src/tsl9_contract.h','tests/test_cache_integration.c','verify-cache-integration.ps1','build-evidence.ps1','tests/test_coupled.c')
if($Baseline){
 $cachePrior=Join-Path $cacheRepo 'apk-analysis\tsl9-function-hardware\seventeenth-round\integration\prior'
 $cachePriorC=Join-Path $cachePrior 'can_receive.c'
 $cachePriorH=Join-Path $cachePrior 'can_receive.h'
 if((Get-FileHash -LiteralPath $cachePriorC -Algorithm SHA256).Hash.ToLowerInvariant() -ne '2239ff3a8ce64c0eef7c5fbfdb95da76683bd131f9af35f8f9e3419402f18ced'){throw 'Baseline C identity mismatch'}
 if((Get-FileHash -LiteralPath $cachePriorH -Algorithm SHA256).Hash.ToLowerInvariant() -ne '10881fde07d5626b42df0288cd4bded68d58cca93cb8f294ecfabec5dd7278cb'){throw 'Baseline header identity mismatch'}
 $cacheSources=@($cacheSources | Where-Object { [IO.Path]::GetFileName($_) -ne 'can_receive.c' })+@($cachePriorC)
 # Force one matching baseline header across every translation unit.
 $cacheFlags+=('/FI'+$cachePriorH)
 $cacheGuardInputs=@($cacheGuardInputs | Where-Object {$_ -ne 'src/can_receive.c' -and $_ -ne 'src/can_receive.h'})
 $cacheGuardInputs+=@('../../apk-analysis/tsl9-function-hardware/seventeenth-round/integration/prior/can_receive.c','../../apk-analysis/tsl9-function-hardware/seventeenth-round/integration/prior/can_receive.h')
}

$cacheBefore=Get-ModelBuildInputHashes -ModelRoot $cacheRoot -Sources $cacheGuardInputs
& $cacheCl @cacheFlags @cacheSources (Join-Path $cacheRoot 'tests\test_cache_integration.c') ('/Fe'+$cacheExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Cache integration compilation failed'}
. (Join-Path $cacheRoot 'build-evidence.ps1')
$cacheManifest=@('src/tsl9_contract.h','tests/test_coupled.c','tests/test_cache_integration.c','verify-cache-integration.ps1','build-evidence.ps1')
foreach($cacheName in $cacheNames){$cacheManifest+='src/'+$cacheName+'.c';if($cacheName -ne 'model'){$cacheManifest+='src/'+$cacheName+'.h'}}
Write-ModelBuildEvidence -ModelRoot $cacheRoot -Compiler $cacheCl -Executable $cacheExe -Mode $cacheMode -Sources $cacheGuardInputs -Before $cacheBefore
& $cacheExe $cacheRuntime $cacheBoot
exit $LASTEXITCODE
