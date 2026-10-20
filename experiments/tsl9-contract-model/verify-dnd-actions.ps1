param([switch]$Cpp,[string]$BaselineSourceRoot='')
$ErrorActionPreference='Stop'
$dndRoot=$PSScriptRoot
$dndVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $dndVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $dndVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$dndVersion=(Get-Content -LiteralPath (Join-Path $dndVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$dndCl=Join-Path $dndVs ('VC\Tools\MSVC\'+$dndVersion+'\bin\Hostx64\x64\cl.exe')
$dndMode=if($Cpp){'dnd-actions-cpp'}else{'dnd-actions-c'}
if($BaselineSourceRoot){$dndMode+='-baseline'}
$dndBuild=Join-Path $dndRoot ('build\'+$dndMode)
New-Item -ItemType Directory -Path $dndBuild -Force | Out-Null
$dndFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $dndRoot 'src')),('/Fo'+$dndBuild+'\'))
$dndFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$dndExe=Join-Path $dndBuild ('test-dnd-'+[Guid]::NewGuid().ToString('N')+'.exe')
$dndNames=@('model','feature','boot_ram','general_ble','general_helpers','boot_startup','rom_candidate','rom_kernel','ram_bridge','native_callbacks','general_deep','general_reports','flash_page','spi_can','can_receive')
$dndCodeRoot=if($BaselineSourceRoot){(Resolve-Path -LiteralPath $BaselineSourceRoot).Path}else{$dndRoot}
if($BaselineSourceRoot){$dndFlags=@($dndFlags | Where-Object {-not $_.StartsWith('/I')})+@('/I'+(Join-Path $dndCodeRoot 'src'))}
if(Test-Path -LiteralPath (Join-Path $dndCodeRoot 'src/dnd_actions.c')){$dndNames+=@('dnd_actions')}
if(Test-Path -LiteralPath (Join-Path $dndCodeRoot 'src/report_packet.c')){$dndNames+='report_packet'}
$dndSources=@($dndNames | ForEach-Object {Join-Path $dndCodeRoot ('src\'+$_+'.c')})
$dndSources+=Join-Path $dndRoot 'tests\test_dnd_actions.c'
$dndBefore=@{};foreach($path in $dndSources+@(Get-ChildItem -LiteralPath (Join-Path $dndCodeRoot 'src') -Filter '*.h' | ForEach-Object FullName)+@($PSCommandPath)){$dndBefore[$path]=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
& $dndCl @dndFlags @dndSources ('/Fe'+$dndExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'DND actions compilation failed'}
$dndLines=@(& $dndExe);$dndExit=$LASTEXITCODE
foreach($path in $dndBefore.Keys){if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $dndBefore[$path]){throw 'DND input changed during test'}}
$dndBytes=[Text.Encoding]::UTF8.GetBytes(($dndLines -join "`n")+"`n")
$dndHash=[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($dndBytes)).Replace('-','').ToLowerInvariant()
[pscustomobject]@{suite=$dndMode;exit_code=$dndExit;summary=@($dndLines | Where-Object {$_ -like 'DND_ACTIONS_RESULT*'});failure_examples=@($dndLines | Where-Object {$_ -like 'FAIL*'} | Select-Object -First 8);stdout_sha256=$dndHash;exe=$dndExe;exe_sha256=(Get-FileHash -LiteralPath $dndExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$dndCl;compiler_sha256=(Get-FileHash -LiteralPath $dndCl -Algorithm SHA256).Hash.ToLowerInvariant();flags=$dndFlags;source_sha256=$dndBefore;original_executed=$false;network=$false;hardware=$false}|ConvertTo-Json -Depth 5 -Compress
exit $dndExit
