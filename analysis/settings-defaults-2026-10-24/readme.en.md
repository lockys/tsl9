# Settings defaults and persistence wrappers

[繁體中文](README.md) · [C/C++](../../src/native/startup/settings_defaults.c) · [Original instructions](evidence.json) · [Summary](summary.json) · [Persistence contract](persistence-contract.json)

Twelve complete functions add878B/297 instructions,31 private regions,12 control relocations and one data-address pair. Six pending fallback entries now have real implementations;six persistence wrappers are separately reconstructed. Missing providers75→70:69 have direct-control references,and one is an opaque data-address dependency.

Original main-settings initialization copies four bytes through ROM from a PC-relative source address into the runtime pointer loaded fromGP+84,plus12. This flow is retained with genuine undefined data symboltsl9_settings_default_data_1a69c. No contents,independent content hash,guess or substitute is supplied. An address is not data-content evidence;the diagnostic ELF retains only a reference address.

|Writer|Explicit copy|Destination operand|Stack suffix not initialized by this wrapper|
|---|---|---|---|
|12E54|256B|0x08077900|None|
|12EE6|256B|0x08077800|None|
|12F48|256B|0x08077700|None|
|13052|256B|0x08077600|None|
|130D6|133B|0x08077500|bytes133..255,123B|
|13138|112B|0x08077A00|bytes112..255,144B|

All retain a272B frame,RA+268,ROM0x4004C copy and the existing9C0A call.9C0A calls18EF2,whose original loop reads/writes four bytes per iteration until offset256. Short-record suffix contents are therefore not established by these wrappers. No hardware action,physical failure or data disclosure is claimed;no zero/FF padding or original behavior was changed.

116 C/H files and89 code units pass180 comparisons/360 objects including independent pointer data. Previous115 sources and1057 artifact records remain unchanged. The component contains21866B code+714B data;all22580B match the official ID2966 BIN at native original addresses. This scope excludes the unprovided four-byte data.

Flow covers7584 instructions,1212 direct transfers(1143 measured/69 reference-only),7013 ordinary next positions without gaps,and467 potential call-return positions.393 register-indirect transfers,10MRET and1EBREAK remain short of a complete CFG or physical proof. Diagnostic ELF entry0/PT_LOAD0 is not flashable.

Next:remaining runtime entries and ROM/BOOT/APP/IRQ compatibility. A proposed settings-integrity/reserved-byte feature could read a complete original page,preserve unknown bytes,and verify writeback after hardware/mapping proof. It is not implemented;the current reconstruction retains original behavior. No target/HOST-model/ISA execution,hardware or network actions occurred. Historical privacy findings keep commit/push held.
