param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools='C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin'
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-rf-queue-native-cpp'}else{'target-rf-queue-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-rf-queue-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_rf_queue.c','src/target_rf_queue.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_rf_queue')){
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
 if(-not $nativeRelocation.defined -and $nativeRelocation.symbol -notin @('__tsl9_rf_queue','__tsl9_rf_queue_lookup','__tsl9_scheduler_slots','tsl9_internal_scheduler_register_9102','tsl9_runtime_unported_1730e','tsl9_runtime_unported_c612')){throw 'Unexpected unresolved dependency'}
}
if($nativeGlobals.Count -ne 2){throw 'Unexpected public ABI symbols'}
$nativeHidden=@($nativeSymbolLookup.Values|Where-Object {$_.binding -eq 1 -and $_.visibility -eq 2 -and $_.index -ne 0})
$nativeAlias=@($nativeHidden|Where-Object {$_.name -eq 'tsl9_internal_scheduler_cancel_908e'})
$nativeAliasTarget=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq 'tsl9_scheduler_cancel_908e'})
$nativeAliasOk=$false
if($nativeAlias.Count -eq 1 -and $nativeAliasTarget.Count -eq 1 -and $nativeHidden.Count -eq 1){
 $a=$nativeAlias[0];$t=$nativeAliasTarget[0]
 $nativeAliasOk=$a.binding -eq 1 -and $a.visibility -eq 2 -and $a.type -eq 2 -and $a.size -eq 116 -and $t.binding -eq 0 -and $t.type -eq 2 -and $a.index -eq $t.index -and $a.value -eq $t.value -and $a.size -eq $t.size
}
$nativeAliasProofs=@([pscustomobject]@{name='tsl9_internal_scheduler_cancel_908e';target='tsl9_scheduler_cancel_908e';bytes=116;global=$nativeAliasOk;hidden=$nativeAliasOk;type='STT_FUNC';same_section_value_size=$nativeAliasOk;duplicate_body=$false;verified=$nativeAliasOk;observed_hidden_count=$nativeHidden.Count})

if($nativeWritable.Count -or @($nativeUndefined|Where-Object {$_ -notin @('__tsl9_rf_queue','__tsl9_rf_queue_lookup','__tsl9_scheduler_slots','tsl9_internal_scheduler_register_9102','tsl9_runtime_unported_1730e','tsl9_runtime_unported_c612')}).Count){throw 'Unexpected external dependency or writable section'}
foreach($nativeApi in @('tsl9_runtime_unported_17650','tsl9_runtime_unported_179ca')){if($nativeApi -notin $nativeGlobals){throw 'Missing C ABI export'}}
$irqOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $irqOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Original Runtime identity mismatch'}
$irqBytes=[IO.File]::ReadAllBytes($irqOriginal)
if($irqBytes.Length -ne 76800){throw 'Unexpected original length'}
$nativePassed=$nativeUndefined.Count -eq 6 -and $nativeAliasOk
$queueSpecs=@(@{name='tsl9_scheduler_cancel_908e';start=37006;bytes=116;calls=@();pairs=@(@{offset=2;lo_offset=6;original_target=536919560;symbol='__tsl9_scheduler_slots';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi'})},@{name='tsl9_rf_queue_complete_1743a';start=95290;bytes=58;calls=@(@{offset=40;width=4;target=37006;name='tsl9_scheduler_cancel_908e';rd=1;defined=$true});pairs=@(@{offset=32;lo_offset=36;original_target=95348;symbol='tsl9_rf_queue_handshake_17474';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'})},@{name='tsl9_rf_queue_handshake_17474';start=95348;bytes=88;calls=@(@{offset=36;width=4;target=94990;name='tsl9_runtime_unported_1730e';rd=1;defined=$false},@{offset=78;width=4;target=37122;name='tsl9_internal_scheduler_register_9102';rd=1;defined=$false});pairs=@(@{offset=16;lo_offset=20;original_target=95290;symbol='tsl9_rf_queue_complete_1743a';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'},@{offset=70;lo_offset=74;original_target=95348;symbol='tsl9_rf_queue_handshake_17474';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'})},@{name='tsl9_rf_queue_task_174cc';start=95436;bytes=388;calls=@(@{offset=72;width=4;target=94990;name='tsl9_runtime_unported_1730e';rd=1;defined=$false},@{offset=236;width=4;target=50706;name='tsl9_runtime_unported_c612';rd=1;defined=$false});pairs=@(@{offset=20;lo_offset=24;original_target=536922282;symbol='__tsl9_rf_queue';addend=2;lo_type=24;defined=$false;role='data';low_opcode='lbu'},@{offset=28;lo_offset=32;original_target=536922280;symbol='__tsl9_rf_queue';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi'},@{offset=52;lo_offset=56;original_target=95290;symbol='tsl9_rf_queue_complete_1743a';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'},@{offset=86;lo_offset=90;original_target=536922280;symbol='__tsl9_rf_queue';addend=0;lo_type=25;defined=$false;role='data';low_opcode='sb'},@{offset=100;lo_offset=104;original_target=536922282;symbol='__tsl9_rf_queue';addend=2;lo_type=25;defined=$false;role='data';low_opcode='sb'},@{offset=322;lo_offset=326;original_target=108396;symbol='__tsl9_rf_queue_lookup';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi'})},@{name='tsl9_runtime_unported_17650';start=95824;bytes=124;calls=@(@{offset=110;width=4;target=95290;name='tsl9_rf_queue_complete_1743a';rd=0;defined=$true});pairs=@(@{offset=6;lo_offset=10;original_target=536922282;symbol='__tsl9_rf_queue';addend=2;lo_type=24;defined=$false;role='data';low_opcode='lbu'},@{offset=16;lo_offset=20;original_target=536922282;symbol='__tsl9_rf_queue';addend=2;lo_type=24;defined=$false;role='data';low_opcode='lbu'},@{offset=30;lo_offset=34;original_target=536922280;symbol='__tsl9_rf_queue';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi'},@{offset=74;lo_offset=78;original_target=536922281;symbol='__tsl9_rf_queue';addend=1;lo_type=25;defined=$false;role='data';low_opcode='sb'},@{offset=88;lo_offset=92;original_target=536922282;symbol='__tsl9_rf_queue';addend=2;lo_type=25;defined=$false;role='data';low_opcode='sb'})},@{name='tsl9_rf_queue_empty_frame_176cc';start=95948;bytes=80;calls=@(@{offset=70;width=4;target=95824;name='tsl9_runtime_unported_17650';rd=1;defined=$true});pairs=@()},@{name='tsl9_rf_queue_frame_1771c';start=96028;bytes=66;calls=@(@{offset=60;width=4;target=95824;name='tsl9_runtime_unported_17650';rd=0;defined=$true});pairs=@()},@{name='tsl9_rf_queue_select_1775e';start=96094;bytes=114;calls=@(@{offset=80;width=4;target=95824;name='tsl9_runtime_unported_17650';rd=1;defined=$true});pairs=@()},@{name='tsl9_rf_queue_start_17966';start=96614;bytes=50;calls=@(@{offset=30;width=4;target=37122;name='tsl9_internal_scheduler_register_9102';rd=1;defined=$false});pairs=@(@{offset=16;lo_offset=20;original_target=95348;symbol='tsl9_rf_queue_handshake_17474';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'})},@{name='tsl9_rf_queue_enable_17998';start=96664;bytes=50;calls=@(@{offset=14;width=4;target=37006;name='tsl9_scheduler_cancel_908e';rd=1;defined=$true},@{offset=26;width=4;target=96094;name='tsl9_rf_queue_select_1775e';rd=0;defined=$true},@{offset=46;width=4;target=37122;name='tsl9_internal_scheduler_register_9102';rd=0;defined=$false});pairs=@(@{offset=4;lo_offset=8;original_target=95948;symbol='tsl9_rf_queue_empty_frame_176cc';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'},@{offset=38;lo_offset=42;original_target=95948;symbol='tsl9_rf_queue_empty_frame_176cc';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'})},@{name='tsl9_runtime_unported_179ca';start=96714;bytes=88;calls=@(@{offset=66;width=4;target=37006;name='tsl9_scheduler_cancel_908e';rd=1;defined=$true},@{offset=74;width=4;target=96094;name='tsl9_rf_queue_select_1775e';rd=1;defined=$true},@{offset=84;width=4;target=96614;name='tsl9_rf_queue_start_17966';rd=0;defined=$true});pairs=@(@{offset=30;lo_offset=34;original_target=536922280;symbol='__tsl9_rf_queue';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi'},@{offset=44;lo_offset=48;original_target=95436;symbol='tsl9_rf_queue_task_174cc';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'},@{offset=58;lo_offset=62;original_target=95948;symbol='tsl9_rf_queue_empty_frame_176cc';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi'})})
$queueBodies=@();$queueAllPassed=$true
foreach($expected in $queueSpecs){
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
 if(-not$match){$queueAllPassed=$false}
 $queueBodies+=@([pscustomobject]@{name=$expected.name;original_va=$expected.start;expected_bytes=$expected.bytes;actual_bytes=$symbol.size;nonrelocated_bytes_identical=$match;original_normalized_sha256=$originalHash;compiled_normalized_sha256=$actualHash;symbolic_jumps=$jumpChecks;pc_relative_pairs=$pairChecks})
}
$nativePassed=$nativePassed -and $queueAllPassed

if(@($nativeSections|Where-Object {($_.flags-band2) -and -not($_.flags-band4) -and $_.size}).Count){throw 'Unexpected allocated non-executable data'}

if($nativeRelocations -ne 58){$nativePassed=$false}
foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Native module input changed'}}
[pscustomobject]@{suite=$nativeMode;passed=$nativePassed;queue_bodies=$queueBodies;internal_aliases=$nativeAliasProofs;symbolic_jumps=16;pc_relative_pairs=21;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;physical_irq_abi_verified=$false;network=$false;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 7 -Compress
exit $(if($nativePassed){0}else{1})
