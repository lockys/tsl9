param([switch]$Cpp)
$ErrorActionPreference='Stop'
$deepRoot=$PSScriptRoot
$deepRepo=(Resolve-Path (Join-Path $deepRoot '..\..')).Path
$deepInput=Join-Path $deepRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
if((Get-FileHash -LiteralPath $deepInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$deepVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $deepVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $deepVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$deepVersion=(Get-Content -LiteralPath (Join-Path $deepVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$deepCl=Join-Path $deepVs ('VC\Tools\MSVC\'+$deepVersion+'\bin\Hostx64\x64\cl.exe')
$deepFiles=@('src\general_deep.c','src\general_deep.h','src\report_packet.c','src\report_packet.h','src\dnd_actions.h','tests\test_general_deep.c','verify-general-deep.ps1','src\general_ble.h','src\feature.h','src\tsl9_contract.h')
$deepBefore=@{}
foreach($deepFile in $deepFiles){$deepBefore[$deepFile]=(Get-FileHash -LiteralPath (Join-Path $deepRoot $deepFile) -Algorithm SHA256).Hash.ToLowerInvariant()}
$deepMode=if($Cpp){'deep-cpp'}else{'deep-c'}
$deepBuild=Join-Path $deepRoot ('build\'+$deepMode)
New-Item -ItemType Directory -Path $deepBuild -Force | Out-Null
$deepExe=Join-Path $deepBuild ('test-deep-'+[Guid]::NewGuid().ToString('N')+'.exe')
$deepFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $deepRoot 'src')),('/Fo'+$deepBuild+'\'))
$deepFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $deepCl @deepFlags (Join-Path $deepRoot 'src\general_deep.c') (Join-Path $deepRoot 'src\report_packet.c') (Join-Path $deepRoot 'tests\test_general_deep.c') ('/Fe'+$deepExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'General deep compilation failed'}
$deepAfter=@{}
foreach($deepFile in $deepFiles){$deepAfter[$deepFile]=(Get-FileHash -LiteralPath (Join-Path $deepRoot $deepFile) -Algorithm SHA256).Hash.ToLowerInvariant();if($deepAfter[$deepFile] -ne $deepBefore[$deepFile]){throw ('Compiler source drift: '+$deepFile)}}
[pscustomobject]@{mode=$deepMode;compiler=$deepCl;compiler_sha256=(Get-FileHash -LiteralPath $deepCl -Algorithm SHA256).Hash.ToLowerInvariant();source_sha256_before=$deepBefore;source_sha256_after=$deepAfter;guard=$true;exe=$deepExe;exe_sha256=(Get-FileHash -LiteralPath $deepExe -Algorithm SHA256).Hash.ToLowerInvariant();target_executed=$false}|ConvertTo-Json -Compress -Depth 5
& $deepExe $deepInput
exit $LASTEXITCODE
