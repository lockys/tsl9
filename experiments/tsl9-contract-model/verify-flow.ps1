param([switch]$Cpp)
$ErrorActionPreference='Stop'
$flowRoot=$PSScriptRoot
$flowVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $flowVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $flowVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$flowVersion=(Get-Content -LiteralPath (Join-Path $flowVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$flowCl=Join-Path $flowVs ('VC\Tools\MSVC\'+$flowVersion+'\bin\Hostx64\x64\cl.exe')
$flowMode=if($Cpp){'flow-cpp'}else{'flow-c'}
$flowBuild=Join-Path $flowRoot ('build\'+$flowMode)
New-Item -ItemType Directory -Path $flowBuild -Force | Out-Null
$flowFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $flowRoot 'src')),('/Fo'+$flowBuild+'\'))
$flowFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$flowExe=Join-Path $flowBuild ('test-flow-'+[Guid]::NewGuid().ToString('N')+'.exe')
$flowSources=@('src/model.c','src/general_ble.c','src/general_reports.c')
$flowInputs=$flowSources+@('src/tsl9_contract.h','src/general_ble.h','src/general_reports.h','src/feature.h','tests/test_flow.c','verify-flow.ps1','build-evidence.ps1')
. (Join-Path $flowRoot 'build-evidence.ps1')
$flowBefore=Get-ModelBuildInputHashes -ModelRoot $flowRoot -Sources $flowInputs
$flowCompile=$flowSources | ForEach-Object {Join-Path $flowRoot $_}
& $flowCl @flowFlags @flowCompile (Join-Path $flowRoot 'tests/test_flow.c') ('/Fe'+$flowExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Flow compilation failed'}
Write-ModelBuildEvidence -ModelRoot $flowRoot -Compiler $flowCl -Executable $flowExe -Mode $flowMode -Sources $flowInputs -Before $flowBefore
& $flowExe
exit $LASTEXITCODE
