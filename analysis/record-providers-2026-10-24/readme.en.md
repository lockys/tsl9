# Record providers and the static SPI call chain

[繁體中文](README.md)

Bound the 81AA, 821E, 16B7C and 18CA4 entries and their necessary fill, register-read and SPI dependencies. Eight existing C/C++ units supply **1,000B / 349 instructions / 67 regions**. Both C11 and C++17 reproduce all original bytes after static original-VA encoding. The 47 added typed references and resolved branches inside ordinary functions retain their real owners.

| C/C++ source | Selected scope |
| --- | --- |
| [queue-small-providers](../../src/native/receive/queue_small_providers.c) | 6B / 2 instructions / 1 regions |
| [record-predicate](../../src/native/receive/record_predicate.c) | 42B / 15 instructions / 1 regions |
| [fill-provider](../../src/native/receive/fill_provider.c) | 168B / 55 instructions / 13 regions |
| [spi-transfer](../../src/native/receive/spi_transfer_ports.c) | 72B / 25 instructions / 8 regions |
| [spi-write-providers](../../src/native/receive/spi_write_providers.c) | 182B / 68 instructions / 20 regions |
| [register-read](../../src/native/receive/register_read.c) | 72B / 26 instructions / 2 regions |
| [tagged-dispatch](../../src/native/receive/tagged_dispatch.c) | 246B / 86 instructions / 15 regions |
| [peripheral-write](../../src/native/receive/peripheral_write.c) | 212B / 72 instructions / 7 regions |

The main component contains **5,636B code + 456B data**, 455 nonzero FUNC regions, 22 genuine entry aliases, 356 RELA and 16 UND. C/C++ component hashes match. All previous 4,636B code, 456B data and 62 selected nonzero vector bindings remain unchanged. No executable stubs or ABS providers were added.

The 95 C/H files and manifest are unchanged. Current curation still covers 136 code comparisons / 272 objects plus two pointer-data comparisons / four objects, totalling 138 / 276. This round reuses existing objects; it does not add eight translation units. The complete six-byte 81AA leaf is selected; its separate 18-byte clear function is also audited but is not linked.

The original instruction at 18730 is JAL x0 to 40000, outside the APP image ([evidence](resident-tail.json)). That resident entry remains unproved; function-table metadata and ABS symbols cannot replace executable code. [Next providers](next-providers.json) lists all 16 gaps and existing source candidates. The earlier 18834 clock-query has a 196B versus 174B scope difference and remains unbound.

Use the replay commands in the [experiment](../../experiments/tsl9-record-providers/readme.en.md). [Summary](summary.json), [pending providers](pending-providers.json), [publication provenance](publication-provenance.json).

Possible features include passive busy, SPI wait and timeout diagnostics alongside an offline raw-record preview. These features are not implemented. **Static closure does not prove successful CAN/SPI transfer. This unresolved VMA-zero ET_REL is not a flashable BIN.** Physical MCU, installed ROM/ABI, original placement, memory/IRQ and BLE OTA compatibility remain unproved. No target, HOST-model or ISA execution, hardware access, commit or push occurred. Historical privacy findings remain.
