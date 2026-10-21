# APK 1.2.7 OTA wire sender, readable C/C++ contract

This host library reconstructs the original packaged JavaScript sender's byte
framing, chunk snapshots, shared mutable queue and explicit SDK callback effects.
It has no BLE backend and is not firmware, a target ISA interpreter, an OTA
installer or proof of hardware compatibility. C11 and C++17 compile the same
source. All tests use synthetic payloads and synthetic transport identifiers.

## Evidence and boundaries

`source-map.json` binds the original APK, wxapkg and appservice identities to the
independently extracted source at `tx-source/exact-source.json`. Its ranges are
Unicode codepoints, end exclusive, in the original appservice, not line numbers
in a reformatted file. `check-source.py --check` rereads the APK ZIP/wxapkg chain,
compares all21 exact source sections and rejects eight mutated source predicates.
Neither checker nor host tests execute the original JavaScript.

- `ble.tx` at120075: prefix55 7F, command, low16 length in big endian, payload,
  sum8 of command/length/payload; prefix excluded. There is no source rejection
  for payload65536: length wraps to0000. This encoder intentionally preserves it.
- `ble.initial-shared-state`, Babel `defineProperty`, `ble.txData-definition`
  at120531: the initially declared txData object is overwritten by a function
  object. `.index`, `.buf` and `.retryCount` are attached to that same function.
- `ble.tx` replaces current chunks and index before `txCallback(true)` resets
  retryCount if connected. An older write remains outstanding; its callback uses
  current shared state. No per-transfer closure, generation guard or serialization
  is present in the selected source.
- `ble.txCallback-definition` at120911: a success closure increments the shared
  index before checking connectivity, then the true branch resets retryCount.
  A failure checks connectivity first, preincrements retryCount, and resends
  while it is<10. The tenth consecutive failure stops this chain. No completion,
  Promise, timer, updater.stop or outer failure propagation occurs here.
- The failure branch has no index<buf.length guard. A delayed failure after
  other successes can submit an undefined value. The observation marks this
  explicitly; the actual SDK's reaction and resulting callbacks are unknown.
- MTU initially20, later ATT MTU minus3; tx caps it at244 without a positive
  lower bound. Chunk sizing snapshots this value. The endpoint IDs/writeType
  are read fresh at each SDK call. A nonpositive MTU cannot make the source
  splice loop progress; the host returns a boundary after queue/index reset,
  without simulating allocation exhaustion or inventing a fallback MTU. The
  original loop would block further event-loop callbacks. The host-only stalled
  flag therefore stops all later operations in this trace until reinitialization
  starts a separate scenario; it is not an added APK recovery mechanism.
- `app.getUidUint8Array` at132174 returns bytes4..17 only for an existing
  byte array of length>=18, otherwise14zero bytes for a short existing array.
  A missing object can throw; the host marks that boundary. The displayed
  device ID covers only bytes4..15 and cannot establish all14 UID bytes.

Only byte-array inputs, U8 command values, integer MTU values and exact counters
below2^53 are represented. JS arbitrary objects/getters, nonbyte coercions,
allocation failures, synchronous exceptions inside wx/getApp and external SDK
callback scheduling remain outside the contract. A submit observation is the SDK
call boundary; whether it returns, throws or eventually callbacks is an external
provider fact. Callers supply explicit success/fail events from previous calls,
one event per request as an interface assumption; the library does not authenticate
callback origins. It does not add per-call pending state. Counters/queue fields
must not be mutated directly by consumers outside the deliberate test probes.

Host capacity/domain errors are preflight errors with no source state effects;
they are not claimed original APK guards. Source allocations are assumed to
succeed in the modeled domain. Output and input storage do not overlap.
The reusable wire storage packs original ArrayBuffer snapshots contiguously.
Returned byte/string views are borrowed until the next mutation. An observer
must copy submitted data immediately if it needs to retain a pending write;
this preserves old write values while replacement changes shared queue state.

`AT_IDLE` means no next submission at this selected callback, including retry
exhaustion. It does not mean end-to-end transfer completion, no outstanding
writes, successful peripheral acknowledgement, correct Flash or compatible BIN.
`AT_DISCONNECTED` represents getApp().msg boundary, not a proved UI return.
Resetting transport fields does not cancel outstanding callback effects.

## Validation

`verify.ps1` and `verify.ps1 -Cpp` compile with MSVC /W4 /WX and run synthetic
host behavior tests. The suite includes length wrap, retry thresholds,
overlapping writes and stale callbacks, disconnect ordering, live endpoints,
MTU snapshot/cap/nonprogress, original UID helper and source-domain boundaries.
It also feeds chunked encoded bytes into the independently source-bound existing
APK receive model. This shows the two host reconstructions compose within their
domains; it is not original APK execution or physical BLE evidence. The clean
empty W frame produces the parser's retained[0] and passes the APK's onebyte0
shortcut; this is explicitly not Flash verification.

The outer updater's timers/Read/Write/stop/E response handling are separately
documented by `updater-flow`, and the selected candidate BOOT by `boot-acceptance`.
The sender model must not be presented as those complete state machines. The
old modern-page response's Runtime identity differs from ID2966; candidate
ID2966 fitting75 numeric BOOT pages does not establish original metadata,
installed BOOT, UID checks, Flash aliasing or physical acceptance.
