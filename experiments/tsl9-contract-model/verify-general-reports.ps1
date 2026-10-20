param([switch]$Cpp)
$ErrorActionPreference='Stop'
$reportsRoot=$PSScriptRoot
$reportsRepo=(Resolve-Path (Join-Path $reportsRoot '..\..')).Path
$reportsInput=Join-Path $reportsRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $reportsInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$reportsVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $reportsVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $reportsVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$reportsVersion=(Get-Content -LiteralPath (Join-Path $reportsVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$reportsCl=Join-Path $reportsVs ('VC\Tools\MSVC\'+$reportsVersion+'\bin\Hostx64\x64\cl.exe')
$reportsFiles=@('src\general_reports.c','src\general_reports.h','tests\test_general_reports.c','verify-general-reports.ps1','src\general_ble.h','src\feature.h')
$reportsBefore=@{}
foreach($reportsFile in $reportsFiles){$reportsBefore[$reportsFile]=(Get-FileHash -LiteralPath (Join-Path $reportsRoot $reportsFile) -Algorithm SHA256).Hash.ToLowerInvariant()}
$reportsMode=if($Cpp){'reports-cpp'}else{'reports-c'}
$reportsBuild=Join-Path $reportsRoot ('build\'+$reportsMode)
New-Item -ItemType Directory -Path $reportsBuild -Force | Out-Null
$reportsExe=Join-Path $reportsBuild ('test-reports-'+[Guid]::NewGuid().ToString('N')+'.exe')
$reportsFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $reportsRoot 'src')),('/Fo'+$reportsBuild+'\'))
$reportsFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $reportsCl @reportsFlags (Join-Path $reportsRoot 'src\general_reports.c') (Join-Path $reportsRoot 'tests\test_general_reports.c') ('/Fe'+$reportsExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'General reports compilation failed'}
$reportsAfter=@{}
foreach($reportsFile in $reportsFiles){$reportsAfter[$reportsFile]=(Get-FileHash -LiteralPath (Join-Path $reportsRoot $reportsFile) -Algorithm SHA256).Hash.ToLowerInvariant();if($reportsAfter[$reportsFile] -ne $reportsBefore[$reportsFile]){throw ('Compiler source drift: '+$reportsFile)}}
[pscustomobject]@{mode=$reportsMode;compiler=$reportsCl;compiler_sha256=(Get-FileHash -LiteralPath $reportsCl -Algorithm SHA256).Hash.ToLowerInvariant();source_sha256_before=$reportsBefore;source_sha256_after=$reportsAfter;guard=$true;exe=$reportsExe;exe_sha256=(Get-FileHash -LiteralPath $reportsExe -Algorithm SHA256).Hash.ToLowerInvariant();target_executed=$false}|ConvertTo-Json -Compress -Depth 5
& $reportsExe $reportsInput
exit $LASTEXITCODE
