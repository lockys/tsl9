param([switch]$Cpp)
$ErrorActionPreference='Stop'
$kernelRoot=$PSScriptRoot
$kernelRepo=(Resolve-Path (Join-Path $kernelRoot '..\..')).Path
$kernelInput=Join-Path $kernelRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $kernelInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Server Runtime identity mismatch'}
$kernelVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $kernelVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $kernelVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$kernelVersion=(Get-Content -LiteralPath (Join-Path $kernelVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$kernelCl=Join-Path $kernelVs ('VC\Tools\MSVC\'+$kernelVersion+'\bin\Hostx64\x64\cl.exe')
$kernelMode=if($Cpp){'rom-kernel-cpp'}else{'rom-kernel-c'}
$kernelBuild=Join-Path $kernelRoot ('build\'+$kernelMode)
New-Item -ItemType Directory -Path $kernelBuild -Force | Out-Null
$kernelFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $kernelRoot 'src')),('/Fo'+$kernelBuild+'\'))
$kernelFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$kernelExe=Join-Path $kernelBuild ('test-rom-kernel-'+[Guid]::NewGuid().ToString('N')+'.exe')
& $kernelCl @kernelFlags (Join-Path $kernelRoot 'src\rom_candidate.c') (Join-Path $kernelRoot 'src\rom_kernel.c') (Join-Path $kernelRoot 'src\feature.c') (Join-Path $kernelRoot 'tests\test_rom_kernel.c') ('/Fe'+$kernelExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'ROM kernel compilation failed'}
. (Join-Path $kernelRoot 'build-evidence.ps1')
Write-ModelBuildEvidence -ModelRoot $kernelRoot -Compiler $kernelCl -Executable $kernelExe -Mode $kernelMode -Sources @('src/rom_candidate.c','src/rom_candidate.h','src/rom_kernel.c','src/rom_kernel.h','src/feature.c','src/feature.h','tests/test_rom_kernel.c','verify-rom-kernel.ps1','build-evidence.ps1')
& $kernelExe $kernelInput
exit $LASTEXITCODE
