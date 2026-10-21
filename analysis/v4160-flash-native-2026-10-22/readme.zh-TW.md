# V4.1.60 Flash 寫入層的可讀 C/C++ 重建

[English](readme.en.md)

本輪將原廠 ID2966 V4.1.60 的六個 Flash 函式重建為共用 C11／C++17 來源，提供合成主機測試與 RV32 原址元件編譯。原廠 BIN 的 262 bytes／99 條指令是靜態來源證據；沒有執行或模擬原廠／重建 RV32，沒有連接硬體或呼叫廠商 API。

| 函式起點 | 功能 | 原始 bytes | C／C++ 元件 bytes |
| --- | --- | ---: | ---: |
| `0x9C0A` | 四分之一頁寫入流程 | 64 | 64 |
| `0x18E90` | 寫入 status | 8 | 8 |
| `0x18E98` | 依序寫入解鎖 key | 30 | 30 |
| `0x18EB6` | CTLR lock | 14 | 14 |
| `0x18EC4` | 256-byte 對齊擦除流程 | 46 | 46 |
| `0x18EF2` | 64 次 fresh word 讀取／寫入 | 100 | 94 |

原生元件共 256 bytes；status 與 lock 共 22 bytes 與原版完全一致。其他函式核對有序 MMIO、輪詢、正常返回暫存器與 frame；不能稱為所有 bytes 或逐指令狀態一致。流程以 C 寫成，CSR、固定暫存器與明確 JAL 使用小範圍編譯器組語介面。

## 已驗證的契約與限制

quarter 保留 32-byte frame，erase 後重新讀取 `SP+12` 的 source；依序 unlock、status 49、erase、program、lock，操作 CSR `0x800` 的 mask 136。正常結束是無條件設回這些 bit，不是還原進入時的 CSR。正常返回的 A0 是對齊目的位址，不能當成硬體成功碼。program 的正常 A2 為 256，A6 為最後一個 fresh source word，A1 保留。

主機 C／C++ 每語言通過 5 組／481 案例／247,191 斷言，並實際編譯、執行及拒絕六個語義變異。獨立 expected-effect oracle 每語言另有 12 情境／8,964 斷言，並各拒絕 12 個已編譯變異。這些是合成 provider 結果，不是實體 Flash 結果。原生靜態審查每語言核對六個函式、五個 JAL 及 LLVM IR，另拒絕 15 個機器碼與三個 IR 反例。

原生輪詢保持無界；主機 observation budget 只用來停止觀察，沒有把 timeout 偷加到原生實作。未知 provider 值與非返回路徑不能繼續偽造 cleanup 或成功。frame 保存順序與 program 的 A0 對齊時機仍和原指令不同，因此非返回／fault GPR prefix、逐指令與非同步等價仍未證明。

program 的六-byte 差額 `0x18F50..0x18F55` 尚無新的儲存來源，不補洞、不借鄰段、不輸出新 BIN。上一輪 76,800-byte IRQ 離線映像保留原樣，仍是 **NOT-FLASH-VALIDATED**。原機晶片、ROM、安裝中的 BOOT、實體 Flash 行為與 BLE OTA 相容性仍未通過。

## 可攜驗證入口

以下命令由專案根目錄執行。Python 入口可直接使用；`.sh` 是 POSIX 包裝，Windows 本輪結果不代表已在 Linux／macOS 或 shell 執行成功。

```sh
python experiments/tsl9-v4160-flash-native/verify.py --language both
python analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /absolute/path/to/LLVM/bin --language both
python analysis/v4160-flash-native-2026-10-22/callers/inspect_callers.py --project-root . --check
```

主機入口需要 Python 及 C11／C++17 編譯器。原生入口另外需要與工具 pins 相符的 Clang、LLD、LLVM objdump，只編譯並讀取自己的元件。目的地重新編譯、封存 seal 核對與歷史 build 回放是不同的證據；來源原始 carrier 檢查與整合 frontier 的實際物件重讀需另提供其匹配 build。

主機入口在每次啟動合成測試前，先核對產物格式與主機架構，拒絕 RISC-V ELF 與不匹配的執行檔。這只補強測試入口，沒有改動六函式來源。原 `review` 保留補強前的封存內容；[review-v2](review-v2/README.md) 明確綁定補強後入口與新主機收據，作為目前的獨立審查入口。

目前架構檢查以正在執行的 Python 檔案 header 為準；macOS 需要 thin Mach-O Python，universal／fat Python 會先拒絕。Linux／macOS header fixture 只驗證解析分支，不能替代該平台的實際執行結果。

## 證據入口與下一步

- [原始六函式與 ABI](source/README.md)：262 bytes、99 指令與 20 個 raw 語義反例。
- [六個高位址呼叫端](callers/README.md)：84 bytes、24 指令與 60 個語義反例；不推定容量或設定區語義。
- [原生編譯與正常返回審查](compiler-review/README.md)：實際機器碼、IR 與正常返回契約。
- [完整映像整合 frontier](integration-frontier/README.md)：12 筆外部入口、11 筆 owned 重定位與六-byte 差額。
- [既有新功能候選](../v4160-irq-callframe-2026-10-21/feature-candidates/readme.zh-TW.md)：提案與已實作功能分開列示；本輪沒有新增車輛控制功能。

下一步是明確處理原始六個儲存區段、incoming alias 與 11 筆 owned 重定位，再對完整映像做所有區段與匯出 byte 的來源核對。即使離線映像整合通過，仍不能跳過原機啟動／ROM／記憶體／中斷／更新相容性證明。
