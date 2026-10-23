# Portable local tools and neutral Android identity

Version `0.7.1-test` uses namespace `dev.tsl9.morphe` and installed debug package `dev.tsl9.morphe.test`. This is a separate installation from previous builds; settings, local logs and Android permissions are not migrated automatically. Existing release tags and historical verification receipts identify the original binaries and remain unchanged.

No tracked build/test script depends on a particular Windows account, Downloads folder, Gradle cache hash or emulator port. `../scripts/android-tools.ps1` resolves installed tools locally without downloading anything:

- Explicit executable arguments (`-GradlePath`, `-AdbPath`) take precedence, then PATH.
- SDK discovery uses the project's ignored `local.properties` (`sdk.dir`), `ANDROID_SDK_ROOT`, `ANDROID_HOME`, then standard directories under the current user's profile. An explicit SDK directory overrides discovery.
- Without Gradle on PATH, discovery selects the newest installed Gradle 8.x version at least 8.13 from `GRADLE_USER_HOME` or the current profile's `.gradle` cache. It excludes Gradle 9, which this AGP setup does not support. Builds stay offline.
- Signing discovers the newest installed stable SDK build-tools version, or accepts `-SdkBuildTools`.
- The earlier Morphe patch/sign scripts require `-InputApk`; relative inputs resolve before changing the working directory. Input hash checks remain intact.
- Emulator tests and screenshot capture require an explicit `-Serial`. They reject physical-device serials and perform no BLE operations.

Run `pwsh -File ../scripts/test-android-tools.ps1` for isolated discovery fixtures with paths containing spaces, escaped Java properties, semantic version ordering and missing explicit overrides. These fixtures do not execute Android tools or access hardware.

After building and installing both debug APKs on your own emulator, capture the three actual Traditional Chinese screens with:

```powershell
pwsh -File ./capture-ui.ps1 -Serial '<your-emulator-serial>'
```

The script runs synthetic instrumentation, verifies the visible App title, selects each real tab and captures screenshots under `../artifacts/ui-screenshots/`. It does not fabricate connection status or vehicle data.
