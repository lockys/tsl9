param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools=$env:TSL9_LLVM_BIN
if([string]::IsNullOrWhiteSpace($nativeTools)){throw 'Set TSL9_LLVM_BIN to the existing LLVM toolchain bin directory.'}
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-events-native-cpp'}else{'target-events-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-events-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_events.c','src/target_events.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_events')){
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
 if(-not $nativeRelocation.defined -and $nativeRelocation.symbol -notin @()){throw 'Unexpected unresolved dependency'}
}
if($nativeGlobals.Count -ne 3){throw 'Unexpected public ABI symbols'}
$nativeHidden=@($nativeSymbolLookup.Values|Where-Object {$_.binding -eq 1 -and $_.visibility -eq 2 -and $_.index -ne 0})
$nativeAlias=@($nativeHidden|Where-Object {$_.name -eq 'tsl9_internal_rtc_wait_18fc6'})
$nativeAliasTarget=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq 'tsl9_event_rtc_wait_18fc6'})
if($nativeHidden.Count -ne 1 -or $nativeAlias.Count -ne 1 -or $nativeAliasTarget.Count -ne 1){throw 'Missing unique hidden internal alias'}
if($nativeAlias[0].type -ne 2 -or $nativeAlias[0].size -ne 16 -or $nativeAliasTarget[0].binding -ne 0 -or $nativeAliasTarget[0].type -ne 2 -or $nativeAlias[0].index -ne $nativeAliasTarget[0].index -or $nativeAlias[0].value -ne $nativeAliasTarget[0].value -or $nativeAlias[0].size -ne $nativeAliasTarget[0].size){throw 'Internal alias must name the exact private function body'}
$nativeAliasProof=[pscustomobject]@{name='tsl9_internal_rtc_wait_18fc6';target='tsl9_event_rtc_wait_18fc6';bytes=16;global=$true;hidden=$true;type='STT_FUNC';same_section_value_size=$true;duplicate_body=$false}

if($nativeWritable.Count -or $nativeUndefined.Count -ne 0 -or @($nativeUndefined|Where-Object {$_ -notin @()}).Count){throw 'Unexpected external dependency or writable section'}
foreach($nativeApi in @('tsl9_context_restore_irq','tsl9_exti_5_9_irq','tsl9_rtc_alarm_irq')){if($nativeApi -notin $nativeGlobals){throw 'Missing C ABI export'}}
$irqOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $irqOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Original Runtime identity mismatch'}
$irqBytes=[IO.File]::ReadAllBytes($irqOriginal)
if($irqBytes.Length -ne 76800){throw 'Unexpected original length'}
$nativePassed=$true

$eventSpecs=@(
 @{name='tsl9_context_restore_irq';start=0x8440;bytes=78;calls=@()},
 @{name='tsl9_exti_5_9_irq';start=0x16d22;bytes=76;calls=@()},
 @{name='tsl9_rtc_alarm_irq';start=0x19928;bytes=28;calls=@(@{offset=10;target=0x18bda;name='tsl9_event_exti_clear_18bda'},@{offset=16;target=0x18fea;name='tsl9_event_rtc_clear_18fea'},@{offset=20;target=0x18fc6;name='tsl9_event_rtc_wait_18fc6'})},
 @{name='tsl9_event_exti_clear_18bda';start=0x18bda;bytes=10;calls=@()},
 @{name='tsl9_event_rtc_wait_18fc6';start=0x18fc6;bytes=16;calls=@()},
 @{name='tsl9_event_rtc_clear_core_18fd6';start=0x18fd6;bytes=20;calls=@()},
 @{name='tsl9_event_rtc_clear_18fea';start=0x18fea;bytes=4;calls=@(@{offset=0;target=0x18fd6;name='tsl9_event_rtc_clear_core_18fd6'})}
)
$eventBodies=@();$eventAllPassed=$true
foreach($eventExpected in $eventSpecs){
 $eventSymbols=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $eventExpected.name})
 if($eventSymbols.Count -ne 1){throw 'Missing unique event function'}
 $eventSymbol=$eventSymbols[0];$eventSection=$nativeSections[$eventSymbol.index]
 if($eventSymbol.type -ne 2 -or ($eventSection.flags-band7) -ne 6 -or $eventSymbol.value+$eventSymbol.size -gt $eventSection.size){throw 'Invalid event code range'}
 $eventActual=[byte[]]::new($eventSymbol.size);[Array]::Copy($nativeBytes,$eventSection.offset+$eventSymbol.value,$eventActual,0,$eventSymbol.size)
 $eventSource=[byte[]]::new($eventExpected.bytes);[Array]::Copy($irqBytes,$eventExpected.start-0x8000,$eventSource,0,$eventExpected.bytes)
 $eventMatch=$eventActual.Length -eq $eventSource.Length
 $eventCallChecks=@()
 foreach($eventCall in $eventExpected.calls){
  $originalWord=[BitConverter]::ToUInt32($eventSource,$eventCall.offset)
  $originalImm=(($originalWord-shr31)-band1)*0x100000+(($originalWord-shr21)-band0x3ff)*2+(($originalWord-shr20)-band1)*0x800+(($originalWord-shr12)-band255)*0x1000
  if($originalImm-band0x100000){$originalImm-=0x200000}
  if(($originalWord-band0x7f) -ne 0x6f -or $eventExpected.start+$eventCall.offset+$originalImm -ne $eventCall.target){throw 'Original symbolic call oracle mismatch'}
  $calls=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $eventSymbol.index -and $_.offset -eq $eventSymbol.value+$eventCall.offset})
  $ok=$false
  if($eventMatch -and $calls.Count -eq 1){
   $actualWord=[BitConverter]::ToUInt32($eventActual,$eventCall.offset)
   $ok=$calls[0].type -eq 17 -and $calls[0].addend -eq 0 -and ($actualWord-band0xfff) -eq ($originalWord-band0xfff)
   $targetSymbols=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $eventCall.name})
   if($targetSymbols.Count -ne 1 -or -not$targetSymbols[0].index){$ok=$false}else{
    $target=$targetSymbols[0];$relocSymbol=$nativeSymbolLookup[$calls[0].symbol_table.ToString()+':'+$calls[0].symbol_index.ToString()]
    $ok=$ok -and $relocSymbol.index -eq $target.index -and $relocSymbol.value+$calls[0].addend -eq $target.value
   }
   # Only JAL immediate bits are excluded; opcode/rd and target proof remain.
   [BitConverter]::GetBytes([uint32]($actualWord-band0xfff)).CopyTo($eventActual,$eventCall.offset)
   [BitConverter]::GetBytes([uint32]($originalWord-band0xfff)).CopyTo($eventSource,$eventCall.offset)
  }
  if(-not$ok){$eventMatch=$false}
  $eventCallChecks+=@([pscustomobject]@{offset=$eventCall.offset;original_target=$eventCall.target;symbol=$eventCall.name;jump_relocation_verified=$ok})
 }
 $eventActualHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($eventActual)).ToLowerInvariant()
 $eventSourceHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($eventSource)).ToLowerInvariant()
 $eventMatch=$eventMatch -and $eventActualHash -eq $eventSourceHash
 $eventExpectedRelocs=@($eventExpected.calls).Count
 $eventActualRelocs=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $eventSymbol.index -and $_.offset -ge $eventSymbol.value -and $_.offset -lt $eventSymbol.value+$eventSymbol.size}).Count
 if($eventActualRelocs -ne $eventExpectedRelocs){$eventMatch=$false}
 if(-not$eventMatch){$eventAllPassed=$false}
 $eventBodies+=@([pscustomobject]@{name=$eventExpected.name;original_va=$eventExpected.start;expected_bytes=$eventExpected.bytes;actual_bytes=$eventSymbol.size;original_normalized_sha256=$eventSourceHash;compiled_normalized_sha256=$eventActualHash;exact_nonrelocated_bytes=$eventMatch;symbolic_jumps=$eventCallChecks})
}
$nativePassed=$nativePassed -and $eventAllPassed

if($nativeRelocations -ne 4){$nativePassed=$false}

foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Native module input changed'}}
[pscustomobject]@{suite=$nativeMode;passed=$nativePassed;event_bodies=$eventBodies;symbolic_jump_count=$nativeRelocations;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;internal_aliases=@($nativeAliasProof);relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;physical_irq_abi_verified=$false;network=$false;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 7 -Compress
exit $(if($nativePassed){0}else{1})

