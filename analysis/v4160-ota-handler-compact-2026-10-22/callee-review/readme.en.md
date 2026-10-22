# UID callees: confirmed App and conditional resident references

[繁體中文](readme.zh-TW.md)

This bounded review reads official ID2966 `92BA..9334` (56-byte builder plus66-byte comparator,48 instructions) and the58-byte leaf selected by slot4004C in two existing SDK candidates. No compiler/HOST run, RV32 execution/emulation, hardware, download or network occurs. No actual chip UID value was read or transmitted.

`contracts.json` separates **confirmed App bytes, conditional local candidate behavior, and unknown installed identity/transitive ABI**. This does not authorize narrowing the current full8 call bridge.

## Confirmed App

92F2 compares full A1 with14 before any frame. An invalid length returns A0=1 directly, preserving entry A1..A4/A6/A7 and S/GP/SP. Not reading a value does not authorize losing its return-time preservation.

For length14, allocate32 bytes, save S0/RA, set A0=currentSP, and use9302 **C.JAL** to92BA/link9304. The builder allocates16 bytes and saves S1/S0/S2/RA in source order. The first target load at92C2 even precedes the later S0/S2/RA saves, so its fault/alias prefix cannot be arbitrarily moved.

| Boundary | Source obligation |
|---|---|
| First copy92D6 | A0=entry destination, A1=1FFFF7EC, A2=8, A5=READ32(4004C); ambient A3/A4/A6/A7 pass through. JALR link92D8. |
| Tail copy92F0 |92D8 forms A1 from post-call liveS0+7E8;92DE freshly loads liveS1+4C intoT1; A0=liveS2+8 and A2=6. Fresh liveSP reads restore S0/RA/S1/S2 at their exact interleaved positions, then SP+=16 and JR T1. A3..A7 carry first-callee outputs; A5 is not the second target. |
| Comparator9308 | After builder returns, index=0 and A3=14. LBU input at liveS0+index FIRST, then LBU constructed byte at currentSP+index SECOND. First mismatch returns1; all14 equal returns0. No standard memcmp sign convention or valid-length NULL guard. |
| Return9324 | Fresh RA at currentSP+28, fresh S0 at+24, SP+=32, then JR RA. Arbitrary opaque SP/frame changes prevent unconditional restoration claims. |

The App body does not directly read A6/A7 or access GP, but the builder reaches unknown resident code and the fast path preserves ambient values. **This122-byte local read-set cannot justify removing ambient arguments/register obligations.** The second slot load remains fresh: memory aliases, resident writes or other changes can make it differ from the first.

## Two bounded candidate conclusions

Existing sealed initialization proof maps flash405E2 inV1.40 and405A2 inV1.31 toRAM20000332. Both captured slot4004C words equal20000332. The mapped `[20000332,2000036C)` bodies are identical58 bytes/18 instructions, SHA256 `558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36`. Both actual sources are reread; identical bytes need only one operand ledger. The following word-copy body is excluded; no wider ROM survey occurred.

The leaf first reads4002420C intoA4, writes zero there and executesFENCE.I, **then** checks null destination/source and zero length. All normal/early returns restore savedA4 toMMIO. Positive-length copy is forward bytewise, with sourceLBU before destinationSB and index increment before store; no memmove/wrap/fault guard exists.

These58 bytes require A0/A1/A2 plus control linkRA, with no nested calls and no explicit S/GP/SP/RA/A7 writes. A0/A1/A2 remain unchanged; normal A0 is destination, **not a Boolean success code**. ScratchA3/A4/A5/A6 can change. This slice needs no Xwchc decode, but installed identity, copied executable RAM/coherence, instruction/MMIO/memory/return success and lack of asynchronous interference remain conditions. None measures the TSL9 installed resident.

## Replay and stopping boundary

```sh
# Sealed/pin metadata only; no official BIN or external candidate body read
python3 -B check.py --project-root ROOT

# Actual App/two-candidate reads,48+18 rows and six single-field controls
python3 -B check.py --project-root ROOT --firmware OFFICIAL_BIN \
  --candidate-root EXISTING_WCH_REFERENCE

# Optional: --original-object ACTUAL_PREVIOUS_APP_CARRIER.o
```

Default reports `metadata_only=true`, `actual_original_firmware_read=false`, `actual_candidate_source_bodies_read=0`. Explicit firmware enables actual App/two-source reads and reports true/2, without historical W builds unless an object is explicitly requested. The checker resolves working `apk-analysis/tsl9-` and delivered `analysis/` reference layouts.

The six raw controls change UID14, builder link, second-slot live base, tail count6, candidate MMIO-restore source and the source-byte destination register. Only field decoding/comparison occurs. `app-llvm.txt` is actual static LLVM output; `candidate-static-display.json` retains only r2 addresses/bytes/opcodes, with no ESIL use/execution. The proof stops at these two candidate leaves: `installed_resident_identity_proved=false`, `dropping_ambient_args_authorized=false`, `transitive_original_ABI_proved=false`.
