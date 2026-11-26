# v4.1.60 callback 註冊入口與非零 payload 返回後流程

2026-11-26。原 decoded APP：76800 bytes，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。延續 [表消費與 9f7a](v4160-callback-dispatch-cpu.zh-TW.md) 及 [9124 表更新](v4160-register-gate-cpu.zh-TW.md)，在有限 CPU 內執行原 APP 指令，僅使用合成記憶體。未知 provider 皆停在入口；下列「正常返回」及資料變化是明示 fixture 假設，不是執行 provider 所得的證據。

## `0x907a` 將消費者交給未知服務

入口 frame16，保存 caller S0/RA，令 S0=`0x40000`。原指令順序如下：

| 步驟 | 可驗證的 APP 行為 |
|---|---|
| 首次呼叫 | 讀 `[0x40048]`，參數 A0=`0x2000be08`、A1=0、A2=180，RA=`0x9096` |
| 首次返回後 | 不檢查返回值或表內容；經仍 live 的 S0 重新讀 `[0x40080]` |
| 第二次呼叫 | A0=`0x901a`，RA=`0x90a4`，SP=caller−16 |
| 第二次返回後 | 依序恢復 caller RA、S0，寫 `U8[GP+166]=low8(A0)`，恢復 SP 返回 |

GP fixture=`0x20004000`。第二次返回 A0 保留完整 word，只有寫入 task byte 時截斷。

**APP 本身沒有清表 stores**。`[40048]` 的參數形狀符合填零用途，但不能由呼叫參數直接證明 provider 的實作。測試明示兩種返回情境：「將180 bytes填零」及「整張表保持」，兩者都繼續呼叫 `[40080]`。因此不能假設 APP 已檢查清零成功。

首個返回假設必須保存 S0=`0x40000`、SP/GP 與 saved frame；第二個返回後 S0 已不再 live，可以故意破壞 S0，原 epilogue 仍從 frame 恢復 caller 值。測試同時破壞 A/T 暫存器，以免依賴不必要的 caller-saved 保存。

在首個返回 hook 中改變 `[40080]`，下一個呼叫確實到達新 target。這只證明 APP 重新載入指標；尚未識別真實 provider，也未證明它儲存 callback 或投遞事件。

## 非零舊 payload：取消與更新依賴不同 live state

原指令把非零舊 payload 傳給 `[0x40068]`。本批沿用「free」作服務邊界名稱，**沒有證明其釋放語意或 ownership**。

| 邊界 | `0x90b0` 取消 | `0x9124` 更新既有 key |
|---|---|---|
| provider 入口 RA | `0x90e0` | `0x91b6` |
| SP | caller−16 | caller−32 |
| 返回後仍 live | S0=index、S1=table | S0=完整flag、S1=index、S2=table、S3=duration、S4=新payload |
| task | 返回後重新讀 GP+166 | 返回後重新讀 GP+166 |
| key | 清零，沒有重新搜尋 | 不重寫，也不重新搜尋 |
| payload | 清零 | 寫入原輸入的新payload |
| 下一個服務 | 重新讀 `[4005c]`，恢復 frame 後尾跳 | 完整flag=0 讀 `[40058]` 呼叫；非零讀 `[4022c]` 尾跳 |

兩條路徑都不檢查 free 的返回 A0，也不重新讀 key、flag 或舊 payload。本批正常返回 hook 保存上述 live state、SP/GP/frame，並破壞 A/T 暫存器。

`0x90e0` 後的可見順序：恢復 caller S0/RA → 讀新 task byte → 清 key → 清 payload → 讀 `[4005c]` → 恢復 S1/SP → 尾跳。尾跳入口 `(A0,A1)=(task,1<<index)`，RA 已為原 caller RA。hook 即使改過選中槽的 key/payload，原 APP 仍清同一槽；flag 與其他槽保持。

`0x91b6` 後則先讀 task，再寫 flag 低 byte、寫新 payload。hook 改過的 key 會保留，包括改成 0；原 APP 不重建原 key、不重新驗證槽位。分支仍使用**完整 S0 flag**，所以 flag=`0x100` 雖儲存 byte=0，仍尾跳 `[4022c]`。延遲量是 `((duration*1000)&0xffffffff)//625`，乘法先截成32位。

測試 hook 也替換 task byte 和下一個服務指標，確認後續確實使用新值。這是可觀察的 APP 依賴，不表示真實 free 會做這些修改。若真實 provider 破壞上述 live S 暫存器，這些條件性結果便不成立；其保存合約仍需由實際 provider 證據確認。

## 驗證與限制

[test_v4160_callback_lifecycle_cpu.py](test_v4160_callback_lifecycle_cpu.py) 沿用已推送的執行器，這批沒有改動共享 CPU 或 C。C 對應已有 `src/native/receive/callback_table.c`、`src/native/receive/scheduler.c`；本批不新增 C 覆蓋百分比。

```text
python analysis/test_v4160_callback_lifecycle_cpu.py
python -O analysis/test_v4160_callback_lifecycle_cpu.py
```

兩種模式皆輸出：

```text
PASS: 1036 original 907a install cases; table cleared AND unchanged return hypotheses; full A0/low8 task
PASS: 23040 cancel/free-return cases; 3000 update/free-return cases; 15 declared-clear/consumer chains; 4 mutations
PASS: exact post-return accesses/stores/live frames; changed task/key/slot hooks explicit; provider code NOT executed
```

覆蓋包括：

- 註冊入口：全部256個 task 返回低 byte，另含高位 word；清表/不清表與替換 install target 的組合。
- 取消返回：每槽、全部256個新 task byte、3個非零舊 payload、2個 event target；hook 改 key 為0或全1，最終仍清原槽。
- 更新返回：每槽、flag={0,1,255,256,全1}、duration={0,1,10000,0x40000000,全1}、新payload零/非零、新task=0/255、原/替換服務target。duration=0 的 fixture 無空槽，因此沿一般既有key路徑。
- 15組「明示清表後 → 原 `0x901a` 空 key 消費」；事件仍由 fixture 輸入，不宣稱 provider 投遞。
- 4個記憶體內 mutation：填零參數180改179、callback參數901a改901c、取消清payload位移8改12、更新flag來源S0改zero。皆由指定檢查拒絕，未將解碼失敗算作成功。

原指令區段 SHA-256（右界不含）：

| 區段 | SHA-256 |
|---|---|
| `0x907a..0x90b0` | `901ef49b5e03e522d166f5ea11ae041f799b6733971e69ad6fc8fb252c6923f8` |
| `0x90e0..0x9110` | `673e6887bbaf419ffea8b64382396df1d04448e682eab72541463f26facf902b` |
| `0x91b6..0x91fe` | `fdad65912090d2884c2d268d9520618007d147602765dfaa1fdf6d3d6ce6bf56` |

尚未釐清的是 resident provider 實際綁定、保存合約、真正的 payload 生命週期，以及 callback 更新 GP+172 後的可達狀態流程。本批沒有執行 fill/install/free/timer/event provider、IRQ 或設備操作。
