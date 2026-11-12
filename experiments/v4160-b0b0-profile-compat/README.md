# V4.1.60 `0xb0b0` profile compatibility witness

這是隔離的 profile 差異紀錄，不是正式 build 或替換提案。`leaf.c` 的 SHA-256 是 `87e2f32124ff79e6e034845c0edb9ed33dc9b3dc96a491cf46eab279433a8884`；以下六次隔離編譯與連結結果是主程序先前觀察，**本目錄的 Python 不會重跑或獨立驗證這些編譯結果**。

## 先前觀察

基礎 flags 取自 `scripts/verify-curated-source.py` 的 `queue-consumer-a0-a5`：RV32 `rv32imac_zicsr` / `ilp32`、`-Oz`、停用 machine outliner、freestanding 等 flags；對所有 `1 <= N <= 31` 且 `N` 不在 `{10,11,12,13,14,15}` 加 `-ffixed-xN`。分別以 C11 和 C++17 編譯（C++ 另有 `-fno-exceptions`）。三組各兩種模式，共六次，兩種模式各組輸出相同。共同 link 選項為 `--no-relax --section-start=.text=0xb0b0 --defsym=destination=0x2000beeb -e tsl9_record_dispatch_provider_b0b0`。

| 相對基礎 flags 的附加選項 | 觀察到的 linked `.text`（10 bytes） | 相對 reference |
|---|---|---|
| 無 | `b7c50020a385a5ee8280` | 不同 |
| `-mcmodel=medany -fno-pic` | `97150020a38da5e28280` | 不同 |
| 上述兩項加 `-ffixed-x11 -ffixed-x12 -ffixed-x13 -ffixed-x14` | `97170020a38da7e28280` | 相同 |

靜態欄位解讀：第一組為 LUI x11、SB x10 到 x11-0x115；第二組為 AUIPC x11、SB x10 到 x11-0x1c5；第三組為 AUIPC x15、SB x10 到 x15-0x1c5。各以 `0xb0b0` 計算目標均為 `0x2000beeb`，末尾皆為 `c.ret`。這只是局部欄位解碼，並非實際執行。

## 參考與界線

參考 image 為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，映像基底 `0x8000`。`[0xb0b0,0xb0ba)` 固定 bytes `97170020a38da7e28280`，視窗 SHA-256 `e3f6cec8c02b5619561c69f571f2b440db3d1b264b672e0f7520483a03dcf7eb`。正式 owner 來源 `experiments/tsl9-record-helpers/src/record_helpers.v1.c` 的 SHA-256 為 `deebd11bf4d9f852eade96fb581004ae2edbbbc14e3fbd11c5811bcd64e9e2f6`。

附加 flags 本身改變了正式 profile，這不是正式 build。`destination` 是外部符號、以 linker `--defsym` 提供的 witness，不是已證實的正式資料 owner。正式 owner 是 `void(void)`、`noreturn` 的 assembly private regions；實驗則是 `uint32_t(uint32_t)`。即使符號同名，也不能當作 C 類型互換；兩份同名定義不可一起連接。正式替換仍須另證 ABI、符號 ownership、linker 與 metadata 等；局部相同 bytes 不能證明完整等價。

## 離線靜態測試

從 repo 根目錄執行：

```text
python -I -S -B experiments/v4160-b0b0-profile-compat/test_static.py
python -I -S -B -O experiments/v4160-b0b0-profile-compat/test_static.py
```

測試 source、owner 與 image hash，單獨核對 reference 視窗，並對三組固定 bytes 做簡單欄位解碼。逐 bit 突變與截斷直接測 byte／欄位／視窗檢查，不讓整檔 hash 先擋住負例；窗外突變則保持視窗有效但使 image hash 失敗。使用 `unittest`，`-O` 不移除檢查。

Python 僅驗證固定值與本地參考檔案，不重跑編譯或連結、不檢驗 ELF 真實來源、不執行 C/target、不模擬 ISA，也不證明完整等價或硬體行為。
