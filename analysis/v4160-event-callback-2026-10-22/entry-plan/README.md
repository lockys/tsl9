# callback 註冊與緩衝區參數的靜態來源

[English](readme.en.md)

本節讀取官方 ID2966 V4.1.60 的原始 bytes，核對初始化 `0x8E88..0x9008`（384 bytes）與 callback `0x8614..0x888C`（632 bytes）的完整雜湊，再解析二十七個指定指令的真實運算元。不是 CPU 狀態模型、目標執行或 ROM 語意證明。

## 已確認的來源事實

- `0x8E9C/0x8EA0` 的 AUIPC／ADDI 形成 A0=`0x2000B18C`，A1=0、A2=2124；`0x8EA6` 透過 A5 間接呼叫，返回位址 `0x8EA8`。2124 恰為兩個 1062-byte 範圍的總長。A5 先於 `0x8E90` 從 S0+`0x48` 載入，而前面的 LUI 將 S0 設為 `0x40000`。這些參數像初始化操作，但未知 callee 的實作尚未證明會填零或遵守候選 SDK 型別。
- `0x8EC8/0x8ECC` 的 AUIPC／ADDI 形成 A0=`0x8614`，接著 `0x8ED0` 透過 A5 間接呼叫，返回位址 `0x8ED2`。A1 與後續引數仍是先前不透明呼叫後的 live 殘值，不能自行宣告它只有一個參數。
- `0x8ED2` 實際執行 byte store，把回傳 A0 的低八位寫到 `GP_after+0x9D`。未證明該呼叫保存 GP；不能將地址默認為 entry GP+`0x9D`。

第二次 A5 載入位於 `0x8EC4`，真實公式為 `LW(S0_live+0x80)`。中間已有數個直接與間接呼叫，只有在它們保存 S0 時，slot 才是候選 `0x40080`。上述來源支持「callback 地址被交給一個 ROM 間接呼叫，回傳 byte 被保存」；不等於已觀測註冊成功、callback 被執行或 BLE 實際送出。

同一初始化中，`0x8F82/0x8F86` 與 `0x8F98/0x8F9C` 也各形成 A0=`0x8614`，在 `0x8F8A/0x8FA0` 呼叫。回傳 byte 分別存入 GP_after+`0x94/0x98`；隨後以 halfword store 將 S1_live 寫入 GP+`0x96/0x9A`。雖然 `0x8F7A` 先將 S1 設成 -2，但中間有不透明呼叫，因此初始 halfword 值為 `0xFFFE` 仍以 S1 被保存為前提。這些位置與 callback 比對的兩組 context／connection 欄位相符；不證明候選 ROM 註冊函式的真實型別。

## 驗證與限制

callback 也為既有「更新等待原因」提案增加可追查的來源位置：`0x87A6` 的回傳零分支、`0x87C8/0x87CA` 的最低位元判斷，以及 `0x8814` 的非零分支，最後都可能走向重試路徑。`0x87F8` 只證明傳入 context、2、2，沒有證明時間單位是毫秒。成功路徑則在 `0x8824` 更新 16-bit 已處理長度，再提交值為 1 的事件。這可用於設計離線診斷，但尚未新增 App UI 或硬體功能，也不能把未知 ROM 回傳碼命名為已確認的藍牙錯誤。

```sh
python3 -B analysis/v4160-event-callback-2026-10-22/entry-plan/check.py --firmware /absolute/ID-2966-V4.1.60-decoded.bin --report /absolute/new-registration-report.json
```

研究工作區對應入口在 `apk-analysis/tsl9-v4160-event-callback-2026-10-22/entry-plan/`。二十七個實際運算元位元變異直接進入運算元檢查，繞過檔案雜湊閘門，以確認不是只測整檔身分。報告只能新建，原始 BIN 不被修改。

REA 6.4.0 MCP 本次可連線，但 Windows 原生分析 provider 仍未配置：Ghidra、IDA 缺少設定，Hopper 不支援此主機。因此指定指令另外以既有 LLVM 靜態反組譯交叉核對；沒有安裝工具、執行或模擬 RV32、網路呼叫或硬體操作。完整初始化語意、原機 ROM／BOOT 與 OTA 仍待證。
