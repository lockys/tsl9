param([switch]$Cpp)
$ErrorActionPreference='Stop'
$nativeRoot=$PSScriptRoot
$nativeRepo=(Resolve-Path (Join-Path $nativeRoot '..\..')).Path
$nativeRuntime=Join-Path $nativeRepo 'apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin'
$nativeBoot=Join-Path $nativeRepo 'apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin'
if((Get-FileHash -LiteralPath $nativeRuntime -Algorithm SHA256).Hash.ToLowerInvariant() -ne '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'){throw 'Runtime identity mismatch'}
if((Get-FileHash -LiteralPath $nativeBoot -Algorithm SHA256).Hash.ToLowerInvariant() -ne '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'){throw 'BOOT identity mismatch'}
$nativeVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $nativeVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $nativeVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$nativeVersion=(Get-Content -LiteralPath (Join-Path $nativeVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$nativeCl=Join-Path $nativeVs ('VC\Tools\MSVC\'+$nativeVersion+'\bin\Hostx64\x64\cl.exe')
$nativeMode=if($Cpp){'native-callbacks-cpp'}else{'native-callbacks-c'}
$nativeBuild=Join-Path $nativeRoot ('build\'+$nativeMode)
New-Item -ItemType Directory -Path $nativeBuild -Force | Out-Null
$nativeFlags=@('/nologo','/W4','/WX','/Od','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $nativeRoot 'src')),('/Fo'+$nativeBuild+'\'))
$nativeFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$nativeNames=@('src\native_callbacks.c','src\native_callbacks.h','src\feature.h','tests\test_native_callbacks.c')
$nativeIdentity=@{}
foreach($nativeName in $nativeNames){$nativeIdentity[$nativeName]=(Get-FileHash -LiteralPath (Join-Path $nativeRoot $nativeName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$nativeExe=Join-Path $nativeBuild ('native-callbacks-'+[Guid]::NewGuid().ToString('N')+'.exe')
& $nativeCl @nativeFlags (Join-Path $nativeRoot 'src\native_callbacks.c') (Join-Path $nativeRoot 'tests\test_native_callbacks.c') ('/Fe'+$nativeExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Native callback compilation failed'}
foreach($nativeName in $nativeNames){if($nativeIdentity[$nativeName] -ne (Get-FileHash -LiteralPath (Join-Path $nativeRoot $nativeName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Source changed during compile'}}
Write-Output ('NATIVE_CALLBACKS_BUILD '+(@{mode=$nativeMode;sourceSha256=$nativeIdentity;executable=$nativeExe;executableSha256=(Get-FileHash -LiteralPath $nativeExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$nativeCl;compilerSha256=(Get-FileHash -LiteralPath $nativeCl -Algorithm SHA256).Hash.ToLowerInvariant();originalExecuted=$false;hardware=$false}|ConvertTo-Json -Compress))
& $nativeExe $nativeRuntime $nativeBoot
exit $LASTEXITCODE
