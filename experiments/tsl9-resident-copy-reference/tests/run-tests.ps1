param([switch]$Cpp,[string]$UidRoot,[string]$CommandRoot)
$ErrorActionPreference='Stop'
$rpRoot=Split-Path -Parent $PSScriptRoot
$rpRepo=(Resolve-Path (Join-Path $rpRoot '../..')).Path
if(-not $UidRoot){$UidRoot=Join-Path $rpRepo 'experiments/tsl9-boot2580-uid-helper'}
if(-not $CommandRoot){$CommandRoot=Join-Path $rpRepo 'experiments/tsl9-boot2580-command-adapter'}
$rpVs='C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools'
Import-Module (Join-Path $rpVs 'Common7/Tools/Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $rpVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$rpVersion=(Get-Content -LiteralPath (Join-Path $rpVs 'VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$rpCompiler=Join-Path $rpVs ('VC/Tools/MSVC/'+$rpVersion+'/bin/Hostx64/x64/cl.exe')
$rpMode=if($Cpp){'cpp'}else{'c'}
$rpBuild=Join-Path $rpRoot ('build/'+[guid]::NewGuid().ToString('N')+'-'+$rpMode)
New-Item -ItemType Directory -Path $rpBuild | Out-Null
$rpExe=Join-Path $rpBuild 'host-reference-copy-tests.exe'
$rpFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $rpRoot 'src')),('/I'+(Join-Path $UidRoot 'src')),('/I'+(Join-Path $CommandRoot 'src')),('/Fo'+$rpBuild+'/'))
$rpFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$rpLog=& $rpCompiler @rpFlags (Join-Path $rpRoot 'src/reference_copy.c') (Join-Path $rpRoot 'tests/test_reference_copy.c') ('/Fe'+$rpExe) /link /INCREMENTAL:NO 2>&1
$rpLog | Set-Content -LiteralPath (Join-Path $rpBuild 'compiler.log') -Encoding utf8
if($LASTEXITCODE -ne 0){throw ('Own reference model compilation failed: '+($rpLog -join [Environment]::NewLine))}
$rpOutput=& $rpExe
$rpOutput | Set-Content -LiteralPath (Join-Path $rpBuild 'test-output.json') -Encoding utf8
if($LASTEXITCODE -ne 0){throw 'Own reference model tests failed'}
$rpTest=$rpOutput | ConvertFrom-Json
if(-not $rpTest.passed){throw 'Own reference test result'}
$rpBuildResult=@{passed=$true;mode=$rpMode;tests=$rpTest;executable=$rpExe;executable_sha256=(Get-FileHash -LiteralPath $rpExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$rpCompiler;compiler_sha256=(Get-FileHash -LiteralPath $rpCompiler -Algorithm SHA256).Hash.ToLowerInvariant()}
$rpBuildResult | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $rpBuild 'build-result.json') -Encoding utf8
Write-Output ($rpBuildResult | ConvertTo-Json -Depth 8 -Compress)
