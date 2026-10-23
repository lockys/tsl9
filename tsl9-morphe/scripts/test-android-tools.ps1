$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'android-tools.ps1')
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('tsl9-tools-' + [guid]::NewGuid())
$saved = @{}
foreach ($name in @('PATH','GRADLE_USER_HOME','ANDROID_HOME','ANDROID_SDK_ROOT')) { $saved[$name] = [Environment]::GetEnvironmentVariable($name) }
$checks = 0
function Check($condition, $label) { if (-not $condition) { throw "FAIL $label" }; $script:checks++ }
try {
    $env:PATH = ''
    $env:GRADLE_USER_HOME = Join-Path $fixture 'gradle cache'
    $env:ANDROID_HOME = ''; $env:ANDROID_SDK_ROOT = ''
    $project = Join-Path $fixture 'project space'; $sdk = Join-Path $fixture 'sdk space'
    $adbName = if ($IsWindows) { 'adb.exe' } else { 'adb' }
    $gradleName = if ($IsWindows) { 'gradle.bat' } else { 'gradle' }
    foreach ($path in @($project, (Join-Path $sdk 'platform-tools'), (Join-Path $sdk 'build-tools/9.0.0'), (Join-Path $sdk 'build-tools/36.0.0'))) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
    $adb = Join-Path $sdk "platform-tools/$adbName"; Set-Content -LiteralPath $adb -Value ''
    $env:ANDROID_HOME = $sdk
    Check ((Resolve-AndroidSdk $project) -eq $sdk) 'SDK environment discovery with spaces'
    Check ((Resolve-AndroidAdb $project) -eq $adb) 'ADB SDK discovery'
    Check ((Resolve-AndroidBuildTools $project) -eq (Join-Path $sdk 'build-tools/36.0.0')) 'build-tools numeric ordering'
    Set-Content -LiteralPath (Join-Path $project 'local.properties') -Value ('sdk.dir=' + $sdk.Replace('\','\\').Replace(':','\:'))
    $env:ANDROID_HOME = Join-Path $fixture 'missing'
    Check ((Resolve-AndroidSdk $project) -eq $sdk) 'escaped local.properties'
    Check ((Resolve-AndroidAdb $project $adb) -eq $adb) 'explicit executable override'
    $rejected = $false
    try { Resolve-AndroidAdb $project (Join-Path $fixture 'missing-adb') | Out-Null } catch { $rejected = $true }
    Check $rejected 'missing explicit executable does not fall back'
    foreach ($version in @('8.12','8.13','8.14.3','9.5.1')) {
        $bin = Join-Path $env:GRADLE_USER_HOME "wrapper/dists/gradle-$version-bin/test-cache/gradle-$version/bin"
        New-Item -ItemType Directory -Path $bin -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $bin $gradleName) -Value ''
    }
    Check ((Resolve-LocalGradle) -like '*gradle-8.14.3*') 'compatible cached Gradle selection excludes major 9'
    $explicit = Join-Path $env:GRADLE_USER_HOME "wrapper/dists/gradle-8.13-bin/test-cache/gradle-8.13/bin/$gradleName"
    Check ((Resolve-LocalGradle $explicit) -eq $explicit) 'explicit Gradle override'
    Write-Output "PASS $checks portable tool discovery checks"
} finally {
    foreach ($name in $saved.Keys) { [Environment]::SetEnvironmentVariable($name, $saved[$name]) }
    # Only the freshly created GUID-named fixture under the OS temp directory.
    $resolved = [IO.Path]::GetFullPath($fixture)
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if (-not $resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path $resolved -Leaf) -notlike 'tsl9-tools-*') { throw 'Unexpected fixture cleanup path.' }
    if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}
