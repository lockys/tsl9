# Original ROM-table and callback reconstruction

[繁體中文](README.md)

Six complete functions now bind in [C/C++](../../src/native/receive/rom_driver_family.c): **564B/208 instructions,57 original regions,37 direct transfers and two callable-address pairs**. This covers171BA,the173A2 initializer and four required functions,including relevant paths after earlier RETs.

| Complete original extent | Size |
| --- | --- |
| `171BA–171DE` | 36B / 14i |
| `171DE–172B6` | 216B / 76i |
| `172B6–17320` | 106B / 38i |
| `17320–17344` | 36B / 14i |
| `17344–173A2` | 94B / 37i |
| `173A2–173EE` | 76B / 29i |

C11/C++17 components match: **15232B code+674B data,5304 instructions,1004 RELA,80 genuine UND**. All previous14668B code and674B data are retained. Binding two old entries exposes9792,9FC2,A2EE,ABF2,so78→80;none is replaced by a stub. Native placement makes all selected **15906B** match the official BIN at original VMAs. The entry-zero ELF has no PT_LOAD and **is not flashable**.

171BA loads a callable address from40060,calls with A0=byte[GP+365],A1=1,then computes low32(A0*10),logical shift4,and+50. Related paths retain40038/40048/40050/40058/4005C/40080 slots,original16B frames,S0/S1 and DIVU/REMU. The initializer passes172B6 to the40080-table callable,then stores the low return byte atGP+365. Passing an address does not prove registration or execution. Units and ROM semantics remain unknown.

The existing D272 entry forwards A0=2000BF48,A1=0,A2=19 to the40048-table callable. The new initializer uses that same slot with GP+364,0,1. These are zero-fill-shaped argument tuples,not observed writes or proven ROM implementations. The reset pair at186AA statically computesGP=20004000;runtime GP preservation,RAM ownership and the19B field meaning remain unknown. No VIN identity is inferred.

[Original instructions and coverage limits](evidence.json) · [Results,slots and hashes](summary.json) · [80 pending providers](next-providers.json) · [Integrator](../../experiments/tsl9-rom-driver-family/integrate-v1.py)

The collection has104 C/H files,77 code units and one independent data unit:156 comparisons/312 objects. Prior152 results and913 artifact records are unchanged. Of875 direct transfers,795 target measured instructions and80 remain unimplemented references. All4873 ordinary sequential and311 potential call-return positions are owned. Runtime context/targets for254 register-indirect transfers,10 MRET and the8034 EBREAK remain unproved;this is not a complete CFG.

Native v1 compilation required extra S-register preservation and rejected three c.j forms. Accepted v2 uses explicit original register ports without changing compiler flags. Integration v1 was rejected by a mistaken ELF-info validator constant;component-v2 passes the restored correct FUNC info18 check. Failed trials remain retained and are not accepted evidence.

Next: the four newly exposed providers and installed-ROM contract. Possible added feature: an **offline ROM-slot argument and conversion inspector**,currently only a proposal,retaining unknown units rather than changing hardware controls.

Physical MCU,RAM/ROM,full startup/private ABI/asynchronous IRQ and OTA remain unproved. No target/HOST/ISA execution,hardware,network,BIN,commit or push. Historical personal information remains unresolved.

```sh
python3 experiments/tsl9-rom-driver-family/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rom-driver-family/build/component-v2
python3 experiments/tsl9-original-layout/build-v10.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/rom-driver-family-v1
python3 experiments/tsl9-original-layout/verify-flow-v9.py --replay experiments/tsl9-original-layout/build/rom-driver-family-flow-v1
```
