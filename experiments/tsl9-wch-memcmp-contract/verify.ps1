param([switch]$Cpp,[string]$Case)
$ErrorActionPreference='Stop'
$mcRoot=$PSScriptRoot
$mcRepo=(Resolve-Path (Join-Path $mcRoot '..\..')).Path
if(-not $Case){
    $Case=Join-Path $mcRepo 'apk-analysis\tsl9-wch-resident-candidate-2026-10-21'
    if(-not(Test-Path -LiteralPath $Case)){$Case=Join-Path $mcRepo 'analysis\wch-resident-candidate-2026-10-21'}
}
$mcMap=Get-Content -LiteralPath (Join-Path $mcRoot 'source-map.json') -Raw|ConvertFrom-Json
foreach($mcInput in $mcMap.inputs){
    $mcPath=Join-Path $Case $mcInput.path
    if((Get-FileHash -LiteralPath $mcPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mcInput.sha256){throw ('Source identity changed: '+$mcInput.path)}
}
foreach($mcRange in $mcMap.ranges){
    $mcRaw=[IO.File]::ReadAllBytes((Join-Path $Case $mcRange.path))
    $mcSlice=[byte[]]::new($mcRange.bytes)
    [Array]::Copy($mcRaw,$mcRange.offset,$mcSlice,0,$mcSlice.Length)
    if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($mcSlice)).ToLowerInvariant() -ne $mcRange.sha256){throw 'Resident source range changed'}
}
$mcVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $mcVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $mcVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64'|Out-Null
$mcVersion=(Get-Content -LiteralPath (Join-Path $mcVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$mcCompiler=Join-Path $mcVs ('VC\Tools\MSVC\'+$mcVersion+'\bin\Hostx64\x64\cl.exe')
$mcMode=if($Cpp){'cpp'}else{'c'}
$mcBuild=Join-Path $mcRoot ('build\'+[Guid]::NewGuid().ToString('N')+'-'+$mcMode)
New-Item -ItemType Directory -Path $mcBuild|Out-Null
$mcNames=@('src\memcmp_contract.c','src\memcmp_contract.h','tests\test_memcmp_contract.c','verify.ps1','source-map.json','README.md')
$mcPins=@{}
foreach($mcName in $mcNames){$mcPins[$mcName]=(Get-FileHash -LiteralPath (Join-Path $mcRoot $mcName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$mcExe=Join-Path $mcBuild 'host-memcmp-tests.exe'
$mcFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $mcRoot 'src')),('/Fo'+$mcBuild+'\'))
$mcFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $mcCompiler @mcFlags (Join-Path $mcRoot 'src\memcmp_contract.c') (Join-Path $mcRoot 'tests\test_memcmp_contract.c') ('/Fe'+$mcExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Host comparison compilation failed'}
$mcOutput=& $mcExe
if($LASTEXITCODE -ne 0){throw 'Host comparison behavior failed'}
$mcTests=$mcOutput|ConvertFrom-Json
if(-not $mcTests.passed){throw 'Host test receipt missing'}
$mcClang='C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin\clang.exe'
$mcTarget=Join-Path $mcBuild 'freestanding-memcmp-rv32.o'
$mcTargetFlags=@('--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-exceptions','-fno-rtti','-Wall','-Wextra','-Werror')
$mcTargetFlags+=if($Cpp){@('-x','c++','-std=c++17')}else{@('-x','c','-std=c11')}
& $mcClang @mcTargetFlags '-c' (Join-Path $mcRoot 'src\memcmp_contract.c') '-o' $mcTarget
if($LASTEXITCODE -ne 0){throw 'Freestanding RV32 compile failed'}
foreach($mcName in $mcNames){if($mcPins[$mcName] -ne (Get-FileHash -LiteralPath (Join-Path $mcRoot $mcName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Inputs changed during verification'}}
$mcReceipt=@{passed=$true;mode=$mcMode;tests=$mcTests;source_sha256=$mcPins;executable=$mcExe;executable_sha256=(Get-FileHash -LiteralPath $mcExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$mcCompiler;compiler_sha256=(Get-FileHash -LiteralPath $mcCompiler -Algorithm SHA256).Hash.ToLowerInvariant();target_object=$mcTarget;target_object_sha256=(Get-FileHash -LiteralPath $mcTarget -Algorithm SHA256).Hash.ToLowerInvariant();target_compiler_sha256=(Get-FileHash -LiteralPath $mcClang -Algorithm SHA256).Hash.ToLowerInvariant();target_compile_flags=$mcTargetFlags;original_executed=$false;target_executed=$false;emulation=$false;network=$false;hardware=$false;native_bin=$false;OTA_ready=$false;native_providers_changed=$false}
$mcReceipt|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $mcBuild 'verification.json') -Encoding utf8
Write-Output ('MEMCMP_RESULT '+($mcReceipt|ConvertTo-Json -Depth 8 -Compress))
