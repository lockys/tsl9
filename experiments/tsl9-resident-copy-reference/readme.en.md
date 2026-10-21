# Resident byte-copy reference

The candidate-specific C/C++ model covers58 bytes/18 original instructions. The portable raw proof rejects23 operand mutations; host suites run5 groups/772 checks per language.

```sh
sh ./verify.sh --language both
```

The entry verifies the exact carrier, BOOT bridge artifact, source seal and declared dependencies. It preserves MMIO save/clear/FENCE before guards, live forward byte reads and increment-before-store. Restoration and RET occur only on the ordinary path; HALT, TRANSFER and observation limits retain their prefixes. RAM helper binding is an explicit host identity condition.

This reference does not identify the installed resident or prove original ABI, physical Flash or BLE OTA behavior. Only our synthetic host tests run. The [historical sealed note](README.md) preserves its original bytes for old receipts.
