# 0x58498 根函式與真實相依鏈

[English](readme.en.md) · [前輪雙尾跳](../tsl9-resident-record-transition/README.md) · [原 APP callback 條件證據](../tsl9-original-callback-provenance/README.md)

[C/C++](resident_record_root_chain.c) 新增 **10 個完整候選 SDK 本體／1,700 bytes／572 條指令**。保留原 context；不是 HOST API 或恢復出的原廠 C 原始碼。

| 原始半開範圍 | Bytes／指令 | 自身 frame |
| --- | --- | --- |
| `0x58498..0x585C8` | 304／104 | 16 |
| `0x58462..0x58498` | 54／20 | 16 |
| `0x5784A..0x57862` | 24／9 | 0 |
| `0x59D3E..0x59E3E` | 256／84 | 32 |
| `0x59E64..0x5A004` | 416／128 | 32 |
| `0x5E3A8..0x5E40E` | 102／39 | 32 |
| `0x57962..0x57A1E` | 188／64 | 16 |
| `0x57A4A..0x57AC4` | 122／43 | 16 |
| `0x57A1E..0x57A4A` | 44／15 | 16 |
| `0x578A4..0x57962` | 190／66 | 32 |

實際 C11／C++17 物件相同；113 個正尺寸 FUNC、94 relocations（76 個直接控制、9 組 far call）。40 個 Xwchc 指令埠按官方定義與既有 52 個正例核對。全部 bytes 在原位址正規化後相同；完整 CFG 可到達，自身 frame 在出口平衡，早期 RET 後的可達分支保留。

## 本輪發現

- 實際 caller `0x588B4` 在 `0x5895E` 呼叫 `0x58498`。根函式的 `0x585BA → 0x58462` 保留 no-link tail，先恢復參數／RA、釋放 16-byte frame。
- `0x59E3A → 0x56716` 與 `0x5E3F8 → 0x43208` 亦保留各自的 32-byte frame 恢復與 no-link tail。前者目標仍是真正未解析函式；後者已有真實訊息 send 本體。沒有把 tail 改為普通 C call。
- lookup `0x5784A` 從 `0x20003454` 讀取 head，以節點+8 的 unsigned halfword 比較完整 A0，經節點+0 前進。沒有擅自截斷 A0；有效記憶體、無環與終止性尚未證明。
- `0x59E08`／`0x59E16` 都從 `0x20003220` 重新讀取 callback。第一次經 null guard，呼叫參數為 A0=13、A1=record+152 的 word；第二次為 A0=14、A1=record+156 的 word，原碼沒有第二次 null guard。兩個指標值、callback 本體、副作用與事件語意仍未確認；沒有讀取 live record，也沒有自行補 guard 或假 callback。

八個匯入已有真實既有本體。供應 `0x58498` 後，實際揭露 **8 個新的具名未解析入口**：`0x55D00`、`0x55D3C`、`0x5605C`、`0x560AA`、`0x56326`、`0x56716`、`0x57B28`、`0x63966`。所以目前具名缺口由 1 變為 8，另有本輪 2 處原始 callback；這是展開呼叫鏈的結果，不是用 stub 隱藏相依。

唯一 CODE 所有權與兩個獨立 ELF 讀取器核對後，候選組合為 **34,086 CODE + 256 DATA bytes／11,781 指令**，2300 FUNC、1848 relocations。原 APP 159 個 C/H 與 **95.54% 靜態 byte 覆蓋**不變；這不是功能完成度。

證據：[audit-result-v1.json](audit-result-v1.json)、[evidence-v1.json](evidence-v1.json)、[summary.json](summary.json)、[frames_abi.c](frames_abi.c)。候選 SDK 與實機 ROM 身分、RAM／ISA／IRQ、Flash／OTA、全域初始化與 callback 效果仍未證明；啟動來源仍缺 4 bytes。**沒有新增 BIN，尚不可宣稱可刷。**

## 重驗

備妥 spec／evidence 所列的雜湊參考、前序產物與本機工具，不會自動下載。從專案根目錄執行：

```sh
python experiments/tsl9-resident-record-root-chain/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-record-root-chain/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1 --output audit-result-v1.json
```

建立名稱須尚不存在。已有產物時，第一行改用 `--replay experiments/tsl9-resident-record-root-chain/build/native-v1`，第二行移除 `--link-trial` 與 `--output`。沒有執行目標、HOST 模型、ISA 模擬或硬體。

可新增方向：離線 callback／lookup 來源追蹤與初始化診斷。尚未實作；不推定 live callback 綁定或發送硬體控制命令。
