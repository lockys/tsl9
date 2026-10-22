# Independent reply-object and save-slot review

[繁體中文](readme.zh-TW.md)

The original530B and delivered568B functions share seven save locations: RA44,S040,S136,S232,S328,S424,S520. Their save order differs. The568B function additionally savesS6@16,S7@12,S8@8. Equal48B frame sizes do not establish identical memory effects.

Original reply bytes occupy liveSP+12/+13. The actual568B separate volatile two-byte object occupiesSP+6/+7. The final556B/188-instruction candidate retains a48B frame, removes theS8 save/reload pair and places its genuine object atSP+10/+11. SavedS7 still occupiesSP+12; no spill bytes are borrowed.

For common entrySPE, frameF and reply offsetR, original address isE−36. Numeric matching requiresR−F=−36, not a universal literalSP12 requirement. The568B offset is−42; the556B offset is−38. A larger frame could in principle use anotherR, but ownership, alignment, lifetimes, saves and callee contracts still need evidence.

Matching the pointer alone is insufficient. A saved wordA1B2C3D4 becomesA1B20105 if reply bytes05/01 overwrite its low half. A normal savedS7 reload then corrupts the caller. This is little-endian storage overlap algebra, not instruction execution. Borrowing a save area requires genuine independent backup/restoration evidence for applicable exits; it cannot be advertised as an independent C reply object.

Before original call14094, A3 comes from liveS2,A2 from liveS0,A0 from liveS1 andA1 retains command. At14098 the caller immediately restores RA/S0/S1/S2/S3 from its192B frame and returns. It neither testsA0 locally nor restoresS7. Failure to readS7 in this immediate continuation does not prove it dead farther up the call chain.

The UID comparator's length!=14 fastpath returns1 without a frame; the valid route has its own32B frame and16B builder frame. The bounded App body does not directly use the handler reply pointer as UID data, but opaque ROM/fresh frame reads remain. Original9D96 writes the second reply byte fromS1=1 beforeUID;9DA6 stores post-UID liveS1 into active. Ordinary compiler register allocation does not reconstruct that physical contract by itself.

The candidate's only source delta adds a post-quarter unsigned identity: HOST uint32 identity, native empty read/write-register asm. Header, full8 opaque bridges, memory clobbers and provider effect order are unchanged. No third profile or HOST rerun occurred. The12B net gain and removed save pair are actual codegen evidence, not proof of numeric-pointer or fullABI compatibility.

Read-only evidence includes four existingD/P C/C++568B objects, both final556B candidates,169 original handler operands,24B caller and122B UID source. Two actual-ELF controls reject forcing the reply into savedS7 and reloadingS7 from a wrong slot. The intermediate560B source hypothesis is historical, not current.

```sh
python -B frame-review/check.py --project-root ROOT
python -B frame-review/review.py --project-root ROOT --firmware FW --folder MODE --receipt NEW.json --controls
python -B frame-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

Default checks validate sealed metadata/source deltas only. Actual mode requires explicit firmware/folder and a create-only receipt; replay is read-only without recreating controls. No link, newBIN, CPU/ISA execution or hardware test occurred. The556B candidate is not integrated into the existing wired image. Full frame lifetimes, physical S/SP/GP/RA, unknown callbacks, aliasing, IRQ/fault and OTA remain unproved.
