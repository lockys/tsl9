param([switch]$Cpp)
$ErrorActionPreference='Stop'
$bootRoot=$PSScriptRoot
$bootRepo=(Resolve-Path (Join-Path $bootRoot '..\..')).Path
$bootInput=Join-Path $bootRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $bootInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'BOOT identity mismatch'}
$bootVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $bootVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $bootVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$bootVersion=(Get-Content -LiteralPath (Join-Path $bootVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$bootCl=Join-Path $bootVs ('VC\Tools\MSVC\'+$bootVersion+'\bin\Hostx64\x64\cl.exe')
$bootMode=if($Cpp){'boot-ram-cpp'}else{'boot-ram-c'}
$bootBuild=Join-Path $bootRoot ('build\'+$bootMode)
New-Item -ItemType Directory -Path $bootBuild -Force | Out-Null
$bootFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $bootRoot 'src')),('/Fo'+$bootBuild+'\'))
$bootFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$bootExe=Join-Path $bootBuild ('test-boot-ram-'+[Guid]::NewGuid().ToString('N')+'.exe')
& $bootCl @bootFlags (Join-Path $bootRoot 'src\boot_ram.c') (Join-Path $bootRoot 'tests\test_boot_ram.c') ('/Fe'+$bootExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'BOOT RAM compilation failed'}
. (Join-Path $bootRoot 'build-evidence.ps1')
Write-ModelBuildEvidence -ModelRoot $bootRoot -Compiler $bootCl -Executable $bootExe -Mode $bootMode -Sources @('src/feature.h','src/boot_ram.c','src/boot_ram.h','tests/test_boot_ram.c','verify-boot-ram.ps1','build-evidence.ps1')
& $bootExe $bootInput
exit $LASTEXITCODE
