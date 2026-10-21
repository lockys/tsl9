param([switch]$Cpp)
$ErrorActionPreference='Stop'
$riRoot=Split-Path -Parent $PSScriptRoot
$riRepo=(Resolve-Path (Join-Path $riRoot '../..')).Path
$riVs='C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools'
Import-Module (Join-Path $riVs 'Common7/Tools/Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $riVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$riVersion=(Get-Content -LiteralPath (Join-Path $riVs 'VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$riCompiler=Join-Path $riVs ('VC/Tools/MSVC/'+$riVersion+'/bin/Hostx64/x64/cl.exe')
$riMode=if($Cpp){'cpp'}else{'c'}
$riBuild=Join-Path $riRoot ('build/'+[guid]::NewGuid().ToString('N')+'-'+$riMode)
New-Item -ItemType Directory -Path $riBuild | Out-Null
$riExe=Join-Path $riBuild 'host-resident-entry-tests.exe'
$riFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $riRoot 'src')),('/I'+(Join-Path $riRepo 'experiments/tsl9-v4160-reset-contract/src')),('/Fo'+$riBuild+'/'))
$riFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$riLog=& $riCompiler @riFlags (Join-Path $riRoot 'src/resident_entry.c') (Join-Path $riRoot 'src/reset_entry_bridge.c') (Join-Path $riRoot 'tests/test_resident_entry.c') ('/Fe'+$riExe) /link /INCREMENTAL:NO 2>&1
$riLog | Set-Content -LiteralPath (Join-Path $riBuild 'compiler.log') -Encoding utf8
if($LASTEXITCODE -ne 0){throw ('Own resident entry compilation failed: '+($riLog -join [Environment]::NewLine))}
$riOutput=& $riExe
$riOutput | Set-Content -LiteralPath (Join-Path $riBuild 'test-output.json') -Encoding utf8
if($LASTEXITCODE -ne 0){throw 'Own resident entry tests failed'}
$riTest=$riOutput | ConvertFrom-Json
if(-not $riTest.passed){throw 'Own resident entry test result'}
$riResult=@{passed=$true;mode=$riMode;tests=$riTest;executable=$riExe;executable_sha256=(Get-FileHash -LiteralPath $riExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$riCompiler;compiler_sha256=(Get-FileHash -LiteralPath $riCompiler -Algorithm SHA256).Hash.ToLowerInvariant()}
$riResult | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $riBuild 'build-result.json') -Encoding utf8
Write-Output ($riResult | ConvertTo-Json -Depth 8 -Compress)
