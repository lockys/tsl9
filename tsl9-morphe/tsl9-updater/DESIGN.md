---
name: TSL9 Hardware Tools
description: Native Android hardware utility in warm light surfaces and forest teal.
colors:
  forest-teal: "#205C50"
  warm-background: "#F7F8F5"
  ink: "#202A27"
  muted: "#59655F"
  boundary: "#D4DED8"
  selected-sage: "#E1EFE9"
  white: "#FFFFFF"
  disabled-surface: "#E7ECE8"
  disabled-text: "#69756E"
  unknown-amber: "#956000"
typography:
  headline:
    fontFamily: "sans-serif-medium"
    fontSize: "27sp"
    fontWeight: 500
  title:
    fontFamily: "sans-serif-medium"
    fontSize: "19sp"
    fontWeight: 500
  body:
    fontFamily: "sans"
    fontSize: "14sp"
    fontWeight: 400
    fontFeature: "tnum"
  supporting:
    fontFamily: "sans"
    fontSize: "13sp"
    fontWeight: 400
    fontFeature: "tnum"
  label:
    fontFamily: "sans-serif-medium"
    fontSize: "15sp"
    fontWeight: 500
  caption:
    fontFamily: "sans"
    fontSize: "12sp"
    fontWeight: 400
    fontFeature: "tnum"
  navigation-label:
    fontFamily: "sans"
    fontSize: "11sp"
    fontWeight: 400
  metric:
    fontFamily: "sans-serif-medium"
    fontSize: "28sp"
    fontWeight: 500
    fontFeature: "tnum"
  diagnostic:
    fontFamily: "monospace"
    fontSize: "12sp"
    fontWeight: 400
rounded:
  control: "14dp"
  container: "16dp"
  capsule: "999dp"
spacing:
  text-inset: "4dp"
  half-gap: "5dp"
  small: "8dp"
  control-vertical: "10dp"
  container-vertical: "12dp"
  control-horizontal: "14dp"
  page-horizontal: "20dp"
  page-bottom: "24dp"
components:
  button-primary:
    backgroundColor: "{colors.forest-teal}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10dp 14dp"
  button-secondary:
    backgroundColor: "{colors.white}"
    textColor: "{colors.forest-teal}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10dp 14dp"
  button-disabled:
    backgroundColor: "{colors.disabled-surface}"
    textColor: "{colors.disabled-text}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10dp 14dp"
  selected-control:
    backgroundColor: "{colors.selected-sage}"
    textColor: "{colors.forest-teal}"
    rounded: "{rounded.control}"
  card:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.container}"
    padding: "12dp 14dp"
  navigation:
    backgroundColor: "{colors.white}"
    rounded: "{rounded.capsule}"
    padding: "3dp"
    width: "52% of safe viewport; max 360dp; expand for accessible labels"
    aspect: "approximately 4:1 at default font size"
    minTarget: "48dp x 48dp per destination"
  navigation-selected:
    backgroundColor: "{colors.selected-sage}"
    textColor: "{colors.forest-teal}"
    typography: "{typography.navigation-label}"
    rounded: "{rounded.capsule}"
  navigation-inactive:
    textColor: "{colors.muted}"
    typography: "{typography.navigation-label}"
    rounded: "{rounded.capsule}"
---

# Design System: TSL9 Hardware Tools

## Overview

**Creative North Star: "Concept02 — forest-teal native utility"**

The implemented identity pairs a warm light canvas with restrained forest teal, white containers and a floating capsule navigation bar. It is a native Android utility: controls, language handling and diagnostic text remain familiar, while shared surfaces and line icons connect the four destinations.

This record describes the current `0.7.5-test` source, not the previously published release. The implementation is the authority where the concept image or earlier screenshots differ. It does not establish physical-device, vehicle or hardware verification.

**Key Characteristics:**

- One action accent, with sage selection and explicit muted disabled states.
- Scrollable single-column pages with paired controls and metric tiles.
- Persistent connection context and four labeled icon destinations.
- Advanced content behind explicit disclosures; native confirmations remain visible when invoked.

Source authority: [AppUi.java](app/src/main/java/dev/tsl9/morphe/AppUi.java), [MainActivity.java](app/src/main/java/dev/tsl9/morphe/MainActivity.java), [LivePanel.java](app/src/main/java/dev/tsl9/morphe/LivePanel.java), and the theme files under `app/src/main/res/values*/styles.xml`. [PRODUCT.md](PRODUCT.md) records the approved concept and product constraints; [UI-REDESIGN.md](UI-REDESIGN.md) records implementation scope.

## Colors

The palette is a quiet green-tinted neutral family, with a dark forest accent and a separate amber uncertainty signal. Frontmatter values are normative.

### Primary

- **Forest teal:** enabled primary actions, secondary action text, selected navigation and connected/status accents.
- **Selected sage:** selected seat selector, expanded disclosure and selected destination surfaces.

### Neutral

- **Warm background:** page canvas, status bar and modern system-navigation bar.
- **White:** cards, secondary controls and the navigation capsule.
- **Ink:** page/section headings and primary content.
- **Muted:** supporting copy, inactive navigation, unavailable/stale metric values and inactive icon state.
- **Boundary:** thin card and secondary-control outlines.
- **Disabled surface / disabled text:** explicit disabled control treatment independent of primary/secondary intent.

Amber is a semantic exception for a received but unknown gear value; it is not a decorative secondary accent.

**The State Has Two Channels Rule.** Selection and availability use both text/icon treatment and surface treatment. Do not make a control appear enabled by accent color alone.

**The Unknown Stays Unknown Rule.** Keep unknown, absent and stale data distinguishable through the implemented labels, dashes and muted/amber treatment. Never fill the interface with demonstration readings.

## Typography

**Body Font:** Android `sans`.
**Heading and Control Font:** Android `sans-serif-medium`.
**Diagnostic Font:** Android monospace.

These names describe the current native implementation; platform font resolution and fallback handle Traditional Chinese, Simplified Chinese and English. Type sizes use Android `sp`, geometry uses `dp`; CSS pixel sizes in the sidecar are schematic previews at baseline scale. Line heights and letter spacing are platform defaults, not custom tokens.

### Hierarchy

- **Headline:** destination title, using the headline role.
- **Title:** reusable section heading, using the title role.
- **Body:** descriptions, connection/readiness text and detailed vehicle data.
- **Supporting:** help, summary and file/version metadata.
- **Label:** sentence-case action labels, with all-caps transformation disabled.
- **Caption:** metric field labels.
- **Navigation label:** short, single-line destination text in the compact pill.
- **Metric:** prominent received values, using tabular figures where requested.
- **Diagnostic:** selectable logs. CAN stream text also uses monospace at the supporting size.

The ramp is functional rather than a fixed mathematical ratio. `AppUi.text()` requests tabular numerals and includes a small vertical text inset. Headers replace this inset with section-specific spacing. Do not force a fixed text height or truncate prose to imitate a screenshot.

## Layout

All four destinations use a vertical `ScrollView` with a fill-viewport body. Shared page padding uses the page-horizontal and page-bottom tokens, with a compact top inset (10dp). The common header sits above the changing page and contains the TSL9 wordmark, connection text and language disclosure button.

Paired controls share available width equally. Each contributes a half-gap toward the adjacent item, making a central gap (10dp). Live metric tiles use the same two-column arrangement and independent content heights; the implementation does not equalize tiles or switch to a desktop grid.

The bottom capsule occupies its own centered layout row below the scrolling content. Its nominal width is 52% of the safe viewport, capped at 360dp; it retains at least 16dp of side clearance, a small top margin (6dp), and bottom breathing room (12dp). Each destination is at least 48dp square. Window insets are applied to the outer tab body. See the compact pill pattern below for accessibility expansion.

### Compact centered pill navigation — pinned reference

**Lifecycle invariant:** the compact geometry and short labels must survive tab changes, background/foreground transitions, document-picker return, Activity recreation, orientation changes and language changes. Verify the actual drawn bounds after each transition, including the return to portrait; a launch screenshot alone does not establish this contract. Large-font expansion remains allowed when required to fit accessible labels.

The user's dialer screenshot `11138.jpg` is the proportion authority for this component. Visual estimates: image width 858px, capsule about 450px wide and 110px high, giving approximately 52% viewport width and 4.1:1 width/height. These are reference proportions, not physical-device dp measurements. Preserve the App's light/forest-teal palette; the reference pins geometry and hierarchy.

- **Outer silhouette:** a compact capsule centered above the system gesture area, with visibly generous empty space on both sides. Do not stretch it across almost the full screen merely because its corners are round.
- **Four equal destinations:** each gets one third of the usable inner width, a 20dp line icon above a short 11sp single-line label, a 2dp icon/label gap, and at least a 48dp square touch region. Inner shell padding is 3dp; normal shell height is approximately 54dp.
- **Selection:** a filled inner pill occupies one slot and almost the full inner height. Keep a 3dp shell rim. Retain sage fill and teal content for the selected destination, muted content for the others, and native ripple/focus feedback.
- **Copy:** compact labels are localized separately (Update / Controls / Live; 更新 / 車控 / 即時). Accessibility descriptions retain the full destination names, including Bluetooth / Update and Car controls. Page headings retain their original full copy.
- **Sizing:** at normal font size, target `width = 0.52 × safeViewportWidth` and an aspect near 4:1. At large fonts or with longer translations, measure the actual label and expand all three slots equally before compromising readability. Minimum target size, readable labels and system insets take priority over the nominal ratio. Do not shrink text or clip it to preserve the screenshot shape. In wide windows cap the nominal width at 360dp; labels may require a larger accessible width within the safe viewport.
- **Behavior:** selecting a destination updates its active inner pill. Preserve native tab semantics, existing destinations, state, lifecycle behavior and the stop-seat request when leaving car controls. No navigation animation may delay a stop request.
- **Verification:** inspect the three actual App pages together at default font size, landscape and 200% text. Check horizontal centering, normal width/aspect, one-line labels, equal slots, 48dp targets, selected/inactive contrast, and full accessibility names. Screenshots must show real empty/disconnected states when no hardware is connected.

Implementation authority: `AppUi.PillNavigation`, `AppUi.tab`, and `MainActivity`'s localized tab indicators. The same pattern is stored in `.impeccable/design.json` under `extensions.navigationPattern`; future App navigation changes must follow both records.

The layout remains a scrollable single column in landscape and at larger font settings; no application breakpoint or alternative landscape composition is defined. Let native text measurement and scrolling carry expanded content.

**The Reachable Detail Rule.** Reduce initial density with explicit disclosure controls while retaining the detailed content, diagnostics, firmware format options and exports in the same destination.

## Elevation & Depth

Cards and buttons are flat. White surfaces, pale selection fills and thin boundaries provide most separation. The navigation capsule alone has Android elevation (5dp), giving the persistent destination switcher a slight lift. Buttons explicitly clear elevation and the platform state-list animator.

Primary and secondary buttons use a native teal ripple with alpha `0x25`; navigation uses a quieter ripple with alpha `0x19`. These are Android `RippleDrawable` states, not a custom hover or timed motion system. Native dialogs, fields, spinners and checkboxes retain platform behavior.

**The Navigation Lift Rule.** Preserve the navigation capsule's hierarchy without adding shadows to ordinary cards or actions.

## Shapes

Use gently rounded control surfaces, slightly rounder content containers and a fully rounded navigation capsule. The capsule token is the implementation's large-radius sentinel; effective rounding is limited by the view's dimensions.

Cards and secondary actions carry a thin boundary (1dp). Primary, disabled and selected fills have no added outline in the shared drawable. Selection is sage rather than a heavier border. Shared icons are custom geometric strokes with rounded caps and joins, drawn on a 24-unit coordinate grid with stroke width (1.7 units). Inline icons are normally 22dp; navigation icons are 20dp; directional controls use 24dp icons. Use these drawn icons instead of substituting emoji or typographic symbols.

## Components

### Buttons

Solid forest-teal primary actions and outlined white secondary actions share the control radius, label role and padding tokens. Standard buttons have a minimum height (52dp), no forced minimum width and vertical margins (5dp). Disabled state takes precedence over selection and intent. Keep the native ripple; no separate application hover/focus style is defined.

### Cards / Containers

White, thinly outlined containers use the container radius and padding tokens. The connection card and live metric tiles share this primitive. Containers do not acquire elevation for emphasis.

### Inputs / Fields

Text fields, spinners, checkboxes, progress bars and alert dialogs retain `Theme.Material.Light.NoActionBar` styling with the forest accent. Fields and spinners have explicit minimum targets of 48dp or 52dp according to their existing use. They have no custom field radius, border or error-surface token. Preserve the native focus and validation presentation.

### Navigation

Three labeled geometric icons sit inside an inset white capsule: Bluetooth/updates, car controls and live data. The selected destination has a sage capsule and forest-teal text/icon; inactive destinations use muted text/icon and a transparent fill. Labels remain present alongside icon accessibility descriptions. There is no horizontal tab strip underline.

The status bar follows the warm canvas. The base theme uses dark ink for the system-navigation bar; API26 overrides it to the light canvas, and API27 additionally declares light-navigation-bar styling. The activity applies the corresponding dark-icon flag on API26+. These are compatibility treatments, not additional app palette variants.

### Disclosure Rows

An outlined secondary button with a leading geometric chevron toggles a following detail column. Closed details are `GONE`; expanded headers use the selected sage surface. The header label remains explicit. The chevron is not animated or rotated by the shared helper.

### Seat Selection and Directional Pad

Two equal-width selectors choose driver or passenger. Only the selected seat's pad is visible. Four labeled-for-accessibility arrow buttons form a three-by-three spatial cross around a decorative seat icon. Cells have equal width and fixed height (48dp), with horizontal/vertical margins (4dp/2dp). The visual arrows are drawn icons; the glyph strings in code supply content descriptions.

The pad represents press-and-hold movement with release/cancel/exit stop handling; a separate stop action stays in the content flow. Selecting another seat requests stop before changing the pad. Preserve these semantics when changing visual presentation.

### Live Metrics and Diagnostic Stream

Four white tiles show gear, raw speed, battery percentage and reply age. Missing values use dashes. Stale speed, battery and age are muted; unknown received gear is amber. Field meanings and full vehicle detail remain accessible below the summary. CAN rows use selectable monospace, with byte visibility explicitly controlled.

### Vehicle Illustration

`app/src/main/res/drawable-nodpi/vehicle_profile.png` is a decorative generated sedan profile, fitted centrally into a compact image area (88dp high). It is excluded from accessibility reading order. Its appearance does not indicate connection, verified hardware identity or live vehicle state.

## Do's and Don'ts

### Do:

- **Do** reuse the shared `AppUi` colors, surfaces, button states and line icons.
- **Do** preserve explicit unknown/stale labels and native enabled/disabled state.
- **Do** retain labeled destinations, accessible icon controls and native font scaling.
- **Do** keep advanced information reachable through named disclosures.
- **Do** use `sp` for text and `dp` for geometry in the native implementation.

### Don't:

- **Don't** replace received-data placeholders with sample values.
- **Don't** add elevated cards or button shadows to the flat content surfaces.
- **Don't** substitute emoji or text glyphs for the implemented geometric icons.
- **Don't** hide confirmation, stop or cancellation behavior to simplify a screen.
- **Don't** infer a custom field, dialog, motion or responsive token from platform defaults.

Not canonized: the system-font destination headline is recorded as an implementation fact, not a reusable display-face identity; isolated wordmark sizes and the reply-age size override are not new type roles. Earlier screenshot geometry is superseded by the current source. Sidecar component previews are schematic HTML equivalents, not Android runtime evidence.


## Settings destination

The user selected a fourth bottom destination, Settings, on 2026-10-27. Keep the existing centered capsule, with four equal icon/label slots. Nominal width remains 52% of the safe viewport, expanding only when four 48dp targets or scaled labels require it; retain the 360dp nominal cap and side clearance. Settings is a normal scrollable page in the same Activity, preserving the shared BLE session.

Group language first, module and local password management second, then advanced update options and diagnostics. Keep bin selection, compatibility confirmation, update/cancel and version queries in the update workflow. Lighting feature settings remain with car controls. Show saved-password presence without the password value; forgetting clears the local encrypted copy without changing hardware credentials or the current authentication session. English, Simplified Chinese and Traditional Chinese share this structure.
