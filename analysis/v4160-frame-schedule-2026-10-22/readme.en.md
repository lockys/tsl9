# Explicit ABI save order and replayable object transformation

[繁體中文](README.md)

This step restores the original stack-save order of two C/C++ functions. The tool and declarative policy are in the [standalone model](../../experiments/tsl9-v4160-frame-schedule/README.md). The final object explicitly combines compiler output and ABI save scheduling; it is not claimed as compiler-only output, complete source recovery or flashable firmware.

Parent verification transforms the previous milestone's actual C/C++ compiler objects. Each changes only 14 bytes; replay rereads both objects, metadata, symbols and all RELA. Seven actual receipt/output tamper controls per language are rejected. This standalone check performs no fresh C/C++ compilation and does not replace the new full-image compilation chain.

The independent ABI audit is published under [frame-pass-review](../v4160-flash-register-prefix-2026-10-22/ABI-review/frame-pass-review/). It separately checks actual objects, original save instructions, full-image witness links, entries and malformed controls. Each receipt's exact tool/input identities remain authoritative; early diagnostic receipts are not presented as current passing evidence.

```sh
python3 -B analysis/v4160-frame-schedule-2026-10-22/implementation/check.py --project-root /absolute/project
```

The default checks published source/evidence identities and **does not replay local actual objects**. Add `--actual-verification /absolute/project/path/verification.json` to explicitly reread actual project-local objects and controls. Unrecorded interior entries, resident ROM, physical interrupt/fault behavior and BLE OTA remain outside this evidence.

Independent `build/` compiler archives are retained in the local delivery and excluded from GitHub; their original seal is unchanged. This checker explicitly reports missing archive-member counts. Source/metadata checks are not complete independent artifact replay. Run the independent review's original `check_seal.py` in the complete local delivery for full archive replay; the new full-image pipeline separately reviews its actual freshly compiled objects.
