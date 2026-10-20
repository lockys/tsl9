param([switch]$Cpp,[string]$BaselineSourceRoot='')
$ErrorActionPreference='Stop'
$dndRoot=$PSScriptRoot
$dndVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $dndVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $dndVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$dndVersion=(Get-Content -LiteralPath (Join-Path $dndVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$dndCl=Join-Path $dndVs ('VC\Tools\MSVC\'+$dndVersion+'\bin\Hostx64\x64\cl.exe')
$dndMode=if($Cpp){'dnd-effects-cpp'}else{'dnd-effects-c'}
if($BaselineSourceRoot){$dndMode+='-baseline'}
$dndBuild=Join-Path $dndRoot ('build\'+$dndMode)
New-Item -ItemType Directory -Path $dndBuild -Force | Out-Null
$dndFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $dndRoot 'src')),('/Fo'+$dndBuild+'\'))
$dndFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$dndExe=Join-Path $dndBuild ('test-dnd-'+[Guid]::NewGuid().ToString('N')+'.exe')
$dndNames=@('dnd_actions')
$dndCodeRoot=if($BaselineSourceRoot){(Resolve-Path -LiteralPath $BaselineSourceRoot).Path}else{$dndRoot}
if($BaselineSourceRoot){$dndFlags=@($dndFlags | Where-Object {-not $_.StartsWith('/I')})+@('/I'+(Join-Path $dndCodeRoot 'src'))}
$dndSources=@($dndNames | ForEach-Object {Join-Path $dndCodeRoot ('src\'+$_+'.c')})
$dndSources+=Join-Path $dndRoot 'tests\test_dnd_effects.c'
$dndBefore=@{};foreach($path in $dndSources+@(Join-Path $dndCodeRoot 'src\dnd_actions.h')+@($PSCommandPath)){$dndBefore[$path]=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
& $dndCl @dndFlags @dndSources ('/Fe'+$dndExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'DND freestanding compilation failed'}
$dndLines=@(& $dndExe);$dndExit=$LASTEXITCODE
foreach($path in $dndBefore.Keys){if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $dndBefore[$path]){throw 'DND input changed during test'}}
$dndBytes=[Text.Encoding]::UTF8.GetBytes(($dndLines -join "`n")+"`n")
$dndHash=[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($dndBytes)).Replace('-','').ToLowerInvariant()
[pscustomobject]@{suite=$dndMode;exit_code=$dndExit;summary=@($dndLines | Where-Object {$_ -like 'DND_EFFECTS_RESULT*'});failure_examples=@($dndLines | Where-Object {$_ -like 'FAIL*'} | Select-Object -First 8);stdout_sha256=$dndHash;exe=$dndExe;exe_sha256=(Get-FileHash -LiteralPath $dndExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$dndCl;compiler_sha256=(Get-FileHash -LiteralPath $dndCl -Algorithm SHA256).Hash.ToLowerInvariant();flags=$dndFlags;source_sha256=$dndBefore;original_executed=$false;network=$false;hardware=$false}|ConvertTo-Json -Depth 5 -Compress
exit $dndExit
