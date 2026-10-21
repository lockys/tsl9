# V4.1.60 Flash 函式的可讀 C/C++ 重建

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本模型固定對應 ID2966、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，
不修改或混用舊 Runtime／BOOT 的 `flash_page.c`。
六個函式已實際以 C11 與 C++17 編譯及嚴格連結，保留正常返回時的非標準暫存器結果、
32-bit volatile 存取與原生無上限的 busy 輪詢。原生程式未曾執行。

| 入口 | 功能 | 原始 bytes | C/C++ bytes |
|---|---|---:|---:|
| `9C0A` | 一個 256-byte quarter 的控制流程 | 64 | 64 |
| `18E90` | 寫入 status | 8 | 8 |
| `18E98` | 四次 unlock key 寫入 | 30 | 30 |
| `18EB6` | fresh CTRL read／設定 lock bit | 14 | 14 |
| `18EC4` | 對齊、erase 控制及輪詢 | 46 | 46 |
| `18EF2` | 64 次 fresh word read／write／輪詢 | 100 | 94 |

預設只執行合成主機測試，不需要 LLVM 或硬體：

```sh
python3 -B experiments/tsl9-v4160-flash-native/verify.py --project-root . --language both
```

`verify.sh` 接受相同參數。原生編譯入口與限制見分析案例的 `implementation/readme.zh-TW.md`；
發布目錄使用 `analysis/v4160-flash-native-2026-10-22/`，原始工作目錄使用
`apk-analysis/tsl9-v4160-flash-native-2026-10-22/`。

每個主機測試及六個編譯負例都先檢查 PE／ELF／thin Mach-O 的機器及位元寬度，
以目前 Python 自身執行檔與執行期指標寬度辨識可用架構，不從待執行檔推測主機。
RISC-V ELF243、未知及不符格式在 subprocess 啟動前拒絕；唯讀 replay 重讀七個執行檔。
macOS 目前要求 thin Mach-O Python，拒絕 universal／fat Python；Linux／macOS fixture
只驗證標頭解析，並非在該 OS 實際執行。

主機 provider 只處理數值位址及記憶體內測試資料。未知條件、未知位址、HALT／TRANSFER、
輪詢診斷上限均保留已觀察效果，不補做 lock／CSR set，也不假裝原生有 timeout。
暫存器輸出契約只適用於正常返回；非返回途中每個原始 GPR 狀態未證明等價。

SP+12 的來源指標與 RA／S0／S1 都會重新讀取。A0 返回對齊後的目的地，不是成功旗標；
A2 不是輸入長度。helper 沒有新增目的地範圍檢查，外層 OTA 的範圍不能套用到一般 helper。

`program` 剩餘的 6 bytes 未取得整合所有權，不能自動補 NOP 或當作空間使用。
保存順序、程式時序及非返回路徑 GPR 前綴仍有差異。本輪不產生 BIN，不更改既有 IRQ 映像，
也未證明晶片、實體 Flash、ROM、開機或 OTA 相容性。`build/` 保留本機證據，不隨來源發布。
