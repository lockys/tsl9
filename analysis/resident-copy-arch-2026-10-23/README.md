# Resident copy 候選：58B 架構重建

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

[最可靠來源](../../src/native/resident/copy_arch.c)現在保留 SDK V1.31 copy 的完整 58B／18 指令；C11 與 C++17 連結後全碼相同。條件式映射為 `0x405A2 → 0x20000332`；候選檔 `[0x4004C]`＝`0x20000332`。來源 SHA-256：`d004661257866b3c8e11ad424dffc47c969f640f9d2bc87c6835aae9be9be660`。

這僅是公開 SDK 候選。原 Runtime `[0x8000,0x1AC00)` 與 BOOT `[0x1000,0x4000)` 都沒有涵蓋 slot；目前沒有實際裝置 resident dump。快取官方 V1.40 header 的 `0x40000+0x34+6*4=0x4004C` 對應 tmos_memcpy，不能證明裝置版本或 ABI；header SHA-256 為 `fab43e7b8e351596a14d2a434eea4fa79587a8b9bba12738897d35ee2c3dbf2e`，固定來源見[官方 commit](https://github.com/openwch/ch32v20x/blob/baef0054588f4826548429ff4e7a9257d752ef2f/EVT/EXAM/BLE/LIB/wchble_rom.h#L2777)。

[實作契約](../../experiments/tsl9-resident-copy-arch/README.md)保留 MMIO／FENCE.I／暫存器／故障前綴順序，不把普通 memcpy 當作相同替代品。全 linked code SHA-256 為 `558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36`，ELF 為 `a7a4157ed51c60ad5d21e88ec913079b379c83dad40add0968f60fe4f95ed317`。

- [v3 正式收據](evidence/candidate-v3.json)：每種語言 50 個負向控制；原始 C／C++ 編譯及連結產物相同，全部 18 筆 LLVM 位址／位元組吻合。
- [獨立檢查](independent-review.json)：38／38 個來源與 PHDR 變異被拒絕；先前 v2 漏檢的 p_align=3 已由新增 v3 修正，舊版本原封保留。
- 來源整理通過 76 組比對／152 物件，共 64 個 C/H、38 個 native units；[公開收據](evidence/curated-source.json)是路徑匿名化衍生物，不冒稱原始收據。
- [公開來源對照](publication-provenance.json)：三份可攜收據保留原位元組；編譯收據僅換行正規化，整理收據僅路徑匿名化。原始收據／私人日誌保留本機，衍生 JSON 完整值比對通過。

歷史來源包唯讀重播在 `seal member drift:README.md` 失敗：README 實際 4704B，舊 seal 預期 4750B；其餘 seal 成員及原始資料／23-operand gate 仍吻合。本輪保留該失敗，不改舊 seal／收據；新的獨立位元組檢查不依賴整包成功。

尚未證明安裝 resident、完整 startup／物理 ISA／IRQ／MMIO／OTA。未執行 HOST 模型、指令模擬、藍牙／CAN／UART／Flash 或網路；未新增可燒錄 BIN，原 740B 傳送鏈證明保持不變。
