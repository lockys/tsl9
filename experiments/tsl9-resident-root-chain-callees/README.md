# 根函式鏈的八個具名缺口與兩個 helper

[English](readme.en.md) · [前輪根函式鏈](../tsl9-resident-record-root-chain/README.md) · [排程配置契約](../tsl9-scheduler-allocation-contract/README.md)

[C/C++](resident_root_chain_callees.c) 新增 **10 個完整候選 SDK 本體／1,064 bytes／352 條指令**，供應前輪八個具名缺口及兩個實際 callee。保留原執行 context；不是 HOST API 或原廠 C 原始碼。

| 原始半開範圍 | Bytes／指令 | 最大自身 frame |
| --- | --- | --- |
| `0x55D00..0x55D3C` | 60／21 | 32 |
| `0x55D3C..0x55DEA` | 174／55 | 0 |
| `0x5605C..0x56086` | 42／14 | 0 |
| `0x560AA..0x560B2` | 8／4 | 0 |
| `0x56326..0x5649C` | 374／120 | 48 |
| `0x56716..0x567BE` | 168／50 | 16 |
| `0x57B28..0x57B7C` | 84／33 | 32 |
| `0x63966..0x639CA` | 100／37 | 0 |
| `0x6DEC2..0x6DEEE` | 44／15 | 0 |
| `0x43ED2..0x43EDC` | 10／3 | 0 |

實際 C11／C++17 物件相同；85 個正尺寸 FUNC、56 筆直接控制重定位，12 個 Xwchc ports。全部 bytes 在原位址正規化後吻合；完整 CFG 可到達，含延後配置 frame 的各路徑，原始出口皆無殘留自身 frame。第一個 RET 後可達的分支保留。

## 關鍵證據與限制

- `0x55D38 → 0x43874` 保留原始 no-link tail、RA 恢復與 32-byte frame 釋放。A0 由 LUI／ADDI 組成 **`0x56CDC`**，此位址沒有供應本體，實體 CODE-pointer 角色也未證明；沒有因具名符號解析完成就隱藏它。
- `0x567B4 → 0x43414` 亦保留 no-link tail。原函式有延後配置 frame 的路徑；只證明原出口沒有殘留自身 frame，不宣稱每條 tail 路徑都先配置過 16 bytes。
- `0x56078` 的原始有號 `DIV`、`0x6DEC2` 的原始變數移位都保留指令埠；沒有加入除數非零或 shift count 範圍假設。`0x560AA` 只確認對原指標 byte+12 清除 bit2／bit3，不推定硬體功能名稱。
- `0x43ED6` 將原 A0 的 32-bit word 寫至 `0x20003244`；沒有讀取 live 值或推定其實體用途。前輪兩處 callback 及其他原始記憶體／回呼／初始化不確定性仍保留。

這份候選部分連結為 **35,150 CODE + 256 DATA bytes／12,133 指令**，2385 FUNC、1904 relocations。四個新匯入皆有真實既有本體；具名 UND 從 8 降至 **0**。**零具名 UND 不代表 raw pointer、callback、實機 ROM／RAM／IRQ 或執行環境已閉合。**

## 讀取器與驗證

實際 C／C++ 組合都有 **4,147 sections**，超過舊 v6 的 4,096 上限。[v7](elf_reader-v7.py) 只把上限提高至 8,192 並更新說明。舊 v6、ownership-v2、compare-v2 保持原樣；新 [ownership-v3](verify-ownership-v3.py)／[compare-v3](compare-readers-v3.py) 僅切換讀取器與對應固定 hash。驗證器逐字核對這些變更，並與另一個獨立 ELF 讀取器比較所有 section 欄位／bytes、符號與重定位。

證據：[audit-result-v1.json](audit-result-v1.json)、[evidence-v1.json](evidence-v1.json)、[summary.json](summary.json)、[frames_abi.c](frames_abi.c)。原 APP 159 個 C/H 與 **95.54% 靜態 byte 覆蓋**不變，不是功能完成度。實機 ROM／RAM／ISA／IRQ、Flash／OTA 與全域初始化仍未證明；啟動來源仍缺 4 bytes。**沒有新增 BIN，尚不可宣稱可刷。**

## 重驗現有產物

需本機保存的雜湊參考、前序原生產物及這輪部分連結測量收據。下列是現有產物的唯讀重驗流程；不會下載參考或自動補齊建置產物：

```sh
python experiments/tsl9-resident-root-chain-callees/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-resident-root-chain-callees/build/native-v1
python experiments/tsl9-resident-root-chain-callees/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

沒有執行目標、HOST 模型、ISA 模擬或硬體。可新增方向：離線數值 flag／callback 參數來源解碼；尚未實作或驗證硬體功能。
