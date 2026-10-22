param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools=$env:TSL9_LLVM_BIN
if([string]::IsNullOrWhiteSpace($nativeTools)){throw 'Set TSL9_LLVM_BIN to the existing LLVM toolchain bin directory.'}
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-ble-event-handler-native-cpp'}else{'target-ble-event-handler-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-ble-event-handler-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_ble_event_handler.c','src/target_ble_event_handler.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_ble_event_handler')){
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
   $nativeSymbolLookup[($nativeSection.index.ToString()+':'+($j/16).ToString())]=@{name=$nativeSymbol;index=$nativeIndex;value=(Read-Native32 ($offset+4));size=(Read-Native32 ($offset+8));type=($nativeBytes[$offset+12]-band15)}
   if($nativeSymbol -and $nativeIndex -eq 0){$nativeUndefined+=@($nativeSymbol)}
   if($nativeSymbol -and $nativeIndex -ne 0 -and (($nativeBytes[$offset+12] -shr 4) -eq 1)){$nativeGlobals+=@($nativeSymbol)}
  }
 }
}
foreach($nativeRelocation in $nativeRelocationRecords){
 $nativeKey=$nativeRelocation.symbol_table.ToString()+':'+$nativeRelocation.symbol_index.ToString()
 if(-not $nativeSymbolLookup.ContainsKey($nativeKey)){throw 'Relocation symbol absent'}
 $nativeRelocation.symbol=$nativeSymbolLookup[$nativeKey].name
 $nativeRelocation.defined=$nativeSymbolLookup[$nativeKey].index -ne 0
 if(-not $nativeRelocation.defined -and $nativeRelocation.symbol -notin @('tsl9_runtime_unported_8386','tsl9_internal_scheduler_register_9102','tsl9_runtime_unported_10bdc','tsl9_internal_service_events_scan_10c48','tsl9_runtime_unported_10cfe','tsl9_runtime_unported_10d2e','tsl9_internal_service_events_dispatch_111d2','tsl9_runtime_unported_17dfa','tsl9_event_reference_94e6','__tsl9_ble_service_state_12','__tsl9_ble_service_state_24','__tsl9_ble_connections_36','__tsl9_ble_event_ro_1a240','__tsl9_ble_event_ro_1a248','__tsl9_ble_event_ro_1a250','__tsl9_ble_event_ro_1a264','__tsl9_ble_event_ro_1a26c','__tsl9_ble_event_ro_1a278','__tsl9_ble_event_ro_1a280','__tsl9_ble_event_ro_1a288','__tsl9_ble_event_ro_1a298','__tsl9_ble_event_ro_1a2a0','__tsl9_ble_event_ro_1a2ac','__tsl9_ble_event_ro_1a2b4','__tsl9_ble_event_ro_1a2c0','__tsl9_ble_event_ro_1a2c4','__tsl9_ble_event_ro_1a2d0','__tsl9_ble_event_ro_1a300','__tsl9_ble_event_ro_1a30c')){throw 'Unexpected unresolved dependency'}
}
if($nativeGlobals.Count -ne 1){throw 'Unexpected public ABI symbols'}
if($nativeWritable.Count -or @($nativeUndefined|Where-Object {$_ -notin @('tsl9_runtime_unported_8386','tsl9_internal_scheduler_register_9102','tsl9_runtime_unported_10bdc','tsl9_internal_service_events_scan_10c48','tsl9_runtime_unported_10cfe','tsl9_runtime_unported_10d2e','tsl9_internal_service_events_dispatch_111d2','tsl9_runtime_unported_17dfa','tsl9_event_reference_94e6','__tsl9_ble_service_state_12','__tsl9_ble_service_state_24','__tsl9_ble_connections_36','__tsl9_ble_event_ro_1a240','__tsl9_ble_event_ro_1a248','__tsl9_ble_event_ro_1a250','__tsl9_ble_event_ro_1a264','__tsl9_ble_event_ro_1a26c','__tsl9_ble_event_ro_1a278','__tsl9_ble_event_ro_1a280','__tsl9_ble_event_ro_1a288','__tsl9_ble_event_ro_1a298','__tsl9_ble_event_ro_1a2a0','__tsl9_ble_event_ro_1a2ac','__tsl9_ble_event_ro_1a2b4','__tsl9_ble_event_ro_1a2c0','__tsl9_ble_event_ro_1a2c4','__tsl9_ble_event_ro_1a2d0','__tsl9_ble_event_ro_1a300','__tsl9_ble_event_ro_1a30c')}).Count){throw 'Unexpected external dependency or writable section'}
foreach($nativeApi in @('tsl9_runtime_unported_11844')){if($nativeApi -notin $nativeGlobals){throw 'Missing C ABI export'}}
$irqOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $irqOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Original Runtime identity mismatch'}
$irqBytes=[IO.File]::ReadAllBytes($irqOriginal)
if($irqBytes.Length -ne 76800){throw 'Unexpected original length'}
$nativePassed=$nativeUndefined.Count -eq 29
$bleEventSpecs=@(@{name='tsl9_runtime_unported_11844';start=71748;bytes=2884;calls=@(@{offset=418;width=4;target=70098;name='tsl9_internal_service_events_dispatch_111d2';rd=1;defined=$false},@{offset=478;width=4;target=97786;name='tsl9_runtime_unported_17dfa';rd=1;defined=$false},@{offset=492;width=4;target=97786;name='tsl9_runtime_unported_17dfa';rd=1;defined=$false},@{offset=516;width=4;target=97786;name='tsl9_runtime_unported_17dfa';rd=1;defined=$false},@{offset=542;width=4;target=97786;name='tsl9_runtime_unported_17dfa';rd=1;defined=$false},@{offset=564;width=4;target=97786;name='tsl9_runtime_unported_17dfa';rd=1;defined=$false},@{offset=2018;width=4;target=70098;name='tsl9_internal_service_events_dispatch_111d2';rd=1;defined=$false},@{offset=2250;width=4;target=68910;name='tsl9_runtime_unported_10d2e';rd=1;defined=$false},@{offset=2416;width=4;target=68572;name='tsl9_runtime_unported_10bdc';rd=1;defined=$false},@{offset=2422;width=4;target=68862;name='tsl9_runtime_unported_10cfe';rd=1;defined=$false},@{offset=2442;width=4;target=37122;name='tsl9_internal_scheduler_register_9102';rd=1;defined=$false},@{offset=2454;width=4;target=68680;name='tsl9_internal_service_events_scan_10c48';rd=1;defined=$false},@{offset=2530;width=4;target=33670;name='tsl9_runtime_unported_8386';rd=1;defined=$false},@{offset=2772;width=4;target=68910;name='tsl9_runtime_unported_10d2e';rd=1;defined=$false},@{offset=2806;width=4;target=68910;name='tsl9_runtime_unported_10d2e';rd=1;defined=$false});pairs=@(@{offset=68;lo_offset=72;original_target=536920042;symbol='__tsl9_ble_connections_36';addend=2;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lhu'},@{offset=76;lo_offset=80;original_target=536920040;symbol='__tsl9_ble_connections_36';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='addi'},@{offset=88;lo_offset=92;original_target=536920054;symbol='__tsl9_ble_connections_36';addend=14;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lhu'},@{offset=100;lo_offset=104;original_target=536920066;symbol='__tsl9_ble_connections_36';addend=26;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lhu'},@{offset=178;lo_offset=182;original_target=536920016;symbol='__tsl9_ble_service_state_24';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='addi'},@{offset=214;lo_offset=218;original_target=107080;symbol='__tsl9_ble_event_ro_1a248';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=236;lo_offset=240;original_target=107088;symbol='__tsl9_ble_event_ro_1a250';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=374;lo_offset=378;original_target=536920015;symbol='__tsl9_ble_service_state_12';addend=11;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'},@{offset=384;lo_offset=388;original_target=536920015;symbol='__tsl9_ble_service_state_12';addend=11;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sb'},@{offset=392;lo_offset=396;original_target=536920008;symbol='__tsl9_ble_service_state_12';addend=4;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sw'},@{offset=400;lo_offset=404;original_target=536920012;symbol='__tsl9_ble_service_state_12';addend=8;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sh'},@{offset=410;lo_offset=414;original_target=536920014;symbol='__tsl9_ble_service_state_12';addend=10;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sb'},@{offset=434;lo_offset=438;original_target=536920004;symbol='__tsl9_ble_service_state_12';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'},@{offset=580;lo_offset=584;original_target=107108;symbol='__tsl9_ble_event_ro_1a264';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=674;lo_offset=678;original_target=536920015;symbol='__tsl9_ble_service_state_12';addend=11;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'},@{offset=682;lo_offset=686;original_target=536920004;symbol='__tsl9_ble_service_state_12';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='addi'},@{offset=696;lo_offset=700;original_target=536920015;symbol='__tsl9_ble_service_state_12';addend=11;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sb'},@{offset=704;lo_offset=708;original_target=536920008;symbol='__tsl9_ble_service_state_12';addend=4;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sw'},@{offset=712;lo_offset=716;original_target=536920012;symbol='__tsl9_ble_service_state_12';addend=8;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sh'},@{offset=720;lo_offset=724;original_target=536920014;symbol='__tsl9_ble_service_state_12';addend=10;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sb'},@{offset=740;lo_offset=744;original_target=536920004;symbol='__tsl9_ble_service_state_12';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'},@{offset=762;lo_offset=766;original_target=536920004;symbol='__tsl9_ble_service_state_12';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'},@{offset=782;lo_offset=786;original_target=107116;symbol='__tsl9_ble_event_ro_1a26c';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=876;lo_offset=880;original_target=107128;symbol='__tsl9_ble_event_ro_1a278';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=896;lo_offset=900;original_target=107136;symbol='__tsl9_ble_event_ro_1a280';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=916;lo_offset=920;original_target=107144;symbol='__tsl9_ble_event_ro_1a288';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=940;lo_offset=944;original_target=107160;symbol='__tsl9_ble_event_ro_1a298';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=1322;lo_offset=1326;original_target=107168;symbol='__tsl9_ble_event_ro_1a2a0';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=1566;lo_offset=1570;original_target=107180;symbol='__tsl9_ble_event_ro_1a2ac';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=1652;lo_offset=1656;original_target=107216;symbol='__tsl9_ble_event_ro_1a2d0';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=1776;lo_offset=1780;original_target=107188;symbol='__tsl9_ble_event_ro_1a2b4';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=1882;lo_offset=1886;original_target=107200;symbol='__tsl9_ble_event_ro_1a2c0';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=1902;lo_offset=1906;original_target=107204;symbol='__tsl9_ble_event_ro_1a2c4';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=2010;lo_offset=2014;original_target=536920014;symbol='__tsl9_ble_service_state_12';addend=10;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sb'},@{offset=2030;lo_offset=2034;original_target=536920004;symbol='__tsl9_ble_service_state_12';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'},@{offset=2080;lo_offset=2084;original_target=536920016;symbol='__tsl9_ble_service_state_24';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='addi'},@{offset=2338;lo_offset=2342;original_target=536920029;symbol='__tsl9_ble_service_state_24';addend=13;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'},@{offset=2356;lo_offset=2360;original_target=536920031;symbol='__tsl9_ble_service_state_24';addend=15;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='addi'},@{offset=2364;lo_offset=2368;original_target=536920030;symbol='__tsl9_ble_service_state_24';addend=14;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'},@{offset=2404;lo_offset=2408;original_target=536920016;symbol='__tsl9_ble_service_state_24';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='addi'},@{offset=2434;lo_offset=2438;original_target=38118;symbol='tsl9_event_reference_94e6';addend=0;lo_type=24;defined=$false;role='opaque-callback-address';low_opcode='addi'},@{offset=2446;lo_offset=2450;original_target=536920028;symbol='__tsl9_ble_service_state_24';addend=12;lo_type=25;defined=$false;role='known-numeric-RAM-reference';low_opcode='sb'},@{offset=2480;lo_offset=2484;original_target=107276;symbol='__tsl9_ble_event_ro_1a30c';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=2488;lo_offset=2492;original_target=107264;symbol='__tsl9_ble_event_ro_1a300';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=2548;lo_offset=2552;original_target=107072;symbol='__tsl9_ble_event_ro_1a240';addend=0;lo_type=24;defined=$false;role='opaque-flash-address';low_opcode='addi'},@{offset=2740;lo_offset=2744;original_target=536920016;symbol='__tsl9_ble_service_state_24';addend=0;lo_type=24;defined=$false;role='known-numeric-RAM-reference';low_opcode='lbu'})})
$bleEventBodies=@();$bleEventAllPassed=$true
foreach($expected in $bleEventSpecs){
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
 if(-not$match){$bleEventAllPassed=$false}
 $bleEventBodies+=@([pscustomobject]@{name=$expected.name;original_va=$expected.start;expected_bytes=$expected.bytes;actual_bytes=$symbol.size;nonrelocated_bytes_identical=$match;original_normalized_sha256=$originalHash;compiled_normalized_sha256=$actualHash;symbolic_jumps=$jumpChecks;pc_relative_pairs=$pairChecks})
}
$nativePassed=$nativePassed -and $bleEventAllPassed


if(@($nativeSections|Where-Object {($_.flags-band2) -and -not($_.flags-band4) -and $_.size}).Count){throw 'Unexpected allocated non-executable data'}

if($nativeRelocations -ne 107){$nativePassed=$false}
foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Native module input changed'}}
[pscustomobject]@{suite=$nativeMode;passed=$nativePassed;ble_event_bodies=$bleEventBodies;symbolic_jumps=@($bleEventBodies|ForEach-Object {$_.symbolic_jumps}).Count;pc_relative_pairs=@($bleEventBodies|ForEach-Object {$_.pc_relative_pairs}).Count;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;physical_irq_abi_verified=$false;network=$false;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 10 -Compress
exit $(if($nativePassed){0}else{1})
