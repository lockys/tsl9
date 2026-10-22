param([switch]$Cpp,[string]$Firmware)
$ErrorActionPreference='Stop'
$clockRoot=$PSScriptRoot
$clockRepo=(Resolve-Path (Join-Path $clockRoot '..\..')).Path
if(-not $Firmware){
    foreach($candidate in @('firmware-downloads\legacy-options-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin','exports\TSL-firmware-options-22-BINs-2026-10-20\BINs\ID-2966-V4.1.60-decoded.bin')){
        $clockCandidate=Join-Path $clockRepo $candidate
        if(Test-Path -LiteralPath $clockCandidate){$Firmware=$clockCandidate;break}
    }
}
if(-not $Firmware -or (Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant() -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'){throw 'Original ID2966 identity required'}
$clockMap=Get-Content -LiteralPath (Join-Path $clockRoot 'source-map.json') -Raw | ConvertFrom-Json
$clockRaw=[IO.File]::ReadAllBytes($Firmware)
if($clockMap.firmware_sha256 -ne '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' -or $clockMap.source_base -ne 32768 -or $clockMap.source_bytes -ne $clockRaw.Length -or $clockMap.source_ranges.Count -ne 1){throw 'Original source-map scope'}
foreach($clockRange in $clockMap.source_ranges){
    $clockSlice=[byte[]]::new($clockRange.bytes)
    [Array]::Copy($clockRaw,([int]$clockRange.address-32768),$clockSlice,0,$clockSlice.Length)
    if([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($clockSlice)).ToLowerInvariant() -ne $clockRange.sha256){throw 'Original clock source changed'}
}
$clockVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $clockVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $clockVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$clockVersion=(Get-Content -LiteralPath (Join-Path $clockVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$clockCompiler=Join-Path $clockVs ('VC\Tools\MSVC\'+$clockVersion+'\bin\Hostx64\x64\cl.exe')
$clockMode=if($Cpp){'cpp'}else{'c'}
$clockBuild=Join-Path $clockRoot ('build\'+[Guid]::NewGuid().ToString('N')+'-'+$clockMode)
New-Item -ItemType Directory -Path $clockBuild | Out-Null
$clockNames=@('src\clock_contract.c','src\clock_contract.h','tests\test_clock_contract.c','verify.ps1','source-map.json','README.md')
$clockPins=@{}
foreach($clockName in $clockNames){$clockPins[$clockName]=(Get-FileHash -LiteralPath (Join-Path $clockRoot $clockName) -Algorithm SHA256).Hash.ToLowerInvariant()}
$clockExe=Join-Path $clockBuild 'host-clock-tests.exe'
$clockFlags=@('/nologo','/W4','/WX','/Od',('/I'+(Join-Path $clockRoot 'src')),('/Fo'+$clockBuild+'\'))
$clockFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
& $clockCompiler @clockFlags (Join-Path $clockRoot 'src\clock_contract.c') (Join-Path $clockRoot 'tests\test_clock_contract.c') ('/Fe'+$clockExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Host clock compilation failed'}
$clockOutput=& $clockExe
if($LASTEXITCODE -ne 0){throw 'Host clock behavior failed'}
$clockTests=$clockOutput | ConvertFrom-Json
if(-not $clockTests.passed){throw 'Host clock result missing'}
$clockTools=$env:TSL9_LLVM_BIN
if([string]::IsNullOrWhiteSpace($clockTools)){throw 'Set TSL9_LLVM_BIN to the existing LLVM toolchain bin directory.'}
$clockClang=Join-Path $clockTools 'clang.exe'
$clockTarget=Join-Path $clockBuild 'freestanding-clock-rv32.o'
$clockTargetFlags=@('--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-exceptions','-fno-rtti','-Wall','-Wextra','-Werror')
$clockTargetFlags+=if($Cpp){@('-x','c++','-std=c++17')}else{@('-x','c','-std=c11')}
& $clockClang @clockTargetFlags '-c' (Join-Path $clockRoot 'src\clock_contract.c') '-o' $clockTarget
if($LASTEXITCODE -ne 0){throw 'Freestanding RV32 compile failed'}
foreach($clockName in $clockNames){if($clockPins[$clockName] -ne (Get-FileHash -LiteralPath (Join-Path $clockRoot $clockName) -Algorithm SHA256).Hash.ToLowerInvariant()){throw 'Inputs changed during verification'}}
$clockReceipt=@{passed=$true;mode=$clockMode;tests=$clockTests;source_sha256=$clockPins;executable=$clockExe;executable_sha256=(Get-FileHash -LiteralPath $clockExe -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$clockCompiler;compiler_sha256=(Get-FileHash -LiteralPath $clockCompiler -Algorithm SHA256).Hash.ToLowerInvariant();firmware_sha256=(Get-FileHash -LiteralPath $Firmware -Algorithm SHA256).Hash.ToLowerInvariant();target_object=$clockTarget;target_object_sha256=(Get-FileHash -LiteralPath $clockTarget -Algorithm SHA256).Hash.ToLowerInvariant();target_compiler_sha256=(Get-FileHash -LiteralPath $clockClang -Algorithm SHA256).Hash.ToLowerInvariant();target_compile_flags=$clockTargetFlags;target_executed=$false;original_executed=$false;emulation=$false;network=$false;hardware=$false;native_bin=$false;OTA_ready=$false}
$clockReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $clockBuild 'verification.json') -Encoding utf8
Write-Output ('CLOCK_RESULT '+($clockReceipt|ConvertTo-Json -Depth 8 -Compress))
