# OTA page reply implementation and verification

[繁體中文](README.md)

This scope provides readable C11/C++17 for9B8E..9C0A, a named synthetic HOST provider and actual native compilation/link verification. `../source-review/` independently establishes the original124-byte/50-instruction contract; `../ABI-review/` and `../code-review/` independently review native artifacts and HOST effects.

Both compiler outputs contain124 bytes/50 instructions with two ABI-order windows different. The pipeline retains `page_reply.o` and IR, executes project-local `reply-abi-order/order.py`, then retains `source-ordered.o` and `ABI-order.json`. It only permutes freshly compiled words:28 bytes change; ELF metadata, symbols and the sole TX relocation stay unchanged. Original BIN bytes are not code-generation inputs. After ordering, the component linked at9B8E equals all124 original bytes.

Strict linking must reject the missing TX provider. Successful `ADDRESS-WITNESS-ONLY.elf` uses numeric8A56 without supplying that280-byte provider. There is no new whole image, BIN, ROM implementation or flashability claim.

## Commands

```sh
python -B experiments/tsl9-v4160-ota-page-reply/verify_host.py --project-root . --language both
python -B experiments/tsl9-v4160-ota-page-reply/verify_native.py --project-root . --tool-dir "$LLVM" --language both
```

Shell wrappers and create-only project-local `--build-root` are available. Both `--replay RECEIPT` paths only recheck actual artifacts. Native exports `context(root)`, `static_checks(ctx,folder)`, `replay(root,receipt)`; HOST exports `replay(root,receipt)`. Native metadata contains `checks`,6 actual pipeline commands,11 raw/IR controls,3 actual compiled mutants and artifact hashes. HOST contains exact3/87/3634 counters,6 actual compiled mutants and pre/post host-machine checks on every launch.

`results.json` indexes four selected receipts; `receipts/` keeps byte-identical metadata. Generated artifacts/logs remain only in ignored model `build/`. Default `check.py --project-root ROOT` checks sealed members/current inputs only; it does not claim a new compile/run or access to unpublished archives. `--archives` reopens the four actual local archives. `--host-receipt` / `--native-receipt` accepts fresh receipts generated under another root.

Returned READ/WRITE callbacks cannot alter registers. Only named opaque calls allow arbitrary GPR/SP/frame changes. Unknown/nonreturn stops preserve committed effects without invented cleanup or normalized success. Raw and JALR-masked targets/links are separate. Broad HOST mutation coverage is not a native unknown-callee/SP ABI proof. Guard code supports PE/ELF/thin Mach-O, with Windows actually tested; fat/universal macOS Python is unsupported.

Ordered byte identity, conditional native C ABI and synthetic HOST results remain separate. Computed interior entries, resident ABI, async/fault effects, hardware and OTA remain unverified. No RV32 execution, ISA emulation, network or device I/O occurs.
