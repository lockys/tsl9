# Task 0 記錄 callback 的 C/C++

[English](readme.en.md)

新增完整 RAM callback **`2000138E..200013E8`，90 bytes／35 條指令**。其來源為候選 SDK Flash `415FE..41658`，依既有啟動 copy mapping 對應 RAM；**實機採用此 ROM／mapping 尚未證明**。

`56716` 的實際無連結尾跳 `567B4 → 43414` 明確傳入 callback `2000138E`。`43414` 掃描前 16 筆、每筆 12 bytes 的空記錄，正常配置後分別寫入 callback、參數及清理模式（offset 0／4／8）。記錄陣列指標儲存於 RAM `2000322C`。

當排程器以 task ID 0 與對應 event bit 進入 `432A4`、指定記錄及指標維持穩定時，`432EA` 會以記錄的第二個 word 作 A0，呼叫 `2000138E`。非零 callback guard、全部指標定義及完整 CFG 已核對；初始化順序、記憶體有效性與 live 值仍未觀察。

消費端索引是 `16*taskID+k`，但 callback 後的第三 word 檢查使用 `k`。**在 taskID=0 且陣列 base 穩定的情境，兩者才對應同一筆記錄**。第三 word 從 callback 返回後重新讀取的全域 base 取得；若零則清除原選取記錄的 callback／參數，非零略過。這不是回呼替換、並行安全或一般一次性語意的證明。

C11／C++17 實際物件相同；90 個原位址重編碼 bytes、完整 CFG／自身 frame、獨立 ELF readers 與非載入式合併通過。累計 **36,852 CODE＋392 DATA bytes／12,721 條指令**。

| 尚未提供本體的真實 callee | 來源 |
|---|---|
| `20001122` | 直接呼叫 |
| `20000D50` | 直接呼叫 |
| `436A8` | 實際 AUIPC／JALR pair |

三個依賴保留為具名 UND；沒有 stub 或假造 provider。新 callback 的全部效果尚未封閉。

**僅目前這份部分 SDK 物件的 51 個 register-transfer sites，各已有至少一種條件情境**（41 個目標／集合、10 個略過／呼叫者條件）。這不涵蓋整份 APP、未提供 callee 內的呼叫或所有 live 綁定，不能視為執行期閉合或功能完成率。

原 APP 靜態覆蓋率維持 **95.54%**。啟動來源 4 bytes、實機晶片／ROM／RAM／IRQ／Flash／OTA 與完整功能相容性仍未確認。未執行目標、模型、模擬器或硬體；**未產生 BIN，尚不可宣稱可燒錄**。

[C/C++](resident_task0_RAM_callback.c) · [原始指令](evidence-v1.json) · [來源與註冊證據](provenance-inputs-v1.json) · [檢查器](audit-v1.py) · [收據](audit-result-v1.json) · [摘要](summary.json)

在專案根目錄，以本機保留參考檔、物件與已核對的 LLVM 唯讀重驗：

```sh
python3 experiments/tsl9-resident-task0-RAM-callback/audit-v1.py --tool-dir "$LLVM_BIN"
```

Windows 可改用 `py -3`；公開文字收據不能替代原物件與參考檔。
