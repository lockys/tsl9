# Native UI 0.7.0-test

Implements the approved concept02 with native Android views: forest teal on a warm light surface, consistent stateful controls, an inset pill TabWidget with line icons, shared language/connection header, and structured Bluetooth/firmware/diagnostic sections.

The car page uses one selected driver/passenger segment and a directional pad. Its existing command mapping and one-second/release/cancel stop behavior are retained. Changing the selected seat requests stop before changing the visible pad. The live page adds received-data metric tiles; complete details, field meanings, CAN bytes opt-in and exports remain available. No example/mockup data is used as live data. Invalid/cleared status or a reset CAN count bypasses the normal display throttle so previously displayed data clears immediately.

Long descriptions and advanced controls use explicit disclosure rows. Firmware formats, compatibility confirmation, module password verification, full lighting configuration checks and all logging/export paths remain available. Header language selection stays disabled during an active connection or job as before.

Native geometry tests assert accessible icon tabs, 48dp targets, visible capsule margins, destination switching and language disclosure. Existing tests exercise direct lock/unlock, seat release/cancel/switch stop, production queue guards, malformed/changed identity, lighting readback, data clearing and lifecycle behavior. The old UI was observed failing the new inset-navigation assertion before implementation.

Visual inspection covers all three phone pages, landscape, and 200% font scaling. API23–25 use a dark system-navigation fallback; API26 uses the existing dark-icon flag with a light bar, and API27+ also declares the matching theme attribute. Legacy-device runtime verification remains outstanding.

The vehicle profile is an AI-generated illustrative asset, not a verified rendering of hardware or vehicle state. It was generated with the built-in image tool from this prompt direction: transparent-background, logo-free side elevation of a compact electric sedan; restrained forest-teal contours and light body fill for a 320dp utility-app illustration. Source asset: `app/src/main/res/drawable-nodpi/vehicle_profile.png`.

The initial UI redesign shipped as `0.7.0-test`. Version `0.7.1-test` retains this UI and adds neutral Android identity and portable local tool discovery; see [PORTABILITY.md](PORTABILITY.md). Historical releases and their verification receipts retain the original binaries.
