param([switch]$Cpp)
$ErrorActionPreference='Stop'
$romRoot=$PSScriptRoot
$romRepo=(Resolve-Path (Join-Path $romRoot '..\..')).Path
$romInput=Join-Path $romRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $romInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$romVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $romVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $romVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$romVersion=(Get-Content -LiteralPath (Join-Path $romVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$romCl=Join-Path $romVs ('VC\Tools\MSVC\'+$romVersion+'\bin\Hostx64\x64\cl.exe')
$romMode=if($Cpp){'rom-candidate-cpp'}else{'rom-candidate-c'}
$romBuild=Join-Path $romRoot ('build\'+$romMode)
New-Item -ItemType Directory -Path $romBuild -Force | Out-Null
$romFlags=@('/nologo','/W4','/WX','/Od','/Zi','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $romRoot 'src')),('/Fo'+$romBuild+'\'),('/Fd'+(Join-Path $romBuild 'compiler.pdb')))
$romFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$romExe=Join-Path $romBuild ('test-rom-candidate-'+[Guid]::NewGuid().ToString('N')+'.exe')
$romSourceNames=@('src\feature.c','src\feature.h','src\rom_candidate.c','src\rom_candidate.h','tests\test_rom_candidate.c','tests\rom_candidate_fixture.h')
$romSourceBefore=@{}
foreach($romName in $romSourceNames){$romSourceBefore[$romName]=(Get-FileHash -LiteralPath (Join-Path $romRoot $romName) -Algorithm SHA256).Hash.ToLowerInvariant()}
& $romCl @romFlags (Join-Path $romRoot 'src\feature.c') (Join-Path $romRoot 'src\rom_candidate.c') (Join-Path $romRoot 'tests\test_rom_candidate.c') ('/Fe'+$romExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'ROM candidate compilation failed'}
foreach($romName in $romSourceNames){if($romSourceBefore[$romName] -ne (Get-FileHash -LiteralPath (Join-Path $romRoot $romName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw ('Source changed during compile: '+$romName)}}
$romBuildIdentity=@{mode=$romMode;compiler=$romCl;compilerVersion=$romVersion;compilerSha256=(Get-FileHash -LiteralPath $romCl -Algorithm SHA256).Hash.ToLowerInvariant();executable=$romExe;executableSha256=(Get-FileHash -LiteralPath $romExe -Algorithm SHA256).Hash.ToLowerInvariant();sources=$romSourceBefore;originalExecuted=$false;hardware=$false}
Write-Output ('ROM_CANDIDATE_BUILD '+($romBuildIdentity | ConvertTo-Json -Compress))
& $romExe $romInput
exit $LASTEXITCODE
