# 原 APP RF 狀態回呼綁定

[English](readme.en.md)

將原 APP 的 `174EE` 與十個候選 SDK RF 間接呼叫點串接。核對 **9 個完整 SDK 函式／2,666 bytes／940 條指令**，及原 APP 主初始化、constructor、callback 的 **586 bytes**。本輪沒有新增目標 C/C++、編譯或 BIN。

原 constructor 的 32-byte 設定含 mode `01`、channel `25`（十進位 37）及 offset 16 的 callback `174EE`。候選 `RF_Config` 的兩個實際 far calls 分別清零並複製至 `20003540`；正常完成且欄位未被改寫時，`20003550` 對應 `174EE`。這仍要求實機 ROM／RAM 對應、有效不重疊記憶體與原 private ABI；未觀察實際安裝或執行順序。

| 呼叫點 | 所有到達的 A0 狀態值 | 原 APP callback 路徑 |
|---|---|---|
| `63F26` | 17 | 尾跳 `17442` 重試 |
| `64452`、`64588` | 1／17 | 返回／重試 |
| `64658` | 2 | A1 非零則重試；否則讀 buffer 並比較 |
| `64690` | 18 | 重試 |
| `6534C`、`6553E`、`6555A` | 3 | 返回 |
| `6565E` | 4／20 | 返回 |
| `657AE` | 34／36 | 返回 |

四個呼叫點有分支匯合；共 **14 個實際 pointer loads**。完整 CFG 的有限 may-reaching-definitions 保留全部來源，呼叫保守視為改寫 volatile register；跨 callee 的 saved register 值仍依賴原 private ABI。

`64658` 的狀態 2 在 `A1=0` 時讀 `A2+1`、`+2`、`+3`，至少要求 4 bytes 可讀範圍；**原碼沒有本地長度／null guard**。符合全部比較才以 `A0=0` 尾跳 `173EE`，否則走 `17442`。這不是完整封包協定或呼叫前所有記憶體安全性的證明。

原 byte、已編譯 C/C++ 的原位址重編碼、完整 CFG、自身 frame、APP 來源與非載入式診斷 ELF 比對通過。累計間接呼叫 **50／51 處**具有至少一種條件情境；唯一尚未串接的是 `432EA`。這不是功能完成率或所有 live 綁定皆已解析。

原 APP 覆蓋率維持 **95.54%**；候選組合維持 **36,762 CODE＋392 DATA bytes**。4-byte 啟動來源、實機 ROM／晶片／RAM／IRQ／Flash／OTA 與完整功能相容性仍未證明。未執行目標、模型、模擬器或硬體，**尚不可宣稱可燒錄**。

功能候選：離線 RF 狀態解碼與 callback 路由診斷；目前僅提案，尚未實作。

[檢查器](verify-v1.py) · [證據](evidence-v1.json) · [逐點清單](ledger-v1.json) · [驗證收據](verification-v1.json) · [摘要](summary.json)

在專案根目錄，以保留的參考檔、原物件及已核對的 LLVM 唯讀重驗：

```sh
python3 experiments/tsl9-original-RF-status-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```

Windows 可改用 `py -3`；公開文字收據不能替代實際參考檔。
