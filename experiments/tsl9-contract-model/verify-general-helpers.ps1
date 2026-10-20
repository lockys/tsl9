param([switch]$Cpp)
$ErrorActionPreference='Stop'
$helperRoot=$PSScriptRoot
$helperRepo=(Resolve-Path (Join-Path $helperRoot '..\..')).Path
$helperInput=Join-Path $helperRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $helperInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$helperVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $helperVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $helperVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$helperVersion=(Get-Content -LiteralPath (Join-Path $helperVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$helperCl=Join-Path $helperVs ('VC\Tools\MSVC\'+$helperVersion+'\bin\Hostx64\x64\cl.exe')
$helperMode=if($Cpp){'helpers-cpp'}else{'helpers-c'}
$helperBuild=Join-Path $helperRoot ('build\'+$helperMode)
New-Item -ItemType Directory -Path $helperBuild -Force | Out-Null
$helperFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $helperRoot 'src')),('/Fo'+$helperBuild+'\'))
$helperFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$helperExe=Join-Path $helperBuild ('test-helpers-'+[Guid]::NewGuid().ToString('N')+'.exe')
& $helperCl @helperFlags (Join-Path $helperRoot 'src\general_helpers.c') (Join-Path $helperRoot 'src\dnd_actions.c') (Join-Path $helperRoot 'tests\test_general_helpers.c') ('/Fe'+$helperExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'General helpers compilation failed'}
& $helperExe $helperInput
$helperExit=$LASTEXITCODE
$helperFiles=@('src\general_helpers.c','src\general_helpers.h','src\dnd_actions.c','src\dnd_actions.h','tests\test_general_helpers.c','verify-general-helpers.ps1','src\general_ble.h','src\feature.h')
$helperHashes=@{}
foreach($helperFile in $helperFiles){$helperHashes[$helperFile]=(Get-FileHash -LiteralPath (Join-Path $helperRoot $helperFile) -Algorithm SHA256).Hash.ToLowerInvariant()}
[pscustomobject]@{exe=$helperExe;exe_sha256=(Get-FileHash -LiteralPath $helperExe -Algorithm SHA256).Hash.ToLowerInvariant();source_sha256=$helperHashes;target_executed=$false;exit_code=$helperExit}|ConvertTo-Json -Compress -Depth 4
exit $helperExit
