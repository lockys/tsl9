param([switch]$Cpp)
$ErrorActionPreference='Stop'
$startupRoot=$PSScriptRoot
$startupRepo=(Resolve-Path (Join-Path $startupRoot '..\..')).Path
$startupInput=Join-Path $startupRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $startupInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'BOOT identity mismatch'}
$startupVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $startupVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $startupVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$startupVersion=(Get-Content -LiteralPath (Join-Path $startupVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$startupCl=Join-Path $startupVs ('VC\Tools\MSVC\'+$startupVersion+'\bin\Hostx64\x64\cl.exe')
$startupMode=if($Cpp){'boot-startup-cpp'}else{'boot-startup-c'}
$startupBuild=Join-Path $startupRoot ('build\'+$startupMode)
New-Item -ItemType Directory -Path $startupBuild -Force | Out-Null
$startupFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $startupRoot 'src')),('/Fo'+$startupBuild+'\'))
$startupFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$startupExe=Join-Path $startupBuild ('test-boot-startup-'+[Guid]::NewGuid().ToString('N')+'.exe')
$startupNames=@('src\feature.c','src\feature.h','src\rom_candidate.c','src\rom_candidate.h','src\boot_startup.c','src\boot_startup.h','tests\test_boot_startup.c')
$startupBefore=@{}
foreach($startupName in $startupNames){$startupBefore[$startupName]=(Get-FileHash -LiteralPath (Join-Path $startupRoot $startupName) -Algorithm SHA256).Hash.ToLowerInvariant()}
& $startupCl @startupFlags (Join-Path $startupRoot 'src\feature.c') (Join-Path $startupRoot 'src\rom_candidate.c') (Join-Path $startupRoot 'src\boot_startup.c') (Join-Path $startupRoot 'tests\test_boot_startup.c') ('/Fe'+$startupExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'BOOT startup compilation failed'}
foreach($startupName in $startupNames){if($startupBefore[$startupName] -ne (Get-FileHash -LiteralPath (Join-Path $startupRoot $startupName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw ('Source changed during compile: '+$startupName)}}
Write-Output ('BOOT_STARTUP_BUILD '+(@{mode=$startupMode;compiler=$startupCl;compilerSha256=(Get-FileHash -LiteralPath $startupCl -Algorithm SHA256).Hash.ToLowerInvariant();executable=$startupExe;executableSha256=(Get-FileHash -LiteralPath $startupExe -Algorithm SHA256).Hash.ToLowerInvariant();sources=$startupBefore;originalExecuted=$false;hardware=$false}|ConvertTo-Json -Compress))
& $startupExe $startupInput
exit $LASTEXITCODE
