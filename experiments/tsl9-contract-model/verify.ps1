param([switch]$Cpp)
$ErrorActionPreference='Stop'
$contractRoot=$PSScriptRoot
$contractRepo=(Resolve-Path (Join-Path $contractRoot '..\..')).Path
$contractInputs=@(
    @{Path='apk-analysis\tsl9-server-current\TSL9-boot-api-payload.bin';Bytes=12288;Hash='650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'},
    @{Path='apk-analysis\tsl9-server-current\TSL9-runtime-api-payload.bin';Bytes=76800;Hash='32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'}
)
foreach($contractInput in $contractInputs) {
    $contractPath=Join-Path $contractRepo $contractInput.Path
    if((Get-Item -LiteralPath $contractPath).Length -ne $contractInput.Bytes -or (Get-FileHash -LiteralPath $contractPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $contractInput.Hash) { throw 'Captured payload identity mismatch' }
}
$contractEvidence=Get-Content -LiteralPath (Join-Path $contractRoot 'fixtures\evidence.json') -Raw | ConvertFrom-Json
foreach($contractImage in $contractEvidence.images.PSObject.Properties) {
    $contractImagePath=Join-Path $contractRepo $contractImage.Value.path
    if((Get-Item -LiteralPath $contractImagePath).Length -ne $contractImage.Value.bytes -or (Get-FileHash -LiteralPath $contractImagePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $contractImage.Value.sha256) { throw 'Fixture image identity mismatch' }
}
foreach($contractRange in $contractEvidence.ranges.PSObject.Properties) {
    $contractRangeImage=$contractEvidence.images.($contractRange.Value.image)
    $contractRangeBytes=[IO.File]::ReadAllBytes((Join-Path $contractRepo $contractRangeImage.path))
    $contractStart=[Convert]::ToInt32($contractRange.Value.start_va.Substring(2),16)
    $contractEnd=[Convert]::ToInt32($contractRange.Value.end_va_exclusive.Substring(2),16)
    $contractBase=[Convert]::ToInt32($contractRangeImage.base.Substring(2),16)
    $contractSlice=[byte[]]::new($contractEnd-$contractStart)
    [Array]::Copy($contractRangeBytes,$contractStart-$contractBase,$contractSlice,0,$contractSlice.Length)
    $contractHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($contractSlice)).ToLowerInvariant()
    if($contractHash -ne $contractRange.Value.raw_sha256) { throw ('Raw range identity mismatch: '+$contractRange.Name) }
}
Write-Output ('PROVENANCE images=2 raw_ranges='+$contractEvidence.ranges.PSObject.Properties.Name.Count+' matched=yes')
$contractVs='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
Import-Module (Join-Path $contractVs 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll')
Enter-VsDevShell -VsInstallPath $contractVs -SkipAutomaticLocation -DevCmdArguments '-arch=x64 -host_arch=x64' | Out-Null
$contractVersion=(Get-Content -LiteralPath (Join-Path $contractVs 'VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt') -Raw).Trim()
$contractCl=Join-Path $contractVs ('VC\Tools\MSVC\'+$contractVersion+'\bin\Hostx64\x64\cl.exe')
$contractMode=if($Cpp){'host-cpp'}else{'host-c'}
$contractBuild=Join-Path $contractRoot ('build\'+$contractMode)
New-Item -ItemType Directory -Path $contractBuild -Force | Out-Null
$contractFlags=@('/nologo','/W4','/WX','/Od','/Zi','/D_CRT_SECURE_NO_WARNINGS',('/I'+(Join-Path $contractRoot 'src')),('/Fo'+$contractBuild+'\'),('/Fd'+(Join-Path $contractBuild 'compiler.pdb')))
$contractFlags+=if($Cpp){@('/TP','/std:c++17')}else{@('/TC','/std:c11')}
$contractExe=Join-Path $contractBuild 'test-contract.exe'
& $contractCl @contractFlags (Join-Path $contractRoot 'src\model.c') (Join-Path $contractRoot 'tests\test_contract.c') ('/Fe'+$contractExe) /link /INCREMENTAL:NO
if($LASTEXITCODE -ne 0){throw 'Contract model compilation failed'}
& $contractExe $contractRepo
exit $LASTEXITCODE
