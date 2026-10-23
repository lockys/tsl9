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
    padding: "4dp 5dp"
  navigation-selected:
    backgroundColor: "{colors.selected-sage}"
    textColor: "{colors.forest-teal}"
    typography: "{typography.caption}"
    rounded: "{rounded.capsule}"
  navigation-inactive:
    textColor: "{colors.muted}"
    typography: "{typography.caption}"
    rounded: "{rounded.capsule}"
---

# Design System: TSL9 Hardware Tools

## Overview

**Creative North Star: "Concept02 — forest-teal native utility"**

The implemented identity pairs a warm light canvas with restrained forest teal, white containers and a floating capsule navigation bar. It is a native Android utility: controls, language handling and diagnostic text remain familiar, while shared surfaces and line icons connect the three destinations.

This record describes the current `0.7.0-test` source, not the previously published release. The implementation is the authority where the concept image or earlier screenshots differ. It does not establish physical-device, vehicle or hardware verification.

**Key Characteristics:**

- One action accent, with sage selection and explicit muted disabled states.
- Scrollable single-column pages with paired controls and metric tiles.
- Persistent connection context and three labeled icon destinations.
- Advanced content behind explicit disclosures; native confirmations remain visible when invoked.

Source authority: [AppUi.java](app/src/main/java/com/lockys/tsl9updater/AppUi.java), [MainActivity.java](app/src/main/java/com/lockys/tsl9updater/MainActivity.java), [LivePanel.java](app/src/main/java/com/lockys/tsl9updater/LivePanel.java), and the theme files under `app/src/main/res/values*/styles.xml`. [PRODUCT.md](PRODUCT.md) records the approved concept and product constraints; [UI-REDESIGN.md](UI-REDESIGN.md) records implementation scope.

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
- **Caption:** navigation labels and metric field labels.
- **Metric:** prominent received values, using tabular figures where requested.
- **Diagnostic:** selectable logs. CAN stream text also uses monospace at the supporting size.

The ramp is functional rather than a fixed mathematical ratio. `AppUi.text()` requests tabular numerals and includes a small vertical text inset. Headers replace this inset with section-specific spacing. Do not force a fixed text height or truncate prose to imitate a screenshot.

## Layout

All three destinations use a vertical `ScrollView` with a fill-viewport body. Shared page padding uses the page-horizontal and page-bottom tokens, with a compact top inset (10dp). The common header sits above the changing page and contains the TSL9 wordmark, connection text and language disclosure button.

Paired controls share available width equally. Each contributes a half-gap toward the adjacent item, making a central gap (10dp). Live metric tiles use the same two-column arrangement and independent content heights; the implementation does not equalize tiles or switch to a desktop grid.

The bottom capsule occupies its own layout row below the scrolling content. It has horizontal page margins, a small top margin (6dp) and bottom breathing room (12dp). Each destination is at least 64dp high, with labels allowed two lines. Window insets are applied to the outer tab body.

The layout remains a scrollable single column in landscape and at larger font settings; no application breakpoint or alternative landscape composition is defined. Let native text measurement and scrolling carry expanded content.

**The Reachable Detail Rule.** Reduce initial density with explicit disclosure controls while retaining the detailed content, diagnostics, firmware format options and exports in the same destination.

## Elevation & Depth

Cards and buttons are flat. White surfaces, pale selection fills and thin boundaries provide most separation. The navigation capsule alone has Android elevation (5dp), giving the persistent destination switcher a slight lift. Buttons explicitly clear elevation and the platform state-list animator.

Primary and secondary buttons use a native teal ripple with alpha `0x25`; navigation uses a quieter ripple with alpha `0x19`. These are Android `RippleDrawable` states, not a custom hover or timed motion system. Native dialogs, fields, spinners and checkboxes retain platform behavior.

**The Navigation Lift Rule.** Preserve the navigation capsule's hierarchy without adding shadows to ordinary cards or actions.

## Shapes

Use gently rounded control surfaces, slightly rounder content containers and a fully rounded navigation capsule. The capsule token is the implementation's large-radius sentinel; effective rounding is limited by the view's dimensions.

Cards and secondary actions carry a thin boundary (1dp). Primary, disabled and selected fills have no added outline in the shared drawable. Selection is sage rather than a heavier border. Shared icons are custom geometric strokes with rounded caps and joins, drawn on a 24-unit coordinate grid with stroke width (1.7 units). Inline icons are normally 22dp; navigation icons are 23dp; directional controls use 24dp icons. Use these drawn icons instead of substituting emoji or typographic symbols.

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
