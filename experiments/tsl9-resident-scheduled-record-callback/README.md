# 排程 record callback：0x56CDC

[English](readme.en.md) · [前輪零具名 UND](../tsl9-resident-root-chain-callees/README.md) · [原排程 callback handler](../tsl9-resident-task-callbacks/README.md)

[C/C++](resident_scheduled_record_callback.c) 新增兩個完整候選 SDK 本體：`0x56CDC..0x56D0E` **50 bytes／20 指令**，`0x568F6..0x56972` **124 bytes／42 指令**。兩者最大自身 frame 為 16 bytes，保留 null 分支與原始 context；不是 HOST API 或原廠 C 原始碼。

實際 C11／C++17 物件相同，174 bytes／62 指令、16 FUNC、10 direct relocations、5 個 Xwchc ports 全部核對。唯一匯入 `0x5E3A8` 已有真實本體。唯一 CODE 所有權與獨立 ELF 讀取器核對後，組合為 **35,324 CODE + 256 DATA bytes／12,195 指令**，2401 FUNC、1914 relocations、4173 sections；具名 UND 仍為 0。

## 位址如何成為 callback

[provenance-v1.json](provenance-v1.json) 重新核對七個完整本體的 **1,158 bytes／407 指令**，建立以下條件式來源：

1. `0x55D00` 將 A0 設為 `0x56CDC`、A1 設為原 record 指標、A3 設為 record+40，恢復 RA／釋放 frame 後尾跳至 `0x43874`。
2. `0x43874` 在原 helper 回傳非零的寫入路徑，將 `0x56CDC` 存至選定記錄 word0、record 指標存至 word4，並輸出 ID byte。表格指標槽為 `0x2000322C`，stride=12，掃描 ID16..47。
3. 若 `i=16*t+k`、t 為 1 或 2、`0≤k<15`，handler `0x43326` 收到單一 event `1<<k` 時，計算相同的 `table+12*i`，取 word0 作為間接目標、word4 作為 A0，在 `0x43390` 呼叫。

這需要有效且不重疊的記憶體、相容初始化／private ABI、表格與 record 維持穩定、helper 正常返回，且 IRQ／重入不替換綁定。初始化計數為 0 的原路徑會將 task slots1／2 設為 `0x43326`，但未證明全域初始化一定早於 dispatch，也沒有觀察 live 綁定或 timer 投遞。

**bit15 會走訊息分支並返回，不進入該次 callback 呼叫。** 因此 ID31／47 不在這項 callback 路徑證明內；尚未確認原 timer／配置流程是否會排除這些 ID，不能宣稱它們一定無法使用。原始行為未修改。

## 本體做了什麼

- `0x56CDC` 的 A0 為零時直接返回。非零 record 的 byte+15 bit1 決定傳給 `0x568F6` 的 A1：zero→62、nonzero→8。正常呼叫後，寫 byte+43=`low8(A0)`、byte+16=0、byte+40=255。
- `0x568F6` 保留對 `0x5E3A8` 的三個原始訊息呼叫，其中兩個有原條件；寫入 record byte+10／+16=0、byte+84=`low8(entry_A1)`，以及兩個條件式全域清除。其正常返回路徑將 A0 設為 0；**不代表訊息已送達或硬體操作成功**。helper 會讀取 record+288 的 word，配置容量／所有權尚未證明。

## 整份間接轉移盤點

[indirect-inventory-v1.json](indirect-inventory-v1.json) 對實際 C／C++ 物件、原 SDK 指令與重定位做唯讀盤點：169 個 return 編碼、146 組可核對的 AUIPC／JALR 固定轉移、**51 處需另外分析綁定的 register transfer**。51 不是缺失函式數，亦未推翻先前條件式綁定證據。61 組落在候選數值區域的相鄰 literal 指令序列，只代表編碼出的位址，不自動證明 function-pointer 角色。

零 UND、條件式來源與原 PC-tag 中已有本體，都不代表已完成原位址載入／實機執行。證據：[audit-result-v1.json](audit-result-v1.json)、[evidence-v1.json](evidence-v1.json)、[summary.json](summary.json)。原 APP 159 個 C/H 與 **95.54% 靜態 byte 覆蓋**不變，不是功能完成度。ROM／RAM／ISA／IRQ、Flash／OTA、callback 效果與啟動來源 4-byte 缺口仍未閉合。**沒有新增 BIN，尚不可宣稱可刷。**

## 重驗

需保留 spec／evidence 雜湊所列的本機參考、前序產物與這輪原生物件；不會自動下載或操作硬體：

```sh
python experiments/tsl9-resident-scheduled-record-callback/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-resident-scheduled-record-callback/build/native-v1
python experiments/tsl9-resident-scheduled-record-callback/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
python experiments/tsl9-resident-scheduled-record-callback/indirect-inventory-v1.py
python experiments/tsl9-resident-scheduled-record-callback/provenance-v1.py
```

可新增方向：唯讀 event-route／message-bit 診斷。尚未實作，不發送硬體控制或推定原 ID 配置政策。
