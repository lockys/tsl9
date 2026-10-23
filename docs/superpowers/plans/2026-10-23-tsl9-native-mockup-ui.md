# TSL9 native UI implementation

Approved direction: UI concept 02, warm light surfaces and forest teal with a floating pill navigation bar. Native Android Java views remain the implementation. No BLE/OTA wire-protocol or command-policy changes.

1. Add native geometry/navigation regression checks before implementation: three accessible icon tabs, inset bottom capsule, usable targets, and tab switching preserves firmware state. Run once against the previous UI to observe the expected failure.
2. Introduce a shared native visual helper for typography, state colors, rounded controls, line icons, grouped sections and disclosure rows. Keep localization and disabled/focus states explicit.
3. Recompose MainActivity: Bluetooth/version and firmware first; secondary logging/configuration under accessible disclosures; keep all three firmware formats and compatibility gates. Add one selected-seat segment and a directional pad with unchanged commands and stop semantics. Reuse the existing TabHost inside an inset capsule and handle system/cutout/keyboard insets centrally.
4. Recompose LivePanel with real received gear/speed/battery/freshness, compact metrics, details and readable CAN rows. Missing/old data remain visibly missing/old; never populate production sample values.
5. Build 0.7.0-test, run local model/resource and emulator native lifecycle/vehicle/queue/selector tests, then real DocumentsUI regression with synthetic input. Inspect the three portrait screens plus landscape and large-font layouts in one batch; make one correction batch if needed. Rebuild only after relevant changes.
6. Obtain a read-only review and retain exact verification receipts and screenshots. Deliver the local APK with explicit emulator versus physical-hardware boundaries. No push or hardware actuation is part of this UI task.
