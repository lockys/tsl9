# GATT service registration and UUIDs: candidate execution layer

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ bodies](resident_gatt_registration.c) · [UUID DATA](uuid_data.c)

Four complete archived SDK candidates add **536 CODE bytes/219 instructions plus20 DATA bytes**. C11/C++17 objects match the original instruction roles,including six far-call pairs,42 direct controls and16 conditional Xwchc ports. Compile-only assertions check the official candidate GATT layout with zero runtime bytes.

|Verified location|Behavior and extent|
|---|---|
|`0x445E6..0x44624`|Expand a two-byte UUID into template offsets12/13;retain null/copy ordering|
|`0x44624..0x4468A`|Compare2/16-byte UUIDs with required expansion and the candidate Boolean convention|
|`0x4CE22..0x4CF22`|Check the first service type/key size,assign handles at16-byte stride and register a service node|
|`0x4CF22..0x4CF96`|Register the service,then conditionally allocate/register a12-byte callback node|
|APP `0x8FCC`|Whole384B/126-instruction initializer uniquely supplies `A0=GP,A1=4,A2=16,A3=0x19DFC` to candidate slot `0x40130→0x4CF22`|

The first64B of the original128B reset initializer match four16-byte `gattAttribute_t` rows:UUID length offset0,pointer4,permission8,handle10,value pointer12. This interpretation requires completed reset copy,stable GP/rows and matching installed ROM/header/Xwchc/saved-register ABI.

The rows reference unselected APP addresses `0x1AB38/0x1AB42/0x1AB44`;**a pointer does not establish the value length**. No such APP DATA was selected,and no withheld router/default payload was used. Key size16 is within the candidate7..16 domain;it does not establish encrypted or authorized communication.

The candidate core may already have registered the service when later callback-node allocation fails with **19**. The complete wrapper has no rollback call. Preserve possible partial state;do not assume errors imply no mutation or invent cleanup/retry behavior. This is conditional static semantics,not an observed physical outcome.

The20 UUID bytes come from actual sparse HEX records. All11,973 records/191,244 data bytes are rechecked,including the two UUID segments beyond the main contiguous carrier. No gaps are filled with zero/FF,and empty slices are not interpreted as values. The inherited4-byte startup-source gap remains.

Real partial linkage with the SDK parent yields identical C/C++ objects:**41,410 CODE+412 DATA bytes/14,279 instructions**,2,879 positive FUNCs,five DATA OBJECTs,2,295 relocations and no named UND. Every old allocation/global/typed relation remains;four normal external entries bind to real parent CODE. Zero UND does not close runtime ROM/RAM/callback/IRQ/Flash/OTA obligations.

[`verification-v1.json`](verification-v1.json) and[`summary.json`](summary.json) retain whole CFGs,unique reaching definitions and native/independent-reader evidence. Formal APP provenance remains162 files/**95.67% static byte coverage**. No APP linkage,final original-address placement,BIN or target/HOST-model/ISA/hardware execution occurred. **A usable replacement firmware remains unproved.**

With frozen local inputs and LLVM,read-only replay is:

```sh
python3 experiments/tsl9-resident-gatt-registration/verify-v1.py --tool-dir "$LLVM_BIN"
```

Only text sources/evidence are committed. Stopped composition-v1/v2 trials remain local;composition-v3 is the successful trial. The[feature candidate](feature-candidates.json)is an unimplemented offline GATT consistency/partial-registration diagnostic.
