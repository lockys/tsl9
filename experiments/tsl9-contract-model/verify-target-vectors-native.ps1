param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools='C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin'
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-vectors-native-cpp'}else{'target-vectors-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-vectors-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_reset.h','src/target_irq.h','src/target_vectors.c','src/target_vectors.h','src/target_events.h','src/target_peripherals.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_vectors')){
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
 if(-not $nativeRelocation.defined -and $nativeRelocation.symbol -notin @('tsl9_reset_entry','tsl9_ble_bb_irq','tsl9_ble_lle_irq','tsl9_context_restore_irq','tsl9_timer3_irq','tsl9_can_rx0_irq','tsl9_exti_5_9_irq','tsl9_rtc_alarm_irq')){throw 'Unexpected unresolved dependency'}
}
if($nativeGlobals.Count -ne 2){throw 'Unexpected public ABI symbols'}
if($nativeWritable.Count -or $nativeUndefined.Count -ne 8 -or @($nativeUndefined|Where-Object {$_ -notin @('tsl9_reset_entry','tsl9_ble_bb_irq','tsl9_ble_lle_irq','tsl9_context_restore_irq','tsl9_timer3_irq','tsl9_can_rx0_irq','tsl9_exti_5_9_irq','tsl9_rtc_alarm_irq')}).Count){throw 'Unexpected external dependency or writable section'}
foreach($nativeApi in @('tsl9_image_entry','__tsl9_vector_table')){if($nativeApi -notin $nativeGlobals){throw 'Missing C ABI export'}}
$irqOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $irqOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Original Runtime identity mismatch'}
$irqBytes=[IO.File]::ReadAllBytes($irqOriginal)
if($irqBytes.Length -ne 76800){throw 'Unexpected original length'}
$irqBodies=@();$nativePassed=$true
foreach($irqExpected in @()){
 $irqSymbols=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $irqExpected.name})
 if($irqSymbols.Count -ne 1){throw 'Missing or ambiguous IRQ function'}
 $irqSymbol=$irqSymbols[0];$irqSection=$nativeSections[$irqSymbol.index]
 if($irqSymbol.type -ne 2 -or ($irqSection.flags-band6) -ne 6 -or ($irqSection.flags-band1) -ne 0 -or $irqSymbol.value+$irqSymbol.size -gt $irqSection.size){throw 'Invalid IRQ function range'}
 $irqActual=[byte[]]::new($irqSymbol.size);[Array]::Copy($nativeBytes,$irqSection.offset+$irqSymbol.value,$irqActual,0,$irqSymbol.size)
 $irqSource=[byte[]]::new($irqExpected.bytes);[Array]::Copy($irqBytes,$irqExpected.start-0x8000,$irqSource,0,$irqExpected.bytes)
 $irqActualHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($irqActual)).ToLowerInvariant()
 $irqSourceHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($irqSource)).ToLowerInvariant()
 $irqMatch=$irqActual.Length -eq $irqSource.Length -and $irqActualHash -eq $irqSourceHash
 if(-not$irqMatch){$nativePassed=$false}
 $irqBodies+=@([pscustomobject]@{name=$irqExpected.name;original_va=$irqExpected.start;expected_bytes=$irqExpected.bytes;actual_bytes=$irqActual.Length;original_body_sha256=$irqSourceHash;compiled_body_sha256=$irqActualHash;exact_original_bytes=$irqMatch})
}


# Resolve the pointer table against original raw words, not inferred IRQ names.
$vectorSymbols=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq '__tsl9_vector_table'})
if($vectorSymbols.Count -ne 1){throw 'Missing unique vector object'}
$vectorSymbol=$vectorSymbols[0];$vectorSection=$nativeSections[$vectorSymbol.index]
if($vectorSymbol.type -ne 1 -or $vectorSymbol.size -ne 328 -or ($vectorSection.flags-band7) -ne 2 -or $vectorSymbol.value+$vectorSymbol.size -gt $vectorSection.size){throw 'Vector must be readonly allocated 328B object'}
$vectorRelocs=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $vectorSymbol.index})
if($vectorRelocs.Count -ne 62){throw 'Expected 62 vector pointer relocations'}
$vectorPrimitiveBodies=@();$vectorSlots=@();$vectorPassed=$true
$vectorUnported=@()
for($slot=0;$slot -lt 82;$slot++){
 $originalTarget=[BitConverter]::ToUInt32($irqBytes,0x38+4*$slot)
 $tableOffset=$vectorSymbol.value+4*$slot
 if((Read-Native32 ($vectorSection.offset+$tableOffset)) -ne 0){throw 'Unrelocated table contains absolute pointer or nonzero addend'}
 $slotRelocs=@($vectorRelocs|Where-Object {$_.offset -eq $tableOffset})
 if($originalTarget -eq 0){
  if($slotRelocs.Count){throw 'Relocation at zero word'}
  $vectorSlots+=@([pscustomobject]@{word=$slot;original_target=0;kind='observed-zero';relocation=$false})
  continue
 }
 $symbolName=if($originalTarget -eq 0x8000){'tsl9_image_entry'}elseif($originalTarget -eq 0x18492){'tsl9_ble_bb_irq'}elseif($originalTarget -eq 0x8490){'tsl9_ble_lle_irq'}elseif($originalTarget -eq 0x8440){'tsl9_context_restore_irq'}elseif($originalTarget -eq 0x16d22){'tsl9_exti_5_9_irq'}elseif($originalTarget -eq 0x19928){'tsl9_rtc_alarm_irq'}elseif($originalTarget -eq 0x977c){'tsl9_timer3_irq'}elseif($originalTarget -eq 0x12a34){'tsl9_can_rx0_irq'}elseif($originalTarget -in $vectorUnported){'tsl9_vector_unported_'+$originalTarget.ToString('x')}else{'tsl9_default_irq_'+$originalTarget.ToString('x')}
 if($slotRelocs.Count -ne 1 -or $slotRelocs[0].type -ne 1 -or $slotRelocs[0].addend -ne 0){throw 'Expected one R_RISCV_32 pointer with zero addend'}
 $reloc=$slotRelocs[0];$relocSymbol=$nativeSymbolLookup[$reloc.symbol_table.ToString()+':'+$reloc.symbol_index.ToString()]
 $targets=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $symbolName})
 if($targets.Count -ne 1){throw ('Missing unique target: '+$symbolName)}
 $target=$targets[0]
 if($target.index -eq 0){
  if($relocSymbol.name -ne $symbolName -or $reloc.defined){throw 'Unported target is not explicit undefined reference'}
 }else{
  if($relocSymbol.index -ne $target.index -or $relocSymbol.value+$reloc.addend -ne $target.value){throw 'Pointer relocation does not resolve to real target'}
 }
 $vectorSlots+=@([pscustomobject]@{word=$slot;original_target=$originalTarget;symbol=$symbolName;kind=$(if($target.index -eq 0){'unresolved'}else{'defined'});relocation=$true})
}
foreach($primitive in @($vectorSlots|Where-Object {$_.symbol -like 'tsl9_default_irq_*'}|Sort-Object symbol -Unique)){
 $sym=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq $primitive.symbol})[0];$sec=$nativeSections[$sym.index]
 $expectedSize=if($primitive.original_target -eq 0x1848c){4}else{2}
 if($sym.type -ne 2 -or ($sec.flags-band7) -ne 6 -or $sym.value+$sym.size -gt $sec.size){throw 'Invalid default primitive function'}
 $actual=[byte[]]::new($sym.size);[Array]::Copy($nativeBytes,$sec.offset+$sym.value,$actual,0,$sym.size)
 $original=[byte[]]::new($expectedSize);[Array]::Copy($irqBytes,$primitive.original_target-0x8000,$original,0,$expectedSize)
 $actualHex=[Convert]::ToHexString($actual).ToLowerInvariant();$originalHex=[Convert]::ToHexString($original).ToLowerInvariant()
 if($originalHex -ne $(if($expectedSize -eq 4){'73002030'}else{'01a0'})){throw 'Original default classification changed'}
 $match=$actualHex -eq $originalHex
 if(-not$match){$vectorPassed=$false}
 $vectorPrimitiveBodies+=@([pscustomobject]@{symbol=$sym.name;original_va=$primitive.original_target;bytes=$sym.size;original_hex=$originalHex;compiled_hex=$actualHex;exact_original_bytes=$match;section=$sym.index})
}
if($vectorPrimitiveBodies.Count -ne 53 -or @($vectorPrimitiveBodies.section|Sort-Object -Unique).Count -ne 53){throw 'Expected 53 separate default functions'}
$imageSymbol=@($nativeSymbolLookup.Values|Where-Object {$_.name -eq 'tsl9_image_entry'})[0];$imageSection=$nativeSections[$imageSymbol.index]
if($imageSymbol.type -ne 2 -or $imageSymbol.size -ne 4 -or ($imageSection.flags-band7) -ne 6){throw 'Invalid image entry function'}
$imageWord=Read-Native32 ($imageSection.offset+$imageSymbol.value)
$imageReloc=@($nativeRelocationRecords|Where-Object {$_.target_section -eq $imageSymbol.index -and $_.offset -eq $imageSymbol.value})
if(($imageWord-band0xfff) -ne 0x6f -or $imageReloc.Count -ne 1 -or $imageReloc[0].type -ne 17 -or $imageReloc[0].symbol -ne 'tsl9_reset_entry' -or $imageReloc[0].addend -ne 0){throw 'Expected true JAL x0 reset relocation'}
$nativePassed=$nativePassed -and $vectorPassed

if($nativeRelocations -ne 63){throw 'Unexpected native relocation count'}
foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Native module input changed'}}
[pscustomobject]@{suite=$nativeMode;passed=$nativePassed;vector_words=82;zero_words=20;pointer_relocations=62;vector_slots=$vectorSlots;default_bodies=$vectorPrimitiveBodies;image_entry_jal_verified=$true;vector_placement_verified=$false;physical_irq_count_verified=$false;irq_bodies=$irqBodies;original_body_equality_verified=$nativePassed;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;relocatable_bundle=$true;final_layout_dependencies=$nativeUndefined;direct_clock_c_symbols_closed=$false;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld -Algorithm SHA256).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;network=$false;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 7 -Compress
exit $(if($nativePassed){0}else{1})


