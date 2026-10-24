# Navigation lifecycle investigation

User report: the capsule looks correct on first launch, then returns to nearly full width. The supplied image also contains the longer destination labels. Do not assume that the image establishes the installed APK version or that a launch screenshot proves persistence.

`0.7.3-nav-debug` adds local `UI_NAV` records when the measured navigation geometry changes. Records include the installed package/version, Android API, window/safe widths, bar width/height, font scale, density and navigation labels. They contain no Bluetooth address, vehicle identity or firmware contents. The existing debug export includes these records. Startup records now use the installed version instead of the obsolete literal `v0.7.0-test`.

This is an investigation build, **not a verified fix for the reported hardware symptom**. The navigation sizing implementation and vehicle/firmware commands are unchanged.

## Reproduce on an emulator

Build with `./build.ps1`, install both generated APKs on a dedicated emulator, then run:

```powershell
adb -s <emulator-serial> shell am instrument -w -e locale zh-Hant -e navigation true dev.tsl9.morphe.test.test/dev.tsl9.morphe.SmokeInstrumentation
```

Repeat with `en` and `zh-Hans`. Add `-e switches true -e locale system` to exercise actual application language changes first. The test observes real drawn frames, confirms focus leaves and returns, and waits for actual orientation changes. It measures first launch, nine tab changes, three background returns, system document-picker cancellation/return, three Activity recreations, landscape and the return to portrait. It checks centered geometry, localized label fit and 48dp touch targets. No Bluetooth is scanned or connected.

## Physical-device evidence still needed

Install this diagnostic version over `dev.tsl9.morphe.test`, reproduce the transition to full width, and use the existing debug-log export. The last `UI_NAV` lines and the immediately preceding action distinguish geometry changes from font expansion, app-version confusion or a device-specific transition. A result from the emulator must not be presented as reproduction or resolution on the user's phone.
