# Offline data index and owner enumeration

[繁體中文](README.md)

For `0x1AB48+2*index`, enumerate all byte indices 0–255 and check whether each two-byte read lies within one current original-coordinate DATA owner. Seventy-six meet this address criterion, but only indices 0–3 belong to the dedicated counter window; 4–7 belong to another record-dispatch object, 8–11 to service-threshold data, and 12–75 to the reset initializer. Adjacent owner coverage does not establish table membership or runtime reachability.

For `0x1A078+16*mode+column`, enumerate 256 rows of 16 bytes: 149 rows fit entirely within one DATA owner; the other 107 cross owners, lack coverage or lie outside the image. The previously reported 164 rows had all bytes covered by some DATA owner, including rows spanning multiple owners. Neither metric establishes semantic table membership.

From the project root run `python experiments/tsl9-index-owner-enumeration/verify.py`. The checker reads only the pinned existing layout map, no firmware payload, and executes no target. It does not establish a global index bound, resolve the six dependencies, or prove physical or OTA compatibility.
