# V1.31 startup copy 來源與缺口（離線、非刷機）

## 固定來源與結論

- 本目錄 `wchble_rom.hex` 是 WCH 官方 [固定提交 ec059e0b18046b111ee850e44f105fcd095e775c](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.hex) 的原始 Intel HEX，526,184 bytes；SHA-256 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`，Git blob SHA-1 `13202d1678c9766117d787d98b4de55ed61fc571`。以 raw.githubusercontent.com 固定提交取得後校驗；不是設備備份。
- HEX 經逐記錄 checksum、位址、重疊、EOF 檢查，含 191,244 個有記錄的 bytes。主連續區 `[0x40000,0x6ea66)` 為 191,078 bytes，SHA-256 `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22`；另有 15 個兩 byte 稀疏區及尾區 `[0x6eaa4,0x6eb2c)` 136 bytes，SHA-256 `7416a8d7c1d595a759e14b05918b732a9168c6003af658359d8c3f452840b450`。這兩個重算雜湊與既有候選 carrier／尾檔 ledger 相符；原本稽核指定的 `apk-analysis/tsl9-wch-resident-candidate-2026-10-21/` 在此工作目錄不存在，故不是直接驗證那些本地檔案。
- **抽取缺漏**：只抽主連續區時，整段 `[0x6eaa4,0x6eb2c)` 雖在 HEX 卻不在主 carrier。**源檔缺失**：`[0x6eb2c,0x6eb30)` 的四個位址在完整固定 HEX 都沒有資料記錄，並非抽取時丟掉；不得視作 00 或 FF。這不表示實體 Flash 一定不可讀或必然 fault。

## 為何需要四 bytes

既有原始指令解碼 gate 由 HEX 主區檢查入口、參數與 helper：`0x40000` 跳到 `0x6de7e`；第二次呼叫在 `0x6de6e`，來源 `0x6eaa4`，目的 `0x20002e70`，最後目的 **word 起址** `0x20002ef8`。從 `0x40280` 搬到 RAM 的 helper 使用含端點的 unsigned 比較與 word 讀取，所以需要 35 words／140 bytes，即 `[0x6eaa4,0x6eb30)`。有完整尾段時前 34 words 有記錄，第 35 次讀 `0x6eb2c`、待寫 `0x20002ef8`；僅主 carrier 時第一次讀 `0x6eaa4` 已無來源。後續清零不能證明先前讀取成功。這是候選指令與資料的條件式分析，不是目標執行。

## ELF 與來源限制

既有 `scripts/verify-sparse-resident-link.py` 將固定來源 map 的 17 個分段以 `.incbin` 建成 RISC-V 物件，再依原地址連為 `NOT-FLASHABLE-sparse-reference-{c,cpp}.elf`；它檢查分段雜湊、沒有 PT_LOAD 和上述缺口。這是**後製診斷 ELF，不是上游原始 ELF**，不提供缺失 bytes；只放入口四 bytes 也能通過鏈結，並不證明啟動完整。本工作未取得可重跑該連結的原參考目錄及工具鏈，也未聲稱重建了該 ELF。

查詢同一固定提交的 GitHub recursive tree（未截斷）：`EVT/EXAM/BLE/LIB/` 提供 HEX、header、`libwchble.a` 等，沒有 resident 原始 ELF；整棵樹的 ELF 不因此被認定為此 HEX 的來源。未找到可證明可補末端的原始 blob，也不能由這個查詢排除其他未公開工件。HEX 生成時為何沒有這筆記錄，缺乏原始 ELF、link map 或生成命令，無法確定；不能將 inclusive copy 與 HEX 末端的差異歸因於已證實的工具 bug。無 V1.40 借值或產品 gate 修改。

## 重跑

```sh
python -B analysis/v131-startup-source/check.py
python -B analysis/v131-startup-source/test_check.py
```

檢查固定 HEX、重新計算兩段雜湊、重用 `analysis/resident-entry-reference-2026-10-21/source/inspect-source.py` 的指令解碼，並分開報告抽取缺漏和源檔缺失。測試涵蓋真實來源、合成缺口分類、損壞／重疊／EOF、雜湊變造及 inclusive branch 變造。所有測試離線，不輸出填洞映像、不連接裝置；未證明實機 resident、ABI、硬體啟動或可刷性。
