param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools='C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin'
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-init-check-native-cpp'}else{'target-init-check-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-init-check-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_init_check.c','src/target_init_check.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_init_check')){
 $nativePart=Join-Path $nativeBuild ($nativeUnit+'-'+[Guid]::NewGuid().ToString('N')+'.o')
 & $nativeClang @nativeFlags -c (Join-Path $nativeRoot ('src/'+$nativeUnit+'.c')) -o $nativePart
 if($LASTEXITCODE -ne 0){throw ('Freestanding component compile failed: '+$nativeUnit)}
 $nativeObjects+=@($nativePart)
 $nativePartRecords+=@([pscustomobject]@{object=$nativePart;object_sha256=(Get-FileHash -LiteralPath $nativePart -Algorithm SHA256).Hash.ToLowerInvariant();object_bytes=(Get-Item -LiteralPath $nativePart).Length})
}
& $nativeLld -r --no-relax @nativeObjects -o $nativeObject
if($LASTEXITCODE -ne 0){throw 'Relocatable init-check link failed'}
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


function Hash-Check68([byte[]]$b){[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($b)).ToLowerInvariant()}
$checkSpecs=ConvertFrom-Json '[{"name":"tsl9_runtime_unported_935c","start":37724,"end":37768,"bytes":44,"instructions":17,"sha256":"165818a297c434e2ca546b964e6944e6ff9f4e5686f7d9c6b54add4ebd27fe72","global":true},{"name":"tsl9_init_check_value_9312","start":37650,"end":37724,"bytes":74,"instructions":31,"sha256":"e7784c1cddcc75b7b2215a2c15b1862a88b90900fe473b49e96075dac90cef9a","global":false},{"name":"tsl9_init_check_identifier_9298","start":37528,"end":37584,"bytes":56,"instructions":22,"sha256":"c68e81ca8b76f4b7ccec0329967a2c991fedd9115392b899c79301ff86f5ccb6","global":false},{"name":"tsl9_init_check_transform_926e","start":37486,"end":37528,"bytes":42,"instructions":17,"sha256":"e4b80c5cd4c8313a390c9480b805ee93063f5d4dd7cb9e9be089788bb6791b85","global":false}]'
$checkCalls=ConvertFrom-Json '[{"from":37724,"pc":37730,"width":4,"type":17,"target":40350,"symbol":"tsl9_internal_config_read_9d9e","defined":false},{"from":37724,"pc":37742,"width":2,"type":45,"target":37650,"symbol":"tsl9_init_check_value_9312","defined":true},{"from":37650,"pc":37662,"width":2,"type":45,"target":37528,"symbol":"tsl9_init_check_identifier_9298","defined":true},{"from":37650,"pc":37694,"width":2,"type":45,"target":37486,"symbol":"tsl9_init_check_transform_926e","defined":true},{"from":37650,"pc":37698,"width":2,"type":45,"target":37486,"symbol":"tsl9_init_check_transform_926e","defined":true},{"from":37650,"pc":37704,"width":2,"type":45,"target":37486,"symbol":"tsl9_init_check_transform_926e","defined":true}]'
$checkOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $checkOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Fixed original identity mismatch'}
$checkCarrier=[IO.File]::ReadAllBytes($checkOriginal)
if($checkCarrier.Length -ne 76800){throw 'Original length'}
foreach($rel in $nativeRelocationRecords){
 $key=$rel.symbol_table.ToString()+':'+$rel.symbol_index.ToString()
 if(-not $nativeSymbolLookup.ContainsKey($key)){throw 'Invalid relocation symbol'}
 $sym=$nativeSymbolLookup[$key];$rel.symbol=$sym.name;$rel.defined=($sym.index -ne 0)
}
$checkBodies=@();$checkCallResults=@()
foreach($spec in $checkSpecs){
 $oracle=[byte[]]$checkCarrier[($spec.start-0x8000)..($spec.end-0x8000-1)]
 if((Hash-Check68 $oracle) -ne $spec.sha256 -or $oracle.Length -ne $spec.bytes){throw 'Admitted original code changed'}
 $symbols=@($nativeSymbolLookup.Values|Where-Object {$_.name -ceq $spec.name -and $_.index -ne 0})
 $bodyPassed=$symbols.Count -eq 1;$actual=[byte[]]@();$section=$null;$sym=$null
 if($bodyPassed){
  $sym=$symbols[0];$section=$nativeSections[$sym.index]
  if($sym.size -gt 0){$actual=[byte[]]$nativeBytes[($section.offset+$sym.value)..($section.offset+$sym.value+$sym.size-1)]}
  $bodyPassed=$sym.type -eq 2 -and $sym.binding -eq $(if($spec.global){1}else{0}) -and $sym.visibility -eq 0 -and $sym.value -eq 0 -and $sym.size -eq $spec.bytes -and $section.size -eq $spec.bytes -and $section.flags -eq 6
 }
 $actualNormalized=[byte[]]$actual.Clone();$originalNormalized=[byte[]]$oracle.Clone()
 foreach($call in @($checkCalls|Where-Object {$_.from -eq $spec.start})){
  $relative=[int]($call.pc-$spec.start);$originalWord=0;$actualWord=0
  if($call.width -eq 4){
   $originalWord=[BitConverter]::ToUInt32($oracle,$relative);$mask=[uint32]0x00000fff
   $imm=([int64](($originalWord-shr31)-band1)-shl20)-bor([int64](($originalWord-shr21)-band1023)-shl1)-bor([int64](($originalWord-shr20)-band1)-shl11)-bor([int64](($originalWord-shr12)-band255)-shl12)
   if($imm-band0x100000){$imm-=0x200000}
   $originalTarget=$call.pc+$imm
   $opcodePassed=($originalWord-band0x7f)-eq 0x6f -and (($originalWord-shr7)-band31)-eq 1
  }else{
   $originalWord=[BitConverter]::ToUInt16($oracle,$relative);$mask=[uint32]0xe003
   $imm=([int64](($originalWord-shr12)-band1)-shl11)-bor([int64](($originalWord-shr11)-band1)-shl4)-bor([int64](($originalWord-shr9)-band3)-shl8)-bor([int64](($originalWord-shr8)-band1)-shl10)-bor([int64](($originalWord-shr7)-band1)-shl6)-bor([int64](($originalWord-shr6)-band1)-shl7)-bor([int64](($originalWord-shr3)-band7)-shl1)-bor([int64](($originalWord-shr2)-band1)-shl5)
   if($imm-band0x800){$imm-=0x1000}
   $originalTarget=$call.pc+$imm
   $opcodePassed=($originalWord-band0xe003)-eq 0x2001
  }
  if(-not $opcodePassed -or $originalTarget -ne $call.target){throw 'Original call decode mismatch'}
  $callPassed=$false;$hits=@()
  if($sym){
   $hits=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $sym.index -and $_.offset -eq $sym.value+$relative})
   if($actual.Length -ge $relative+$call.width){
    $actualWord=if($call.width -eq 4){[BitConverter]::ToUInt32($actual,$relative)}else{[BitConverter]::ToUInt16($actual,$relative)}
    $maskedOriginal=[BitConverter]::GetBytes([uint32]($originalWord-band$mask))
    $maskedActual=[BitConverter]::GetBytes([uint32]($actualWord-band$mask))
    [Array]::Copy($maskedOriginal,0,$originalNormalized,$relative,[int]$call.width)
    [Array]::Copy($maskedActual,0,$actualNormalized,$relative,[int]$call.width)
    $callPassed=$hits.Count -eq 1 -and $hits[0].type -eq $call.type -and $hits[0].symbol -ceq $call.symbol -and $hits[0].defined -eq $call.defined -and $hits[0].addend -eq 0 -and $actualWord -eq ($originalWord-band$mask)
   }
  }
  $checkCallResults+=@([pscustomobject]@{original_pc=$call.pc;original_target=$originalTarget;bytes=$call.width;type=$call.type;symbol=$call.symbol;defined_expected=$call.defined;passed=$callPassed})
  $bodyPassed=$bodyPassed -and $callPassed
 }
 $normalizedEqual=[Convert]::ToHexString($actualNormalized) -ceq [Convert]::ToHexString($originalNormalized)
 $bodyPassed=$bodyPassed -and $normalizedEqual
 $checkBodies+=@([pscustomobject]@{name=$spec.name;original_va=$spec.start;original_bytes=$spec.bytes;original_instructions=$spec.instructions;native_bytes=$actual.Length;original_sha256=$spec.sha256;normalized_sha256=(Hash-Check68 $originalNormalized);native_normalized_sha256=(Hash-Check68 $actualNormalized);exact_nonrelocation_bytes=$normalizedEqual;passed=$bodyPassed})
}
$checkFunctions=@($nativeSymbolLookup.Values|Where-Object {$_.index -and $_.type -eq 2 -and $_.size -and $_.visibility -ne 2})
$checkAllocated=@($nativeSections|Where-Object {($_.flags-band2) -and $_.size})
$nativePassed=@($checkBodies|Where-Object {-not $_.passed}).Count -eq 0 -and $checkBodies.Count -eq 4 -and $checkFunctions.Count -eq 4 -and $checkAllocated.Count -eq 4 -and $nativeRelocations -eq 6 -and $nativeUndefined.Count -eq 1 -and $nativeUndefined[0] -ceq 'tsl9_internal_config_read_9d9e' -and $nativeGlobals.Count -eq 1 -and $nativeGlobals[0] -ceq 'tsl9_runtime_unported_935c' -and $nativeWritable.Count -eq 0
foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Input changed'}}
# R73 aliases must share the unique existing private body.
$r73AliasProofs=@()
$r73Hidden=@($nativeSymbolLookup.Values|Where-Object {$_.binding -eq 1 -and $_.visibility -eq 2 -and $_.index -ne 0})
if($r73Hidden.Count -ne 1){throw 'R73 hidden alias cardinality'}
foreach($spec in @(@{name='tsl9_internal_init_check_identifier_9298';target='tsl9_init_check_identifier_9298';bytes=56})){
 $a=@($r73Hidden|Where-Object {$_.name -ceq $spec.name});$b=@($nativeSymbolLookup.Values|Where-Object {$_.name -ceq $spec.target})
 if($a.Count -ne 1 -or $b.Count -ne 1 -or $a[0].type -ne 2 -or $b[0].binding -ne 0 -or $a[0].size -ne $spec.bytes -or $a[0].index -ne $b[0].index -or $a[0].value -ne $b[0].value -or $a[0].size -ne $b[0].size){throw 'R73 alias is not exact private body'}
 $r73AliasProofs+=@([pscustomobject]@{name=$spec.name;target=$spec.target;bytes=$spec.bytes;same_section_value_size=$true;duplicate_body=$false;hidden=$true})
}

[pscustomobject]@{suite=$nativeMode;r73_internal_aliases=$r73AliasProofs;passed=$nativePassed;init_check_bodies=$checkBodies;direct_calls=$checkCallResults;original_code_bytes=216;original_instructions=87;unchecked_ROM_semantics_verified=$false;actual_identity_values_read=$false;activation_generator=$false;false_outcome_bypassed=$false;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;network=$false;original_executed=$false;reconstructed_target_executed=$false;hardware=$false;emulation=$false}|ConvertTo-Json -Depth 8 -Compress
if(-not $nativePassed){exit 1}
