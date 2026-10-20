param([switch]$Cpp)
$ErrorActionPreference='Stop'
$spiRoot=$PSScriptRoot
$spiRepo=(Resolve-Path (Join-Path $spiRoot '..\..')).Path
$spiRuntime=Join-Path $spiRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $spiRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$spiVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $spiVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $spiVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$spiVersion=(Get-Content -LiteralPath (Join-Path $spiVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$spiCl=Join-Path $spiVs ('VC\Tools\MSVC\'+$spiVersion+'\bin\Hostx64\x64\cl.exe')
$spiCompilerBefore=(Get-FileHash -LiteralPath $spiCl -Algorithm SHA256).Hash.ToLowerInvariant()
$spiInputBefore=(Get-FileHash -LiteralPath $spiRuntime -Algorithm SHA256).Hash.ToLowerInvariant()
$spiMode=if($Cpp){'spi-can-cpp'}else{'spi-can-c'}
$spiBuild=Join-Path $spiRoot ('build\'+$spiMode)
New-Item -ItemType Directory -Path $spiBuild -Force | Out-Null
$spiFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $spiRoot 'src')),('/Fo'+$spiBuild+'\'))
$spiFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$spiNames=@('src\spi_can.c','src\spi_can.h','src\feature.h','tests\test_spi_can.c','verify-spi-can.ps1')
$spiIdentity=@{}
foreach($spiName in $spiNames){$spiIdentity[$spiName]=(Get-FileHash -LiteralPath (Join-Path $spiRoot $spiName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$spiExe=Join-Path $spiBuild ('spi-can-'+[Guid]::NewGuid().ToString('N')+'.exe')
& $spiCl @spiFlags (Join-Path $spiRoot 'src\spi_can.c') (Join-Path $spiRoot 'tests\test_spi_can.c') ('/Fe'+$spiExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'SPI CAN compilation failed'}
if($spiCompilerBefore -ne (Get-FileHash -LiteralPath $spiCl -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Compiler changed during compile'}
if($spiInputBefore -ne (Get-FileHash -LiteralPath $spiRuntime -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Original input changed during compile'}
foreach($spiName in $spiNames){if($spiIdentity[$spiName] -ne (Get-FileHash -LiteralPath (Join-Path $spiRoot $spiName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source changed during compile'}}
Write-Output ('SPI_CAN_BUILD '+(@{mode=$spiMode;sourceSha256=$spiIdentity;executable=$spiExe;executableSha256=(Get-FileHash -LiteralPath $spiExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$spiCl;compilerSha256=(Get-FileHash -LiteralPath $spiCl -Algorithm SHA256).Hash.ToLowerInvariant();originalExecuted=$false;hardware=$false}|ConvertTo-Json -Compress))
$spiExeBefore=(Get-FileHash -LiteralPath $spiExe -Algorithm SHA256).Hash.ToLowerInvariant()
& $spiExe $spiRuntime
$spiCode=$LASTEXITCODE
foreach($spiName in $spiNames){if($spiIdentity[$spiName] -ne (Get-FileHash -LiteralPath (Join-Path $spiRoot $spiName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source changed during host run'}}
if($spiInputBefore -ne (Get-FileHash -LiteralPath $spiRuntime -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Original input changed during host run'}
if($spiCompilerBefore -ne (Get-FileHash -LiteralPath $spiCl -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Compiler changed during host run'}
if($spiExeBefore -ne (Get-FileHash -LiteralPath $spiExe -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Executable changed during host run'}
Write-Output ('SPI_CAN_POSTRUN '+(@{exitCode=$spiCode;beforeAfterMatched=$true;inputSha256=$spiInputBefore;sourceSha256=$spiIdentity;compilerSha256=$spiCompilerBefore;executableSha256=$spiExeBefore;originalExecuted=$false;hardware=$false}|ConvertTo-Json -Compress))
exit $spiCode

