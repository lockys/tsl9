# Offline record-dispatch reconstruction
[繁體中文](readme.zh-TW.md)

Adds two selected C/C++ units under `src/`:102B/35i record dispatcher12A08 and42B/15i predicate821E. The predicate compiles from C arithmetic plus empty register ports and matches all42 original V4.1.60 bytes. The dispatcher retains private architectural frame/control ports,74 whole noncontrol bytes and689 original bits.

Three existing formal objects are actually partially linked into950B/330i/42 genuine FUNCs, binding12A08,81AA and821E. C/C++ ELF outputs are identical;50 pending RELAs and six external providers remain. This is neither an executable image nor a flashable BIN. See [summary.json](summary.json) and the [independent raw ELF review](final-root-review.json).

Verification includes212 dispatcher,65 predicate and25 actual-join negatives per language plus fresh complete upstream receipt replays.59 C/H files/33 native TUs pass66 comparisons/132 objects; all prior62 results and373 artifacts remain identical. Both languages' strict firmware gates exit1 after bounded PASS. No target/ISA/MMIO/hardware execution or network API calls.

[Publication provenance](publication-provenance.json) records four exact portable originals and three explicit path-only derivatives. Derivatives retain original hashes/sizes/local relative paths and pass inverse complete JSON equality; original bytes/replay are not claimed. Raw receipts remain local, including `build/record-original-receipts-20261023.zip`. Check:
```sh
python scripts/check-record-publication.py
python scripts/anonymize_public_evidence.py --check
```

The initial failed predicate verifier was not archived; source history states this limitation. The known pre-root-repair verifier and failed outputs are preserved. Only interpreter-path normalization changed; a different actual Python executable hash correctly rejects replay.

Next is the [212B/72i peripheral-write provider18CA4](next-peripheral.en.md). A three-bank transmit-interface interpretation remains inference. CAN identity, seat/DND semantics, full ABI and OTA compatibility remain unproved. [Feature candidates](feature-candidates.en.md) remain diagnostic requirements rather than unverified vehicle controls.
