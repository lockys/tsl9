param([switch]$Cpp,[string]$PlatformReceiptPath)
$ErrorActionPreference='Stop'
$layoutRoot=$PSScriptRoot
$layoutContractPath=Join-Path $layoutRoot 'layout/known-runtime-layout.json'
$layoutScript=Join-Path $layoutRoot 'layout/known-runtime-layout.ld'
$layoutContract=Get-Content -LiteralPath $layoutContractPath -Raw|ConvertFrom-Json
if($layoutContract.schema -ne 'R77-known-runtime-relocatable-layout' -or $layoutContract.code_entries -ne 618 -or $layoutContract.groups.Count -ne 659){throw 'Wrong known layout contract'}
$layoutMode=if($Cpp){'image-layout-relocatable-cpp'}else{'image-layout-relocatable-c'}
$layoutBuild=Join-Path $layoutRoot ('build/'+$layoutMode+'/'+[guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($layoutBuild)|Out-Null
if(-not $PlatformReceiptPath){
 $layoutPwsh=Join-Path $PSHOME 'pwsh.exe'
 $layoutArgs=@('-NoProfile','-File',(Join-Path $layoutRoot 'verify-image-platform-native.ps1'))
 if($Cpp){$layoutArgs+=@('-Cpp')}
 $layoutLines=@(& $layoutPwsh @layoutArgs);$layoutProducerExit=$LASTEXITCODE
 $layoutJSON=@($layoutLines|Where-Object {$_ -is [string] -and $_.StartsWith('{')})
 if($layoutProducerExit -or $layoutJSON.Count -ne 1){throw 'Platform producer failed'}
 $PlatformReceiptPath=Join-Path $layoutBuild 'platform-receipt.json'
 [IO.File]::WriteAllText($PlatformReceiptPath,$layoutJSON[0],[Text.UTF8Encoding]::new($false))
}
$layoutPlatform=Get-Content -LiteralPath $PlatformReceiptPath -Raw|ConvertFrom-Json
if(-not $layoutPlatform.passed -or $layoutPlatform.native_bin -or $layoutPlatform.suite -ne ('image-platform-native-'+$(if($Cpp){'cpp'}else{'c'}))){throw 'Wrong platform producer'}
function Layout-Hash([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
$layoutSources=@{}
foreach($entry in $layoutPlatform.source_sha256.PSObject.Properties){
 if((Layout-Hash $entry.Name) -ne $entry.Value){throw 'Platform source drift'}
 $layoutSources[$entry.Name]=$entry.Value
}
foreach($p in @($PSCommandPath,$layoutContractPath,$layoutScript,$PlatformReceiptPath)){$layoutSources[$p]=Layout-Hash $p}
if((Layout-Hash $layoutPlatform.object) -ne $layoutPlatform.object_sha256 -or (Get-Item -LiteralPath $layoutPlatform.object).Length -ne $layoutPlatform.object_bytes){throw 'Platform object drift'}
if((Layout-Hash $layoutPlatform.linker) -ne $layoutPlatform.linker_sha256){throw 'Linker drift'}
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
$layoutBefore=Layout-ELF $layoutPlatform.object
$layoutFunctions=@($layoutBefore.Symbols|Where-Object {$_.Type -eq 2 -and $_.Index -and $_.Size})
$layoutInputBases=@{};$layoutConflict=@();$layoutCodeRows=@($layoutContract.groups|Where-Object {$_.kind -eq 'code'}|ForEach-Object {$_.members})
foreach($r in $layoutCodeRows){
 $matches=@($layoutFunctions|Where-Object {$_.Name -ceq $r.name});if($matches.Count -ne 1){throw 'Missing unique input function'}
 $sym=$matches[0];if($sym.Size -ne $r.bytes){throw 'Input function size'}
 $base=[long]$r.original_va-$sym.Value
 if($layoutInputBases.ContainsKey([int]$sym.Index) -and $layoutInputBases[[int]$sym.Index] -ne $base){$layoutConflict+=@([pscustomobject]@{section=$layoutBefore.Sections[$sym.Index].Name;function=$r.name;required_base=$base;already_required_base=$layoutInputBases[[int]$sym.Index]})}
 else{$layoutInputBases[[int]$sym.Index]=$base}
}
if($layoutConflict.Count){
 [pscustomobject]@{suite=$layoutMode;passed=$false;reason='Noncontiguous original functions share an indivisible input section';conflicts=$layoutConflict;platform_object=$layoutPlatform.object;platform_sha256=$layoutPlatform.object_sha256;source_sha256=$layoutSources;linker_invoked=$false;native_bin=$false;network=$false;hardware=$false;target_executed=$false}|ConvertTo-Json -Depth 5 -Compress
 exit 1
}
foreach($r in $layoutCodeRows){
 $sym=@($layoutFunctions|Where-Object {$_.Name -ceq $r.name})[0]
 if($layoutBefore.Sections[$sym.Index].Name -cne $r.input_section){throw 'Unexpected input section name'}
}
foreach($g in $layoutContract.groups|Where-Object {$_.kind -eq 'readonly'}){
 $r=$g.members[0];$sections=@($layoutBefore.Sections|Where-Object {$_.Name -ceq $r.input_section})
 if($sections.Count -ne 1 -or $sections[0].Size -ne $r.bytes -or $sections[0].Flags -ne 2 -or $sections[0].Alignment -ne $r.alignment){throw 'Readonly input shape'}
 $layoutInputBases[[int]$sections[0].Index]=[long]$r.original_va
}
$layoutInputAlloc=@($layoutBefore.Sections|Where-Object {($_.Flags -band 2) -and $_.Size})
if($layoutInputAlloc.Count -ne $layoutInputBases.Count){throw 'Unaccounted allocated input section'}
$layoutObject=Join-Path $layoutBuild 'known-layout.o'
$layoutLog=@(& $layoutPlatform.linker -r --no-relax -T $layoutScript $layoutPlatform.object -o $layoutObject)
if($LASTEXITCODE){throw ('Relocatable layout failed: '+($layoutLog -join ' '))}
$layoutAfter=Layout-ELF $layoutObject
$layoutOutputBases=@{};$layoutGroups=@()
foreach($g in $layoutContract.groups){
 $sections=@($layoutAfter.Sections|Where-Object {$_.Name -ceq $g.output_section})
 if($sections.Count -ne 1 -or $sections[0].Size -ne $g.bytes -or $sections[0].Address -ne 0 -or $sections[0].Flags -ne $(if($g.kind -eq 'code'){6}else{2})){throw 'Output group shape or unexpected serialized VMA'}
 $section=$sections[0];$layoutOutputBases[[int]$section.Index]=[long]$g.original_va
 foreach($r in $g.members){
  $old=@($layoutBefore.Sections|Where-Object {$_.Name -ceq $r.input_section})[0]
  $oldHex=[Convert]::ToHexString($layoutBefore.Raw,[int]$old.Offset,[int]$old.Size)
  $newHex=[Convert]::ToHexString($layoutAfter.Raw,[int]($section.Offset+$r.output_offset),[int]$r.bytes)
  if($oldHex -cne $newHex){throw 'Input bytes changed or padding introduced'}
 }
 $layoutGroups+=@([pscustomobject]@{section=$section.Name;bytes=$section.Size;serialized_sh_addr=$section.Address;planned_original_va=$g.original_va;members=$g.members.Count;bytes_preserved=$true})
}
if(@($layoutAfter.Sections|Where-Object {($_.Flags -band 2) -and $_.Size}).Count -ne 659){throw 'Unaccounted output allocation'}
$layoutAfterFunctions=@($layoutAfter.Symbols|Where-Object {$_.Type -eq 2 -and $_.Index -and $_.Size})
if($layoutFunctions.Count -ne 707 -or $layoutAfterFunctions.Count -ne 707){throw 'Function name coverage'}
foreach($old in $layoutFunctions){
 $matches=@($layoutAfterFunctions|Where-Object {$_.Name -ceq $old.Name});if($matches.Count -ne 1){throw 'Function name changed'}
 $new=$matches[0]
 foreach($key in @('Size','Binding','Type','Visibility')){if($old.$key -ne $new.$key){throw 'Function metadata changed'}}
 if([long]$layoutInputBases[[int]$old.Index]+$old.Value -ne [long]$layoutOutputBases[[int]$new.Index]+$new.Value -or (Layout-Bytes $layoutBefore $old) -cne (Layout-Bytes $layoutAfter $new)){throw 'Function bytes or relative origin changed'}
}
$layoutOldUndefined=@($layoutBefore.Symbols|Where-Object {-not $_.Index -and $_.Name}|ForEach-Object {$_.Name+'|'+$_.Binding+'|'+$_.Type+'|'+$_.Visibility+'|'+$_.Size+'|'+$_.Value}|Sort-Object)
$layoutNewUndefined=@($layoutAfter.Symbols|Where-Object {-not $_.Index -and $_.Name}|ForEach-Object {$_.Name+'|'+$_.Binding+'|'+$_.Type+'|'+$_.Visibility+'|'+$_.Size+'|'+$_.Value}|Sort-Object)
if($layoutOldUndefined.Count -ne 49 -or ($layoutOldUndefined -join [char]10) -cne ($layoutNewUndefined -join [char]10)){throw 'Undefined obligations changed'}
$layoutOldRelocs=Layout-Relocations $layoutBefore $layoutInputBases
$layoutNewRelocs=Layout-Relocations $layoutAfter $layoutOutputBases
if($layoutOldRelocs.Count -ne 4591 -or ($layoutOldRelocs -join [char]10) -cne ($layoutNewRelocs -join [char]10)){throw 'Normalized symbolic relocation changed'}
$layoutPhysical=@($layoutAfterFunctions|ForEach-Object {$_.Index.ToString()+':'+$_.Value+':'+$_.Size}|Sort-Object -Unique)
if($layoutPhysical.Count -ne 618){throw 'Physical body coverage'}
$layoutReset=@($layoutAfter.Sections|Where-Object {$_.Name -eq '.tsl9_code_000183fe'})[0]
$layoutResetPieces=@()
foreach($r in @($layoutContract.groups|Where-Object {$_.original_va -eq 99326})[0].members){
 $sym=@($layoutAfterFunctions|Where-Object {$_.Name -ceq $r.name})[0]
 if($sym.Index -ne $layoutReset.Index -or $sym.Value -ne $r.output_offset -or $sym.Size -ne $r.bytes){throw 'Reset composite offset'}
 $layoutResetPieces+=@([pscustomobject]@{name=$r.name;offset=$sym.Value;bytes=$sym.Size;planned_original_va=$r.original_va})
}
foreach($p in $layoutSources.Keys){if((Layout-Hash $p) -ne $layoutSources[$p]){throw 'Layout source drift'}}
$layoutPublic=@($layoutAfter.Symbols|Where-Object {$_.Index -and $_.Name -and $_.Binding -eq 1 -and $_.Visibility -eq 0})
$layoutHidden=@($layoutAfter.Symbols|Where-Object {$_.Index -and $_.Name -and $_.Binding -eq 1 -and $_.Visibility -eq 2})
$layoutPublicBefore=@($layoutBefore.Symbols|Where-Object {$_.Index -and $_.Name -and $_.Binding -eq 1 -and $_.Visibility -eq 0}|ForEach-Object {$_.Name+'|'+$_.Type+'|'+$_.Size}|Sort-Object)
$layoutPublicAfter=@($layoutPublic|ForEach-Object {$_.Name+'|'+$_.Type+'|'+$_.Size}|Sort-Object)
if($layoutPublic.Count -ne $layoutContract.public_exports -or $layoutHidden.Count -ne $layoutContract.hidden_aliases -or ($layoutPublicBefore -join [char]10) -cne ($layoutPublicAfter -join [char]10)){throw 'Actual ELF exports differ from layout contract'}
$layoutRelocHasher=[Security.Cryptography.SHA256]::Create()
try{$layoutRelocDigest=[Convert]::ToHexString($layoutRelocHasher.ComputeHash([Text.Encoding]::UTF8.GetBytes(($layoutOldRelocs -join [char]10)))).ToLowerInvariant()}finally{$layoutRelocHasher.Dispose()}
[pscustomobject]@{suite=$layoutMode;passed=$true;platform_receipt=$PlatformReceiptPath;platform_receipt_sha256=(Layout-Hash $PlatformReceiptPath);platform_object=$layoutPlatform.object;platform_object_sha256=$layoutPlatform.object_sha256;object=$layoutObject;object_sha256=(Layout-Hash $layoutObject);object_bytes=(Get-Item -LiteralPath $layoutObject).Length;elf_type='ET_REL';compiler=$layoutPlatform.compiler;compiler_sha256=$layoutPlatform.compiler_sha256;linker=$layoutPlatform.linker;linker_sha256=$layoutPlatform.linker_sha256;linker_flags=@('-r','--no-relax','-T',$layoutScript);source_sha256=$layoutSources;code_physical=618;function_names=707;hidden_aliases=$layoutHidden.Count;public_exports=$layoutPublic.Count;public_function_exports=@($layoutPublic|Where-Object {$_.Type -eq 2}).Count;public_object_exports=@($layoutPublic|Where-Object {$_.Type -eq 1}).Count;undefined=49;relocations=4591;readonly_bytes=3455;normalized_relocation_sha256=$layoutRelocDigest;normalized_relocations_preserved=$true;all_function_bytes_and_metadata_preserved=$true;reset_composite_bytes=148;reset_pieces=$layoutResetPieces;groups=$layoutGroups;output_allocated_sections=659;synthetic_allocated_padding_bytes=0;absolute_placement_serialized=$false;link_script_address_asserts_passed_but_ET_REL_addresses_are_zero=$true;final_VMA_or_LMA_proved=$false;linked_image=$false;native_bin=$false;device_abi_verified=$false;network=$false;hardware=$false;original_executed=$false;reconstructed_target_executed=$false;emulation=$false}|ConvertTo-Json -Depth 8 -Compress

