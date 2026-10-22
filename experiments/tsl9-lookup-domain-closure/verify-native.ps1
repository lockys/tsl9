param([switch]$Cpp,[string]$BaselineReceiptPath)
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$python=$env:TSL9_PYTHON
$pythonPrefix=@()
if(-not $python){
    $pythonCommand=Get-Command python -CommandType Application -ErrorAction SilentlyContinue
    if($pythonCommand){$python=$pythonCommand.Source}else{
        $pythonCommand=Get-Command py -CommandType Application -ErrorAction SilentlyContinue
        if(-not $pythonCommand){throw 'Set TSL9_PYTHON to a Python 3 executable, or add python/py to PATH.'}
        $python=$pythonCommand.Source
        $pythonPrefix=@('-3')
    }
}
$mode=if($Cpp){'cpp'}else{'c'}
$build=Join-Path $root ('build/'+$mode+'/'+[guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($build)|Out-Null
function Hash([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
$sources=@{}
foreach($name in @('src/target_stack_address_r81.c','src/target_stack_address_r81.h','src/target_ble_compare_view_r80.c','src/target_ble_compare_view_r80.h','src/target_lookup_domain_closure.c','src/target_lookup_domain_closure.h','src/target_runtime_ram_only.c','src/target_runtime_memory.h','src/target_callback_native_r79.c','src/target_callback_native_r79.h','src/target_callback_tables_r79.c','src/target_callback_tables_r79.h','provenance/target_runtime_memory-r77.c','layout/coalesce-ro.ld','layout/runtime-known-memory.ld','layout/closure.json','layout/callback-native-plan.json','verify-native.ps1','audit-native.py')){
 $p=Join-Path $root $name;$sources[$p]=Hash $p
}
$basePath=Join-Path $build 'baseline-platform.json'
if($BaselineReceiptPath){
 $baseText=[IO.File]::ReadAllText([IO.Path]::GetFullPath($BaselineReceiptPath))
}else{
 $baseArgs=@('-NoProfile','-File',(Join-Path $root '../tsl9-contract-model/verify-image-platform-native.ps1'))
 if($Cpp){$baseArgs+=@('-Cpp')}
 $baseLines=@(& (Join-Path $PSHOME 'pwsh.exe') @baseArgs);$baseExit=$LASTEXITCODE
 $baseRows=@($baseLines|Where-Object {$_ -is [string] -and $_.StartsWith('{')})
 if($baseExit -or $baseRows.Count -ne 1){throw ('R77 platform producer failed '+$baseExit)}
 $baseText=$baseRows[0]
}
[IO.File]::WriteAllText($basePath,$baseText,[Text.UTF8Encoding]::new($false))
$baseline=$baseText|ConvertFrom-Json
if(-not $baseline.passed -or $baseline.native_bin -or $baseline.suite -ne ('image-platform-native-'+$mode) -or $baseline.undefined_symbols.Count -ne 49 -or $baseline.object_sha256 -ne 'a484f81cfda535ecf01b55e271da243b100f750be8ea28768db86fd3cf830f59'){throw 'Unexpected baseline platform'}
if((Hash $baseline.object) -ne $baseline.object_sha256){throw 'Baseline ELF drift'}
foreach($entry in $baseline.source_sha256.PSObject.Properties){if((Hash $entry.Name) -ne $entry.Value){throw 'Baseline source drift'}}
foreach($kind in @('compiler','linker')){if((Hash $baseline.$kind) -ne $baseline.($kind+'_sha256')){throw 'Tool identity drift'}}
$lookup=Join-Path $build 'lookup-fragments.o';$ram=Join-Path $build 'ram-only.o'
$callbacks=Join-Path $build 'callback-code.o';$tables=Join-Path $build 'callback-tables.o'
$compare=Join-Path $build 'ble-compare-view.o'
$stackLiteral=Join-Path $build 'stack-address-expectation.o'
$namedBaseline=Join-Path $build 'baseline-with-section-relative-names.o'
$plan=Get-Content -LiteralPath (Join-Path $root 'layout/callback-native-plan.json') -Raw|ConvertFrom-Json
$objcopy=Join-Path (Split-Path -Parent $baseline.linker) 'llvm-objcopy.exe';$objcopySHA=Hash $objcopy
if($plan.baseline_aliases.Count -ne 16 -or $plan.new_code_bytes -ne 9868 -or $plan.new_entry_views -ne 41){throw 'Wrong callback code plan'}
$aliasArgs=@($plan.baseline_aliases|ForEach-Object {'--add-symbol='+$_.name+'='+$_.section+':'+$_.value+',global,hidden'})
& $objcopy @aliasArgs $baseline.object $namedBaseline
if($LASTEXITCODE){throw 'Existing real code alias emission failed'}
$platform=Join-Path $build 'coalesced-platform.o';$memory=Join-Path $build 'known-memory.o'
Push-Location -LiteralPath $root
try{
 & $baseline.compiler @($baseline.flags) -I (Join-Path $root 'src') -c (Join-Path $root 'src/target_stack_address_r81.c') -o $stackLiteral
 if($LASTEXITCODE){throw 'Original initial-SP address C/C++ compile failed'}
 & $baseline.compiler @($baseline.flags) -I (Join-Path $root 'src') -c (Join-Path $root 'src/target_ble_compare_view_r80.c') -o $compare
 if($LASTEXITCODE){throw 'Finite BLE compare view C/C++ compile failed'}
 & $baseline.compiler @($baseline.flags) -I (Join-Path $root 'src') -c (Join-Path $root 'src/target_lookup_domain_closure.c') -o $lookup
 if($LASTEXITCODE){throw 'Lookup C/C++ compile failed'}
 & $baseline.compiler @($baseline.flags) -I (Join-Path $root 'src') -c (Join-Path $root 'src/target_runtime_ram_only.c') -o $ram
 if($LASTEXITCODE){throw 'RAM-only C/C++ compile failed'}
 & $baseline.compiler @($baseline.flags) -I (Join-Path $root 'src') -c (Join-Path $root 'src/target_callback_native_r79.c') -o $callbacks
 if($LASTEXITCODE){throw 'Original callback C/C++ compile failed'}
 & $baseline.compiler @($baseline.flags) -I (Join-Path $root 'src') -c (Join-Path $root 'src/target_callback_tables_r79.c') -o $tables
 if($LASTEXITCODE){throw 'Symbolic callback descriptor C/C++ compile failed'}
 & $baseline.linker -r --no-relax -T (Join-Path $root 'layout/coalesce-ro.ld') $namedBaseline $lookup $callbacks $tables $compare $stackLiteral -o $platform
 if($LASTEXITCODE){throw 'RO coalescing failed'}
 & $baseline.linker -r --no-relax -T (Join-Path $root 'layout/runtime-known-memory.ld') $platform $ram -o $memory
 if($LASTEXITCODE){throw 'Known memory representation failed'}
 $wouldBe=Join-Path $build 'would-be-firmware.elf'
 $strictLines=@(& $baseline.linker --no-relax --error-limit=0 -T (Join-Path $root 'layout/runtime-known-memory.ld') $memory -o $wouldBe 2>&1)
 $strictExit=$LASTEXITCODE
 if(-not $strictExit -or (Test-Path -LiteralPath $wouldBe)){throw 'Incomplete image must be rejected'}
}finally{Pop-Location}
$strictPath=Join-Path $build 'strict-final-link.log'
[IO.File]::WriteAllText($strictPath,(($strictLines|ForEach-Object {$_.ToString()})-join [char]10),[Text.UTF8Encoding]::new($false))
foreach($p in $sources.Keys){if((Hash $p) -ne $sources[$p]){throw 'Source changed during compilation'}}
$objects=@{}
foreach($pair in @(@('stack_literal',$stackLiteral),@('compare',$compare),@('lookup',$lookup),@('ram',$ram),@('callbacks',$callbacks),@('tables',$tables),@('baseline_aliases',$namedBaseline),@('platform',$platform),@('memory',$memory))){$objects[$pair[0]]=[pscustomobject]@{path=$pair[1];bytes=(Get-Item -LiteralPath $pair[1]).Length;sha256=(Hash $pair[1])}}
$receipt=Join-Path $build 'producer.json'
if((Hash $objcopy) -ne $objcopySHA){throw 'Alias tool changed'}
$producer=[pscustomobject]@{schema='R81-native-closure-producer';mode=$mode;baseline_reused=[bool]$BaselineReceiptPath;baseline_receipt=$basePath;baseline_receipt_sha256=(Hash $basePath);objcopy=$objcopy;objcopy_sha256=$objcopySHA;alias_args=$aliasArgs;objects=$objects;sources=$sources;strict_exit=$strictExit;strict_log=$strictPath;strict_log_sha256=(Hash $strictPath);network=$false;target_executed=$false;emulation=$false;hardware=$false;native_bin=$false}
[IO.File]::WriteAllText($receipt,($producer|ConvertTo-Json -Depth 8 -Compress),[Text.UTF8Encoding]::new($false))
$auditLines=@(& $python @pythonPrefix -X utf8 -B (Join-Path $root 'audit-native.py') --receipt $receipt);$auditExit=$LASTEXITCODE
if($auditExit -or $auditLines.Count -ne 1){throw ('Native audit failed '+$auditExit)}
$audit=$auditLines[0]|ConvertFrom-Json
if(-not $audit.passed){throw 'Native audit rejected'}
$auditPath=Join-Path $build 'audit.json'
[IO.File]::WriteAllText($auditPath,$auditLines[0],[Text.UTF8Encoding]::new($false))
[pscustomobject]@{passed=$true;mode=$mode;producer=$receipt;producer_sha256=(Hash $receipt);audit=$auditPath;audit_sha256=(Hash $auditPath);platform_sha256=$objects.platform.sha256;memory_sha256=$objects.memory.sha256;old_physical_code=618;new_emission_regions=$audit.new_emission_regions;new_entry_views=$audit.new_entry_views;function_names=$audit.function_names;relocations=$audit.relocations;remaining_UND=$audit.remaining_UND;readonly_bytes=$audit.readonly_bytes;native_bin=$false;target_ready=$false;network=$false;target_executed=$false}|ConvertTo-Json -Compress
