# Curated integration of remaining CODE

[繁體中文](README.md)

Ten candidate bodies now have curated backing in [`src/native/runtime/safe_gap_functions.c`](../../src/native/runtime/safe_gap_functions.c), adding **764B / 288 instructions**. All158 preceding C/H files,248 CODE results and1489 artifact records remain unchanged.

| Evidence scope | Actual result |
|---|---|
| Complete source | 159 C/H files;125 CODE＋8 DATA units;266 comparisons /532 objects |
| Original addresses | 69,412B CODE＋3,962B DATA＝73,374/76,800B; **95.54% byte coverage** |
| Real backing | 6182 positive FUNC,56 DATA OBJECTs,71 CODE aliases and6 DATA labels |
| References / flow | 5270 relocation roles;23602 instructions,4619 direct transfers,1432 normal return positions and13 guarded dispatch tables |
| Native objects / ELF | Identical C11/C++17 results;independent ELF readers agree;no ABS FUNC,entry=0,no PT_LOAD |

See the [summary](summary.json) and [hashed evidence](evidence.json). All17 new standalone compiler dependencies bind to existing positive FUNC providers. The same six original UND remain explicit,with an additional unbounded static DATA dependency outside that count.

The new bodies retain three opaque ROM indirect calls and four indirect tails. The full922 indirect-transfer records **include RET**;they are not all unknown calls. Owned sequential and return positions do not prove a whole runtime CFG or reachability. Physical invocation of the new candidates remains unproved.

**Byte coverage is not feature completion or flash readiness.** Physical MCU,ROM/RAM/IRQ,startup,OTA and rebooted features remain unverified. No BIN,target/emulator execution,hardware access or vendor request occurred. See [remaining contracts](provider-contracts.json) and two [offline feature ideas](feature-candidates.json),neither implemented.

## Local read-only replay

Requires exact pinned local LLVM tools and preceding native outputs. Set `LLVM_BIN` to the tool directory. This receipt used Windows/Android NDK27.1/LLVM18;other operating systems remain unverified. These commands do not produce firmware:

```sh
python3 scripts/verify-curated-source.py --replay build/curated-source/safe-gap-20261026-v1/verification.json
python3 experiments/tsl9-safe-gap-functions/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-safe-gap-functions/build/component-v1
python3 experiments/tsl9-original-layout/build-v65.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/safe-gap-v2
python3 experiments/tsl9-original-layout/verify-flow-v65.py --replay experiments/tsl9-original-layout/build/safe-gap-flow-v1
```

On Windows,`py -3` can replace `python3`. Native outputs and full local receipts are excluded from this text-only publication. A fresh clone without the prerequisite outputs cannot replay them directly.
