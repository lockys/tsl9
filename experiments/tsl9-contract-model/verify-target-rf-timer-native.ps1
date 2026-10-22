param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools=$env:TSL9_LLVM_BIN
if([string]::IsNullOrWhiteSpace($nativeTools)){throw 'Set TSL9_LLVM_BIN to the existing LLVM toolchain bin directory.'}
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-rf-timer-native-cpp'}else{'target-rf-timer-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-rf-timer-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_rf_timer.c','src/target_rf_timer.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_rf_timer')){
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
 if(-not $nativeRelocation.defined -and $nativeRelocation.symbol -notin @('__tsl9_timer_state','__tsl9_state_bfb4','tsl9_runtime_unported_13b5c','tsl9_runtime_unported_170e2','tsl9_internal_timer_stop_93cc','tsl9_internal_gate_8214','tsl9_internal_scheduler_cancel_908e','tsl9_internal_gpio_setup_9a02','tsl9_internal_scheduler_register_9102')){throw 'Unexpected unresolved dependency'}
}
if($nativeGlobals.Count -ne 3){throw 'Unexpected public ABI symbols'}
if($nativeWritable.Count -or @($nativeUndefined|Where-Object {$_ -notin @('__tsl9_timer_state','__tsl9_state_bfb4','tsl9_runtime_unported_13b5c','tsl9_runtime_unported_170e2','tsl9_internal_timer_stop_93cc','tsl9_internal_gate_8214','tsl9_internal_scheduler_cancel_908e','tsl9_internal_gpio_setup_9a02','tsl9_internal_scheduler_register_9102')}).Count){throw 'Unexpected external dependency or writable section'}
foreach($nativeApi in @('tsl9_runtime_unported_9432','tsl9_runtime_unported_9936','tsl9_runtime_unported_17176')){if($nativeApi -notin $nativeGlobals){throw 'Missing C ABI export'}}
$irqOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $irqOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Original Runtime identity mismatch'}
$irqBytes=[IO.File]::ReadAllBytes($irqOriginal)
if($irqBytes.Length -ne 76800){throw 'Unexpected original length'}
$nativeHidden=@($nativeSymbolLookup.Values|Where-Object {$_.binding -eq 1 -and $_.visibility -eq 2 -and $_.index -ne 0})
$nativeAliasProofs=@();$nativeAliasOk=$nativeHidden.Count -eq 7
foreach($spec in @(@{name='tsl9_internal_rf_enabled_843a';target='tsl9_rf_enabled_843a';bytes=6},@{name='tsl9_internal_timer_mode_9770';target='tsl9_timer_mode_9770';bytes=12},@{name='tsl9_internal_rf_control_17048';target='tsl9_rf_control_17048';bytes=154},@{name='tsl9_internal_rf_cancel_1049a';target='tsl9_rf_cancel_1049a';bytes=20},@{name='tsl9_internal_timer_prepare_93ee';target='tsl9_timer_prepare_93ee';bytes=68},@{name='tsl9_internal_timer_start_9388';target='tsl9_timer_start_9388';bytes=68})){
 $as=@($nativeHidden|Where-Object {$_.name -eq $spec.name});$ts=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $spec.target})
 $ok=$false
 if($as.Count -eq 1 -and $ts.Count -eq 1){
  $a=$as[0];$t=$ts[0]
  $ok=$a.binding -eq 1 -and $a.visibility -eq 2 -and $a.type -eq 2 -and $a.size -eq $spec.bytes -and $t.binding -eq 0 -and $t.type -eq 2 -and $a.index -eq $t.index -and $a.value -eq $t.value -and $a.size -eq $t.size
 }
 $nativeAliasOk=$nativeAliasOk -and $ok
 $nativeAliasProofs+=@([pscustomobject]@{name=$spec.name;target=$spec.target;bytes=$spec.bytes;global=$ok;hidden=$ok;type='STT_FUNC';same_section_value_size=$ok;duplicate_body=$false;verified=$ok})
}
$nativePassed=$nativeUndefined.Count -eq 9 -and $nativeAliasOk
$rfTimerSpecs=@(@{name='tsl9_rf_flag_81aa';start=33194;bytes=6;calls=@();pairs=@()},@{name='tsl9_rf_enabled_843a';start=33850;bytes=6;calls=@();pairs=@()},@{name='tsl9_timer_start_9388';start=37768;bytes=68;calls=@();pairs=@(@{offset=10;lo_offset=14;original_target=536919744;symbol='__tsl9_timer_state';addend=4;lo_type=24;defined=$false;role='data';low_opcode='lbu';explicit_same_function_relocation=$false},@{offset=22;lo_offset=26;original_target=536919746;symbol='__tsl9_timer_state';addend=6;lo_type=25;defined=$false;role='data';low_opcode='sb';explicit_same_function_relocation=$false},@{offset=30;lo_offset=34;original_target=536919745;symbol='__tsl9_timer_state';addend=5;lo_type=25;defined=$false;role='data';low_opcode='sb';explicit_same_function_relocation=$false},@{offset=38;lo_offset=42;original_target=536919740;symbol='__tsl9_timer_state';addend=0;lo_type=25;defined=$false;role='data';low_opcode='sw';explicit_same_function_relocation=$false})},@{name='tsl9_timer_prepare_93ee';start=37870;bytes=68;calls=@(@{offset=44;width=2;target=37836;name='tsl9_internal_timer_stop_93cc';rd=1;defined=$false});pairs=@(@{offset=2;lo_offset=6;original_target=536919740;symbol='__tsl9_timer_state';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=28;lo_offset=32;original_target=536919756;symbol='__tsl9_timer_state';addend=16;lo_type=25;defined=$false;role='data';low_opcode='sw';explicit_same_function_relocation=$false},@{offset=36;lo_offset=40;original_target=536919752;symbol='__tsl9_timer_state';addend=12;lo_type=25;defined=$false;role='data';low_opcode='sw';explicit_same_function_relocation=$false})},@{name='tsl9_runtime_unported_9432';start=37938;bytes=154;calls=@(@{offset=28;width=2;target=37870;name='tsl9_timer_prepare_93ee';rd=1;defined=$true},@{offset=82;width=2;target=37768;name='tsl9_timer_start_9388';rd=0;defined=$true},@{offset=108;width=2;target=37870;name='tsl9_timer_prepare_93ee';rd=1;defined=$true});pairs=@(@{offset=30;lo_offset=34;original_target=536919756;symbol='__tsl9_timer_state';addend=16;lo_type=25;defined=$false;role='data';low_opcode='sw';explicit_same_function_relocation=$false},@{offset=110;lo_offset=114;original_target=536919756;symbol='__tsl9_timer_state';addend=16;lo_type=25;defined=$false;role='data';low_opcode='sw';explicit_same_function_relocation=$false})},@{name='tsl9_timer_mode_9770';start=38768;bytes=12;calls=@(@{offset=10;width=2;target=37938;name='tsl9_runtime_unported_9432';rd=0;defined=$true});pairs=@()},@{name='tsl9_runtime_unported_9936';start=39222;bytes=144;calls=@(@{offset=50;width=2;target=39426;name='tsl9_internal_gpio_setup_9a02';rd=1;defined=$false},@{offset=142;width=2;target=37836;name='tsl9_internal_timer_stop_93cc';rd=0;defined=$false});pairs=@(@{offset=14;lo_offset=18;original_target=536919740;symbol='__tsl9_timer_state';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_rf_flag_9edc';start=40668;bytes=6;calls=@();pairs=@()},@{name='tsl9_rf_cancel_1049a';start=66714;bytes=20;calls=@(@{offset=16;width=4;target=37006;name='tsl9_internal_scheduler_cancel_908e';rd=0;defined=$false});pairs=@(@{offset=0;lo_offset=4;original_target=536919988;symbol='__tsl9_state_bfb4';addend=0;lo_type=25;defined=$false;role='data';low_opcode='sb';explicit_same_function_relocation=$false},@{offset=8;lo_offset=12;original_target=66714;symbol='tsl9_rf_cancel_1049a';addend=0;lo_type=24;defined=$true;role='function';low_opcode='addi';explicit_same_function_relocation=$true})},@{name='tsl9_rf_schedule_16f4a';start=94026;bytes=218;calls=@(@{offset=8;width=4;target=33850;name='tsl9_rf_enabled_843a';rd=1;defined=$true},@{offset=142;width=4;target=33300;name='tsl9_internal_gate_8214';rd=1;defined=$false},@{offset=158;width=4;target=40668;name='tsl9_rf_flag_9edc';rd=1;defined=$true});pairs=@()},@{name='tsl9_rf_control_17048';start=94280;bytes=154;calls=@(@{offset=18;width=4;target=94026;name='tsl9_rf_schedule_16f4a';rd=1;defined=$true},@{offset=26;width=4;target=38768;name='tsl9_timer_mode_9770';rd=1;defined=$true},@{offset=82;width=4;target=33194;name='tsl9_rf_flag_81aa';rd=1;defined=$true},@{offset=136;width=4;target=37122;name='tsl9_internal_scheduler_register_9102';rd=1;defined=$false},@{offset=150;width=4;target=66714;name='tsl9_rf_cancel_1049a';rd=0;defined=$true});pairs=@(@{offset=128;lo_offset=132;original_target=80732;symbol='tsl9_runtime_unported_13b5c';addend=0;lo_type=24;defined=$false;role='callback-address';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_runtime_unported_17176';start=94582;bytes=76;calls=@(@{offset=64;width=4;target=94280;name='tsl9_rf_control_17048';rd=0;defined=$true});pairs=@(@{offset=26;lo_offset=30;original_target=94434;symbol='tsl9_runtime_unported_170e2';addend=0;lo_type=24;defined=$false;role='callback-address';low_opcode='addi';explicit_same_function_relocation=$false})})
$rfTimerBodies=@();$rfTimerAllPassed=$true
foreach($expected in $rfTimerSpecs){
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
 if(-not$match){$rfTimerAllPassed=$false}
 $rfTimerBodies+=@([pscustomobject]@{name=$expected.name;original_va=$expected.start;expected_bytes=$expected.bytes;actual_bytes=$symbol.size;nonrelocated_bytes_identical=$match;original_normalized_sha256=$originalHash;compiled_normalized_sha256=$actualHash;symbolic_jumps=$jumpChecks;pc_relative_pairs=$pairChecks})
}
$nativePassed=$nativePassed -and $rfTimerAllPassed

if(@($nativeSections|Where-Object {($_.flags-band2) -and -not($_.flags-band4) -and $_.size}).Count){throw 'Unexpected allocated non-executable data'}

if($nativeRelocations -ne 45){$nativePassed=$false}
foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Native module input changed'}}
# R73 aliases must share the unique existing private body.
$r73AliasProofs=@()
$r73Hidden=@($nativeSymbolLookup.Values|Where-Object {$_.binding -eq 1 -and $_.visibility -eq 2 -and $_.index -ne 0})
if($r73Hidden.Count -ne 7){throw 'R73 hidden alias cardinality'}
foreach($spec in @(@{name='tsl9_internal_rf_schedule_16f4a';target='tsl9_rf_schedule_16f4a';bytes=218})){
 $a=@($r73Hidden|Where-Object {$_.name -ceq $spec.name});$b=@($nativeSymbolLookup.Values|Where-Object {$_.name -ceq $spec.target})
 if($a.Count -ne 1 -or $b.Count -ne 1 -or $a[0].type -ne 2 -or $b[0].binding -ne 0 -or $a[0].size -ne $spec.bytes -or $a[0].index -ne $b[0].index -or $a[0].value -ne $b[0].value -or $a[0].size -ne $b[0].size){throw 'R73 alias is not exact private body'}
 $r73AliasProofs+=@([pscustomobject]@{name=$spec.name;target=$spec.target;bytes=$spec.bytes;same_section_value_size=$true;duplicate_body=$false;hidden=$true})
}

[pscustomobject]@{suite=$nativeMode;r73_internal_aliases=$r73AliasProofs;passed=$nativePassed;rf_timer_bodies=$rfTimerBodies;internal_aliases=$nativeAliasProofs;symbolic_jumps=17;pc_relative_pairs=14;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;physical_irq_abi_verified=$false;network=$false;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 7 -Compress
exit $(if($nativePassed){0}else{1})
