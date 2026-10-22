# TX whole-image implementation evidence

[繁體中文](readme.zh-TW.md)

The formal entry is `verify_image.py`, also exposed through the model's `verify.py` and POSIX `verify.sh`. It freshly compiles 46 units, explicitly orders reply/TX/IRQ-quarter ABI words, partially links the source providers, checks real missing-ROM rejection, links a numeric ROM address witness and exports a new offline image. Original firmware is validation only.

`prototype.py` is a pinned generation substage used by the formal producer. Its standalone `passed` means provisional checks, not formal admission. `tx_order.py` drives the immutable ten-existing-word transform/policy in the new output namespace; it changes no old tool and generates no opcode. `prepare_manifest.py` authors the ledger only.

```sh
python -B PATH/verify_image.py --project-root ROOT --tool-dir LLVM --language both
python -B PATH/verify_image.py --project-root ROOT --replay RECEIPT
```

Builds emit `BUILD/{c,cpp}/verification.json`; stdout lists receipt/hash and image/hash per language. Default UUID and explicit model/build output roots are create-only. Replay forbids build options. An explicit `--firmware` works in both modes for byte-identical original validation data.

Formal replay binds the complete artifact set, all 67 exact chronological recipes, parent generator/resource-query recipes and logs/exits, source/tool stability, 45 MD target/primary/include associations, observed compiler resource header, three pre/post ABI stages, all ELF metadata/provider/RELA roles and section/LOAD/BIN coverage. Seventeen actual ELF/relocation/image byte countercases and seven dependency/recipe/scheduling evidence controls must reject. Independent source and ABI reviews use their own oracles.

Actual inventory: thirteen regions/930 bytes and fifteen real FUNC providers; 691 allocations/678 retained sections; 8,246 outside RELA plus twelve prior typed JALs and three TX records, totaling 8,261; 53 canonical bindings; 29 outside incoming references; fifteen LOADs. The original canonical FUNC280 is explicitly replaced by real FUNC8, LOCAL270 and GLOBAL2. Seven retired control labels and one PCREL anchor are distinct obligations.

C and C++ images are identical: SHA256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. All 93 changed bytes are inside TX280. Numeric ROM witness linking proves no physical ROM, hardware, flashing or OTA behavior. Full ABI, computed targets, fault/interrupt observations remain unproved.

`check.py` defaults to source/metadata only. Explicit `--receipt` replays actual artifacts; `--require-local-builds` requests retained selected local archives. Published selected JSON metadata does not include generated objects, ELF, IR or complete build/log archives. The experimental BIN is a separate, explicitly labeled artifact.
