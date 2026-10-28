# Control-data preparation helpers and copy provenance

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_transmit_control_helpers.c)

**Ten whole original functions add890 CODE bytes /321 instructions.** C11/C++17 match original instructions,21 direct controls and4 far-call pairs (29 relocations). Actual bodies resolve10 parent normal UND: **30 become20**. The sole unit import resolves to the existing copy body20000332. No new DATA,indirect calls,stubs or aliases;historical`unprovided` symbols now have real definitions.

|Whole entry|Static evidence|
|---|---|
|5A120..5A1DC|Length12,numeric opcode0;serialize record fields86/88/90/92/94,preserve conditional counter94 update and the three-halfword match boolean98|
|5A568,5A588,5A614,5A686,5A6E0|Prepare opcodes29/30/35/36/40;retain global byte loads,RV32 low-five-bit variable shifts,signed byte reads and conditional flags. These five bodies have no local null-buffer guard|
|5A70C..5A768|Copy5B fromrecord+296 toframe+3;retain counter302 update and two-byte packing|
|5A7BA..5A804|Opcode8,copy8B fromrecord+248 toframe+3,update flags42/state16;length is written before null guard|
|5A804..5A84E|Opcode9,same copy span,but null guard precedes length write. Successful preparation clearsrecord+43,ORsflags160 with32 and setsstate16=1|
|5A898..5A928|Opcode15,retain manual field packing and12B copy fromrecord+104 toframe+14|

Real calls **5A742/5A7E0/5A828/5A904 → 20000332** have whole-CFG null-guard dominance and exact unique original A0/A1/A2 definitions. No live record/global contents were read. Actual buffer spans,copy overlap/lifetime and protocol opcode names remain unproved. Do not merge the distinct null-path side effects ofopcodes8/9 or interpretreturn0 as physical delivery/ACK.

Identical C/C++ partial links contain **50,292 CODE+412 DATA bytes /17,461 instructions**,3,706 positive FUNCs,2,971 relocations and20 normal UND,with no duplicate original CODE. Parent bytes,globals and relocation roles remain. This candidate is not curated into formal src,linked into APP or finally placed at original addresses.

Formal APP remains **162 sources /73,478 of76,800B (95.67% static byte coverage)**,not functional completion. **No new BIN or proved physical ROM/RAM/IRQ/Flash/OTA compatibility.** The4B startup-source and inherited indirect/RAM gaps remain. No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-transmit-control-helpers/verify-v1.py --tool-dir "$LLVM_BIN"
```
