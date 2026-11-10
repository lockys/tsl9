# ID2580 W wrapper 間接 provider：離線追蹤

## 結論與界限

ID2580 BOOT 的 `0x1848` wrapper 從 **`0x0004013c` 的 32-bit 內容**取得呼叫目標，並非直接呼叫 `0x4013c` 本身。該 BOOT 檔案不包含此位址的 resident bytes，不能從它證明實際 slot 的值或誰初始化／映射該區。

既有兩份**獨立公開 SDK 參考候選**的 HEX，該位置分別含 `0x4b456`（V1.31）與 `0x4b4ee`（V1.40）。V1.31 保存的 SDK 標頭把 `0x40034 + 66*4` 宣告為 `GATTServApp_ReadCharCfg(uint16_t, gattCharCfg_t*)`，傳回 `uint16_t`；V1.40 相同宣告的既有核對見 [版本比較](../../experiments/tsl9-wch-official-v140/README.md)。名稱與簽章是 SDK 契約，**不是 ID2580 真機 provider 身分證明**。候選靜態實作另顯示有條件的 byte 讀取，而非能靠標頭假定任意完整 16-bit 記錄被讀取。

## BOOT 實際可證的呼叫與返回

固定 image `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin` 長 12288，SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`，PC 為 base `0x1000` 的分析座標。以下既有 listing 來源是 [identity source-map](../boot2580-uid-helper-2026-10-21/identity-link/source-map.json)，本檢查器重新核對完整 `[18ea,192c)` raw bytes，並非另一次反組譯。

| PC / bytes | 指令與資料流 |
|---|---|
| `18ea 03d7e107`, `18ee 631ea702` | `lhu a4,126(gp)`，與完整輸入 `a0` 比較，不相等返回。 |
| `18f2 c167`, `18f4 f917`, `18f6 630af702` | 排除 `0xfffe`。 |
| `18fa b7070400`, `18fe 83a7c713` | `lui a5,0x40; lw a5,316(a5)`，因此載入 `[0x4013c]`。 |
| `190c ae84`, `190e 93858106`, `1912 3684`, `1914 3289`, `1916 8297` | 保存原 command/length/data，設 `a1=gp+104`，以原 `a0=context` 間接呼叫；`a2/a3` 仍是入參，不能宣稱 provider 不使用其他 live 暫存器。 |
| `1918 8547`, `191a e30cf5f2` | 比較完整返回 `a0` 是否**恰為 1**；是才跳到 `1852` 封裝。非 1 經 epilogue 返回，`a0` 沒有被此 epilogue 改寫。 |

過長、context 不符及 sentinel 的提前返回路徑不經 provider；不可把回值一律命名成錯誤碼。成功封裝的後續與 tail slot `0x40050` 見 [wrapper](../boot2580-w-wrapper-offline/README.md)；其結果取決於該下游，不能視為已傳送。上游 W 的 `(context,0x57,0,0)` 是有條件靜態追蹤，見 [W 回覆](../boot2580-w-reply-offline/README.md)。

## 公開候選中的查找與返回

參考來源是已保存的 [V1.31 HEX（固定 commit）](https://raw.githubusercontent.com/openwch/ch32v20x/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.hex)（SHA-256 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`）及 [V1.40 HEX（固定 commit）](https://raw.githubusercontent.com/openwch/ch32v20x/baef0054588f4826548429ff4e7a9257d752ef2f/EVT/EXAM/BLE/LIB/wchble_rom.hex)（`5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23`）。兩份 Intel HEX 是稀疏映射，checker 驗證各 record checksum、重疊一致、slot 和被引用 bytes；不以零填補缺口。參考函式以下僅在候選版本及相關指令集解讀成立時適用，並假設正常 memory access、沒有並行干擾。

V1.31 slot bytes `56 b4 04 00` → `4b456`；V1.40 `ee b4 04 00` → `4b4ee`。兩入口 22 bytes 相同；`jal` 目標分別是 `4b2e4`、`4b37c`。下表 V1.31，V1.40 相對對應同樣指令但容量位址不同。語意與 Xwchc decode 沿用既有 [`resident_gatt_CCC_write.c`](../../experiments/tsl9-resident-gatt-CCC-write/resident_gatt_CCC_write.c) / [`verify-v2.py`](../../experiments/tsl9-resident-gatt-CCC-write/verify-v2.py)，並由本次原始 bytes 錨定：

| PC / bytes | 候選路徑 |
|---|---|
| `4b2e4 b7370020`, `4b2e8 83c6573b` | 容量從 byte `[0x200033b5]` 讀取；V1.40 對應 `[0x20003405]`，不可跨版本硬編碼。 |
| `4b2ee 63e5d700`, `4b2f8 2e87`, `4b2fa 9105`, `4b2fc 03d6c5ff`, `4b300 e30aa6fe` | 用容量界定記錄數，從 `a1` 起每筆 stride 4，讀 offset 0 的 little-endian halfword 比對 `a0`，第一個匹配返回該記錄指標；無匹配返回 0。 |
| `4b456 4111`, `4b45a eff0bfe8`, `4b45e 09c5`, `4b460 2821` | 呼叫查找；找到非零指標時，條件 Xwchc `qk.c.lbu a0,2(a0)` 返回 offset 2 的 unsigned byte；找不到時 `4b468 0145` 返回 0。 |

因此**若** BOOT 呼叫的 resident 確為此候選且 GP／記憶體和呼叫約定均成立，`gp+104` 被當成 4-byte 記錄陣列，選中紀錄 offset 2 的 byte 必須恰為 `1` 才進 wrapper 封裝；值 `2` 或 `3` 並不通過，不能改為 bit 0 測試。這是跨映像條件推導；既未證明實機 slot 或記錄內容，也未證明 CCC 訂閱、BLE 傳輸或 ACK。查找結果指標為零也走無匹配分支；不假定空指標可安全讀取。

## 重播與 mutation

```sh
python -B analysis/boot2580-w-provider-offline/check.py
```

檢查完整 BOOT hash、66-byte 呼叫段與兩個完整 HEX hash、record checksums、slot/入口/查找 helper raw bytes，並解算 JAL 目的地。10 個 BOOT 及每候選 10 個獨立記憶體內單 byte mutation **繞過整檔 hash** 測試 raw gate 拒絕，覆蓋 slot、入口呼叫、判斷、讀值與查找；這些是完整性反例，不是執行突變指令或語意獨立證明。無硬體、刷寫、BLE 或 ISA 執行；其他 workspace 改動未觸碰。
