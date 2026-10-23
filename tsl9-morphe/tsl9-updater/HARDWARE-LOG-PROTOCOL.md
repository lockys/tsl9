# Hardware log protocol boundary

Source: original APK SHA-256 `10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee`, extracted `app-service.js`, `define("pages/debug/debug.js",...)`. The extracted bytes remain under `artifacts/firmware-trace/miniapp/`; use the artifact index to map JS offsets into the wxapkg. This is static evidence; it does not prove this particular TSL9 firmware exposes every diagnostic mode.

## Existing firmware CAN receiver

All control payloads use the existing `55 7F | command | len_hi | len_lo | payload | sum8` frame over FFF0/FFF1.

| Action | Command / payload | Original client evidence |
|---|---|---|
| Receive all CAN IDs | `C0 : 01` | `btnrx` long-press handler calls `e.tx(192,new Uint8Array([1]))` |
| Receive selected IDs | `C0 : FF FF id0_low id0_high ...` | `torx()` prefixes `FFFF`, appends 3–4 digit hex IDs, then swaps each byte pair |
| Stop diagnostic stream | `C0 : 00` | `onHide()` / `onUnload()` call `e.tx(192,new Uint8Array([0]))` |
| Pause (not exposed by this APK) | `C0 : 02` | Original `pause` handler and page `onShow()` |
| Received CAN display | `C0` response, first two bytes shown as hex ID; following up to 8 bytes as data | `rx(t,e)` calls `add(e)` only when `t==192`; `add()` prints `e[0]`, `e[1]`, then remaining bytes |

The updater does not expose the original arbitrary CAN transmit UI. The only C0 writes are receive-all, receive-filter and stop. A sent subscription/stop frame is not a peripheral acknowledgement. Zero captured rows are presented as zero, not as a working stream.

Exact static locations in the extracted `app-service.js` (SHA-256 `c5eb7ae87e5edf310379f19743d720114c9717c3484b8abd30ad8b158affc017`): module start UTF-8 byte offset `197202`, `torx:function()` at `198535`, receive-all call at `199195`, stop call at `199568`. These are file byte offsets, not native virtual addresses. The debug module starts at one-based line 3540; minified handlers continue on line 3541.

## Custom firmware UTF-8 logs

This is an explicitly selected passive receive convention, not an undocumented original TSL UART command:

- Your firmware keeps BLE service `0000FFF0-0000-1000-8000-00805F9B34FB`, characteristic `0000FFF1-0000-1000-8000-00805F9B34FB`, and enables notifications.
- Notify UTF-8 text terminated by LF (or CRLF). Lines and multibyte characters may span notifications. Maximum line size is 4096 bytes; invalid UTF-8 or binary control characters become metadata errors instead of fabricated text.
- The APK does not send an enable-text-log command and cannot retrieve MCU UART/printf output unless your firmware forwards it to this BLE notification channel.
- Select this mode separately from binary TSL framing. It does not turn binary telemetry or firmware pages into text. Stop the capture before OTA.
- Known identity/credential labels (including `device_uid`, `refresh_token`, `BLE_MAC`, VIN, password, API key) cause the entire line to be replaced. Unknown application-specific private data cannot be recognized reliably: do not print secrets from custom firmware.

## Local journal

`latest-hardware.jsonl` is separate from the phone's `latest-debug.log`. A header identifies schema, mode, limit/stop reason and count. Every row has `source:"hardware_rx"`, elapsed time and decoded kind. Firmware pages, UID/VIN-bearing A0 bytes and auth payloads are never dumped. CAN data is off by default and is explicitly enabled locally; standard diagnostic transport IDs 7DF/7E0–7EF remain masked. Other CAN bytes can contain vehicle data, so exported logs must be treated accordingly.

Sessions stop at five minutes, 10000 records or the configured character bound. File writes use Android AtomicFile. Starting a new session replaces the previous local journal. Manual export is through the Android document picker; there is no automatic upload.
