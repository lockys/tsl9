# TSL9 Hardware Tools

Native Android companion for the user's TSL9 module and late-2021 Model 3. The user connects their own BLE module, selects a compatible local APP firmware bin, operates supported lock/seat controls, and inspects received module/CAN data. The product is an experimental local tool with no INTERNET permission or bundled firmware.

Platform: Android Java views, minimum API23, target36. Visitor mode: Operate. User-facing locales: English, Simplified Chinese, Traditional Chinese; system-language selection remains supported.

Four destinations share one BLE connection: Bluetooth/updates, car controls, live data, and settings. Preserve existing OTA, authentication, cancellation and lifecycle behavior. User explicitly permits lock/seat operations without a profile checkbox or readable gear; unknown stays unknown. Lighting remains independently gated. CAN reception is read-only and unknown IDs remain undecoded. Local callbacks and synthetic tests do not prove physical vehicle execution.

Approved visual direction: concept02, light warm surfaces, forest teal, native accessible controls, floating pill bottom navigation. Firmware writing remains an explicit confirmation flow; all three supported file formats and diagnostic/export capabilities stay available. Mock values are not production defaults.


Settings is the fourth bottom destination selected by the user. It gathers language, module/password management, advanced OTA options and diagnostic tools in the existing Activity. The update page retains file selection, compatibility confirmation and update/cancel actions. Keep the compact capsule centered with four equal accessible slots; expand only when labels or 48dp targets require it.
