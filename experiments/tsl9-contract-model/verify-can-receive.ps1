param([switch]$Cpp,[switch]$Baseline)
$ErrorActionPreference='Stop'
$crRoot=$PSScriptRoot
$crRepo=(Resolve-Path (Join-Path $crRoot '..\..')).Path
$crRuntime=Join-Path $crRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$crRuntimeBefore=(Get-FileHash -LiteralPath $crRuntime -Algorithm SHA256).Hash.ToLowerInvariant()
if($crRuntimeBefore -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
$crVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $crVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $crVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$crVersion=(Get-Content -LiteralPath (Join-Path $crVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$crCompiler=Join-Path $crVs ('VC\Tools\MSVC\'+$crVersion+'\bin\Hostx64\x64\cl.exe')
$crCompilerBefore=(Get-FileHash -LiteralPath $crCompiler -Algorithm SHA256).Hash.ToLowerInvariant()
$crMode=if($Cpp){'can-receive-cpp'}else{'can-receive-c'}
if($Baseline){$crMode+='-r18-baseline'}
$crBuild=Join-Path $crRoot ('build\'+$crMode)
New-Item -ItemType Directory -Path $crBuild -Force | Out-Null
$crBefore=@{}
$crFiles=@('src\can_receive.c','src\can_receive.h','src\feature.h','tests\test_can_receive.c','verify-can-receive.ps1')
$crSource=Join-Path $crRoot 'src\can_receive.c'
$crPrior=Join-Path $crRepo 'apk-analysis\tsl9-function-hardware\nineteenth-round\integration\prior'
if($Baseline){
 $crExpected=@{'can_receive.c'='afbfdf00ca171166831580744959608572f22194133325bcfea63f9906383d24';'can_receive.h'='2a98f03d41ea5e5d938964b9171d9f0000c9fdb5233f338c311021606ad331a8'}
 foreach($crName in $crExpected.Keys){if((Get-FileHash -LiteralPath (Join-Path $crPrior $crName) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $crExpected[$crName]){throw 'CR exact R18 baseline mismatch'}}
 $crFiles=@('src\feature.h','tests\test_can_receive.c','verify-can-receive.ps1','..\..\apk-analysis\tsl9-function-hardware\nineteenth-round\integration\prior\can_receive.c','..\..\apk-analysis\tsl9-function-hardware\nineteenth-round\integration\prior\can_receive.h')
 $crSource=Join-Path $crPrior 'can_receive.c'
}
foreach($crFile in $crFiles){$crBefore[$crFile]=(Get-FileHash -LiteralPath (Join-Path $crRoot $crFile) -Algorithm SHA256).Hash.ToLowerInvariant()}
$crExe=Join-Path $crBuild ('test-can-receive-'+[Guid]::NewGuid().ToString('N')+'.exe')
$crFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $crRoot 'src')),('/Fo'+$crBuild+'\'))
$crFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
if($Baseline){$crFlags+=('/FI'+(Join-Path $crPrior 'can_receive.h'))}
& $crCompiler @crFlags $crSource (Join-Path $crRoot 'tests\test_can_receive.c') ('/Fe'+$crExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'CR leaf compilation failed'}
$crAfter=@{}
foreach($crFile in $crFiles){$crAfter[$crFile]=(Get-FileHash -LiteralPath (Join-Path $crRoot $crFile) -Algorithm SHA256).Hash.ToLowerInvariant();if($crBefore[$crFile] -ne $crAfter[$crFile]){throw 'CR compiler source drift'}}
$crExeBefore=(Get-FileHash -LiteralPath $crExe -Algorithm SHA256).Hash.ToLowerInvariant()
$crCompilerAfter=(Get-FileHash -LiteralPath $crCompiler -Algorithm SHA256).Hash.ToLowerInvariant()
$crRuntimeAfter=(Get-FileHash -LiteralPath $crRuntime -Algorithm SHA256).Hash.ToLowerInvariant()
if($crCompilerBefore -ne $crCompilerAfter -or $crRuntimeBefore -ne $crRuntimeAfter){throw 'CR compiler/Runtime drift'}
Write-Output ('CAN_RECEIVE_BUILD '+(@{mode=$crMode;before=$crBefore;after=$crAfter;guard=$true;exe=$crExe;exe_sha256=$crExeBefore;compiler=$crCompiler;compiler_sha256=$crCompilerBefore;compiler_sha256_after=$crCompilerAfter;runtime=$crRuntime;runtime_before=$crRuntimeBefore;runtime_after=$crRuntimeAfter;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 6 -Compress))
& $crExe $crRuntime
$crRunExit=$LASTEXITCODE
$crRunSources=@{}
foreach($crFile in $crFiles){$crRunSources[$crFile]=(Get-FileHash -LiteralPath (Join-Path $crRoot $crFile) -Algorithm SHA256).Hash.ToLowerInvariant();if($crBefore[$crFile] -ne $crRunSources[$crFile]){throw 'CR run source drift'}}
$crRunCompiler=(Get-FileHash -LiteralPath $crCompiler -Algorithm SHA256).Hash.ToLowerInvariant()
$crRunRuntime=(Get-FileHash -LiteralPath $crRuntime -Algorithm SHA256).Hash.ToLowerInvariant()
$crRunExe=(Get-FileHash -LiteralPath $crExe -Algorithm SHA256).Hash.ToLowerInvariant()
if($crCompilerBefore -ne $crRunCompiler -or $crRuntimeBefore -ne $crRunRuntime -or $crExeBefore -ne $crRunExe){throw 'CR run compiler/Runtime/exe drift'}
Write-Output ('CAN_RECEIVE_RUN_GUARD '+(@{guard=$true;after_run=$crRunSources;compiler_sha256=$crRunCompiler;runtime_sha256=$crRunRuntime;exe_sha256=$crRunExe;exit_code=$crRunExit;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 6 -Compress))
exit $crRunExit
