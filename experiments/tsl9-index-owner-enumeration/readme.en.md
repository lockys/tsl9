# Offline data index and owner enumeration

[繁體中文](README.md)

For `0x1AB48+2*index`, enumerate all byte indices 0–255 and check whether each two-byte read lies within one current original-coordinate DATA owner. Seventy-six meet this address criterion, but only indices 0–3 belong to the dedicated counter window; 4–7 belong to another record-dispatch object, 8–11 to service-threshold data, and 12–75 to the reset initializer. Adjacent owner coverage does not establish table membership or runtime reachability.

For `0x1A078+16*mode+column`, enumerate 256 rows of 16 bytes: 149 rows fit entirely within one DATA owner; the other 107 cross owners, lack coverage or lie outside the image. The previously reported 164 rows had all bytes covered by some DATA owner, including rows spanning multiple owners. Neither metric establishes semantic table membership.

For `0x1A638+6*(2*channel+state)`, enumerate channel 0–3 and byte state 0–255: of 1,024 pairs, 20 fit the dedicated 48-byte window, 872 fall in another single DATA owner, 72 span owners or lack one complete owner, 8 touch excluded data, and 52 are partly or entirely outside the APP. Classification checks excluded ranges before image and owner bounds; it reads no data values. Multiple channel/state pairs among the 20 address the same location, so these are not 20 independent table entries or proven reachable states.

The exact address bounds follow from the formula, with six-byte reads and inclusive state ranges. Excluded-data overlap is calculated by address only; its contents are not read.

| Channel | Entirely in the 48-byte window | Overlaps the excluded four bytes | Partly or entirely outside the APP |
| --- | --- | --- | --- |
| 0 | 0–7 | 16–17 | 246–255 |
| 1 | 0–5 | 14–15 | 244–255 |
| 2 | 0–3 | 12–13 | 242–255 |
| 3 | 0–1 | 10–11 | 240–255 |

These are geometric ownership conditions, not proof that states above 1 are valid entries. For example, `(channel,state)=(0,2)` and `(1,0)` address the same location. No excluded or out-of-image combination is established to be reachable on hardware.

From the project root run `python experiments/tsl9-index-owner-enumeration/verify.py`. The checker reads only the pinned existing layout map, no firmware payload, and executes no target. It does not establish a global index bound, resolve the six dependencies, or prove physical or OTA compatibility.
