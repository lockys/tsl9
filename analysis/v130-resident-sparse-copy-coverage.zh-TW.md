# V1.30 resident：原始 Intel HEX 補足 136 個來源 bytes

接續[初始化範圍分析](v130-resident-initializer-bounds.zh-TW.md)。該分析的 140 bytes 缺口是針對單一連續主段，不是完整載體。重新讀取 [openwch/ch32v20x 固定 revision 的 wchble_rom.hex](https://github.com/openwch/ch32v20x/blob/64be9554615df522899579633530fd234d685682/EVT/EXAM/BLE/LIB/wchble_rom.hex)，Git blob `cee2a8168c9abfede4cd5baa7c2654efd4e278ff`，原檔 SHA-256 `42766be9b9aea7a819b61ee6bdb6c49c47838b2177947a460364888c4b621c57`。逐筆驗證 Intel HEX 長度、checksum、地址延伸、EOF 與不重疊，得到 17 個區段、190,864 個有效 bytes；`0x40034` 指向 `0x6e524` 的完整 V1.30 字串，主段 `[0x40000,0x6e8ea)` 的 SHA-256 與前次快照相同。

第二次 copy 要讀取 `[0x6e928,0x6e9b4)`；原始 HEX **覆蓋 136/140 bytes**，其中 `[0x6e928,0x6e9b0)` 的 SHA-256 為 `6bb6e500576b4db244b9952d3717e95da192fb61e8d8dc3f28abe3676a68184a`。唯獨最後一個字 `[0x6e9b0,0x6e9b4)` 未被任何資料紀錄覆蓋。它對應目的 `[0x20002da8,0x20002dac)`，雖然成功執行後會由 zero helper 覆寫，仍不能假定先前的 load 不會失敗。沒有補值、沒有發佈載體本身、沒有接入正式映像或連設備，也沒有證明 TSL9 裝有此參考版本。
