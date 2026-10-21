param([switch]$Cpp)
$ErrorActionPreference='Stop'
$mlRoot=Split-Path -Parent $PSScriptRoot
$mlRepo=(Resolve-Path (Join-Path $mlRoot '../..')).Path
$mlVs='C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools'
Import-Module (Join-Path $mlVs 'Common7/Tools/Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $mlVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$mlVersion=(Get-Content -LiteralPath (Join-Path $mlVs 'VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$mlCompiler=Join-Path $mlVs ('VC/Tools/MSVC/'+$mlVersion+'/bin/Hostx64/x64/cl.exe')
$mlMode=if($Cpp){'cpp'}else{'c'}
$mlBuild=Join-Path $mlRoot ('build/'+[guid]::NewGuid().ToString('N')+'-'+$mlMode)
New-Item -ItemType Directory -Path $mlBuild | Out-Null
$mlExe=Join-Path $mlBuild 'host-runtime-loop-tests.exe'
$mlFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $mlRoot 'src')),('/I'+(Join-Path $mlRepo 'experiments/tsl9-resident-entry-reference/src')),('/I'+(Join-Path $mlRepo 'experiments/tsl9-v4160-reset-contract/src')),('/Fo'+$mlBuild+'/'))
$mlFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$mlLog=& $mlCompiler @mlFlags (Join-Path $mlRoot 'src/runtime_loop.c') (Join-Path $mlRoot 'tests/test_runtime_loop.c') ('/Fe'+$mlExe) /link /INCREMENTAL:NO 2>&1
$mlLog | Set-Content -LiteralPath (Join-Path $mlBuild 'compiler.log') -Encoding utf8
if($LASTEXITCODE -ne 0){throw ('Own runtime-loop compilation failed: '+($mlLog -join [Environment]::NewLine))}
$mlOutput=& $mlExe
$mlOutput | Set-Content -LiteralPath (Join-Path $mlBuild 'test-output.json') -Encoding utf8
if($LASTEXITCODE -ne 0){throw 'Own runtime-loop tests failed'}
$mlTest=$mlOutput | ConvertFrom-Json
if(-not $mlTest.passed){throw 'Own runtime-loop test result'}
$mlResult=@{passed=$true;mode=$mlMode;tests=$mlTest;executable=$mlExe;executable_sha256=(Get-FileHash -LiteralPath $mlExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$mlCompiler;compiler_sha256=(Get-FileHash -LiteralPath $mlCompiler -Algorithm SHA256).Hash.ToLowerInvariant()}
$mlResult | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $mlBuild 'build-result.json') -Encoding utf8
Write-Output ($mlResult | ConvertTo-Json -Depth 8 -Compress)
