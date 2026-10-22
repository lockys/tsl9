param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools=$env:TSL9_LLVM_BIN
if([string]::IsNullOrWhiteSpace($nativeTools)){throw 'Set TSL9_LLVM_BIN to the existing LLVM toolchain bin directory.'}
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-startup-callbacks-native-cpp'}else{'target-startup-callbacks-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-startup-callbacks-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_startup_callbacks.c','src/target_startup_callbacks.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_startup_callbacks')){
 $nativePart=Join-Path $nativeBuild ($nativeUnit+'-'+[Guid]::NewGuid().ToString('N')+'.o')
 & $nativeClang @nativeFlags -c (Join-Path $nativeRoot ('src/'+$nativeUnit+'.c')) -o $nativePart
 if($LASTEXITCODE -ne 0){throw ('Freestanding component compile failed: '+$nativeUnit)}
 $nativeObjects+=@($nativePart)
 $nativePartRecords+=@([pscustomobject]@{object=$nativePart;object_sha256=(Get-FileHash -LiteralPath $nativePart -Algorithm SHA256).Hash.ToLowerInvariant();object_bytes=(Get-Item -LiteralPath $nativePart).Length})
}
& $nativeLld -r --no-relax @nativeObjects -o $nativeObject
if($LASTEXITCODE -ne 0){throw 'Relocatable reset-and-clock link failed'}
$nativeBytes=[IO.File]::ReadAllBytes($nativeObject)
function Read-Native16([int]$offset){[BitConverter]::ToUInt16($nativeBytes,$offset)}
function Read-Native32([int]$offset){[BitConverter]::ToUInt32($nativeBytes,$offset)}
function Read-NativeName([int]$start){
 $end=$start;while($end -lt $nativeBytes.Length -and $nativeBytes[$end] -ne 0){$end++}
 if($end -eq $nativeBytes.Length){throw 'Unterminated ELF name'}
 [Text.Encoding]::ASCII.GetString($nativeBytes,$start,$end-$start)
}
if([Text.Encoding]::ASCII.GetString($nativeBytes,1,3) -ne 'ELF' -or $nativeBytes[0] -ne 127 -or $nativeBytes[4] -ne 1 -or $nativeBytes[5] -ne 1){throw 'Expected ELF32 little endian'}
if((Read-Native16 16) -ne 1 -or (Read-Native16 18) -ne 243 -or (Read-Native32 24) -ne 0){throw 'Expected RISC-V ET_REL, entry0'}
$nativeSh=Read-Native32 32;$nativeShSize=Read-Native16 46;$nativeShCount=Read-Native16 48;$nativeShStrings=Read-Native16 50
if($nativeShSize -ne 40 -or $nativeShStrings -ge $nativeShCount -or $nativeSh+$nativeShCount*40 -gt $nativeBytes.Length){throw 'Invalid ELF section table'}
$nativeSections=@()
for($i=0;$i -lt $nativeShCount;$i++){
 $offset=$nativeSh+$i*40
 $nativeSections+=@([pscustomobject]@{index=$i;name_index=(Read-Native32 $offset);type=(Read-Native32 ($offset+4));flags=(Read-Native32 ($offset+8));offset=(Read-Native32 ($offset+16));size=(Read-Native32 ($offset+20));link=(Read-Native32 ($offset+24));info=(Read-Native32 ($offset+28));entry_size=(Read-Native32 ($offset+36))})
}
$nativeNames=$nativeSections[$nativeShStrings].offset
$nativeUndefined=@();$nativeGlobals=@();$nativeWritable=@();$nativeRelocations=0;$nativeSymbolLookup=@{};$nativeRelocationRecords=@()
foreach($nativeSection in $nativeSections){
 $nativeName=Read-NativeName ($nativeNames+$nativeSection.name_index)
 if($nativeSection.type -ne 8 -and $nativeSection.offset+$nativeSection.size -gt $nativeBytes.Length){throw 'Section outside object'}
 if(($nativeSection.flags -band 3) -eq 3 -and $nativeSection.size){$nativeWritable+=@($nativeName)}
 if($nativeSection.type -eq 4 -or $nativeSection.type -eq 9){
  $nativeEntryBytes=if($nativeSection.type -eq 4){12}else{8}
  if($nativeSection.entry_size -ne $nativeEntryBytes -or $nativeSection.size%$nativeEntryBytes){throw 'Invalid relocation table'}
  $nativeRelocations+=$nativeSection.size/$nativeEntryBytes
  for($j=0;$j -lt $nativeSection.size;$j+=$nativeEntryBytes){
   $offset=$nativeSection.offset+$j;$nativeInfo=Read-Native32 ($offset+4)
   $nativeRelocationRecords+=@([pscustomobject]@{section=$nativeName;offset=(Read-Native32 $offset);type=($nativeInfo-band255);symbol_index=($nativeInfo-shr8);symbol_table=$nativeSection.link;symbol='';defined=$false;target_section=$nativeSection.info;addend=$(if($nativeEntryBytes -eq 12){[BitConverter]::ToInt32($nativeBytes,$offset+8)}else{0})})
  }
 }
 if($nativeSection.type -eq 2){
  if($nativeSection.entry_size -ne 16 -or $nativeSection.link -ge $nativeShCount){throw 'Invalid symbol table'}
  $nativeStrings=$nativeSections[$nativeSection.link].offset
  for($j=0;$j -lt $nativeSection.size;$j+=16){
   $offset=$nativeSection.offset+$j;$nativeSymbol=Read-NativeName ($nativeStrings+(Read-Native32 $offset));$nativeIndex=Read-Native16 ($offset+14)
   $nativeSymbolLookup[($nativeSection.index.ToString()+':'+($j/16).ToString())]=@{name=$nativeSymbol;index=$nativeIndex;value=(Read-Native32 ($offset+4));size=(Read-Native32 ($offset+8));type=($nativeBytes[$offset+12]-band15);binding=($nativeBytes[$offset+12]-shr4);visibility=($nativeBytes[$offset+13]-band3)}
   if($nativeSymbol -and $nativeIndex -eq 0){$nativeUndefined+=@($nativeSymbol)}
   if($nativeSymbol -and $nativeIndex -ne 0 -and (($nativeBytes[$offset+12] -shr 4) -eq 1) -and ($nativeBytes[$offset+13]-band3) -eq 0){$nativeGlobals+=@($nativeSymbol)}
  }
 }
}
foreach($nativeRelocation in $nativeRelocationRecords){
 $nativeKey=$nativeRelocation.symbol_table.ToString()+':'+$nativeRelocation.symbol_index.ToString()
 if(-not $nativeSymbolLookup.ContainsKey($nativeKey)){throw 'Relocation symbol absent'}
 $nativeRelocation.symbol=$nativeSymbolLookup[$nativeKey].name
 $nativeRelocation.defined=$nativeSymbolLookup[$nativeKey].index -ne 0
}
if($nativeGlobals.Count -ne 30){throw 'Expected 30 emission anchors'}
if($nativeWritable.Count -or $nativeRelocations -ne 109 -or $nativeUndefined.Count -ne 32 -or @($nativeUndefined|Where-Object {$_ -notin @('__tsl9_config_records','__tsl9_feature_state_bed0','__tsl9_feature_state_bee0','__tsl9_feature_state_beec','__tsl9_feature_state_bf18','__tsl9_feature_state_bf24','__tsl9_feature_state_bf34','__tsl9_feature_state_bf44','__tsl9_feature_state_bf58','__tsl9_feature_state_bfa4','__tsl9_feature_state_c91c','tsl9_internal_ble_frame_8cfa','tsl9_internal_config_read_9d9e','tsl9_internal_dispatch_mode_8294','tsl9_internal_gate_8214','tsl9_internal_init_check_identifier_9298','tsl9_internal_mode_channel_mask_16b48','tsl9_internal_periph_clock_81b0','tsl9_internal_rf_control_17048','tsl9_internal_rf_enabled_843a','tsl9_internal_rf_schedule_16f4a','tsl9_internal_scheduler_register_9102','tsl9_internal_service_events_pending_133fa','tsl9_internal_sgpio_idle_9ace','tsl9_internal_spi_byte_1660a','tsl9_internal_spi_read_16708','tsl9_internal_spi_wait_16750','tsl9_internal_spi_write_16652','tsl9_internal_spi_write_reg_167a4','tsl9_runtime_unported_10692','tsl9_runtime_unported_1291c','tsl9_runtime_unported_9e8e')}).Count){throw 'Unexpected dependency, data or relocation'}
$irqOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $irqOriginal).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Fixed image identity'}
$irqBytes=[IO.File]::ReadAllBytes($irqOriginal)
$nativePassed=$true
$startupSpecs=@(@{name='tsl9_runtime_unported_81de';start=33246;bytes=16;calls=@();pairs=@()},@{name='tsl9_runtime_unported_a128';start=41256;bytes=230;calls=@(@{offset=14;width=4;target=43794;name='tsl9_runtime_unported_ab12';rd=1;defined=$true},@{offset=32;width=4;target=52922;name='tsl9_runtime_unported_ceba';rd=0;defined=$true},@{offset=202;width=4;target=46452;name='tsl9_runtime_unported_b574';rd=0;defined=$true});pairs=@()},@{name='tsl9_runtime_unported_a212';start=41490;bytes=142;calls=@(@{offset=10;width=4;target=33428;name='tsl9_internal_dispatch_mode_8294';rd=1;defined=$false},@{offset=20;width=4;target=33246;name='tsl9_runtime_unported_81de';rd=1;defined=$true},@{offset=34;width=2;target=41256;name='tsl9_runtime_unported_a128';rd=1;defined=$true},@{offset=42;width=4;target=33300;name='tsl9_internal_gate_8214';rd=1;defined=$false},@{offset=114;width=4;target=37122;name='tsl9_internal_scheduler_register_9102';rd=0;defined=$false},@{offset=128;width=4;target=67218;name='tsl9_runtime_unported_10692';rd=0;defined=$false});pairs=@(@{offset=104;lo_offset=108;original_target=40590;symbol='tsl9_runtime_unported_9e8e';addend=0;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_a886';start=43142;bytes=14;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919761;symbol='__tsl9_feature_state_bed0';addend=1;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_ab12';start=43794;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919776;symbol='__tsl9_feature_state_bee0';addend=0;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_afc0';start=44992;bytes=6;calls=@();pairs=@()},@{name='tsl9_runtime_unported_b3de';start=46046;bytes=18;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919791;symbol='__tsl9_feature_state_beec';addend=3;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_b574';start=46452;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919820;symbol='__tsl9_feature_state_bf18';addend=-12;lo_type=25;defined=$false})},@{name='tsl9_runtime_unported_c1f6';start=49654;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919826;symbol='__tsl9_feature_state_bf18';addend=-6;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_cbae';start=52142;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919846;symbol='__tsl9_feature_state_bf24';addend=2;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_ceba';start=52922;bytes=32;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919860;symbol='__tsl9_feature_state_bf34';addend=0;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_d006';start=53254;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919876;symbol='__tsl9_feature_state_bf44';addend=0;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_d16e';start=53614;bytes=14;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919896;symbol='__tsl9_feature_state_bf58';addend=0;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_d24c';start=53836;bytes=14;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919899;symbol='__tsl9_feature_state_bf58';addend=3;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_f564';start=62820;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919961;symbol='__tsl9_feature_state_bfa4';addend=-11;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_f596';start=62870;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919963;symbol='__tsl9_feature_state_bfa4';addend=-9;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_f5c8';start=62920;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919966;symbol='__tsl9_feature_state_bfa4';addend=-6;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_f5fa';start=62970;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919968;symbol='__tsl9_feature_state_bfa4';addend=-4;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_f848';start=63560;bytes=6;calls=@();pairs=@()},@{name='tsl9_runtime_unported_f8e0';start=63712;bytes=6;calls=@();pairs=@()},@{name='tsl9_runtime_unported_f8ec';start=63724;bytes=6;calls=@();pairs=@()},@{name='tsl9_runtime_unported_13160';start=78176;bytes=666;calls=@(@{offset=24;width=4;target=40350;name='tsl9_internal_config_read_9d9e';rd=1;defined=$false},@{offset=92;width=4;target=37528;name='tsl9_internal_init_check_identifier_9298';rd=1;defined=$false},@{offset=98;width=4;target=53254;name='tsl9_runtime_unported_d006';rd=1;defined=$true},@{offset=170;width=4;target=63712;name='tsl9_runtime_unported_f8e0';rd=1;defined=$true},@{offset=186;width=4;target=44992;name='tsl9_runtime_unported_afc0';rd=1;defined=$true},@{offset=202;width=4;target=63724;name='tsl9_runtime_unported_f8ec';rd=1;defined=$true},@{offset=226;width=4;target=43142;name='tsl9_runtime_unported_a886';rd=1;defined=$true},@{offset=234;width=4;target=53614;name='tsl9_runtime_unported_d16e';rd=1;defined=$true},@{offset=250;width=4;target=53836;name='tsl9_runtime_unported_d24c';rd=1;defined=$true},@{offset=266;width=4;target=98152;name='tsl9_runtime_unported_17f68';rd=1;defined=$true},@{offset=284;width=4;target=98152;name='tsl9_runtime_unported_17f68';rd=1;defined=$true},@{offset=302;width=4;target=46046;name='tsl9_runtime_unported_b3de';rd=1;defined=$true},@{offset=318;width=4;target=49654;name='tsl9_runtime_unported_c1f6';rd=1;defined=$true},@{offset=334;width=4;target=52142;name='tsl9_runtime_unported_cbae';rd=1;defined=$true},@{offset=350;width=4;target=33850;name='tsl9_internal_rf_enabled_843a';rd=1;defined=$false},@{offset=358;width=4;target=62820;name='tsl9_runtime_unported_f564';rd=1;defined=$true},@{offset=374;width=4;target=62920;name='tsl9_runtime_unported_f5c8';rd=1;defined=$true},@{offset=390;width=4;target=62870;name='tsl9_runtime_unported_f596';rd=1;defined=$true},@{offset=406;width=4;target=62970;name='tsl9_runtime_unported_f5fa';rd=1;defined=$true},@{offset=422;width=4;target=43794;name='tsl9_runtime_unported_ab12';rd=1;defined=$true},@{offset=438;width=4;target=63560;name='tsl9_runtime_unported_f848';rd=1;defined=$true},@{offset=456;width=4;target=33300;name='tsl9_internal_gate_8214';rd=1;defined=$false},@{offset=492;width=4;target=93990;name='tsl9_runtime_unported_16f26';rd=1;defined=$true},@{offset=500;width=4;target=33428;name='tsl9_internal_dispatch_mode_8294';rd=1;defined=$false},@{offset=514;width=4;target=33300;name='tsl9_internal_gate_8214';rd=1;defined=$false},@{offset=524;width=4;target=33300;name='tsl9_internal_gate_8214';rd=1;defined=$false},@{offset=542;width=4;target=33300;name='tsl9_internal_gate_8214';rd=1;defined=$false},@{offset=604;width=4;target=36090;name='tsl9_internal_ble_frame_8cfa';rd=1;defined=$false});pairs=@(@{offset=78;lo_offset=82;original_target=536922000;symbol='__tsl9_config_records';addend=0;lo_type=24;defined=$false})},@{name='tsl9_runtime_unported_13b5c';start=80732;bytes=140;calls=@(@{offset=4;width=4;target=78842;name='tsl9_internal_service_events_pending_133fa';rd=1;defined=$false},@{offset=86;width=4;target=37122;name='tsl9_internal_scheduler_register_9102';rd=0;defined=$false},@{offset=90;width=4;target=33200;name='tsl9_internal_periph_clock_81b0';rd=1;defined=$false},@{offset=122;width=4;target=78176;name='tsl9_runtime_unported_13160';rd=0;defined=$true});pairs=@(@{offset=10;lo_offset=14;original_target=536922002;symbol='__tsl9_config_records';addend=2;lo_type=24;defined=$false},@{offset=20;lo_offset=24;original_target=536922000;symbol='__tsl9_config_records';addend=0;lo_type=24;defined=$false},@{offset=76;lo_offset=80;original_target=78176;symbol='tsl9_runtime_unported_13160';addend=0;lo_type=24;defined=$true})},@{name='tsl9_runtime_unported_168c4';start=92356;bytes=44;calls=@(@{offset=34;width=4;target=91730;name='tsl9_internal_spi_write_16652';rd=1;defined=$false});pairs=@()},@{name='tsl9_runtime_unported_16b78';start=93048;bytes=124;calls=@(@{offset=50;width=4;target=91658;name='tsl9_internal_spi_byte_1660a';rd=1;defined=$false},@{offset=64;width=4;target=33200;name='tsl9_internal_periph_clock_81b0';rd=1;defined=$false},@{offset=76;width=4;target=33200;name='tsl9_internal_periph_clock_81b0';rd=1;defined=$false},@{offset=108;width=4;target=91912;name='tsl9_internal_spi_read_16708';rd=1;defined=$false});pairs=@()},@{name='tsl9_runtime_unported_16bf4';start=93172;bytes=120;calls=@(@{offset=10;width=4;target=93048;name='tsl9_runtime_unported_16b78';rd=1;defined=$true},@{offset=24;width=4;target=91984;name='tsl9_internal_spi_wait_16750';rd=1;defined=$false},@{offset=36;width=4;target=92068;name='tsl9_internal_spi_write_reg_167a4';rd=1;defined=$false},@{offset=50;width=4;target=92068;name='tsl9_internal_spi_write_reg_167a4';rd=1;defined=$false},@{offset=64;width=4;target=92068;name='tsl9_internal_spi_write_reg_167a4';rd=1;defined=$false},@{offset=72;width=4;target=92356;name='tsl9_runtime_unported_168c4';rd=1;defined=$true},@{offset=80;width=4;target=92356;name='tsl9_runtime_unported_168c4';rd=1;defined=$true},@{offset=92;width=4;target=92068;name='tsl9_internal_spi_write_reg_167a4';rd=1;defined=$false},@{offset=104;width=4;target=92068;name='tsl9_internal_spi_write_reg_167a4';rd=1;defined=$false});pairs=@()},@{name='tsl9_runtime_unported_16c6c';start=93292;bytes=182;calls=@(@{offset=56;width=4;target=93172;name='tsl9_runtime_unported_16bf4';rd=1;defined=$true},@{offset=64;width=4;target=93000;name='tsl9_internal_mode_channel_mask_16b48';rd=1;defined=$false},@{offset=108;width=4;target=93172;name='tsl9_runtime_unported_16bf4';rd=1;defined=$true},@{offset=116;width=4;target=93000;name='tsl9_internal_mode_channel_mask_16b48';rd=1;defined=$false},@{offset=134;width=4;target=93172;name='tsl9_runtime_unported_16bf4';rd=1;defined=$true},@{offset=142;width=4;target=93172;name='tsl9_runtime_unported_16bf4';rd=1;defined=$true},@{offset=148;width=4;target=39630;name='tsl9_internal_sgpio_idle_9ace';rd=1;defined=$false},@{offset=154;width=4;target=76060;name='tsl9_runtime_unported_1291c';rd=1;defined=$false});pairs=@()},@{name='tsl9_runtime_unported_16f26';start=93990;bytes=36;calls=@();pairs=@()},@{name='tsl9_runtime_unported_170e2';start=94434;bytes=148;calls=@(@{offset=16;width=4;target=94026;name='tsl9_internal_rf_schedule_16f4a';rd=1;defined=$false},@{offset=44;width=4;target=33428;name='tsl9_internal_dispatch_mode_8294';rd=1;defined=$false},@{offset=70;width=4;target=41490;name='tsl9_runtime_unported_a212';rd=1;defined=$true},@{offset=112;width=4;target=94280;name='tsl9_internal_rf_control_17048';rd=1;defined=$false},@{offset=122;width=4;target=43794;name='tsl9_runtime_unported_ab12';rd=1;defined=$true},@{offset=138;width=4;target=80732;name='tsl9_runtime_unported_13b5c';rd=1;defined=$true});pairs=@()},@{name='tsl9_runtime_unported_17f68';start=98152;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536922396;symbol='__tsl9_feature_state_c91c';addend=0;lo_type=24;defined=$false})})
$startupBodies=@();$startupAllPassed=$true
foreach($expected in $startupSpecs){
 $symbols=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $expected.name})
 if($symbols.Count -ne 1){throw 'Missing unique peripheral function'}
 $symbol=$symbols[0];$section=$nativeSections[$symbol.index]
 if($symbol.type -ne 2 -or ($section.flags-band7) -ne 6 -or $symbol.value+$symbol.size -gt $section.size){throw 'Invalid peripheral function range'}
 $actual=[byte[]]::new($symbol.size);[Array]::Copy($nativeBytes,$section.offset+$symbol.value,$actual,0,$symbol.size)
 $original=[byte[]]::new($expected.bytes);[Array]::Copy($irqBytes,$expected.start-0x8000,$original,0,$expected.bytes)
 $sameLength=$actual.Length -eq $original.Length;$match=$sameLength;$jumpChecks=@();$pairChecks=@()
 foreach($call in $expected.calls){
  $sourceValue=if($call.width -eq 4){[BitConverter]::ToUInt32($original,$call.offset)}else{[BitConverter]::ToUInt16($original,$call.offset)}
  if($call.width -eq 4){
   if(($sourceValue-band0xfff) -ne (0x6f+128*$call.rd)){throw 'Original JAL rd oracle mismatch'}
   $imm=(($sourceValue-shr31)-band1)*0x100000+(($sourceValue-shr21)-band0x3ff)*2+(($sourceValue-shr20)-band1)*0x800+(($sourceValue-shr12)-band255)*0x1000
   if($imm-band0x100000){$imm-=0x200000};$mask=0xfff;$relocType=17
  }else{
   $compressedOpcode=if($call.rd -eq 0){0xa001}else{0x2001}
   if(($sourceValue-band0xe003) -ne $compressedOpcode){throw 'Original RV32 C.J/C.JAL rd oracle mismatch'}
   $imm=(($sourceValue-shr12)-band1)*2048+(($sourceValue-shr11)-band1)*16+(($sourceValue-shr9)-band3)*256+(($sourceValue-shr8)-band1)*1024+(($sourceValue-shr7)-band1)*64+(($sourceValue-shr6)-band1)*128+(($sourceValue-shr3)-band7)*2+(($sourceValue-shr2)-band1)*32
   if($imm-band2048){$imm-=4096};$mask=0xe003;$relocType=45
  }
  if($expected.start+$call.offset+$imm -ne $call.target){throw 'Original direct call oracle mismatch'}
  $rr=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $symbol.index -and $_.offset -eq $symbol.value+$call.offset})
  $ok=$false
  if($sameLength -and $rr.Count -eq 1){
   $actualValue=if($call.width -eq 4){[BitConverter]::ToUInt32($actual,$call.offset)}else{[BitConverter]::ToUInt16($actual,$call.offset)}
   $targets=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $call.name})
   if($targets.Count -eq 1){
    $rs=$nativeSymbolLookup[$rr[0].symbol_table.ToString()+':'+$rr[0].symbol_index.ToString()]
    $targetOk=if($call.defined){$targets[0].index -ne 0 -and $rs.index -eq $targets[0].index -and $rs.value -eq $targets[0].value}else{$targets[0].index -eq 0 -and $rs.index -eq 0 -and $rs.name -eq $call.name}
    $ok=$rr[0].type -eq $relocType -and $rr[0].addend -eq 0 -and $targetOk -and ($actualValue-band$mask) -eq ($sourceValue-band$mask)
   }
   if($call.width -eq 4){
    [BitConverter]::GetBytes([uint32]($actualValue-band$mask)).CopyTo($actual,$call.offset);[BitConverter]::GetBytes([uint32]($sourceValue-band$mask)).CopyTo($original,$call.offset)
   }else{
    [BitConverter]::GetBytes([uint16]($actualValue-band$mask)).CopyTo($actual,$call.offset);[BitConverter]::GetBytes([uint16]($sourceValue-band$mask)).CopyTo($original,$call.offset)
   }
  }
  if(-not$ok){$match=$false}
  $jumpChecks+=@([pscustomobject]@{offset=$call.offset;original_target=$call.target;symbol=$call.name;bytes=$call.width;relocation_type=$relocType;verified=$ok})
 }
 foreach($pair in $expected.pairs){
  $hi=[BitConverter]::ToUInt32($original,$pair.offset);$lo=[BitConverter]::ToUInt32($original,$pair.lo_offset)
  if(($hi-band127) -ne 0x17 -or (($hi-shr7)-band31) -ne (($lo-shr15)-band31)){throw 'Original AUIPC/base register oracle mismatch'}
  $upper=[long]($hi-band4294963200);if($upper-ge2147483648){$upper-=4294967296}
  if($pair.lo_type -eq 25){
   if(($lo-band127) -ne 0x23){throw 'Original low must be S form'}
   $lower=(($lo-shr25)-band127)*32+(($lo-shr7)-band31);$loMask=0x01fff07f
  }else{
   if(($lo-band127) -notin @(0x03,0x13)){throw 'Original low must be load/addi I form'}
   $lower=($lo-shr20)-band4095;$loMask=0xfffff
  }
  if($lower-band2048){$lower-=4096}
  $address=($expected.start+$pair.offset+$upper+$lower)-band4294967295
  if($address -ne $pair.original_target){throw 'Original PC-relative address oracle mismatch'}
  $hiRel=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $symbol.index -and $_.offset -eq $symbol.value+$pair.offset})
  $loRel=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $symbol.index -and $_.offset -eq $symbol.value+$pair.lo_offset})
  $ok=$false
  if($sameLength -and $hiRel.Count -eq 1 -and $loRel.Count -eq 1){
   $ah=[BitConverter]::ToUInt32($actual,$pair.offset);$al=[BitConverter]::ToUInt32($actual,$pair.lo_offset)
   $anchor=$nativeSymbolLookup[$loRel[0].symbol_table.ToString()+':'+$loRel[0].symbol_index.ToString()]
   $hs=$nativeSymbolLookup[$hiRel[0].symbol_table.ToString()+':'+$hiRel[0].symbol_index.ToString()]
   if($pair.defined){
    $dest=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $pair.symbol})
    $hiOk=$dest.Count -eq 1 -and $dest[0].index -ne 0 -and $hs.index -eq $dest[0].index -and $hs.value+$hiRel[0].addend -eq $dest[0].value+$pair.addend
   }else{$hiOk=-not $hiRel[0].defined -and $hiRel[0].symbol -eq $pair.symbol -and $hiRel[0].addend -eq $pair.addend}
   $ok=$hiRel[0].type -eq 23 -and $hiOk -and $loRel[0].type -eq $pair.lo_type -and $loRel[0].addend -eq 0 -and $anchor.index -eq $symbol.index -and $anchor.value -eq $symbol.value+$pair.offset -and ($ah-band0xfff) -eq ($hi-band0xfff) -and ($al-band$loMask) -eq ($lo-band$loMask)
   [BitConverter]::GetBytes([uint32]($ah-band0xfff)).CopyTo($actual,$pair.offset);[BitConverter]::GetBytes([uint32]($hi-band0xfff)).CopyTo($original,$pair.offset)
   [BitConverter]::GetBytes([uint32]($al-band$loMask)).CopyTo($actual,$pair.lo_offset);[BitConverter]::GetBytes([uint32]($lo-band$loMask)).CopyTo($original,$pair.lo_offset)
  }
  if(-not$ok){$match=$false}
  $pairChecks+=@([pscustomobject]@{hi_offset=$pair.offset;lo_offset=$pair.lo_offset;original_target=$pair.original_target;symbol=$pair.symbol;addend=$pair.addend;hi_type=23;lo_type=$pair.lo_type;anchor_verified=$ok})
 }
 $actualHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($actual)).ToLowerInvariant()
 $originalHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($original)).ToLowerInvariant()
 $bodyRelocs=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $symbol.index -and $_.offset -ge $symbol.value -and $_.offset -lt $symbol.value+$symbol.size}).Count
 $match=$match -and $actualHash -eq $originalHash -and $bodyRelocs -eq @($expected.calls).Count+2*@($expected.pairs).Count
 if(-not$match){$startupAllPassed=$false}
 $startupBodies+=@([pscustomobject]@{name=$expected.name;original_va=$expected.start;expected_bytes=$expected.bytes;actual_bytes=$symbol.size;nonrelocated_bytes_identical=$match;original_normalized_sha256=$originalHash;compiled_normalized_sha256=$actualHash;symbolic_jumps=$jumpChecks;pc_relative_pairs=$pairChecks})
}
$nativePassed=$nativePassed -and $startupAllPassed
[pscustomobject]@{suite=$nativeMode;passed=$nativePassed;startup_bodies=$startupBodies;original_code_bytes=2064;original_instructions=708;symbolic_jumps=69;pc_relative_pairs=20;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;undefined_symbols=$nativeUndefined;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;components=$nativePartRecords;network=$false;hardware=$false;original_executed=$false;reconstructed_target_executed=$false;emulation=$false;native_bin=$false;linked_image=$false}|ConvertTo-Json -Depth 10 -Compress
exit $(if($nativePassed){0}else{1})
