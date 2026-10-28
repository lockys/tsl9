# Settings destination — 0.7.5-test

The user chose Settings as the fourth visible bottom destination. The four tabs share the existing MainActivity, BLE connection and operation controllers. The capsule keeps its nominal 52% width, four equal slots and 48dp targets; accessible labels can expand it. Screens and copy support English, Simplified Chinese and Traditional Chinese.

| Control | Location |
| --- | --- |
| Language and system-language selection | Settings |
| Module information and Bluetooth password verification | Settings |
| Forget the locally remembered Bluetooth password | Settings |
| Advanced firmware/readback options | Settings disclosure |
| Hardware capture configuration, debug logs and exports | Settings diagnostics |
| Scan/connect, current version, bin selection, compatibility, update/cancel | Bluetooth/update workflow |
| OEM lighting shortcut settings | Car controls |
| Live data and immediate CAN query/start/stop | Live data |

Selecting Settings follows the existing tab-change seat-stop path and does not stop the BLE-owning Activity. Language changes retain the existing idle/disconnected guard, and update/capture policy controls keep their existing operation locks. The selected Settings tab is restored by the existing Activity saved-state path.

Forgetting a password removes the local encrypted file and AtomicFile recovery files. It does not change the module password or revoke the current authenticated connection. The next explicit password verification can remember a new value. Saved-password status exposes presence only, and is refreshed on entering Settings, verification and local clearing rather than decrypting on every UI tick.

## Verification

Run the emulator instrumentation with `-e settings true` for placement, state, encrypted-copy clearing, active-capture continuity and recreation checks. The test uses a separate synthetic password file and Keystore alias. `-e settings preview`, `preview-tools`, `preview-diagnostics` and `preview-landscape` capture actual native UI. Landscape capture waits for the real configuration change. No mode scans, connects or transmits Bluetooth.

See `verification/settings-0.7.5-test.json` and `verification/screens/0.7.5/` for the recorded local evidence. Physical BLE, vehicle actuation and firmware writes were not rerun for this UI change.
