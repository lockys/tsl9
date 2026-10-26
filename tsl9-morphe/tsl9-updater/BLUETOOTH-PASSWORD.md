# Remember the last Bluetooth password

Starting with `0.7.4-test`, the password dialog prefills the last manually submitted, format-valid four-character ASCII password. The user can replace it and must still press Verify. A remembered value does not establish authentication success; a rejected password remains editable. Cancel and invalid input preserve the previous value.

`BluetoothPasswordDialog` reuses the existing English, Simplified Chinese and Traditional Chinese strings and masked input. Android view-state saving and autofill are disabled for this field, and dismissed fields are cleared. The existing connection, operation and authentication guards remain in `MainActivity`; only an explicit Verify sends A8. Passwords remain redacted from debug and hardware logs.

`BluetoothPasswordStore` encrypts the value with an app-scoped Android Keystore AES-256 key and AES-GCM with a fresh 96-bit nonce and 128-bit tag. Only a versioned ciphertext is written atomically to `Context.getNoBackupFilesDir()/bluetooth-password.enc`; no plaintext password is placed in preferences, backups or exported logs. Clearing app data or uninstalling removes the saved value. A missing, corrupt or unavailable store falls back to manual input; inability to save does not prevent manual authentication.

## Local verification

Build with `./build.ps1` and install both APKs on a dedicated emulator. Use the test APK's synthetic, recording transport:

```powershell
adb -s <emulator> shell am instrument -w -e locale zh-Hant -e passwords true dev.tsl9.morphe.test.test/dev.tsl9.morphe.SmokeInstrumentation
```

Repeat with `en` and `zh-Hans`. The checks cover masking, explicit submit, cancel, invalid input, replacement, fresh nonces, ciphertext tampering, key/file reset and unavailable storage. To verify persistence across a genuine process stop, run with `-e passwords seed`, force-stop the target package, then run with `-e passwords restore`. Fixtures use separate test files and Keystore aliases and are cleaned up. These tests never scan, connect or transmit Bluetooth.

`-e passwords preview` captures the actual masked native dialog with a synthetic remembered value to the App's external files directory as `password-prefill.png`. This uses the production dialog component with a recording callback on a disconnected emulator, rather than a physical Bluetooth session.
