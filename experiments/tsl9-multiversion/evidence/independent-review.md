# One bounded cross-version function reconstruction

The complete42-byte routine at original Runtime VA0x8214 is uniquely present and byte-identical in15 of22 retained images. It reads a configuration byte and one of three state bytes and returns0 or1. A small value-level C implementation now compiles as both C11 and C++17 and passes782 host cases per language. This establishes one function's static byte identity and tested portable value behavior; it does not establish whole-firmware equivalence, hardware compatibility or source recovery outside these42 bytes.

All new sources, observations and host test outputs are confined to this directory. The22 decoded inputs and existing D sources were only read. No firmware was executed/emulated, and no network, hardware, peripheral command, authentication modification or vehicle-control implementation was used. The only code executed for tests was a new standalone pure C/C++ function compiled for Windows x64.

## Inputs and format anchors

Every decoded input was rehashed and checked against its own entry in `all-returned-options/receipt.json`. FirmwareID2581 is byte-identical to the retained76800B original Runtime, SHA256 `32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc`. Each image is a raw non-PE/non-ELF blob with an initial decoded RISC-V JAL x0 to an in-file location under the existing Runtime-base0x8000 or12KB-base0x1000 analysis model. At that destination, the actual AUIPC/ADDI pair independently computes GP0x20004000 in all22 inputs. The reviewed routine itself contains ordinary RV32I and compressed instructions. Exact full ISA extensions and a physical MCU identity are not proved by this short routine.

There are18 Runtime-sized inputs, including two77824B images, and four12288B inputs. These size cohorts are separate observations; server labels and sizes alone do not prove a hardware or product type. The42-byte routine has no exact match in the four12KB images or in Runtime IDs2601,2603,2613.

## Complete15-instruction evidence

Relative offsets refer to routine start. `.L_return` is routine+0x26. The original2581 routine occupies half-open VA `[0x8214,0x823E)` / file offsets `[0x214,0x23E)`.

| Relative offset | Exact bytes, little endian | Decoded instruction |
|---|---|---|
|0x00|93874105|addi a5,gp,84|
|0x04|9c43|lw a5,0(a5)|
|0x06|03c74700|lbu a4,4(a5)|
|0x0A|8147|li a5,0|
|0x0C|218b|andi a4,a4,8|
|0x0E|01ef|bnez a4,.L_return|
|0x10|0947|li a4,2|
|0x12|8147|li a5,0|
|0x14|6369a700|bltu a4,a0,.L_return|
|0x18|9387010c|addi a5,gp,192|
|0x1C|aa97|add a5,a5,a0|
|0x1E|83c71700|lbu a5,1(a5)|
|0x22|93b73700|sltiu a5,a5,3|
|0x26|3e85|mv a0,a5|
|0x28|8280|ret|

Complete42B hex:

```text
938741059c4303c747008147218b01ef094781476369a7009387010caa9783c7170093b737003e858280
```

SHA256 for this exact slice in every matched image: `4af30f18b196e304a5b6d30bb167ee2a02c567c4ffcf4e36bb4f72e6204bcdcd`.

The first load reads the32-bit pointer stored at GP+84 (observed GP implies slot0x20004054); the second reads an unsigned byte at that pointer+4. This pointer's actual validity and target allocation remain external premises. The other address expression is `(GP+192)+index+1`, hence state bytes GP+193..GP+195, numerically0x200040C1..0x200040C3 for the observed GP. These bytes are not at `config_pointer+193`.

Only configuration bit0x08 matters. If set, return0. `bltu` compares unsigned RV32 index against2, so3,0x80000000 and0xFFFFFFFF are all rejected; a signed-negative interpretation would be incorrect. State is loaded with LBU and compared using SLTIU with3, so only unsigned values0,1,2 produce1;3..255 produce0. The native routine always reads the config pointer/byte before the index check. It accesses a state byte only if config bit3 is clear and index<=2. It contains no stores, nested calls, MMIO constants or actuator output.

## Exact per-image matches

Each match below is unique within its source and is42B with the same slice hash above. File offsets and modeled VAs are distinct; the VA column uses the existing0x8000 Runtime model. Full decoded-source hashes and exact slice bytes are recorded separately for every image in `evidence.json`.

| FirmwareID | Server version label | Source bytes | File offset | Modeled VA |
|---|---|---|---|---|
|2389|V4.0.49|76800|0x20A|0x820A|
|2410|V4.0.50|76800|0x20A|0x820A|
|2527|V4.1.00|76800|0x214|0x8214|
|2581|V4.1.00|76800|0x214|0x8214|
|2590|V4.1.00|76800|0x214|0x8214|
|2816|V4.1.01|76800|0x214|0x8214|
|2833|V4.1.01|76800|0x214|0x8214|
|2841|V4.1.10|76800|0x214|0x8214|
|2869|V4.1.20|76800|0x21E|0x821E|
|2873|V4.1.20|77824|0x21E|0x821E|
|2914|V4.1.20|77824|0x21E|0x821E|
|2946|V4.1.30|76800|0x21E|0x821E|
|2958|V4.1.40|76800|0x21E|0x821E|
|2963|V4.1.50|76800|0x21E|0x821E|
|2966|V4.1.60|76800|0x21E|0x821E|

No exact match was found in Runtime IDs2601/V4.1.00,2603/V4.1.01,2613/V4.1.01. This bounded pass did not identify a replacement routine there. They may differ in layout, compiler representation, features or hardware type; the present evidence does not distinguish those explanations and does not prove the predicate's behavior was removed or changed. The four12KB images are IDs2349,2492,2580,2815, all labeledV1.0.00 by the server; no42B match is claimed for them either. Matching a short function cannot be used to infer compatibility of the remaining image.

## Recommended readable C/C++ boundary

`observed_predicate.c` implements a value-level adapter with explicit inputs:

```c
uint32_t tsl9_observed_predicate(uint8_t cfg_byte4, uint32_t index,
                                 const uint8_t *state3) {
    if ((cfg_byte4 & UINT8_C(0x08)) != 0 || index > UINT32_C(2))
        return UINT32_C(0);
    return state3[index] < UINT8_C(3) ? UINT32_C(1) : UINT32_C(0);
}
```

The caller supplies the already-read configuration byte and a readable three-byte state view; this implementation deliberately has no device-address binding. `state3` may be null only on a branch that does not read it. On the enabled valid-index branch it must denote readable bytes. It does not model pointer faults, asynchronous SRAM mutation or configuration-fetch side effects. That is an explicit abstraction boundary, not permission to assume target memory valid.

The existing semantic anchor is `D/experiments/tsl9-contract-model/src/dnd_actions.c:154` (`gate_channel`). That helper is called by the existing DND interval logic; this review reconstructs only its read-only decision and does not implement or change any caller scheduling, radio/vehicle behavior, state update or authentication gate. Its source hash is included in the evidence receipt. Avoid renaming it to a broader product feature until callers and variant meanings are independently established.

## Bounded host checks

`verify-host.py` compiled this source twice with the pinned local Clang/LLD toolchain, as C11 and C++17, targeting **Windows x64** DLLs with no entry point/default libraries. It called only the newly compiled pure function, not native firmware code or an instruction emulator.

Both language paths passed14 named boundary cases plus768 exhaustive unsigned-state cases (all256 byte values at each of the three indices),782 cases per language. Named cases include valid indices0/1/2 and state values0/1/2; first rejected state3 and unsigned255; nonmask config bits; bit0x08/all-bits disable; first rejected index3;0x80000000 and0xFFFFFFFF; and null state pointers on rejected/disabled branches. This checks the C adapter's thresholds, index/address selection and short-circuit read boundary. The native-byte interpretation is supported separately by the complete disassembly and per-image identity, not by executing firmware.

`host-tests.json` contains commands, tool/source hashes, every named case and per-language results. `host-c/` and `host-cpp/` contain only generated x64 host artifacts/logs. `inspect-functions.py` produces `evidence.json`, containing all22 pinned input hashes, entry/GP numeric decoding, match offsets, full42B slices and unknowns.

ROM/provider reconstruction, R81's missing272B lookup-domain tail, new feature semantics and physical/OTA acceptance are outside this pass. A new version's76-page size or a shared function is not authorization to transplant missing bytes across versions. No such data was borrowed or claimed complete here.
