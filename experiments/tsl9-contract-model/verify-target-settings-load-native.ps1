param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools='C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin'
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-settings-load-native-cpp'}else{'target-settings-load-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-settings-load-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_settings_load.c','src/target_settings_load.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_settings_load')){
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
 if(-not $nativeRelocation.defined -and $nativeRelocation.symbol -notin @('__tsl9_settings_c298','__tsl9_settings_c308','__tsl9_settings_c408','__tsl9_settings_c490','__tsl9_settings_c590','__tsl9_settings_c690','__tsl9_settings_default_1a334','tsl9_internal_storage_page_9b6c')){throw 'Unexpected unresolved dependency'}
}
if($nativeGlobals.Count -ne 1){throw 'Unexpected public ABI symbols'}
if($nativeWritable.Count -or @($nativeUndefined|Where-Object {$_ -notin @('__tsl9_settings_c298','__tsl9_settings_c308','__tsl9_settings_c408','__tsl9_settings_c490','__tsl9_settings_c590','__tsl9_settings_c690','__tsl9_settings_default_1a334','tsl9_internal_storage_page_9b6c')}).Count){throw 'Unexpected external dependency or writable section'}
foreach($nativeApi in @('tsl9_runtime_unported_12fdc')){if($nativeApi -notin $nativeGlobals){throw 'Missing C ABI export'}}
$irqOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $irqOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Original Runtime identity mismatch'}
$irqBytes=[IO.File]::ReadAllBytes($irqOriginal)
if($irqBytes.Length -ne 76800){throw 'Unexpected original length'}
$nativeHidden=@($nativeSymbolLookup.Values|Where-Object {$_.binding -eq 1 -and $_.visibility -eq 2 -and $_.index -ne 0})
$nativeAliasProofs=@();$nativeAliasOk=$nativeHidden.Count -eq 2
foreach($spec in @(@{name='tsl9_internal_settings_write_12f58';target='tsl9_settings_write_12f58';bytes=50},@{name='tsl9_internal_settings_write_12ef6';target='tsl9_settings_write_12ef6';bytes=50})){
 $as=@($nativeHidden|Where-Object {$_.name -eq $spec.name});$ts=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $spec.target})
 $ok=$false
 if($as.Count -eq 1 -and $ts.Count -eq 1){
  $a=$as[0];$t=$ts[0]
  $ok=$a.binding -eq 1 -and $a.visibility -eq 2 -and $a.type -eq 2 -and $a.size -eq $spec.bytes -and $t.binding -eq 0 -and $t.type -eq 2 -and $a.index -eq $t.index -and $a.value -eq $t.value -and $a.size -eq $t.size
 }
 $nativeAliasOk=$nativeAliasOk -and $ok
 $nativeAliasProofs+=@([pscustomobject]@{name=$spec.name;target=$spec.target;bytes=$spec.bytes;global=$ok;hidden=$ok;type='STT_FUNC';same_section_value_size=$ok;duplicate_body=$false;verified=$ok})
}
$nativePassed=$nativeUndefined.Count -eq 8 -and $nativeAliasOk
$settingsLoadSpecs=@(@{name='tsl9_settings_write_12c5e';start=76894;bytes=50;calls=@(@{offset=38;width=4;target=39788;name='tsl9_internal_storage_page_9b6c';rd=1;defined=$false});pairs=@(@{offset=18;lo_offset=22;original_target=536921232;symbol='__tsl9_settings_c490';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_default_12c90';start=76944;bytes=118;calls=@(@{offset=114;width=4;target=76894;name='tsl9_settings_write_12c5e';rd=0;defined=$true});pairs=@(@{offset=10;lo_offset=14;original_target=536921232;symbol='__tsl9_settings_c490';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_write_12d06';start=77062;bytes=50;calls=@(@{offset=38;width=4;target=39788;name='tsl9_internal_storage_page_9b6c';rd=1;defined=$false});pairs=@(@{offset=18;lo_offset=22;original_target=536920840;symbol='__tsl9_settings_c308';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_default_12d38';start=77112;bytes=48;calls=@(@{offset=44;width=4;target=77062;name='tsl9_settings_write_12d06';rd=0;defined=$true});pairs=@(@{offset=10;lo_offset=14;original_target=536920840;symbol='__tsl9_settings_c308';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_write_12d68';start=77160;bytes=50;calls=@(@{offset=38;width=4;target=39788;name='tsl9_internal_storage_page_9b6c';rd=1;defined=$false});pairs=@(@{offset=18;lo_offset=22;original_target=536921488;symbol='__tsl9_settings_c590';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_default_12d9a';start=77210;bytes=216;calls=@(@{offset=212;width=4;target=77160;name='tsl9_settings_write_12d68';rd=0;defined=$true});pairs=@(@{offset=10;lo_offset=14;original_target=536921488;symbol='__tsl9_settings_c590';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_write_12e72';start=77426;bytes=50;calls=@(@{offset=38;width=4;target=39788;name='tsl9_internal_storage_page_9b6c';rd=1;defined=$false});pairs=@(@{offset=18;lo_offset=22;original_target=536921744;symbol='__tsl9_settings_c690';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_default_12ea4';start=77476;bytes=82;calls=@(@{offset=78;width=4;target=77426;name='tsl9_settings_write_12e72';rd=0;defined=$true});pairs=@(@{offset=10;lo_offset=14;original_target=536921744;symbol='__tsl9_settings_c690';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_write_12ef6';start=77558;bytes=50;calls=@(@{offset=38;width=4;target=39788;name='tsl9_internal_storage_page_9b6c';rd=1;defined=$false});pairs=@(@{offset=18;lo_offset=22;original_target=536921096;symbol='__tsl9_settings_c408';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_default_12f28';start=77608;bytes=48;calls=@(@{offset=44;width=4;target=77558;name='tsl9_settings_write_12ef6';rd=0;defined=$true});pairs=@(@{offset=10;lo_offset=14;original_target=536921096;symbol='__tsl9_settings_c408';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_write_12f58';start=77656;bytes=50;calls=@(@{offset=38;width=4;target=39788;name='tsl9_internal_storage_page_9b6c';rd=1;defined=$false});pairs=@(@{offset=18;lo_offset=22;original_target=536920728;symbol='__tsl9_settings_c298';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_settings_default_12f8a';start=77706;bytes=82;calls=@(@{offset=78;width=4;target=77656;name='tsl9_settings_write_12f58';rd=0;defined=$true});pairs=@(@{offset=12;lo_offset=16;original_target=536920728;symbol='__tsl9_settings_c298';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=58;lo_offset=62;original_target=107316;symbol='__tsl9_settings_default_1a334';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false})},@{name='tsl9_runtime_unported_12fdc';start=77788;bytes=328;calls=@(@{offset=66;width=4;target=77706;name='tsl9_settings_default_12f8a';rd=1;defined=$true},@{offset=114;width=4;target=76944;name='tsl9_settings_default_12c90';rd=1;defined=$true},@{offset=162;width=4;target=77112;name='tsl9_settings_default_12d38';rd=1;defined=$true},@{offset=210;width=4;target=77210;name='tsl9_settings_default_12d9a';rd=1;defined=$true},@{offset=258;width=4;target=77476;name='tsl9_settings_default_12ea4';rd=1;defined=$true},@{offset=310;width=4;target=77608;name='tsl9_settings_default_12f28';rd=0;defined=$true});pairs=@(@{offset=22;lo_offset=26;original_target=536920728;symbol='__tsl9_settings_c298';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=32;lo_offset=36;original_target=536920728;symbol='__tsl9_settings_c298';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=40;lo_offset=44;original_target=536920732;symbol='__tsl9_settings_c298';addend=4;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=88;lo_offset=92;original_target=536921232;symbol='__tsl9_settings_c490';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=98;lo_offset=102;original_target=536921487;symbol='__tsl9_settings_c490';addend=255;lo_type=24;defined=$false;role='data';low_opcode='lbu';explicit_same_function_relocation=$false},@{offset=136;lo_offset=140;original_target=536920840;symbol='__tsl9_settings_c308';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=146;lo_offset=150;original_target=536921095;symbol='__tsl9_settings_c308';addend=255;lo_type=24;defined=$false;role='data';low_opcode='lbu';explicit_same_function_relocation=$false},@{offset=184;lo_offset=188;original_target=536921488;symbol='__tsl9_settings_c590';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=194;lo_offset=198;original_target=536921743;symbol='__tsl9_settings_c590';addend=255;lo_type=24;defined=$false;role='data';low_opcode='lbu';explicit_same_function_relocation=$false},@{offset=232;lo_offset=236;original_target=536921744;symbol='__tsl9_settings_c690';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=242;lo_offset=246;original_target=536921999;symbol='__tsl9_settings_c690';addend=255;lo_type=24;defined=$false;role='data';low_opcode='lbu';explicit_same_function_relocation=$false},@{offset=280;lo_offset=284;original_target=536921096;symbol='__tsl9_settings_c408';addend=0;lo_type=24;defined=$false;role='data';low_opcode='addi';explicit_same_function_relocation=$false},@{offset=290;lo_offset=294;original_target=536921228;symbol='__tsl9_settings_c408';addend=132;lo_type=24;defined=$false;role='data';low_opcode='lbu';explicit_same_function_relocation=$false})})
$settingsLoadBodies=@();$settingsLoadAllPassed=$true
foreach($expected in $settingsLoadSpecs){
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
 if(-not$match){$settingsLoadAllPassed=$false}
 $settingsLoadBodies+=@([pscustomobject]@{name=$expected.name;original_va=$expected.start;expected_bytes=$expected.bytes;actual_bytes=$symbol.size;nonrelocated_bytes_identical=$match;original_normalized_sha256=$originalHash;compiled_normalized_sha256=$actualHash;symbolic_jumps=$jumpChecks;pc_relative_pairs=$pairChecks})
}
$nativePassed=$nativePassed -and $settingsLoadAllPassed

if(@($nativeSections|Where-Object {($_.flags-band2) -and -not($_.flags-band4) -and $_.size}).Count){throw 'Unexpected allocated non-executable data'}

if($nativeRelocations -ne 70){$nativePassed=$false}
foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Native module input changed'}}
[pscustomobject]@{suite=$nativeMode;passed=$nativePassed;settings_load_bodies=$settingsLoadBodies;symbolic_jumps=18;pc_relative_pairs=26;internal_aliases=$nativeAliasProofs;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;physical_irq_abi_verified=$false;network=$false;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 7 -Compress
exit $(if($nativePassed){0}else{1})
