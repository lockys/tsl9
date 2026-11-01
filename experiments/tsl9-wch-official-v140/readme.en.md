# WCH official BLE V1.40 source check

[繁體中文](README.md)

At WCH CH32V20x commit `b375bbbc7dfe8642d6fb7c17e6d3207ee1c3c9c1`, the official [wchble_rom.hex](https://github.com/openwch/ch32v20x/blob/b375bbbc7dfe8642d6fb7c17e6d3207ee1c3c9c1/EVT/EXAM/BLE/LIB/wchble_rom.hex) has SHA-256 `5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23`, identical to the locally retained V1.40 candidate previously used in comparisons. Its [official header](https://github.com/openwch/ch32v20x/blob/b375bbbc7dfe8642d6fb7c17e6d3207ee1c3c9c1/EVT/EXAM/BLE/LIB/wchble_rom.h) identifies V1.40 and version string V1.4; the downloaded header SHA-256 is `fab43e7b8e351596a14d2a434eea4fa79587a8b9bba12738897d35ee2c3dbf2e`.

The local [version checker](../tsl9-six-dependency-ledger/check-gatt-resident-versions.py) passed against this official HEX and the retained V1.31 file: the V1.40 version string differs from the TSL9 APP's 21-byte V1.3 prefix, while the V1.31 prefix matches. The version-gate interpretation remains conditional on the installed comparison implementation, calling convention and execution matching the candidates. This establishes reference-file provenance, not the installed resident, startup success or compatibility; do not flash the candidate HEX.

Verification read only the permitted APP version string and public HEX files; it did not read excluded APP ranges, connect to hardware or execute the target.
