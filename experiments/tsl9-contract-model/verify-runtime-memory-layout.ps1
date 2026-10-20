param([switch]$Cpp)
$ErrorActionPreference='Stop'
$memoryRoot=$PSScriptRoot
$memoryVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $memoryVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $memoryVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64'|Out-Null
$memoryVersion=(Get-Content -LiteralPath (Join-Path $memoryVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$memoryCompiler=Join-Path $memoryVs ('VC\Tools\MSVC\'+$memoryVersion+'\bin\Hostx64\x64\cl.exe')
$memoryMode=if($Cpp){'runtime-memory-layout-cpp'}else{'runtime-memory-layout-c'}
$memoryBuild=Join-Path $memoryRoot ('build/'+$memoryMode)
[IO.Directory]::CreateDirectory($memoryBuild)|Out-Null
$memoryExe=Join-Path $memoryBuild ('memory-layout-'+[Guid]::NewGuid().ToString('N')+'.exe')
$memoryRuntime=Join-Path $memoryRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
$memoryBoot=Join-Path $memoryRoot '../../apk-analysis/tsl9-server-current/TSL9-boot-api-payload.bin'
$memoryWitness=Join-Path $memoryRoot '../../evidence/round57-memory-witness.json'
$memoryFixture=Join-Path $memoryRoot 'tests/fixtures/memory_witnesses_r57.h'
$memoryBindingPath=Join-Path $memoryRoot '../../evidence/round77-memory-native-binding.json'
$memoryCurrentBinding=Get-Content -LiteralPath $memoryBindingPath -Raw|ConvertFrom-Json
if($memoryCurrentBinding.schema -ne 'R77-current-native-memory-witness-binding' -or -not $memoryCurrentBinding.passed -or $memoryCurrentBinding.native_snapshot.Count -ne 108 -or $memoryCurrentBinding.fixture_rows -ne 130 -or $memoryCurrentBinding.current_native_profile_round -ne 77){throw 'Incomplete current native binding'}
if($memoryCurrentBinding.frozen_witness_file -ne 'evidence/round57-memory-witness.json' -or (Get-FileHash -LiteralPath $memoryWitness -Algorithm SHA256).Hash.ToLowerInvariant() -ne $memoryCurrentBinding.frozen_witness_sha256){throw 'Frozen witness provenance changed'}
$memoryInput=Get-Content -LiteralPath $memoryWitness -Raw|ConvertFrom-Json
if($memoryInput.schema -ne 'R57-frozen-memory-witness-input' -or -not $memoryInput.passed -or $memoryInput.cases.Count -ne 130 -or $memoryInput.native_snapshot.Count -ne 54){throw 'Incomplete frozen witness input'}
if((Get-FileHash -LiteralPath $memoryFixture -Algorithm SHA256).Hash.ToLowerInvariant() -ne $memoryInput.fixture_sha256){throw 'Witness fixture identity mismatch'}
$memoryNativePaths=@();$memoryNativeSeen=@{}
foreach($binding in $memoryCurrentBinding.native_snapshot){
 if($binding.file -notmatch '^(src/[A-Za-z0-9_]+\.[ch]|verify-image-platform-native\.ps1|verify-target-system-clock-native\.ps1|verify-target-reset-fidelity-native\.ps1|verify-target-identity-reader-native\.ps1|verify-target-init-check-native\.ps1|verify-target-ble-platform-native\.ps1|verify-target-feature-init-native\.ps1|verify-target-(dependency-closure|dispatch-control|config-storage|settings-load|rf-queue|board-init|settings-accessors|startup-callbacks|ble-service-events|mode-setup|rf-timer|dispatch|can-transmit)-native\.ps1|verify-image-layout-relocatable\.ps1|verify-image-memory-relocatable\.ps1|layout/(known-runtime-layout|runtime-memory)\.(json|ld))$' -or $memoryNativeSeen.ContainsKey($binding.file)){throw 'Invalid native source snapshot member'}
 $memoryNativeSeen[$binding.file]=$binding.sha256
 $path=Join-Path $memoryRoot $binding.file
 if((Get-Item -LiteralPath $path).Length -ne $binding.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $binding.sha256){throw ('Native witness source changed: '+$binding.file)}
 $memoryNativePaths+=@($path)
}
$memoryLegacySources=0;$memoryUnchangedLegacySources=0;$memoryAppendedSources=0
if($memoryCurrentBinding.appended_native_sources.Count -ne 12 -or $memoryCurrentBinding.unchanged_frozen_native_sources -ne 41){throw 'Incomplete source-prefix provenance'}
if($memoryCurrentBinding.frozen_fixture_sha256 -ne $memoryInput.fixture_sha256){throw 'Frozen fixture binding mismatch'}
foreach($legacy in $memoryInput.native_snapshot){
 if($legacy.file -eq 'verify-image-platform-native.ps1'){
  $record=$memoryCurrentBinding.superseded_platform_script
  if($record.file -ne $legacy.file -or $record.legacy_sha256 -ne $legacy.sha256 -or $record.current_sha256 -ne $memoryNativeSeen[$legacy.file]){throw 'Platform provenance transition mismatch'}
 }else{
  $delta=@($memoryCurrentBinding.appended_native_sources|Where-Object {$_.file -eq $legacy.file})
  if($delta.Count){
   if($delta.Count -ne 1 -or $legacy.file -notin @('src/target_dispatch_control.c','src/target_rf_queue.c','src/target_mode_setup.c','src/target_can_transmit.c','src/target_board_init.c','src/target_config_storage.c','src/target_ble_service_events.c','src/target_rf_timer.c','src/target_settings_load.c','src/target_ble_queue_callbacks.c','src/target_ble_platform.c','src/target_feature_init.c')){throw 'Unexpected frozen-source delta'}
   $record=$delta[0]
   if($record.legacy_sha256 -ne $legacy.sha256 -or $record.current_sha256 -ne $memoryNativeSeen[$legacy.file]){throw 'Alias source transition mismatch'}
   $bytes=[IO.File]::ReadAllBytes((Join-Path $memoryRoot $legacy.file))
   $count=[int]$record.frozen_prefix_bytes
   if($count -le 0 -or $count -ge $bytes.Length){throw 'Invalid frozen prefix'}
   $hasher=[Security.Cryptography.SHA256]::Create()
   try{$prefixHash=[Convert]::ToHexString($hasher.ComputeHash($bytes,0,$count)).ToLowerInvariant()}finally{$hasher.Dispose()}
   if($prefixHash -ne $legacy.sha256 -or $bytes.Length-$count -ne $record.appended_bytes){throw 'Frozen source prefix changed'}
   $memoryAppendedSources++
  }else{
   if(-not $memoryNativeSeen.ContainsKey($legacy.file) -or $memoryNativeSeen[$legacy.file] -ne $legacy.sha256){throw 'Frozen native C/H source changed'}
   $memoryUnchangedLegacySources++
  }
  $memoryLegacySources++
 }
}
if($memoryAppendedSources -ne 12 -or $memoryUnchangedLegacySources -ne 41 -or $memoryLegacySources -ne 53 -or $memoryCurrentBinding.preserved_frozen_native_sources -ne 53){throw 'Incomplete frozen-source preservation'}
function Memory-HistoricalContainer([byte[]]$bytes,[int]$count,[string]$digest){
 if($count -le 0 -or $count -gt $bytes.Length){throw 'Historical container extent'}
 $hasher=[Security.Cryptography.SHA256]::Create()
 try{return [Convert]::ToHexString($hasher.ComputeHash($bytes,0,$count)).ToLowerInvariant() -eq $digest}finally{$hasher.Dispose()}
}
# Preserve every bounded historical container, including its old suffix.
$memoryCompletePreviousPrefixes=0
foreach($record in $memoryCurrentBinding.appended_native_sources){
 if($record.file -eq 'src/target_config_storage.c'){
  $transition=$record.current_transition
  $bytes=[IO.File]::ReadAllBytes((Join-Path $memoryRoot $record.file))
  if($transition.from_round -ne 67 -or $transition.prefix_bytes -ne 17664 -or $transition.prefix_sha256 -ne '360211857ed1f2babea5b64cb2e81882014053b2f02573dc32b8c48fef290117' -or -not(Memory-HistoricalContainer $bytes ($transition.prefix_bytes+$transition.appended_bytes) $record.historical_container_sha256) -or $transition.alias -ne 'tsl9_internal_config_read_9d9e'){throw 'Wrong complete previous container binding'}
  $prefix=[byte[]]$bytes[0..($transition.prefix_bytes-1)]
  $suffix=[byte[]]$bytes[$transition.prefix_bytes..($transition.prefix_bytes+$transition.appended_bytes-1)]
  if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($prefix)).ToLowerInvariant() -ne $transition.prefix_sha256 -or $suffix.Length -ne $transition.appended_bytes -or [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($suffix)).ToLowerInvariant() -ne $transition.appended_sha256){throw 'Complete R67 source prefix changed'}
  $memoryCompletePreviousPrefixes++
 }
 if($record.file -eq 'src/target_ble_platform.c'){
  $transition=$record.current_transition
  $bytes=[IO.File]::ReadAllBytes((Join-Path $memoryRoot $record.file))
  if($transition.from_round -ne 71 -or $transition.prefix_bytes -ne 27660 -or $transition.prefix_sha256 -ne '200e6f3fce3e448c1480c7c25b3a52d972f2921077a1df82861fcfc157725de8' -or $transition.entry -ne 'tsl9_runtime_unported_87c4' -or -not(Memory-HistoricalContainer $bytes ($transition.prefix_bytes+$transition.appended_bytes) $record.historical_container_sha256)){throw 'Wrong R71 BLE container binding'}
  $prefix=[byte[]]$bytes[0..($transition.prefix_bytes-1)]
  $suffix=[byte[]]$bytes[$transition.prefix_bytes..($transition.prefix_bytes+$transition.appended_bytes-1)]
  if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($prefix)).ToLowerInvariant() -ne $transition.prefix_sha256 -or $suffix.Length -ne $transition.appended_bytes -or [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($suffix)).ToLowerInvariant() -ne $transition.appended_sha256){throw 'Complete R71 BLE source prefix changed'}
  $memoryCompletePreviousPrefixes++
 }
}
$memoryFeatureTransition=@($memoryCurrentBinding.appended_native_sources|Where-Object {$_.file -eq 'src/target_feature_init.c'})
if($memoryFeatureTransition.Count -ne 1){throw 'Missing feature full-prefix record'}
$featureTransition=$memoryFeatureTransition[0].current_transition
$featureBytes=[IO.File]::ReadAllBytes((Join-Path $memoryRoot 'src/target_feature_init.c'))
$featurePrefix=[byte[]]$featureBytes[0..27068]
if($featureTransition.from_round -ne 70 -or $featureTransition.prefix_bytes -ne 27069 -or $featureTransition.prefix_sha256 -ne '1ec8976673abe9d7c85e23bc0f3955b180f3cc5d9f47db81f950f54f544d05b1' -or $featureTransition.entry -ne 'tsl9_runtime_unported_aeec' -or [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($featurePrefix)).ToLowerInvariant() -ne $featureTransition.prefix_sha256){throw 'Complete R70 feature source prefix changed'}
$memoryCompletePreviousPrefixes++
foreach($transition in $memoryCurrentBinding.r73_complete_previous_sources){
 $bytes=[IO.File]::ReadAllBytes((Join-Path $memoryRoot $transition.file))
 $prefix=[byte[]]$bytes[0..($transition.prefix_bytes-1)];$suffix=[byte[]]$bytes[$transition.prefix_bytes..($transition.prefix_bytes+$transition.appended_bytes-1)]
 if($transition.from_round -ne 72 -or -not(Memory-HistoricalContainer $bytes ($transition.prefix_bytes+$transition.appended_bytes) $transition.current_sha256) -or [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($prefix)).ToLowerInvariant() -ne $transition.prefix_sha256 -or $suffix.Length -ne $transition.appended_bytes -or [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($suffix)).ToLowerInvariant() -ne $transition.appended_sha256){throw 'Complete R72 source prefix changed'}
 $memoryCompletePreviousPrefixes++
}
if($memoryCurrentBinding.r73_complete_previous_sources.Count -ne 6 -or $memoryCompletePreviousPrefixes -ne 9){throw 'Incomplete R73 full-source prefix coverage'}
if($memoryCurrentBinding.r75_complete_previous_sources.Count -ne 6){throw 'Incomplete R74 to R75 prefix set'}
foreach($transition in $memoryCurrentBinding.r75_complete_previous_sources){
 $bytes=[IO.File]::ReadAllBytes((Join-Path $memoryRoot $transition.file))
 if($transition.from_round -ne 74 -or -not(Memory-HistoricalContainer $bytes ($transition.prefix_bytes+$transition.appended_bytes) $transition.current_sha256) -or -not(Memory-HistoricalContainer $bytes $transition.prefix_bytes $transition.prefix_sha256)){throw 'Complete R74 prefix or R75 provenance changed'}
 $suffix=[byte[]]$bytes[$transition.prefix_bytes..($transition.prefix_bytes+$transition.appended_bytes-1)]
 if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($suffix)).ToLowerInvariant() -ne $transition.appended_sha256){throw 'R75 alias append changed'}
 $memoryCompletePreviousPrefixes++
}
if($memoryCompletePreviousPrefixes -ne 15){throw 'Incomplete historical prefix preservation'}
if($memoryCurrentBinding.r76_complete_previous_sources.Count -ne 3){throw 'Incomplete R75 to R76 prefix set'}
foreach($transition in $memoryCurrentBinding.r76_complete_previous_sources){
 $bytes=[IO.File]::ReadAllBytes((Join-Path $memoryRoot $transition.file))
 if($transition.from_round -ne 75 -or -not(Memory-HistoricalContainer $bytes ($transition.prefix_bytes+$transition.appended_bytes) $transition.current_sha256) -or -not(Memory-HistoricalContainer $bytes $transition.prefix_bytes $transition.prefix_sha256)){throw 'Complete R75 prefix or current R76 provenance changed'}
 $suffix=[byte[]]$bytes[$transition.prefix_bytes..($transition.prefix_bytes+$transition.appended_bytes-1)]
 if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($suffix)).ToLowerInvariant() -ne $transition.appended_sha256){throw 'R76 append changed'}
 $memoryCompletePreviousPrefixes++
}
if($memoryCompletePreviousPrefixes -ne 18){throw 'Incomplete R76 historical prefix preservation'}
if($memoryCurrentBinding.r77_complete_previous_sources.Count -ne 1){throw 'Incomplete R76 to R77 full prefix set'}
foreach($transition in $memoryCurrentBinding.r77_complete_previous_sources){
 $bytes=[IO.File]::ReadAllBytes((Join-Path $memoryRoot $transition.file))
 if($transition.from_round -ne 76 -or $transition.current_sha256 -ne $memoryNativeSeen[$transition.file] -or $bytes.Length -ne $transition.prefix_bytes+$transition.appended_bytes -or -not(Memory-HistoricalContainer $bytes $transition.prefix_bytes $transition.prefix_sha256)){throw 'R76 full source prefix or R77 provenance changed'}
 $suffix=[byte[]]$bytes[$transition.prefix_bytes..($bytes.Length-1)]
 if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($suffix)).ToLowerInvariant() -ne $transition.appended_sha256){throw 'R77 data suffix changed'}
 $memoryCompletePreviousPrefixes++
}
if($memoryCompletePreviousPrefixes -ne 19){throw 'Incomplete R77 source prefix preservation'}



$memoryFiles=@('src/runtime_memory_layout.c','src/runtime_memory_layout.h','tests/test_runtime_memory_layout.c'|ForEach-Object {Join-Path $memoryRoot $_})+@($PSCommandPath,$memoryRuntime,$memoryBoot,$memoryWitness,$memoryFixture,$memoryBindingPath)+$memoryNativePaths
$memoryBefore=@{};foreach($memoryPath in $memoryFiles){$memoryBefore[$memoryPath]=(Get-FileHash -LiteralPath $memoryPath -Algorithm SHA256).Hash.ToLowerInvariant()}
if($memoryBefore[$memoryRuntime] -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc' -or $memoryBefore[$memoryBoot] -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'Fixed image identity mismatch'}
$memoryFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $memoryRoot 'src')),('/Fo'+$memoryBuild+'\'))
$memoryFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$memoryCompile=@(& $memoryCompiler @memoryFlags (Join-Path $memoryRoot 'src/runtime_memory_layout.c') (Join-Path $memoryRoot 'tests/test_runtime_memory_layout.c') ('/Fe'+$memoryExe) /link /INCREMENTAL:NO)
if($LASTEXITCODE -ne 0){throw ('Offline memory checker compile failed: '+($memoryCompile -join ' '))}
$memoryLines=@(& $memoryExe $memoryRuntime $memoryBoot);$memoryExit=$LASTEXITCODE
$memorySummaries=@($memoryLines|Where-Object {$_ -like 'RUNTIME_MEMORY_RESULT *'})
if($memorySummaries.Count -ne 1){throw 'Missing complete checker result'}
$memoryResult=$memorySummaries[0].Substring('RUNTIME_MEMORY_RESULT '.Length)|ConvertFrom-Json
if($memoryResult.gp_fixture_rows -ne $memoryInput.cases.Count -or $memoryResult.legacy_checks -ne 262){throw 'Witness/legacy coverage count mismatch'}
foreach($memoryPath in $memoryBefore.Keys){if((Get-FileHash -LiteralPath $memoryPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $memoryBefore[$memoryPath]){throw 'Input changed'}}
[pscustomobject]@{suite=$memoryMode;passed=($memoryExit -eq 0 -and $memoryResult.passed);exit_code=$memoryExit;result=$memoryResult;native_source_guards_checked=$memoryNativePaths.Count;preserved_frozen_native_source_guards=$memoryLegacySources;unchanged_frozen_native_source_guards=$memoryUnchangedLegacySources;appended_alias_source_guards=10;appended_frozen_source_guards=$memoryAppendedSources;appended_executable_source_guards=2;complete_previous_container_prefixes_checked=$memoryCompletePreviousPrefixes;fixture_profile_round=56;native_profile_round=77;fixture_sha256=$memoryInput.fixture_sha256;fixture_rows=$memoryInput.cases.Count;failure_examples=@($memoryLines|Where-Object {$_ -like 'FAIL*'}|Select-Object -First 12);exe=$memoryExe;exe_sha256=(Get-FileHash -LiteralPath $memoryExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$memoryCompiler;compiler_sha256=(Get-FileHash -LiteralPath $memoryCompiler -Algorithm SHA256).Hash.ToLowerInvariant();flags=$memoryFlags;source_sha256=$memoryBefore;network=$false;original_executed=$false;reconstructed_target_executed=$false;emulation=$false;hardware=$false;native_bin=$false}|ConvertTo-Json -Depth 8 -Compress
exit $memoryExit
