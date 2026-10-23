# Shared local discovery; explicit arguments always take precedence. No downloads.
function Resolve-LocalExecutable([string]$Path, [string]$Name) {
    if ($Path) {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Tool not found: $Path" }
        return (Resolve-Path -LiteralPath $Path).Path
    }
    $command = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) { return $command.Source }
    return $null
}

function Resolve-AndroidSdk([string]$ProjectRoot, [string]$SdkPath) {
    $candidates = @($SdkPath)
    $properties = Join-Path $ProjectRoot 'local.properties'
    if (-not $SdkPath -and (Test-Path -LiteralPath $properties)) {
        $line = Get-Content -LiteralPath $properties | Where-Object { $_ -match '^sdk\.dir=' } | Select-Object -First 1
        if ($line) { $candidates += $line.Substring(8).Replace('\:', ':').Replace('\\', '\') }
    }
    if (-not $SdkPath) {
        $candidates += @($env:ANDROID_SDK_ROOT, $env:ANDROID_HOME)
        if ($env:LOCALAPPDATA) { $candidates += Join-Path $env:LOCALAPPDATA 'Android/Sdk' }
        if ($env:HOME) { $candidates += @((Join-Path $env:HOME 'Library/Android/sdk'), (Join-Path $env:HOME 'Android/Sdk')) }
    }
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Container)) { return (Resolve-Path -LiteralPath $candidate).Path }
    }
    throw 'Android SDK not found. Set ANDROID_SDK_ROOT / ANDROID_HOME, local.properties sdk.dir, or pass an SDK path.'
}

function Resolve-AndroidAdb([string]$ProjectRoot, [string]$AdbPath) {
    $found = Resolve-LocalExecutable $AdbPath 'adb'
    if ($found) { return $found }
    $sdk = Resolve-AndroidSdk $ProjectRoot
    $name = if ($IsWindows) { 'adb.exe' } else { 'adb' }
    return Resolve-LocalExecutable (Join-Path $sdk "platform-tools/$name") 'adb'
}

function Resolve-AndroidBuildTools([string]$ProjectRoot, [string]$BuildToolsPath) {
    if ($BuildToolsPath) {
        if (-not (Test-Path -LiteralPath $BuildToolsPath -PathType Container)) { throw 'Specified build-tools directory does not exist.' }
        return (Resolve-Path -LiteralPath $BuildToolsPath).Path
    }
    $sdk = Resolve-AndroidSdk $ProjectRoot
    $tools = Get-ChildItem -LiteralPath (Join-Path $sdk 'build-tools') -Directory | Where-Object { $_.Name -match '^\d+\.\d+\.\d+$' } | Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1
    if (-not $tools) { throw 'Install Android SDK build-tools or pass -SdkBuildTools.' }
    return $tools.FullName
}

function Resolve-LocalGradle([string]$GradlePath) {
    $found = Resolve-LocalExecutable $GradlePath 'gradle'
    if ($found) { return $found }
    $cache = $env:GRADLE_USER_HOME
    if (-not $cache) { $cache = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.gradle' }
    $name = if ($IsWindows) { 'gradle.bat' } else { 'gradle' }
    $candidates = @(Get-ChildItem -Path (Join-Path $cache "wrapper/dists/gradle-*-bin/*/gradle-*/bin/$name") -File -ErrorAction SilentlyContinue | Where-Object { $_.Directory.Parent.Name -match '^gradle-8\.(\d+)(\.\d+)?$' -and [version]($_.Directory.Parent.Name.Substring(7)) -ge [version]'8.13' } | Sort-Object { [version]($_.Directory.Parent.Name.Substring(7)) } -Descending)
    if ($candidates.Count) { return $candidates[0].FullName }
    throw 'Gradle not found. Add compatible Gradle 8.x (8.13+) to PATH or pass -GradlePath. Builds remain offline.'
}
