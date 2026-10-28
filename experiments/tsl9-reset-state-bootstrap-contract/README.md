# APP 清零狀態與候選 bootstrap 寫入範圍

[English](readme.en.md) · [目前正式重建](../tsl9-event-word-table-integration/README.md)

本輪核對現有原始執行層，沒有新增或重編譯韌體。APP 主 reset 的 **138B／37 指令**與目前 C11／C++17 原位址 ELF 逐 byte 相符；五個 SDK bootstrap stage 的 **234B／67 指令、14 個重定位角色**重新解讀通過，且每個實際 native byte 與角色都保留在目前的 SDK 組合中。這些仍是 SDK 候選證據，未確認實機 ROM 相同。

## 已確認的條件式初始化

以原始位址與暫存器環境、有效記憶體、正常執行且無非同步干擾為前提：

- APP 建立 GP=`0x20004000`、SP=`0x20010000`。
- 複製 `[0x1AB60,0x1ABE0)` 的 128B 至 `[0x20004000,0x20004080)`；本輪只核對範圍，不讀取這份初值的內容。
- 從 `0x186EE` 以 word 清零 `[0x20004080,0x2000C958)`，共 8,758 次 store。到達 `0x186F8` 時，下列 bytes 應為零，這不是實機 RAM 讀取結果。

| 狀態 | 半開區間 |
| --- | --- |
| 輸入 counter（GP+176） | `[0x200040B0,0x200040B1)` |
| 四個 sequence state（GP+332） | `[0x2000414C,0x20004150)` |
| 七筆 word 索引（GP+370） | `[0x20004172,0x20004173)` |
| mode 的 enable／mode／selector／countdown | `[0x2000BF38,0x2000BF3C)` |

## 原始 handoff 與 SDK 寫入

APP 在 `0x1872C` 設定 `MEPC=0x9008`，於 `0x18730` 不寫入 RA 地尾跳 `0x40000`。候選 stage 最後在 `0x6DEBE` 執行 **MRET**，使用當時的 MEPC；它不是一般 C return。

候選 bootstrap 的七處明確 memory-store 指令已全部分類，其目的範圍如下。copy／zero helper 的 end 是「包含最後 word」的介面，以下已轉成半開區間；重疊依原碼保留。

| 寫入 | 半開區間 |
| --- | --- |
| RAM slots 0／1／2 | `[0x20000000,0x2000000C)` |
| Seed | `[0x20000010,0x20000040)` |
| 第一次 copy | `[0x20000040,0x20002E74)` |
| 第二次 copy | `[0x20002E70,0x20002EFC)` |
| Zero | `[0x20002EF8,0x20003618)` |
| Loader 自身 16-byte frame 的保守範圍 | `[0x2000FFF0,0x20010000)` |

上述範圍全部避開四組狀態，收斂了已知 bootstrap 的寫入影響。這不涵蓋 APP clock helper、非同步路徑或後續 callback／alias 寫入。第二次 copy 的來源仍缺 `0x6EB2C..0x6EB30` 四個 bytes；它位於 APP 之外，本輪沒有填補或讀取其內容，也沒有把後續 zero 當成來源讀取必定成功。

## 尚未閉合的執行條件

`0x1870C` 的 `CSRRS mstatus` 使用 OR mask `0x1888`，不是把最終 mstatus 指定為該值。依標準 MIE bit 3 解釋，此 mask 設定 MIE 的指令早於 `0x1871C` 的 mtvec 寫入；本輪沒有證明 incoming IRQ 狀態、pending／enable 狀態或無中斷條件。

清零後還會在 `0x18720` 呼叫 clock helper `0x1874A`。其對這些欄位的 noninterference 尚未在本輪證明。要把清零值延伸到 MRET 或第一次使用，還需要 clock、IRQ／DMA／alias、callee 與有效來源記憶體等條件；**沒有證明第一次查表的值、全域 counter／mode 界限或啟動完成**。

舊 SDK native 收據的唯一輸入差異是 manifest。本輪精確重建其 159-source 歷史 manifest，其餘 source／tool／artifact 輸入均保留；沒有直接忽略漂移或宣稱重編全部 SDK。

## 重播

有固定的本機 native 產物與 LLVM 時，在 repo 根目錄執行：

```sh
python3 experiments/tsl9-reset-state-bootstrap-contract/check-v1.py --tool-dir "$LLVM_BIN"
```

[固定輸入](inputs-v1.json) · [驗證收據](verification-v1.json) · [待實作啟動診斷構想](feature-candidates.json)

正式 APP 仍是 **164 個 C/H／95.75% 靜態位元組覆蓋率、六個未解析 source provider**。來源與 native 產物未變；沒有新 BIN、target／HOST model／ISA 執行、硬體或第三方 API 操作。
