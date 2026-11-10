# 0x901a 註冊：離線靜態 checkpoint

以遠端 main `b68672237cd1fd58ff6509b3b0f34506a55ce38d` 為基底；此 checkpoint 不宣稱裝置可執行或可刷寫。APP `0x907a` 先透過 `[0x40048]` 請求清除 180 bytes，正常返回且暫存器契約成立時，再將 `0x901a` 傳給 `[0x40080]`，並保存返回值低 byte。候選 resident 的 `[0x40080]` 為 `0x43c4e`；候選註冊函數有容量檢查，失敗回傳 255。候選 scheduler 可透過 handler 表間接派發，但必須先成立 slot 身分、註冊成功、初始化、索引及表穩定等條件；未證明實際 ROM、派發、事件送達或硬體行為。APP 的另一個註冊 `0x19b16` 使用不同 handler 和 GP 欄位，不能推定相同 ID。

## 輸入與來源

* APP：`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，基底 0x8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，已在基底版本。
* SDK 是**外部公開候選**而非裝置讀取：[openwch/ch32v20x 固定 commit ec059e0b18046b111ee850e44f105fcd095e775c](https://github.com/openwch/ch32v20x/tree/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB)。`wchble_rom.hex` SHA-256 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`；本 checkpoint 保存該 HEX 的連續實有區間 `[0x40000,0x6ea66)`，沒有填洞，SHA-256 `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22`。同 commit 的 `wchble_rom.h` SHA-256 `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c`。候選 embedded 版本標記 V1.31，不代表裝置實際版本。
* 逐指令 JSON 與 `src/native/receive/callback_table.c` 已在基底版本；檢查程式內的 `INPUTS` 明列三份 JSON 路徑和 hash。本 checkpoint 無需網路或額外 SDK 才能執行以下驗證。

## 驗證與限制

```
python -B scripts/verify-901a-registration-static.py
python -B -m unittest discover -s tests -p test_901a_registration_static.py -v
```

checker 固定各輸入整檔 hash，檢查 APP 註冊 opcode、scheduler 視窗 hash、候選五個 slot 與三份既有 opcode 記錄對應 source bytes；它不是獨立反組譯或語義證明。測試包含 hash、opcode、slot、截斷與 scheduler 視窗逐 byte mutation 負例，並非全部可能變異的窮舉。僅本機離線資料分析，未接觸設備、執行或模擬目標。
