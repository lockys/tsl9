param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools='C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin'
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-dispatch-native-cpp'}else{'target-dispatch-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-dispatch-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_dispatch.c','src/target_dispatch.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_dispatch')){
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
 if(-not $nativeRelocation.defined -and $nativeRelocation.symbol -notin @('__tsl9_state_bfb4','tsl9_dispatch_reference_1051c','tsl9_internal_tx_apply_c544','tsl9_runtime_unported_1013a','tsl9_runtime_unported_102be','tsl9_runtime_unported_10564','tsl9_runtime_unported_105c8','tsl9_runtime_unported_106b8','tsl9_runtime_unported_106ec','tsl9_runtime_unported_10754','tsl9_runtime_unported_107b2','tsl9_runtime_unported_107c0','tsl9_runtime_unported_10840','tsl9_runtime_unported_1087c','tsl9_runtime_unported_10892','tsl9_runtime_unported_10942','tsl9_runtime_unported_10986','tsl9_runtime_unported_109dc','tsl9_runtime_unported_139e6','tsl9_runtime_unported_1835a','tsl9_runtime_unported_829e','tsl9_runtime_unported_9f6e','tsl9_runtime_unported_a5fe','tsl9_runtime_unported_aac2','tsl9_runtime_unported_ad16','tsl9_runtime_unported_ad72','tsl9_runtime_unported_af66','tsl9_runtime_unported_afc6','tsl9_runtime_unported_b0f4','tsl9_runtime_unported_b168','tsl9_runtime_unported_b186','tsl9_runtime_unported_b250','tsl9_runtime_unported_b5ba','tsl9_runtime_unported_bc1a','tsl9_runtime_unported_c270','tsl9_runtime_unported_c30e','tsl9_runtime_unported_c4aa','tsl9_runtime_unported_c73e','tsl9_runtime_unported_c7c0','tsl9_runtime_unported_cd1e','tsl9_runtime_unported_cd3a','tsl9_runtime_unported_cdf4','tsl9_runtime_unported_cf62','tsl9_runtime_unported_cfa8','tsl9_runtime_unported_d010','tsl9_runtime_unported_d0e2','tsl9_runtime_unported_d196','tsl9_runtime_unported_d1dc','tsl9_runtime_unported_d25a','tsl9_runtime_unported_d2b0','tsl9_runtime_unported_d324','tsl9_runtime_unported_d420','tsl9_runtime_unported_d526','tsl9_runtime_unported_d8fe','tsl9_runtime_unported_d952','tsl9_runtime_unported_da56','tsl9_runtime_unported_dd7c','tsl9_runtime_unported_ef8a','tsl9_runtime_unported_effe','tsl9_runtime_unported_f076','tsl9_runtime_unported_f714','tsl9_runtime_unported_f918','tsl9_runtime_unported_f932','tsl9_runtime_unported_fa58','tsl9_runtime_unported_fe0c','tsl9_runtime_unported_fe58','tsl9_runtime_unported_fef6','tsl9_runtime_unported_ff48','tsl9_runtime_unported_ff88','tsl9_runtime_unported_ffb2')){throw 'Unexpected unresolved dependency'}
}
if($nativeGlobals.Count -ne 1){throw 'Unexpected public ABI symbols'}
if($nativeWritable.Count -or @($nativeUndefined|Where-Object {$_ -notin @('__tsl9_state_bfb4','tsl9_dispatch_reference_1051c','tsl9_internal_tx_apply_c544','tsl9_runtime_unported_1013a','tsl9_runtime_unported_102be','tsl9_runtime_unported_10564','tsl9_runtime_unported_105c8','tsl9_runtime_unported_106b8','tsl9_runtime_unported_106ec','tsl9_runtime_unported_10754','tsl9_runtime_unported_107b2','tsl9_runtime_unported_107c0','tsl9_runtime_unported_10840','tsl9_runtime_unported_1087c','tsl9_runtime_unported_10892','tsl9_runtime_unported_10942','tsl9_runtime_unported_10986','tsl9_runtime_unported_109dc','tsl9_runtime_unported_139e6','tsl9_runtime_unported_1835a','tsl9_runtime_unported_829e','tsl9_runtime_unported_9f6e','tsl9_runtime_unported_a5fe','tsl9_runtime_unported_aac2','tsl9_runtime_unported_ad16','tsl9_runtime_unported_ad72','tsl9_runtime_unported_af66','tsl9_runtime_unported_afc6','tsl9_runtime_unported_b0f4','tsl9_runtime_unported_b168','tsl9_runtime_unported_b186','tsl9_runtime_unported_b250','tsl9_runtime_unported_b5ba','tsl9_runtime_unported_bc1a','tsl9_runtime_unported_c270','tsl9_runtime_unported_c30e','tsl9_runtime_unported_c4aa','tsl9_runtime_unported_c73e','tsl9_runtime_unported_c7c0','tsl9_runtime_unported_cd1e','tsl9_runtime_unported_cd3a','tsl9_runtime_unported_cdf4','tsl9_runtime_unported_cf62','tsl9_runtime_unported_cfa8','tsl9_runtime_unported_d010','tsl9_runtime_unported_d0e2','tsl9_runtime_unported_d196','tsl9_runtime_unported_d1dc','tsl9_runtime_unported_d25a','tsl9_runtime_unported_d2b0','tsl9_runtime_unported_d324','tsl9_runtime_unported_d420','tsl9_runtime_unported_d526','tsl9_runtime_unported_d8fe','tsl9_runtime_unported_d952','tsl9_runtime_unported_da56','tsl9_runtime_unported_dd7c','tsl9_runtime_unported_ef8a','tsl9_runtime_unported_effe','tsl9_runtime_unported_f076','tsl9_runtime_unported_f714','tsl9_runtime_unported_f918','tsl9_runtime_unported_f932','tsl9_runtime_unported_fa58','tsl9_runtime_unported_fe0c','tsl9_runtime_unported_fe58','tsl9_runtime_unported_fef6','tsl9_runtime_unported_ff48','tsl9_runtime_unported_ff88','tsl9_runtime_unported_ffb2')}).Count){throw 'Unexpected external dependency or writable section'}
foreach($nativeApi in @('tsl9_runtime_unported_14af8')){if($nativeApi -notin $nativeGlobals){throw 'Missing C ABI export'}}
$irqOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $irqOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Original Runtime identity mismatch'}
$irqBytes=[IO.File]::ReadAllBytes($irqOriginal)
if($irqBytes.Length -ne 76800){throw 'Unexpected original length'}
$nativePassed=$nativeUndefined.Count -eq 70
$dispatchSpecs=@(@{name='tsl9_dispatch_mode_8294';start=33428;bytes=10;calls=@();pairs=@(@{offset=0;lo_offset=4;original_target=536919985;symbol='__tsl9_state_bfb4';addend=-3;lo_type=24;defined=$false;role='data';low_opcode='lbu'})},@{name='tsl9_runtime_unported_14af8';start=84728;bytes=1878;calls=@(@{offset=8;width=4;target=33428;name='tsl9_dispatch_mode_8294';rd=1;defined=$true},@{offset=44;width=4;target=68060;name='tsl9_runtime_unported_109dc';rd=0;defined=$false},@{offset=156;width=4;target=52724;name='tsl9_runtime_unported_cdf4';rd=0;defined=$false},@{offset=190;width=4;target=52510;name='tsl9_runtime_unported_cd1e';rd=1;defined=$false},@{offset=202;width=4;target=52538;name='tsl9_runtime_unported_cd3a';rd=0;defined=$false},@{offset=238;width=4;target=45300;name='tsl9_runtime_unported_b0f4';rd=0;defined=$false},@{offset=292;width=4;target=65458;name='tsl9_runtime_unported_ffb2';rd=0;defined=$false},@{offset=370;width=4;target=55550;name='tsl9_runtime_unported_d8fe';rd=0;defined=$false},@{offset=406;width=4;target=53160;name='tsl9_runtime_unported_cfa8';rd=0;defined=$false},@{offset=470;width=4;target=61322;name='tsl9_runtime_unported_ef8a';rd=0;defined=$false},@{offset=556;width=4;target=65270;name='tsl9_runtime_unported_fef6';rd=0;defined=$false},@{offset=586;width=4;target=49934;name='tsl9_runtime_unported_c30e';rd=1;defined=$false},@{offset=598;width=4;target=50346;name='tsl9_runtime_unported_c4aa';rd=0;defined=$false},@{offset=650;width=4;target=65416;name='tsl9_runtime_unported_ff88';rd=0;defined=$false},@{offset=684;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=1;defined=$false},@{offset=696;width=4;target=42494;name='tsl9_runtime_unported_a5fe';rd=0;defined=$false},@{offset=744;width=4;target=53264;name='tsl9_runtime_unported_d010';rd=0;defined=$false},@{offset=774;width=4;target=65036;name='tsl9_runtime_unported_fe0c';rd=1;defined=$false},@{offset=786;width=4;target=65112;name='tsl9_runtime_unported_fe58';rd=0;defined=$false},@{offset=798;width=4;target=53474;name='tsl9_runtime_unported_d0e2';rd=0;defined=$false},@{offset=808;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=1;defined=$false},@{offset=820;width=4;target=56700;name='tsl9_runtime_unported_dd7c';rd=0;defined=$false},@{offset=832;width=4;target=55634;name='tsl9_runtime_unported_d952';rd=0;defined=$false},@{offset=844;width=4;target=66238;name='tsl9_runtime_unported_102be';rd=0;defined=$false},@{offset=860;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=0;defined=$false},@{offset=872;width=4;target=55894;name='tsl9_runtime_unported_da56';rd=0;defined=$false},@{offset=884;width=4;target=45446;name='tsl9_runtime_unported_b186';rd=0;defined=$false},@{offset=896;width=4;target=43714;name='tsl9_runtime_unported_aac2';rd=0;defined=$false},@{offset=902;width=4;target=51006;name='tsl9_runtime_unported_c73e';rd=1;defined=$false},@{offset=914;width=4;target=51136;name='tsl9_runtime_unported_c7c0';rd=0;defined=$false},@{offset=926;width=4;target=65850;name='tsl9_runtime_unported_1013a';rd=0;defined=$false},@{offset=938;width=4;target=53090;name='tsl9_runtime_unported_cf62';rd=0;defined=$false},@{offset=950;width=4;target=53654;name='tsl9_runtime_unported_d196';rd=0;defined=$false},@{offset=960;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=1;defined=$false},@{offset=966;width=4;target=61438;name='tsl9_runtime_unported_effe';rd=1;defined=$false},@{offset=980;width=4;target=61558;name='tsl9_runtime_unported_f076';rd=0;defined=$false},@{offset=992;width=4;target=44998;name='tsl9_runtime_unported_afc6';rd=0;defined=$false},@{offset=1010;width=4;target=44902;name='tsl9_runtime_unported_af66';rd=0;defined=$false},@{offset=1026;width=4;target=45648;name='tsl9_runtime_unported_b250';rd=0;defined=$false},@{offset=1038;width=4;target=53936;name='tsl9_runtime_unported_d2b0';rd=0;defined=$false},@{offset=1050;width=4;target=45416;name='tsl9_runtime_unported_b168';rd=0;defined=$false},@{offset=1072;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=1;defined=$false},@{offset=1084;width=4;target=53850;name='tsl9_runtime_unported_d25a';rd=0;defined=$false},@{offset=1096;width=4;target=53724;name='tsl9_runtime_unported_d1dc';rd=0;defined=$false},@{offset=1110;width=4;target=67256;name='tsl9_runtime_unported_106b8';rd=1;defined=$false},@{offset=1118;width=4;target=66916;name='tsl9_runtime_unported_10564';rd=1;defined=$false},@{offset=1130;width=4;target=63252;name='tsl9_runtime_unported_f714';rd=0;defined=$false},@{offset=1142;width=4;target=54052;name='tsl9_runtime_unported_d324';rd=0;defined=$false},@{offset=1160;width=4;target=54304;name='tsl9_runtime_unported_d420';rd=0;defined=$false},@{offset=1170;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=1;defined=$false},@{offset=1176;width=4;target=63768;name='tsl9_runtime_unported_f918';rd=1;defined=$false},@{offset=1188;width=4;target=63794;name='tsl9_runtime_unported_f932';rd=0;defined=$false},@{offset=1208;width=4;target=46522;name='tsl9_runtime_unported_b5ba';rd=1;defined=$false},@{offset=1220;width=4;target=48154;name='tsl9_runtime_unported_bc1a';rd=0;defined=$false},@{offset=1230;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=1;defined=$false},@{offset=1250;width=4;target=65352;name='tsl9_runtime_unported_ff48';rd=0;defined=$false},@{offset=1268;width=4;target=49776;name='tsl9_runtime_unported_c270';rd=0;defined=$false},@{offset=1278;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=1;defined=$false},@{offset=1292;width=4;target=67256;name='tsl9_runtime_unported_106b8';rd=1;defined=$false},@{offset=1302;width=4;target=44310;name='tsl9_runtime_unported_ad16';rd=1;defined=$false},@{offset=1314;width=4;target=64088;name='tsl9_runtime_unported_fa58';rd=0;defined=$false},@{offset=1332;width=4;target=54566;name='tsl9_runtime_unported_d526';rd=0;defined=$false},@{offset=1360;width=4;target=80358;name='tsl9_runtime_unported_139e6';rd=0;defined=$false},@{offset=1406;width=4;target=99162;name='tsl9_runtime_unported_1835a';rd=0;defined=$false},@{offset=1416;width=4;target=33438;name='tsl9_runtime_unported_829e';rd=1;defined=$false},@{offset=1428;width=4;target=50500;name='tsl9_internal_tx_apply_c544';rd=0;defined=$false},@{offset=1434;width=4;target=40814;name='tsl9_runtime_unported_9f6e';rd=1;defined=$false},@{offset=1454;width=4;target=67256;name='tsl9_runtime_unported_106b8';rd=0;defined=$false},@{offset=1466;width=4;target=44402;name='tsl9_runtime_unported_ad72';rd=0;defined=$false},@{offset=1670;width=4;target=67412;name='tsl9_runtime_unported_10754';rd=0;defined=$false},@{offset=1702;width=4;target=67520;name='tsl9_runtime_unported_107c0';rd=0;defined=$false},@{offset=1742;width=4;target=67308;name='tsl9_runtime_unported_106ec';rd=0;defined=$false},@{offset=1754;width=4;target=67648;name='tsl9_runtime_unported_10840';rd=0;defined=$false},@{offset=1766;width=4;target=67708;name='tsl9_runtime_unported_1087c';rd=0;defined=$false},@{offset=1806;width=4;target=67906;name='tsl9_runtime_unported_10942';rd=0;defined=$false},@{offset=1818;width=4;target=67730;name='tsl9_runtime_unported_10892';rd=0;defined=$false},@{offset=1830;width=4;target=67974;name='tsl9_runtime_unported_10986';rd=0;defined=$false},@{offset=1862;width=4;target=67506;name='tsl9_runtime_unported_107b2';rd=0;defined=$false},@{offset=1874;width=4;target=67016;name='tsl9_runtime_unported_105c8';rd=0;defined=$false});pairs=@(@{offset=18;lo_offset=22;original_target=107324;symbol='tsl9_dispatch_mode_table_1a33c';addend=0;lo_type=24;defined=$true;role='readonly-table';low_opcode='addi'},@{offset=1102;lo_offset=1106;original_target=66844;symbol='tsl9_dispatch_reference_1051c';addend=0;lo_type=24;defined=$false;role='opaque-address';low_opcode='addi'},@{offset=1284;lo_offset=1288;original_target=66844;symbol='tsl9_dispatch_reference_1051c';addend=0;lo_type=24;defined=$false;role='opaque-address';low_opcode='addi'},@{offset=1444;lo_offset=1448;original_target=66844;symbol='tsl9_dispatch_reference_1051c';addend=0;lo_type=24;defined=$false;role='opaque-address';low_opcode='addi'},@{offset=1542;lo_offset=1546;original_target=107352;symbol='tsl9_dispatch_bits_table_1a358';addend=0;lo_type=24;defined=$true;role='readonly-table';low_opcode='addi'})})
$dispatchBodies=@();$dispatchAllPassed=$true
foreach($expected in $dispatchSpecs){
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
 if(-not$match){$dispatchAllPassed=$false}
 $dispatchBodies+=@([pscustomobject]@{name=$expected.name;original_va=$expected.start;expected_bytes=$expected.bytes;actual_bytes=$symbol.size;nonrelocated_bytes_identical=$match;original_normalized_sha256=$originalHash;compiled_normalized_sha256=$actualHash;symbolic_jumps=$jumpChecks;pc_relative_pairs=$pairChecks})
}
$nativePassed=$nativePassed -and $dispatchAllPassed


$dispatchTableSpecs=@(@{base=107324;bytes=28;raw_hex='e0a7ffffeca7ffff26aeffff46aeffff66aeffffa6aeffffe6aeffff';entries=@(@{ordinal=0;offset=-22560;target=84764;case_offset=36},@{ordinal=1;offset=-22548;target=84776;case_offset=48},@{ordinal=2;offset=-20954;target=86370;case_offset=1642},@{ordinal=3;offset=-20922;target=86402;case_offset=1674},@{ordinal=4;offset=-20890;target=86434;case_offset=1706},@{ordinal=5;offset=-20826;target=86498;case_offset=1770},@{ordinal=6;offset=-20762;target=86562;case_offset=1834});name='tsl9_dispatch_mode_table_1a33c';root_start=84728},@{base=107352;bytes=32;raw_hex='bcadffffc4adffffc8adffffe4adffff04aeffff04aeffff04aeffff00aeffff';entries=@(@{ordinal=0;offset=-21060;target=86292;case_offset=1564},@{ordinal=1;offset=-21052;target=86300;case_offset=1572},@{ordinal=2;offset=-21048;target=86304;case_offset=1576},@{ordinal=3;offset=-21020;target=86332;case_offset=1604},@{ordinal=4;offset=-20988;target=86364;case_offset=1636},@{ordinal=5;offset=-20988;target=86364;case_offset=1636},@{ordinal=6;offset=-20988;target=86364;case_offset=1636},@{ordinal=7;offset=-20992;target=86360;case_offset=1632});name='tsl9_dispatch_bits_table_1a358';root_start=84728})
$dispatchTables=@();$dispatchAllTablesPassed=$true
foreach($t in $dispatchTableSpecs){
 $syms=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $t.name})
 if($syms.Count -ne 1){throw 'Missing unique dispatch table'}
 $ts=$syms[0];$sec=$nativeSections[$ts.index]
 if($ts.type -ne 1 -or ($sec.flags-band7) -ne 2 -or $ts.size -ne $t.bytes -or $ts.value+$ts.size -gt $sec.size){throw 'Invalid readonly dispatch object'}
 $rs=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq 'tsl9_runtime_unported_14af8'})[0]
 $entries=@()
 foreach($e in $t.entries){
  $at=$ts.value+4*$e.ordinal
  $rr=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $ts.index -and $_.offset -eq $at})
  $ar=@($rr|Where-Object {$_.type -eq 35});$sr=@($rr|Where-Object {$_.type -eq 39})
  $word=Read-Native32 ($sec.offset+$at);$effective=$null;$recovered=$null;$ok=$false;$a=$null;$b=$null
  if($rr.Count -eq 2 -and $ar.Count -eq 1 -and $sr.Count -eq 1){
   $a=$nativeSymbolLookup[$ar[0].symbol_table.ToString()+':'+$ar[0].symbol_index.ToString()]
   $b=$nativeSymbolLookup[$sr[0].symbol_table.ToString()+':'+$sr[0].symbol_index.ToString()]
   $effective=([long]$word+$a.value+$ar[0].addend-$rs.value-($b.value+$sr[0].addend-$ts.value))-band4294967295
   $recovered=([long]$t.root_start-$t.base+$effective)-band4294967295
   $oracle=[BitConverter]::ToUInt32($irqBytes,$t.base-0x8000+4*$e.ordinal)
   $ok=$a.index -eq $rs.index -and $b.index -eq $ts.index -and $effective -eq $e.case_offset -and $e.target -eq $t.root_start+$e.case_offset -and $recovered -eq $oracle
  }
  if(-not$ok){$dispatchAllTablesPassed=$false}
  $entries+=@([pscustomobject]@{ordinal=$e.ordinal;target=$e.target;case_offset=$e.case_offset;raw_word=$word;effective_case_offset=$effective;recovered_original_word=$recovered;relocations=$rr;add_symbol=$a;subtract_symbol=$b;verified=$ok})
 }
 $dispatchTables+=@([pscustomobject]@{name=$t.name;original_base=$t.base;bytes=$ts.size;section=$ts.index;value=$ts.value;type=$ts.type;entries=$entries})
}
$dispatchReadonly=@($nativeSections|Where-Object {($_.flags-band2) -and -not($_.flags-band4) -and $_.size})
$dispatchReadonlyBytes=($dispatchReadonly|Measure-Object -Property size -Sum).Sum
if($dispatchReadonlyBytes -ne 60 -or $dispatchReadonly.Count -ne 2){throw 'Unexpected allocated non-executable data'}
$nativePassed=$nativePassed -and $dispatchAllTablesPassed


if($nativeRelocations -ne 121){$nativePassed=$false}
foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Native module input changed'}}
[pscustomobject]@{suite=$nativeMode;passed=$nativePassed;dispatch_bodies=$dispatchBodies;symbolic_jumps=79;pc_relative_pairs=6;dispatch_tables=$dispatchTables;readonly_table_bytes=$dispatchReadonlyBytes;table_relocations=30;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;physical_irq_abi_verified=$false;network=$false;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 10 -Compress
exit $(if($nativePassed){0}else{1})
