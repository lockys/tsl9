# Mode 狀態寫入來源

[English](readme.en.md) · [上一輪查表合約](../tsl9-third-provider-lookup-contract/README.md)

離線核對 8 個完整原始函式，合計 **3,104 bytes／1,023 條指令**，與既有 C／C++ 原位址 ELF 相符。這輪沒有新增韌體程式碼或可刷寫 BIN。

## 已確認

以下地址以 APP 名目起點 `0x8000` 與原始暫存器環境計算，實體 RAM 映射仍未確認。

- `0xD05C..0xD07C`：依序寫入 `0x2000BF38..0x2000BF3B`，值為 `1`、`low8(A0)`、`low8(-A2)`、`low8(A1)`。mode 寫入在 `0xD06E`，沒有本地範圍檢查。
- 已選 69,412-byte CODE 中，直接編碼指向此入口的轉移共五處。完整 CFG 證明下表中的常數引數；這不涵蓋間接轉移或排除的 CODE。

| 呼叫／尾轉移 PC | mode 引數 |
| --- | --- |
| `0xA224` | 3 |
| `0xAC6C` | 1 或 3；定義分別在 `0xAC12`、`0xAC64` |
| `0xD528` | 5 |
| `0xE1EA` | 3 |
| `0xE6E8` | 3 |

- `0xD0C8` 的四位元組寫入，依三條原始分支設定 `[enable, mode, selector, countdown]` 為 `[1, 2/4/5, 0, 1]`。
- `0xD0EE..0xD104` 將同一狀態地址、`A1=0`、`A2=16` 傳給表槽 `0x40048` 的間接尾轉移。此處只證明引數；未證明該槽在實體硬體上的身分及清零效果。
- `0xE220..0xEBAC` 的 CFG 包含五張原始相對跳表；756 bytes 跳表均與既有正向 DATA 相同，不能把 `jr` 全當成函式退出而省略分支。

## 下一個具體缺口

依 [原始查表公式](../tsl9-third-provider-lookup-contract/README.md)，若讀取時的 mode 為 1 或 3，欄索引的 `&15` 將地址限制在以下兩列。每列 16 bytes 目前均未納入正式 DATA：

| 條件 mode | 半開區間 | 尚缺 bytes |
| --- | --- | --- |
| 1 | `[0x1A088, 0x1A098)` | 16 |
| 3 | `[0x1A0A8, 0x1A0B8)` | 16 |

本輪只核對位址與覆蓋 metadata，沒有讀取這兩列 payload，也未宣稱每一欄實際可達。後續可依這項使用證據，逐列評估 DATA 重建；不能用補齊或別名替代原資料。

## 尚未證明

明確寫入值的局部集合為 1～5，**不是全域 mode 值域**。setter 接受任意 A0 低位元組；alias、間接呼叫、排除 CODE、IRQ／DMA、初始化效果及寫入至讀取期間的一致性仍未封閉。不能因此宣告完整查表 provider 或把 mode 強制限縮。

正式重建仍為 162 個 C／H、73,478／76,800 bytes（**95.67% 靜態位元組覆蓋率**），6 個 APP source provider 未解析。這不是功能完成比例，也不證明啟動、硬體相容或成功刷入。

## 重現

在 repo 根目錄執行：

```sh
python experiments/tsl9-mode-state-writer-contract/check-v1.py
```

[固定輸入](inputs-v1.json) · [驗證收據](verification-v1.json) · [檢查器](check-v1.py) · [待實作診斷構想](feature-candidates.json)

所有核對均為離線靜態分析；未執行 target、HOST model 或 ISA 模擬，未接觸硬體或第三方 API。
