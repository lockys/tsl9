param(
 [ValidateSet('c','cpp')][string]$Mode='cpp',
 [string]$ProjectRoot,
 [Parameter(Mandatory=$true)][string]$RuntimePath,
 [string]$OutputRoot
)
$ErrorActionPreference='Stop'
if(-not $ProjectRoot){$ProjectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))}
if(-not $OutputRoot){$OutputRoot=Join-Path $PSScriptRoot 'build'}
$build=Join-Path ([IO.Path]::GetFullPath($OutputRoot)) ($Mode+'/'+[guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($build)|Out-Null
$python='C:/Users/locky/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe'
function Hash([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
$sourceHashes=@{}
foreach($n in @('build.ps1','prepare.py','audit.py')){$p=Join-Path $PSScriptRoot $n;$sourceHashes[$p]=Hash $p}
$planLines=@(& $python -X utf8 -B (Join-Path $PSScriptRoot 'prepare.py') --project-root $ProjectRoot --runtime $RuntimePath --output $build --mode $Mode)
if($LASTEXITCODE -or $planLines.Count -ne 1){throw 'Conditional plan preparation failed'}
$planPath=Join-Path $build 'plan.json'
$p=Get-Content -LiteralPath $planPath -Raw|ConvertFrom-Json
$carrier=Join-Path $build 'carrier.o';$elf=Join-Path $build 'tsl9-ch32v208-candidate.elf'
$map=Join-Path $build 'tsl9-ch32v208-candidate.map';$bin=Join-Path $build 'tsl9-ch32v208-candidate.bin'
$compileArgs=@($p.flags)+@('-c',(Join-Path $build 'carrier.c'),'-o',$carrier)
$compileLines=@(& $p.compiler @compileArgs 2>&1);$compileExit=$LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $build 'compile.log'),(($compileLines|ForEach-Object {$_.ToString()})-join [char]10),[Text.UTF8Encoding]::new($false))
if($compileExit){throw 'Carrier C/C++ compilation failed; preserved log'}
$linkArgs=@('--no-relax','--no-undefined','--error-limit=0','--orphan-handling=error','--fatal-warnings','-T',(Join-Path $build 'candidate.ld'),('-Map='+$map),$p.core_object.path,$carrier,'-o',$elf)
$linkLines=@(& $p.linker @linkArgs 2>&1);$linkExit=$LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $build 'link.log'),(($linkLines|ForEach-Object {$_.ToString()})-join [char]10),[Text.UTF8Encoding]::new($false))
if($linkExit){throw 'Conditional final link failed; preserved log'}
$copyArgs=@('-O','binary',$elf,$bin)
$copyLines=@(& $p.objcopy @copyArgs 2>&1);$copyExit=$LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $build 'objcopy.log'),(($copyLines|ForEach-Object {$_.ToString()})-join [char]10),[Text.UTF8Encoding]::new($false))
if($copyExit){throw 'Binary extraction failed; preserved log'}
foreach($path in $sourceHashes.Keys){if((Hash $path) -ne $sourceHashes[$path]){throw 'Candidate build source changed'}}
$outputs=@{}
foreach($n in @('carrier.c','carrier.o','candidate.ld','plan.json','tsl9-ch32v208-candidate.elf','tsl9-ch32v208-candidate.map','tsl9-ch32v208-candidate.bin','compile.log','link.log','objcopy.log')){
 $path=Join-Path $build $n;$outputs[$n]=[pscustomobject]@{path=$path;bytes=(Get-Item -LiteralPath $path).Length;sha256=(Hash $path)}
}
$receipt=Join-Path $build 'producer.json'
$producer=[pscustomobject]@{schema='CH32V208-conditional-candidate-producer-v1';mode=$Mode;plan=$planPath;plan_sha256=(Hash $planPath);sources=$sourceHashes;compiler_args=$compileArgs;linker_args=$linkArgs;objcopy_args=$copyArgs;compile_exit=$compileExit;link_exit=$linkExit;objcopy_exit=$copyExit;outputs=$outputs;target_ready=$false;ota_verified=$false;goal_complete=$false;network=$false;target_executed=$false;hardware=$false;emulation=$false}
[IO.File]::WriteAllText($receipt,($producer|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
$auditLines=@(& $python -X utf8 -B (Join-Path $PSScriptRoot 'audit.py') --receipt $receipt)
if($LASTEXITCODE -or $auditLines.Count -ne 1){throw 'Candidate audit failed'}
$audit=$auditLines[0]|ConvertFrom-Json
if(-not $audit.passed){throw 'Candidate audit rejected'}
[IO.File]::WriteAllText((Join-Path $build 'audit.json'),$auditLines[0],[Text.UTF8Encoding]::new($false))
[pscustomobject]@{passed=$true;mode=$Mode;producer=$receipt;producer_sha256=(Hash $receipt);binary=$bin;bytes=(Get-Item -LiteralPath $bin).Length;sha256=(Hash $bin);audit=(Join-Path $build 'audit.json');target_ready=$false;ota_verified=$false;goal_complete=$false}|ConvertTo-Json -Compress
exit 0
