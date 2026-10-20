param([switch]$Cpp)
$ErrorActionPreference='Stop'
$featureRoot=$PSScriptRoot
$featureRepo=(Resolve-Path (Join-Path $featureRoot '..\..')).Path
$featureInput=Join-Path $featureRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-Item -LiteralPath $featureInput).Length -ne 76800 -or (Get-FileHash -LiteralPath $featureInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$featureVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $featureVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $featureVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$featureVersion=(Get-Content -LiteralPath (Join-Path $featureVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$featureCl=Join-Path $featureVs ('VC\Tools\MSVC\'+$featureVersion+'\bin\Hostx64\x64\cl.exe')
$featureMode=if($Cpp){'feature-cpp'}else{'feature-c'}
$featureBuild=Join-Path $featureRoot ('build\'+$featureMode)
New-Item -ItemType Directory -Path $featureBuild -Force | Out-Null
$featureFlags=@('/nologo','/W4','/WX','/Od','/Zi','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $featureRoot 'src')),('/Fo'+$featureBuild+'\'),('/Fd'+(Join-Path $featureBuild 'compiler.pdb')))
$featureFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$featureExe=Join-Path $featureBuild 'test-features.exe'
& $featureCl @featureFlags (Join-Path $featureRoot 'src\feature.c') (Join-Path $featureRoot 'tests\test_features.c') ('/Fe'+$featureExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Feature model compilation failed'}
& $featureExe $featureInput
exit $LASTEXITCODE
