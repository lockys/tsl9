param([switch]$Cpp)
$ErrorActionPreference='Stop'
$packetRoot=$PSScriptRoot
$packetVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $packetVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $packetVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$packetVersion=(Get-Content -LiteralPath (Join-Path $packetVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$packetCl=Join-Path $packetVs ('VC\Tools\MSVC\'+$packetVersion+'\bin\Hostx64\x64\cl.exe')
$packetMode=if($Cpp){'gatt-parser-cpp'}else{'gatt-parser-c'}
$packetBuild=Join-Path $packetRoot ('build/'+$packetMode)
[IO.Directory]::CreateDirectory($packetBuild)|Out-Null
$packetExe=Join-Path $packetBuild ('test-packet-'+[Guid]::NewGuid().ToString('N')+'.exe')
$packetFiles=@('src/gatt_parser.c','src/gatt_parser.h','src/ble_transport.h','src/dnd_actions.c','src/dnd_actions.h','tests/test_gatt_parser.c','verify-gatt-parser.ps1')
$packetBefore=@{};foreach($name in $packetFiles){$packetBefore[$name]=(Get-FileHash -LiteralPath (Join-Path $packetRoot $name) -Algorithm SHA256).Hash.ToLowerInvariant()}
$packetFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $packetRoot 'src')),('/Fo'+$packetBuild+'\'))
$packetFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $packetCl @packetFlags (Join-Path $packetRoot 'src/gatt_parser.c') (Join-Path $packetRoot 'src/dnd_actions.c') (Join-Path $packetRoot 'tests/test_gatt_parser.c') ('/Fe'+$packetExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Standalone report packet compile failed'}
$packetLines=@(& $packetExe);$packetExit=$LASTEXITCODE
foreach($name in $packetFiles){if((Get-FileHash -LiteralPath (Join-Path $packetRoot $name) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $packetBefore[$name]){throw 'Packet build input changed'}}
[pscustomobject]@{suite=$packetMode;exit_code=$packetExit;summary=@($packetLines|Where-Object {$_ -like 'GATT_PARSER_RESULT*'});failure_examples=@($packetLines|Where-Object {$_ -like 'FAIL*'}|Select-Object -First 8);exe=$packetExe;exe_sha256=(Get-FileHash -LiteralPath $packetExe -Algorithm SHA256).Hash.ToLowerInvariant();source_sha256=$packetBefore;compiler=$packetCl;compiler_sha256=(Get-FileHash -LiteralPath $packetCl -Algorithm SHA256).Hash.ToLowerInvariant();flags=$packetFlags;network=$false;original_executed=$false;hardware=$false}|ConvertTo-Json -Depth 5 -Compress
exit $packetExit
