# Flash program 的原始尺寸與進入順序重建

[English](readme.en.md)

本輪以共用 C11／C++17 來源取代前一版 program 的 94-byte 實作，實際編譯為原區段所需的 **100 bytes／38 指令**。六個 Flash 函式現在合計 **262 bytes／99 指令**，個別尺寸為 64／8／30／14／46／100。沒有補 NOP、借用鄰段或從舊 BIN 回填六個 bytes；末端 AND、store、return 都來自本輪實際編譯的函式。

## 三個有界來源調整

只把 A0 綁定到對齊結果，仍產生 94 bytes，而且編譯器會把 ANDI 移到初始 CTLR read 之前。接著以帶有 read 相依性的 A0 bridge 固定順序，並在原本兩個階段重新產生 A4 基底，得到 102 bytes。最後把兩個初始輪詢的 mask 結果固定到原始 A5，消除額外的 `LI A5,0`，自然回到 100 bytes。

這些調整均有原始指令角色支持；編譯選項沒有搜尋或改換。三個階段的來源快照、C／C++ 診斷收據會分開保留，不能把 94 或 102-byte 嘗試宣稱為已通過原始尺寸。

## 已通過與尚未通過

實際機器碼的順序是初始 read `+4`、A0 ANDI `+6`、首次 CTLR store `+14`。原版 ANDI 在 `+8`，因此新函式仍不是逐指令一致：舊 `+8` 邊界位於新四-byte 指令中，初始 RMW 也使用 A2 而非原始 A5。完整 GPR／fault prefix、非同步中斷與數值間接進入點仍未證明。

program 的五個已記錄內部迴圈目標位於 `+16/+26/+40/+56/+82`，erase 的內部目標仍在 `+28`；原始私有分支的語義須與實際新 CFG 一起核對。相同尺寸或相同數值位址都不能單獨證明整體等價。

主機 C／C++ 各通過 481 案例／247,191 斷言與六個實際編譯變異。新的獨立 expected-effect oracle 直接對本輪來源編譯，每語言通過 12 情境／8,964 斷言，並各拒絕 12 個已編譯變異。主機執行檔在啟動前後都核對格式與架構；原始與重建 RV32 均未執行或模擬。Linux／macOS 的實際執行結果仍未建立，macOS 目前需要 thin Mach-O Python。

## 入口與證據

```sh
python experiments/tsl9-v4160-flash-entry-order/verify.py --project-root . --language both
python analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /absolute/path/to/LLVM/bin --language both
```

主機入口需 Python 與 C11／C++17 編譯器；原生入口另需固定的本機 LLVM。`.sh` 入口同目錄提供，Windows Python／MSVC／LLVM 通過不代表 POSIX shell 或其他作業系統已執行成功。

- [原始來源與獨立測試](source-review/README.md)
- [原生 ABI 與指令順序](ABI-review/README.md)
- [目前實作、可攜檢查與正式收據](implementation/README.md)
- [十一函式完整映像來源規劃](image-plan/README.md)

來源規劃已核對 691 個配置、四個需精確過濾的載體單元、8,259 筆範圍外 RELA 與 20 筆外部起點引用；42 個完整原生編譯單元仍是下一階段規劃。本輪沒有新的完整映像或 BIN，先前所有映像保留原樣。

已記錄更新接收流程的差異，也可用來評估本地更新檔檢查與報告匯出功能；此處是提案，尚未實作 App 更新流程或新增車輛控制功能。原機晶片、ROM、BOOT、實體 Flash、中斷及 BLE OTA 相容性仍未通過，不能宣稱可燒錄。
