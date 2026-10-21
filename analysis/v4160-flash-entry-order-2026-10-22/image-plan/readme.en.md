# Source plan for integrating eleven readable functions

[繁體中文](README.md)

This plan reads the previous actual `source-integrated.o`, the pinned placement manifest and all 34 original C carriers. The original carrier had 8,280 RELA records; the prior IRQ-integrated object has 8,276. This report uses the latter and does not mislabel it as the unmodified vendor object.

Five IRQ/RCC and six Flash functions occupy eleven original sections / 526 bytes. All 691 allocations must remain, including 680 storage sections outside the replacement scope. Four original carrier units require exact quoted-assembly block removal; actual filtered-byte digests are retained without modifying the originals. The planned native unit count is 34 carriers, two readable IRQ units and six Flash units, or 42; this is not an actual complete-build result.

All 8,259 outside-owned RELA roles and multiplicities must survive. Seventeen owned call/branch records need explicit new-source replacements. Twenty outside references target original function entries. The six private Flash branch roles also require semantic admission; equal size does not justify binding old numeric interior aliases to new instructions.

The program function's full 100-byte original extent needs an explicit source. Its last six original bytes are live AND, store and return instructions, not padding. A new 100-byte build still needs actual instruction-boundary, branch, symbol and output-register checks. This plan does not admit incomplete native or image contracts.

```sh
python analysis/v4160-flash-entry-order-2026-10-22/image-plan/prepare_plan.py --project-root . --merged-object /absolute/path/to/source-integrated.o --check
```

The explicit historical object must match the report's digest. Six constraint mutations reject missing storage, waiving six bytes, inventing padding, losing outside RELA, inventing an interior entry and dropping an incoming reference. These are source-plan tests, not CPU or hardware execution.

This scope produces no complete native build, BIN, hardware or OTA result. Recorded-reference coverage does not exclude unknown ROM, computed references or asynchronous state.
