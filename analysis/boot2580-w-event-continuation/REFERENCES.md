# Offline replay inputs

The ID2580 BOOT image is already tracked by the checkpoint. The following independent public WCH SDK inputs are **not included** (the HEX files encode substantial firmware). Obtain the exact raw files separately, without newline conversion, and place them at the paths below. The checkers reject a hash mismatch; they do not download anything.

| Local path, relative to repository root | Fixed upstream source | SHA-256 |
| --- | --- | --- |
| `analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.hex` | [V1.31 HEX](https://raw.githubusercontent.com/openwch/ch32v20x/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.hex) | `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5` |
| `analysis/wch-resident-candidate-2026-10-21/original/wchble_rom.hex` | [V1.40 HEX](https://raw.githubusercontent.com/openwch/ch32v20x/baef0054588f4826548429ff4e7a9257d752ef2f/EVT/EXAM/BLE/LIB/wchble_rom.hex) | `5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23` |
| `analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h` | [V1.31 header](https://raw.githubusercontent.com/openwch/ch32v20x/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h) | `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c` |

Run from the repository root:

```sh
python -B analysis/boot2580-w-provider-offline/check.py
python -B analysis/boot2580-w-downstream-offline/check.py
python -B analysis/boot2580-w-event-scan-offline/check.py
python -B analysis/boot2580-w-event-continuation/check.py
python -B analysis/boot2580-w-event-return-offline/check.py
```

These fixed reference candidates are not evidence of the installed resident or of hardware execution. Do not stage the reference files as part of this evidence checkpoint.
