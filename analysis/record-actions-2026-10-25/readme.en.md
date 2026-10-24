# Record actions and shared mutator

[繁體中文](README.md) · [English](readme.en.md)

Nineteen complete functions add **1,506B / 479 instructions**. Nineteen previous imports now have real bodies; five helper/callback dependencies are newly exposed. The remaining count falls from161 to147. No firmware BIN was generated and no hardware was accessed.

| Static evidence | Result |
| --- | --- |
| Standalone native C11 / C++17 | Same object;97 genuine code regions,79 RELA,71 direct controls,four callback-address pairs |
| All curated sources | 127 C/H;200 function comparisons plus2 independent data comparisons =202 comparisons /404 objects |
| Integrated component | 36,462B code +1,750B data;12,717 instructions;3,051 FUNC,71 retained zero-size aliases,2,395 RELA;147 genuine imports |
| Original coordinates | All38,212 selected bytes match the official BIN;3,064 owners in107 adjacent-only spans |
| Transfer positions | 2,147 direct transfers;754 call-return positions;zero ordinary continuation gaps |
| Semantics | 171 literal opcode witnesses and51 statically decoded address checks |

The C source retains register-bound arithmetic,volatile memory operations and explicit architecture ports for the private ABI. It does not establish an ordinary caller ABI or restore the full original source.

Confirmed behavior:

- `9508/954E/95BC/96A2` call9410 with3/6/4/8,store the result at2000BECC before testing null,write the recorded halfword arrays and submit through93AA. These arguments are not proved byte capacities.
- `BD0A` compares a state byte against the full input;only a different value enters the D052/171DE path. `BD5A/BD6E/CC78` preserve their byte stores and call order.
- `CC8C/D3C6/F672/F97C` distinguish low-byte storage from full-width notification inputs,conditional state clearing and the later13D48 call.
- `F1C2` is a shared record mutator. Its ordered flag reads,one-shot clears,post-call reloads,record bit updates and forced submission are preserved. Flag BF91 value2 invokes DE82(1000);the argument unit is unknown.
- Four wrappers pass their exact RAM pointers,flag bytes,original A0/A1 and callback addresses to F47E. F750/F796 force F1C2 on record2000C1D0 before conditionally forwarding the original full input to9792.

DE82,F058,F47E,F4D0,F578 remain unimplemented. The latter two are callback-address references,not supplied implementations. The remaining imports comprise127 direct provider names and20 address-only names;no unresolved mixed direct/address provider remains.

Unknown: product labels such as seat/do-not-disturb,physical MCU/board,installed ROM,private/asynchronous ABI,RAM reservation/capacity/ownership,IRQ/startup/Flash/OTA compatibility. The opaque default and17 static pools remain unprovided;the full authentication body stays private/unresolved. This diagnostic ELF has entry0 and no PT_LOAD;target,host model and ISA emulator were never executed.

[Instruction evidence](evidence.json) · [Semantic contracts](provider-contracts.json) · [Measured summary](summary.json) · [Remaining providers](next-providers.json) · [Feature candidates](feature-candidates.json)

[Selected source](../../src/native/receive/record_actions.c) · [Native recipe](../../experiments/tsl9-record-actions/spec-v1.json) · [Source proof](../../experiments/tsl9-record-actions/verify-source-v1.py) · [Integration recipe](../../experiments/tsl9-record-actions/integration-v1.json) · [Layout recipe](../../experiments/tsl9-original-layout/spec-v30.json) · [Flow verifier](../../experiments/tsl9-original-layout/verify-flow-v33.py)

From the repo root,with the existing pinned local toolchain and retained local receipts:

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v33.py --replay experiments/tsl9-original-layout/build/record-actions-flow-v1
python3 -B experiments/tsl9-record-actions/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-actions/build/component-v2
```

Set `LLVM_BIN` to your local LLVM bin directory. Public recipes pin identities;raw build receipts and superseded trials stay local. These checks perform no firmware execution or flashing.
