# TSL 1.2.7 minimal Morphe smoke patch

此目錄同時收錄獨立的 [TSL9 Android 硬體工具](tsl9-updater/README.md)，目前來源版本為 `0.7.2-test`。App 原始碼、三語資源、JVM 與 Android 測試位於 `tsl9-updater/`；下方內容記錄較早的 Morphe 文字 patch 實驗。

此來源快照不包含原廠 APK／BIN、附件、實車日誌、反編譯輸出、工具、簽章金鑰或建置快取。部分證據連結與 OEM 差異測試依賴本機 `artifacts/firmware-trace/`，需在本機另備相符輸入，不能將缺少素材視為該測試通過。Android 建置需依文件配置本機 SDK／Gradle；`local.properties` 不納入版本控制。

This local proof of concept changes only the first miniapp tab label, `状态` → `狀態·M`.
It does not change BLE commands, device configuration, permissions, DEX, or native libraries.

## Artifacts

- `artifacts/tsl-text-smoke.mpp`: JVM patch bundle, loaded and executed by Morphe Desktop 1.18.1. Android Morphe Manager loading is not verified; this minimal bundle does not include `classes.dex`.
- `artifacts/tsl-text-smoke.apk`: signed local test APK; not an official release.
- `artifacts/morphe-result.json`: actual Morphe patch/build result.
- `SMOKE-RESULT.md`: runtime observations and limitations.

Generated APKs, tools, local signing keys, runtime captures and build outputs are ignored by Git.
The original APK is never changed and is not included in this source tree.

## Build locally (PowerShell, JDK 21)

Download these official dependencies into this workspace:

1. [Morphe Desktop 1.18.1](https://github.com/MorpheApp/morphe-desktop/releases/download/v1.18.1/morphe-desktop-1.18.1-all.jar) → `tools/morphe-desktop-1.18.1-all.jar`.
2. [Kotlin compiler 2.4.21](https://github.com/JetBrains/kotlin/releases/download/v2.4.21/kotlin-compiler-2.4.21.zip) → extract under `tools/kotlin-2.4.21/` so `kotlinc/bin/kotlinc.bat` exists.

Observed dependency SHA-256:

```text
Morphe JAR: 1b506ab5f03d16a2f65026d5e0e1910d01fc1e2152f21eaeb44ed2f30856597b
Kotlin ZIP: 7cc140e76daf416a0424a5557f99afd7ca89ebd463ea1101261e3e01c33e75cd
```

These hashes identify this run's downloads; they are not an independent authenticity attestation.

```powershell
.\scripts\build.ps1 -InputApk './inputs/original.apk'
.\scripts\sign.ps1 -InputApk './inputs/original.apk'
python scripts\verify-patch.py './inputs/original.apk' artifacts\tsl-text-smoke.apk
```

`build.ps1` checks the original APK SHA-256, compiles the Kotlin patch against the actual Morphe API, asks Morphe to load the `.mpp`, executes the raw-resource patch, and verifies its output. `sign.ps1` discovers the newest installed stable Android SDK Build Tools (override `-SdkBuildTools` if needed) and uses a disposable local debug key. Its public `android` password is suitable only for this local test key. Do not publish the private key.

The Kotlin patch separately requires package `com.tencent.weauth`, version `1.2.7` / code `127`, and the exact original wxapkg SHA-256. A different or already patched wxapkg is rejected before writing. No compatibility force flag or continue-on-error is used.

## Why this is a wxapkg repack test

The first tab label is in `/app-config.json` within the embedded `assets/SaaA_embed/*.wxapkg`.
The replacement increases UTF-8 length by 3 bytes. The patch splices that disjoint config range, updates body size and subsequent file offsets, and keeps all overlapping JavaScript aliases intact. It does not independently duplicate the overlapping `/app-service.js` and chunk data.

The independent Python verifier checks ZIP integrity, the complete wxapkg index, all 76 entry ranges, unchanged payloads for every other miniapp file, and JSON equivalence after restoring this one label. It also confirms that every other APK payload file is byte-identical, including DEX and AndroidManifest. Signing metadata is excluded from payload comparison because this APK is re-signed.

## Runtime boundaries

Use an emulator or test device without an existing valuable installation of this package. A local test signature cannot update an installation signed with the original certificate. The supplied APK's native libraries require a compatible environment; the observed API 37 emulator with 16 KB pages rejected the original `libmmkv.so` before miniapp startup.

Offline launch checks were performed before any online access. The user subsequently authorized exactly one normal online startup of the original and one of the patched APK on the local test emulator. Automatic approval review rejected the first online launch command because destinations and transmitted data were not explicitly specified. Neither online launch was executed. The test app was stopped, networking disabled and the dedicated read-only emulator shut down. No manual API requests, scans, authentication workarounds, retry-button actions, or upload of analysis material are part of this validation.
