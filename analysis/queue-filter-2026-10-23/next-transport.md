# 下一段：8A56傳輸封裝

[English](next-transport.en.md) · [96指令原始證據](next-transport.json)

`[0x8A56,0x8B6E)` 共280B／96指令，SHA256 `3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b`。局部CFG為96 nodes／101 edges；出口是8ACA RET、8B50 JR T1、8B6C RET。RET後8B52的copy loop仍可到達；8B6E是下一個frame。

先拒絕unsigned A3>1039，再建32B frame，保存長度／來源／command到S-register。GP+150／154 halfword比對channel並拒絕FFFE；兩次fresh `[40013C]`間接admission呼叫，在A0==1時選bank0／1。這些resident的身分與preservation未知。

共同路徑PC衍生bankbase`2000B18C`、stride1062。halfword magic `7F55`（little-endian bytes `55 7F`）、command、length高低byte、payload及8-bit加總checksum被寫入bank+6開始的frame；metadata halfword寫length+6與offset0。command與長度都取當時S-register，不把opaque call前的值偷偷帶回。

copy loop條件是 `uint16(index) < then-live S0`，memory offset仍使用完整index。1039檢查在admission呼叫之前，不能宣稱之後S0仍受此上限約束。最後fresh取GP+148+4×bank的byte到A0、A1=1、fresh `[40050]`到T1，以JR tail跳轉，不寫RA。沒有CSR指令；未執行target／ISA／MMIO或驗證實體傳輸。
