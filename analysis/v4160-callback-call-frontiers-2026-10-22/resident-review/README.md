# Resident 候選：兩個 callback slot 的有界證據

[English](readme.en.md)

本 scope 只讀本機已保存的兩份官方 SDK resident 候選，檢查 callback 使用的 `0x40000+0x13C` 與 `+0xD4`。沒有下載、執行 RV32、ISA 模擬、存取硬體、修改已封存程式或產生 BIN。**兩個候選均不等於實機已安裝 resident。**

| 實際 carrier | +0x13C word／直接 helper | +0xD4 word |
| --- | --- | --- |
| embedded V1.40 | 0x4B4EE／0x4B37C | 0x4C25C |
| embedded V1.31 | 0x4B456／0x4B2E4 | 0x4C1C4 |

完整 HEX 與 main sparse segment 的 SHA-256、節錄 bytes／地址／hash 保留於 `review.py`、`evidence.json`。本次只保留每候選296B的有界文字節錄，沒有隨此 scope 發佈整份 vendor ROM。RAM helper 的 source 位移依兩候選分別的 startup-copy 對應：V1.40 flash0x402F0→RAM0x20000040；V1.31 flash0x402B0→同 RAM。這是條件映射，沒有宣稱這些 RAM bytes 實際已被複製。

## +0x13C：封閉短函式，不是 Boolean 門

兩候選均為22B wrapper＋36B lookup。wrapper 的唯一 call 直接到上述 lookup，lookup 無其他 call。依已保存 LLVM `HasVendorXwchc` 定義，wrapper 的原始 `28 21` 條件解為 `qk.c.lbu a0,2(a0)`；不是 r2 預設顯示的浮點 load。lookup 無匹配時返回0；有匹配時 wrapper 讀取 entry+2 的 byte 並 zero-extend，故正常結果範圍是 **0–255，不能縮成0／1**。

已保存 V1.40 header 的 table base 是0x40034，JT66位於+0x13C，名稱為 `GATTServApp_ReadCharCfg`。這支持將 callback 的兩個 gate 解釋為候選 CCC 設定值讀取；名稱本身不證實服務內容或實機身份。原 callback 對第一個 gate 要求 `A0==1`，第二個只要求 `A0&1`：例如結果3會使第一種判斷失敗、第二種成功。保留兩者差異，不把它們合併成 generic link-status Boolean。

這個58B封閉 pair 不讀 GP 或任何 S 暫存器，包括 S4／S7。RA 僅在 wrapper 保存於SP+12、讀回、RET；lookup 僅 RET，沒有把 incoming RA 當數值比較、地址或參數。語義輸入是完整 A0 與 A1 指標；lookup 會先重寫 A2–A5 所需值再使用。**若實際 provider 確實為該候選、採用該 Xwchc 設定，且普通 stack／table／return 記憶體假設成立，則不同 callback call-site RA 數值與 caller S4／S7差異不被此 pair 觀察。** 這不是跨所有 resident 的 ABI 證明，也不消除 callback 自身中間 fault／async／stack-alias 差異。

## +0xD4：本地前沿已讀，深層契約保留未知

header JT40位於+0xD4，候選名稱 `GATT_Notification`。兩候選本地函式均118B，保存／恢復 S0、S1、S2、RA，使用32B frame；本地沒有 GP／S4／S7 operand。它的五個 call 分別為兩個 linked-RAM helpers 及三個更深的 flash routines。

- linked RAM0x20000A1C／0x20000A48 的44B／76B候選 helper 已有界檢查：沒有 nested call，也沒有 S／GP operands；RA僅RET。某些半字讀取仍依賴 Xwchc。
- V1.40 三個未展開目標：0x45228、0x4B82C、0x4EF0A；V1.31：0x45194、0x4B794、0x4EE72。

因此可以說「候選 notification 路徑」，不能宣稱實機真的通知成功，或把三個更深 callee／動態記憶體／SP／S4／S7／RA觀察性視為不存在。沒有為了排除 unknown 而擴展整份 BLE ROM。

## 重播與可攜性

```sh
python3 -B analysis/v4160-callback-call-frontiers-2026-10-22/resident-review/review.py
python3 -B analysis/v4160-callback-call-frontiers-2026-10-22/resident-review/review.py --candidate-root /path/to/existing/wch-resident-candidate-2026-10-21
```

工作區路徑前綴為 `apk-analysis/tsl9-`；發佈路徑為 `analysis/`。Windows可用 `python -B`，或POSIX `review.sh`。**預設不需要vendor檔，actual_candidate_bytes_read=false**，只驗seal與節錄欄位／有限契約／八個來源欄位反例。`--candidate-root` 明確讀固定pin的兩份原HEX、mainsegments與已保存Xwchc參考，核對slots和所有節錄，輸出true；不呼叫r2、不執行目標、不下載缺檔。P可指向D既有的 `analysis/wch-resident-candidate-2026-10-21`，缺少或不同身份會失敗。

`r2-observations.json` 保留十個實際有界靜態命令及其raw view。r2在QK opcode上可能顯示浮點或分裂的invalid bytes，不能單靠那些字串判斷語義；本scope以來源bytes的2／4-byte分界與明示的條件Xwchc欄位解碼作區分。不支持的opcode保持unknown，從不當NOP。
