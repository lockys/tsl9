param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeTools='C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin'
$nativeClang=Join-Path $nativeTools 'clang.exe'
$nativeMode=if($Cpp){'target-identity-reader-native-cpp'}else{'target-identity-reader-native-c'}
$nativeBuild=Join-Path $nativeRoot ('build/'+$nativeMode)
[IO.Directory]::CreateDirectory($nativeBuild)|Out-Null
$nativeObject=Join-Path $nativeBuild ('target-identity-reader-native-'+[Guid]::NewGuid().ToString('N')+'.o')
$nativeFiles=@('src/target_identity_reader.c','src/target_identity_reader.h'|ForEach-Object {Join-Path $nativeRoot $_})+@($PSCommandPath,(Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'))
$nativeLld=Join-Path $nativeTools 'ld.lld.exe'
$nativeBefore=@{};foreach($nativePath in $nativeFiles){$nativeBefore[$nativePath]=(Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeFlags=@('--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-pic','-Oz','-Wall','-Wextra','-Werror')
$nativeFlags+=if($Cpp){@('-x','c++','-std=c++17','-fno-exceptions','-fno-rtti')}else{@('-x','c','-std=c11')}
$nativeObjects=@();$nativePartRecords=@()
foreach($nativeUnit in @('target_identity_reader')){
 $nativePart=Join-Path $nativeBuild ($nativeUnit+'-'+[Guid]::NewGuid().ToString('N')+'.o')
 & $nativeClang @nativeFlags -c (Join-Path $nativeRoot ('src/'+$nativeUnit+'.c')) -o $nativePart
 if($LASTEXITCODE -ne 0){throw ('Freestanding component compile failed: '+$nativeUnit)}
 $nativeObjects+=@($nativePart)
 $nativePartRecords+=@([pscustomobject]@{object=$nativePart;object_sha256=(Get-FileHash -LiteralPath $nativePart -Algorithm SHA256).Hash.ToLowerInvariant();object_bytes=(Get-Item -LiteralPath $nativePart).Length})
}
& $nativeLld -r --no-relax @nativeObjects -o $nativeObject
if($LASTEXITCODE -ne 0){throw 'Relocatable identity-reader link failed'}
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
   if($nativeSymbol -and $nativeIndex -ne 0 -and (($nativeBytes[$offset+12] -shr 4) -eq 1)){$nativeGlobals+=@($nativeSymbol)}
  }
 }
}

if($nativeRelocations -or $nativeUndefined.Count -or $nativeWritable.Count -or $nativeGlobals.Count -ne 1 -or $nativeGlobals[0] -cne 'tsl9_runtime_unported_18caa'){throw 'Unexpected identity-reader dependencies or ABI'}
$identitySymbols=@($nativeSymbolLookup.Values|Where-Object {$_.name -ceq 'tsl9_runtime_unported_18caa'})
if($identitySymbols.Count -ne 1){throw 'Identity symbol missing or ambiguous'}
$identitySymbol=$identitySymbols[0];$identitySection=$nativeSections[$identitySymbol.index]
$identityActual=[byte[]]$nativeBytes[($identitySection.offset+$identitySymbol.value)..($identitySection.offset+$identitySymbol.value+$identitySymbol.size-1)]
$identityOriginal=Join-Path $nativeRoot '../../apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $identityOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Fixed original identity mismatch'}
$identityCarrier=[IO.File]::ReadAllBytes($identityOriginal)
if($identityCarrier.Length -ne 76800){throw 'Original length'}
$identityOracle=[byte[]]$identityCarrier[(0x18caa-0x8000)..(0x18cdc-0x8000-1)]
$identityExpectedSHA='5ea71cc5060b528919272111556388a084fe65e49474efa62683825e4df2eedf'
function Hash-Identity67([byte[]]$b){[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($b)).ToLowerInvariant()}
if((Hash-Identity67 $identityOracle) -ne $identityExpectedSHA){throw 'Admitted original code changed'}
$identityExact=$identitySymbol.size -eq 50 -and [Convert]::ToHexString($identityActual) -ceq [Convert]::ToHexString($identityOracle)
$identityFunctions=@($nativeSymbolLookup.Values|Where-Object {$_.index -and $_.type -eq 2 -and $_.size})
$identityAllocated=@($nativeSections|Where-Object {($_.flags-band2) -and $_.size})
$nativePassed=$identityExact -and $identitySymbol.type -eq 2 -and $identitySymbol.binding -eq 1 -and $identitySymbol.visibility -eq 0 -and $identityFunctions.Count -eq 1 -and $identityAllocated.Count -eq 1 -and $identitySection.flags -eq 6 -and $identitySection.size -eq 50 -and $identitySymbol.value -eq 0
$identityReaderBodies=@([pscustomobject]@{name='tsl9_runtime_unported_18caa';original_va=0x18caa;original_bytes=50;original_instructions=14;native_bytes=$identitySymbol.size;exact_original_bytes=$identityExact;original_sha256=$identityExpectedSHA;native_sha256=(Hash-Identity67 $identityActual);relocations=0;numeric_load_addresses=@(0x1ffff7e8,0x1ffff7ec);output_bytes=6;second_load_after_first_four_stores_preserved=$identityExact;incidental_registers_preserved_by_exact_bytes=$identityExact;actual_identity_values_read=$false})
foreach($nativePath in $nativeBefore.Keys){if((Get-FileHash -LiteralPath $nativePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $nativeBefore[$nativePath]){throw 'Input changed'}}
[pscustomobject]@{suite=$nativeMode;passed=$nativePassed;identity_reader_bodies=$identityReaderBodies;compiler=$nativeClang;compiler_sha256=(Get-FileHash -LiteralPath $nativeClang).Hash.ToLowerInvariant();flags=$nativeFlags;source_sha256=$nativeBefore;object=$nativeObject;object_sha256=(Get-FileHash -LiteralPath $nativeObject).Hash.ToLowerInvariant();object_bytes=$nativeBytes.Length;elf_class=32;elf_type='ET_REL';machine='RISC-V';entry=0;elf_flags=(Read-Native32 36);undefined_symbols=$nativeUndefined;writable_allocated_sections=$nativeWritable;exports=$nativeGlobals;relocations=$nativeRelocations;relocation_records=$nativeRelocationRecords;linker=$nativeLld;linker_sha256=(Get-FileHash -LiteralPath $nativeLld).Hash.ToLowerInvariant();linker_flags=@('-r','--no-relax');components=$nativePartRecords;linked_image=$false;native_bin=$false;device_abi_verified=$false;network=$false;original_executed=$false;reconstructed_target_executed=$false;hardware=$false;emulation=$false}|ConvertTo-Json -Depth 8 -Compress
if(-not $nativePassed){exit 1}

