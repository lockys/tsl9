param([switch]$Cpp,[string]$PlatformReceiptPath)
$ErrorActionPreference='Stop'
$layoutRoot=$PSScriptRoot
$layoutContractPath=Join-Path $layoutRoot 'layout/known-runtime-layout.json'
$layoutScript=Join-Path $layoutRoot 'layout/runtime-memory.ld'
$layoutMemoryPath=Join-Path $layoutRoot 'layout/runtime-memory.json'
$layoutContract=Get-Content -LiteralPath $layoutContractPath -Raw|ConvertFrom-Json
$layoutMemory=Get-Content -LiteralPath $layoutMemoryPath -Raw|ConvertFrom-Json
if($layoutContract.schema -ne 'R77-known-runtime-relocatable-layout' -or $layoutContract.code_entries -ne 618 -or $layoutContract.groups.Count -ne 659 -or $layoutMemory.schema -ne 'R77-runtime-memory-layer' -or $layoutMemory.aliases.Count -ne 38 -or $layoutMemory.stack_top_bound -or $layoutMemory.ready_to_flash){throw 'Wrong memory/layout contract'}
$layoutMode=if($Cpp){'image-memory-relocatable-cpp'}else{'image-memory-relocatable-c'}
$layoutBuild=Join-Path $layoutRoot ('build/'+$layoutMode+'/'+[guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($layoutBuild)|Out-Null
if(-not $PlatformReceiptPath){
 $layoutArgs=@('-NoProfile','-File',(Join-Path $layoutRoot 'verify-image-platform-native.ps1'))
 if($Cpp){$layoutArgs+=@('-Cpp')}
 $layoutLines=@(& (Join-Path $PSHOME 'pwsh.exe') @layoutArgs);$layoutProducerExit=$LASTEXITCODE
 $layoutJSON=@($layoutLines|Where-Object {$_ -is [string] -and $_.StartsWith('{')})
 if($layoutProducerExit -or $layoutJSON.Count -ne 1){throw 'Platform producer failed'}
 $PlatformReceiptPath=Join-Path $layoutBuild 'platform-receipt.json'
 [IO.File]::WriteAllText($PlatformReceiptPath,$layoutJSON[0],[Text.UTF8Encoding]::new($false))
}
$layoutPlatform=Get-Content -LiteralPath $PlatformReceiptPath -Raw|ConvertFrom-Json
if(-not $layoutPlatform.passed -or $layoutPlatform.native_bin -or $layoutPlatform.suite -ne ('image-platform-native-'+$(if($Cpp){'cpp'}else{'c'})) -or $layoutPlatform.undefined_symbols.Count -ne 49 -or $layoutPlatform.writable_allocated_sections.Count -or $layoutPlatform.object_sha256 -ne $layoutMemory.baseline_platform_sha256){throw 'Wrong platform producer'}
function Layout-Hash([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
$layoutSources=@{}
foreach($entry in $layoutPlatform.source_sha256.PSObject.Properties){
 if((Layout-Hash $entry.Name) -ne $entry.Value){throw 'Platform source drift'}
 $layoutSources[$entry.Name]=$entry.Value
}
$layoutSource=Join-Path $layoutRoot 'src/target_runtime_memory.c'
$layoutHeader=Join-Path $layoutRoot 'src/target_runtime_memory.h'
$layoutCarrier=Join-Path $layoutRoot $layoutMemory.carrier.file
foreach($p in @($PSCommandPath,$layoutContractPath,(Join-Path $layoutRoot 'layout/known-runtime-layout.ld'),$layoutScript,$layoutMemoryPath,$layoutSource,$layoutHeader,$PlatformReceiptPath,$layoutCarrier)){$layoutSources[$p]=Layout-Hash $p}
if((Layout-Hash $layoutCarrier) -ne $layoutMemory.carrier.sha256 -or (Get-Item -LiteralPath $layoutCarrier).Length -ne 76800){throw 'Opaque carrier drift'}
if((Layout-Hash $layoutPlatform.object) -ne $layoutPlatform.object_sha256 -or (Get-Item -LiteralPath $layoutPlatform.object).Length -ne $layoutPlatform.object_bytes){throw 'Platform object drift'}
foreach($kind in @('compiler','linker')){if((Layout-Hash $layoutPlatform.$kind) -ne $layoutPlatform.($kind+'_sha256')){throw 'Compiler/linker drift'}}
function Layout-ELF([string]$path){
 $raw=[IO.File]::ReadAllBytes($path)
 if($raw.Length -lt 52 -or $raw[0] -ne 127 -or $raw[1] -ne 69 -or $raw[2] -ne 76 -or $raw[3] -ne 70 -or $raw[4] -ne 1 -or $raw[5] -ne 1 -or [BitConverter]::ToUInt16($raw,16) -ne 1 -or [BitConverter]::ToUInt16($raw,18) -ne 243){throw 'Expected RV32 little-endian ET_REL'}
 function Layout-String([int]$offset){
  if($offset -lt 0 -or $offset -ge $raw.Length){throw 'String range'}
  $end=$offset;while($end -lt $raw.Length -and $raw[$end]){$end++}
  if($end -eq $raw.Length){throw 'Unterminated ELF string'}
  [Text.Encoding]::ASCII.GetString($raw,$offset,$end-$offset)
 }
 $sectionOffset=[BitConverter]::ToUInt32($raw,32);$sectionSize=[BitConverter]::ToUInt16($raw,46);$sectionCount=[BitConverter]::ToUInt16($raw,48);$stringIndex=[BitConverter]::ToUInt16($raw,50)
 if($sectionSize -ne 40 -or $sectionOffset+40L*$sectionCount -gt $raw.Length -or $stringIndex -ge $sectionCount){throw 'Section header range'}
 $sections=@()
 for($i=0;$i -lt $sectionCount;$i++){
  $at=[int]$sectionOffset+$i*40;$v=@(0..9|ForEach-Object {[BitConverter]::ToUInt32($raw,$at+$_*4)})
  if($v[1] -ne 8 -and [long]$v[4]+$v[5] -gt $raw.Length){throw 'Section payload range'}
  $sections+=@([pscustomobject]@{Index=$i;NameOffset=$v[0];Name='';Type=$v[1];Flags=$v[2];Address=$v[3];Offset=$v[4];Size=$v[5];Link=$v[6];Info=$v[7];Alignment=$v[8];EntrySize=$v[9]})
 }
 foreach($section in $sections){$section.Name=Layout-String ([int]($sections[$stringIndex].Offset+$section.NameOffset))}
 $symbols=@();$tables=@{}
 foreach($section in $sections|Where-Object {$_.Type -eq 2}){
  if($section.EntrySize -ne 16 -or $section.Size%16 -or $section.Link -ge $sectionCount){throw 'Symbol table shape'}
  $table=@();$strs=$sections[$section.Link]
  for($i=0;$i -lt $section.Size;$i+=16){
   $at=[int]$section.Offset+$i;$name=[BitConverter]::ToUInt32($raw,$at);$info=$raw[$at+12]
   $symbol=[pscustomobject]@{Name=(Layout-String ([int]($strs.Offset+$name)));Value=[BitConverter]::ToUInt32($raw,$at+4);Size=[BitConverter]::ToUInt32($raw,$at+8);Binding=($info -shr 4);Type=($info -band 15);Visibility=($raw[$at+13] -band 3);Index=[BitConverter]::ToUInt16($raw,$at+14)}
   $table+=@($symbol);$symbols+=@($symbol)
  }
  $tables[[int]$section.Index]=$table
 }
 $relocations=@()
 foreach($section in $sections|Where-Object {$_.Type -eq 4}){
  if($section.EntrySize -ne 12 -or $section.Size%12 -or -not $tables.ContainsKey([int]$section.Link) -or $section.Info -ge $sectionCount){throw 'Rela table shape'}
  for($i=0;$i -lt $section.Size;$i+=12){
   $at=[int]$section.Offset+$i;$info=[BitConverter]::ToUInt32($raw,$at+4);$symidx=$info -shr 8;$table=$tables[[int]$section.Link]
   if($symidx -ge $table.Count){throw 'Relocation symbol index'}
   $relocations+=@([pscustomobject]@{Section=[int]$section.Info;Offset=[BitConverter]::ToUInt32($raw,$at);Type=($info -band 255);Symbol=$table[$symidx];Addend=[BitConverter]::ToInt32($raw,$at+8)})
  }
 }
 if(@($sections|Where-Object {$_.Type -eq 9 -and $_.Size}).Count){throw 'Unexpected REL table'}
 [pscustomobject]@{Raw=$raw;Sections=$sections;Symbols=$symbols;Relocations=$relocations}
}
function Layout-Bytes($e,$symbol){
 $section=$e.Sections[$symbol.Index];$offset=[long]$section.Offset+$symbol.Value
 if($symbol.Value+$symbol.Size -gt $section.Size -or $offset+$symbol.Size -gt $e.Raw.Length){throw 'Function range'}
 [Convert]::ToHexString($e.Raw,[int]$offset,[int]$symbol.Size)
}
function Layout-Relocations($e,$bases){
 $norm=@()
 foreach($r in $e.Relocations){
  if(-not $bases.ContainsKey([int]$r.Section)){throw 'Unmapped relocation site'}
  $site=[long]$bases[[int]$r.Section]+$r.Offset;$sym=$r.Symbol
  if($sym.Index -eq 0){$target='U:'+$sym.Name+':'+$r.Addend}
  elseif($sym.Index -eq 65521){$target='A:'+([long]$sym.Value+$r.Addend)}
  else{
   if(-not $bases.ContainsKey([int]$sym.Index)){throw 'Unmapped relocation target'}
   $target='D:'+([long]$bases[[int]$sym.Index]+$sym.Value+$r.Addend)
  }
  $norm+=@(($site.ToString('x8')+'|'+$r.Type+'|'+$target))
 }
 ,@($norm|Sort-Object)
}

function Memory-Section($elf,[string]$name,[int]$type,[int]$flags,[int]$size){
 $found=@($elf.Sections|Where-Object {$_.Name -ceq $name})
 if($found.Count -ne 1 -or $found[0].Type -ne $type -or $found[0].Flags -ne $flags -or $found[0].Size -ne $size -or $found[0].Address -ne 0 -or $found[0].Alignment -ne 4){throw ('Memory section shape: '+$name)}
 $found[0]
}
function Memory-Symbols($elf,$ram,$init){
 foreach($a in $layoutMemory.aliases){
  $found=@($elf.Symbols|Where-Object {$_.Name -ceq $a.name})
  $section=if($a.section -eq 'ram'){$ram}else{$init}
  if($found.Count -ne 1){throw 'Memory symbol missing or duplicated'}
  $s=$found[0]
  if($s.Index -ne $section.Index -or $s.Value -ne $a.offset -or $s.Size -ne $a.bytes -or $s.Type -ne $a.type -or $s.Binding -ne 1 -or $s.Visibility){throw ('Memory alias shape: '+$a.name)}
 }
}
$layoutBefore=Layout-ELF $layoutPlatform.object
$layoutFunctions=@($layoutBefore.Symbols|Where-Object {$_.Type -eq 2 -and $_.Index -and $_.Size})
$layoutInputBases=@{};$layoutCodeRows=@($layoutContract.groups|Where-Object {$_.kind -eq 'code'}|ForEach-Object {$_.members})
foreach($r in $layoutCodeRows){
 $found=@($layoutFunctions|Where-Object {$_.Name -ceq $r.name});if($found.Count -ne 1){throw 'Input function missing'}
 $s=$found[0];$base=[long]$r.original_va-$s.Value
 if($s.Size -ne $r.bytes -or $layoutBefore.Sections[$s.Index].Name -cne $r.input_section -or ($layoutInputBases.ContainsKey([int]$s.Index) -and $layoutInputBases[[int]$s.Index] -ne $base)){throw 'Input function nonlinear or changed'}
 $layoutInputBases[[int]$s.Index]=$base
}
foreach($g in $layoutContract.groups|Where-Object {$_.kind -eq 'readonly'}){
 $r=$g.members[0];$s=@($layoutBefore.Sections|Where-Object {$_.Name -ceq $r.input_section})
 if($s.Count -ne 1 -or $s[0].Size -ne $r.bytes -or $s[0].Flags -ne 2){throw 'Input RO changed'}
 $layoutInputBases[[int]$s[0].Index]=[long]$r.original_va
}
if(@($layoutBefore.Sections|Where-Object {($_.Flags -band 2) -and $_.Size}).Count -ne 662 -or $layoutInputBases.Count -ne 662 -or @($layoutBefore.Sections|Where-Object {($_.Flags -band 3) -eq 3 -and $_.Size}).Count){throw 'Baseline code-only guard'}
$layoutUnit=Join-Path $layoutBuild 'runtime-memory.o'
$layoutFlags=@($layoutPlatform.flags)
Push-Location -LiteralPath $layoutRoot
try{
 $layoutCompileLog=@(& $layoutPlatform.compiler @layoutFlags -I (Join-Path $layoutRoot 'src') -c $layoutSource -o $layoutUnit)
 if($LASTEXITCODE){throw ('Memory object compile failed: '+($layoutCompileLog -join ' '))}
 $layoutObject=Join-Path $layoutBuild 'known-memory-layout.o'
 $layoutLog=@(& $layoutPlatform.linker -r --no-relax -T $layoutScript $layoutPlatform.object $layoutUnit -o $layoutObject)
 if($LASTEXITCODE){throw ('Memory layer link failed: '+($layoutLog -join ' '))}
}finally{Pop-Location}
$layoutUnitELF=Layout-ELF $layoutUnit
$unitRam=Memory-Section $layoutUnitELF $layoutMemory.ram.input_section 8 3 35152
$unitInit=Memory-Section $layoutUnitELF $layoutMemory.initializer.input_section 1 2 136
Memory-Symbols $layoutUnitELF $unitRam $unitInit
$unitGlobals=@($layoutUnitELF.Symbols|Where-Object {$_.Binding -and $_.Name})
if($unitGlobals.Count -ne 38 -or @($layoutUnitELF.Symbols|Where-Object {$_.Type -eq 2 -and $_.Size}).Count -or @($layoutUnitELF.Symbols|Where-Object {-not $_.Index -and $_.Name}).Count -or $layoutUnitELF.Relocations.Count -or @($layoutUnitELF.Sections|Where-Object {($_.Flags -band 2) -and $_.Size}).Count -ne 2){throw 'Unit added code/UND/relocations or unauthorized allocation'}
$carrierBytes=[IO.File]::ReadAllBytes($layoutCarrier)
$originalWindow=[byte[]]$carrierBytes[75744..75879]
$initializerBytes=[byte[]]$layoutUnitELF.Raw[$unitInit.Offset..($unitInit.Offset+135)]
$initializerSHA=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($initializerBytes)).ToLowerInvariant()
if($initializerSHA -ne $layoutMemory.initializer.sha256 -or [Convert]::ToHexString($originalWindow) -cne [Convert]::ToHexString($initializerBytes)){throw 'Opaque initializer equality failed'}
$layoutAfter=Layout-ELF $layoutObject
$layoutOutputBases=@{};$layoutGroups=@()
foreach($g in $layoutContract.groups){
 $sections=@($layoutAfter.Sections|Where-Object {$_.Name -ceq $g.output_section})
 if($sections.Count -ne 1 -or $sections[0].Type -ne 1 -or $sections[0].Size -ne $g.bytes -or $sections[0].Address -ne 0 -or $sections[0].Flags -ne $(if($g.kind -eq 'code'){6}else{2})){throw 'Output retained section shape'}
 $section=$sections[0];$layoutOutputBases[[int]$section.Index]=[long]$g.original_va
 foreach($r in $g.members){
  $old=@($layoutBefore.Sections|Where-Object {$_.Name -ceq $r.input_section})[0]
  if([Convert]::ToHexString($layoutBefore.Raw,[int]$old.Offset,[int]$old.Size) -cne [Convert]::ToHexString($layoutAfter.Raw,[int]($section.Offset+$r.output_offset),[int]$r.bytes)){throw 'Retained bytes/padding changed'}
 }
 $layoutGroups+=@([pscustomobject]@{section=$section.Name;bytes=$section.Size;planned_original_va=$g.original_va;serialized_sh_addr=$section.Address;bytes_preserved=$true})
}
$memoryRam=Memory-Section $layoutAfter $layoutMemory.ram.output_section 8 3 35152
$memoryInit=Memory-Section $layoutAfter $layoutMemory.initializer.output_section 1 2 136
Memory-Symbols $layoutAfter $memoryRam $memoryInit
$layoutOutputBases[[int]$memoryRam.Index]=[long]$layoutMemory.ram.origin
$layoutOutputBases[[int]$memoryInit.Index]=[long]$layoutMemory.initializer.origin
if([Convert]::ToHexString($layoutAfter.Raw,[int]$memoryInit.Offset,136) -cne [Convert]::ToHexString($initializerBytes)){throw 'Linked initializer changed'}
if(@($layoutAfter.Sections|Where-Object {($_.Flags -band 2) -and $_.Size}).Count -ne 661 -or @($layoutAfter.Sections|Where-Object {($_.Flags -band 3) -eq 3 -and $_.Size}).Count -ne 1 -or @($layoutAfter.Sections|Where-Object {$_.Type -eq 8 -and $_.Size}).Count -ne 1){throw 'Unauthorized allocated/writable/NOBITS section'}
$layoutAfterFunctions=@($layoutAfter.Symbols|Where-Object {$_.Type -eq 2 -and $_.Index -and $_.Size})
if($layoutFunctions.Count -ne 707 -or $layoutAfterFunctions.Count -ne 707){throw 'Function coverage changed'}
foreach($old in $layoutFunctions){
 $found=@($layoutAfterFunctions|Where-Object {$_.Name -ceq $old.Name});if($found.Count -ne 1){throw 'Function missing/duplicated'}
 $new=$found[0]
 foreach($k in @('Size','Binding','Type','Visibility')){if($old.$k -ne $new.$k){throw 'Function metadata changed'}}
 if([long]$layoutInputBases[[int]$old.Index]+$old.Value -ne [long]$layoutOutputBases[[int]$new.Index]+$new.Value -or (Layout-Bytes $layoutBefore $old) -cne (Layout-Bytes $layoutAfter $new)){throw 'Function bytes or origin changed'}
}
$approved=@{};foreach($a in $layoutMemory.aliases){$approved[$a.name]=[long]$a.origin}
$oldUnd=@($layoutBefore.Symbols|Where-Object {-not $_.Index -and $_.Name})
$newUnd=@($layoutAfter.Symbols|Where-Object {-not $_.Index -and $_.Name})
$oldExpected=@($oldUnd|Where-Object {-not $approved.ContainsKey($_.Name)}|ForEach-Object {$_.Name+'|'+$_.Binding+'|'+$_.Type+'|'+$_.Visibility+'|'+$_.Size+'|'+$_.Value}|Sort-Object)
$newActual=@($newUnd|ForEach-Object {$_.Name+'|'+$_.Binding+'|'+$_.Type+'|'+$_.Visibility+'|'+$_.Size+'|'+$_.Value}|Sort-Object)
if($oldExpected.Count -ne 11 -or $newUnd.Count -ne 11 -or ($oldExpected -join [char]10) -cne ($newActual -join [char]10) -or '__tsl9_stack_top' -notin $newUnd.Name){throw 'Undefined obligation laundering'}
$layoutRawOldRelocs=Layout-Relocations $layoutBefore $layoutInputBases
$layoutOldRelocs=@($layoutRawOldRelocs|ForEach-Object {
 $row=$_;foreach($name in $approved.Keys){
  $parts=$row -split '\|';$target=$parts[2]
  if($target.StartsWith('U:'+$name+':',[StringComparison]::Ordinal)){
   $add=[long]$target.Substring(('U:'+$name+':').Length);$row=$parts[0]+'|'+$parts[1]+'|D:'+($approved[$name]+$add);break
  }
 };$row
}|Sort-Object)
$layoutNewRelocs=Layout-Relocations $layoutAfter $layoutOutputBases
if($layoutOldRelocs.Count -ne 4591 -or ($layoutOldRelocs -join [char]10) -cne ($layoutNewRelocs -join [char]10)){throw 'Unexpected relocation change'}
$strictOutput=Join-Path $layoutBuild 'would-be-firmware.elf'
$strictArgs=@('--no-relax','--error-limit=0','-T',$layoutScript,$layoutObject,'-o',$strictOutput)
Push-Location -LiteralPath $layoutRoot
try{$strictLines=@(& $layoutPlatform.linker @strictArgs 2>&1);$strictExit=$LASTEXITCODE}finally{Pop-Location}
$strictText=($strictLines|ForEach-Object {$_.ToString()}) -join [char]10
$strictLog=Join-Path $layoutBuild 'strict-final-link.log'
[IO.File]::WriteAllText($strictLog,$strictText,[Text.UTF8Encoding]::new($false))
$missing=@([regex]::Matches($strictText,'undefined symbol: ([^\r\n]+)')|ForEach-Object {$_.Groups[1].Value.Trim()}|Sort-Object -Unique)
if(-not $strictExit -or (Test-Path -LiteralPath $strictOutput) -or ($missing -join [char]10) -cne (($newUnd.Name|Sort-Object) -join [char]10)){throw 'Strict final link did not reject every remaining obligation'}
foreach($p in $layoutSources.Keys){if((Layout-Hash $p) -ne $layoutSources[$p]){throw 'Source drift during compile/link'}}
[pscustomobject]@{suite=$layoutMode;passed=$true;object=$layoutObject;object_bytes=(Get-Item -LiteralPath $layoutObject).Length;object_sha256=(Layout-Hash $layoutObject);unit_object=$layoutUnit;unit_sha256=(Layout-Hash $layoutUnit);unit_bytes=(Get-Item -LiteralPath $layoutUnit).Length;platform_receipt=$PlatformReceiptPath;platform_receipt_sha256=(Layout-Hash $PlatformReceiptPath);platform_object_sha256=$layoutPlatform.object_sha256;compiler=$layoutPlatform.compiler;compiler_sha256=$layoutPlatform.compiler_sha256;linker=$layoutPlatform.linker;linker_sha256=$layoutPlatform.linker_sha256;flags=$layoutFlags;source_sha256=$layoutSources;code_physical=618;function_names=707;relocations=4591;aliases_bound=38;undefined=11;undefined_symbols=@($newUnd.Name|Sort-Object);readonly_bytes=3591;initializer_bytes=136;initializer_sha256=$initializerSHA;opaque_initializer_preserved=$true;ram_nobits_bytes=35152;data_destination_bytes=136;bss_zero_bytes=35016;new_functions=0;normalized_relocations_preserved_except_allowlisted_U_to_D=$true;all_function_bytes_and_metadata_preserved=$true;output_allocated_sections=661;memory_aliases=$layoutMemory.aliases;groups=$layoutGroups;strict_final_link_rejected=$true;strict_final_link_exit=$strictExit;strict_diagnostic=$strictLog;strict_diagnostic_sha256=(Layout-Hash $strictLog);strict_undefined_fatal=11;stack_top_bound=$false;opaque_pointers_classified=$false;types_or_object_extents_proved=$false;final_VMA_or_LMA_proved=$false;physical_RAM_proved=$false;provider_callability_verified=$false;linked_image=$false;native_bin=$false;device_abi_verified=$false;ota_verified=$false;network=$false;hardware=$false;original_executed=$false;reconstructed_target_executed=$false;emulation=$false}|ConvertTo-Json -Depth 9 -Compress
