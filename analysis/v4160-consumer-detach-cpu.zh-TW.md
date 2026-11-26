# v4.1.60 consumer：固定快照、清 ID、再呼叫

2026-11-26。使用本機原廠 APP（76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）與前批固定的 [V1.31 copy reference](v4160-reference-copy-cpu.zh-TW.md)。SDK 身分與設備安裝 binding 仍分開；全程離線，不操作設備。

## 本次確認的順序

原 consumer 從 `0x12c58` 建立 80-byte frame，依序檢查 32 個 12-byte 槽位的 ID halfword。零 ID 直接跳下一個；非零 ID 才執行：

| 原位址 | 作用 |
|---|---|
| `0x12c96` | `csrc 0x800,S2`，此時 S2=`0x88` |
| `0x12c9a..0x12ca4` | fresh-load `[0x4004c]`，以 `(sp+8,slot,12)` 呼叫 copy |
| `0x12ca6` | copy 正常返回後，只將原槽位的 ID halfword 清零 |
| `0x12caa` | `csrs 0x800,S2` |
| `0x12cae..0x12cb0` | 以 `sp+8` 指向的 stack snapshot 呼叫 APP 本機函式 `0x82d2` |

因此 callback 邊界可見：原 queue 槽已標為空，但 stack snapshot 仍保留原 ID 及其餘 10 bytes。長度欄無論為 0、8 或 255，此處都固定請求複製 **12 bytes**，尚未按長度欄裁切。清 ID 不會清掉原槽其餘 10 bytes。

前一批 [RX producer](v4160-rx-reference-queue.zh-TW.md) 是先寫 ID／長度、copy 後寫 tag；這批 consumer 則是先 copy 全槽、正常返回後清 ID、再交 snapshot 給本機函式。兩者順序均由原指令檢查，沒有據此推論真實並行性。

## CSR 僅為數值模型

測試在原 CSR 指令位址停止，核對完整 encoding 與 live S2，再記錄 clear／set 事件；沒有存取硬體 CSR。按普通 32-bit 位元模型：

```text
clear: value &= ~0x88
set:   value |= 0x88
```

這段指令沒有保存原 CSR 值。經過至少一個非零 ID，模型最終為 `initial | 0x88`，不是任意 initial 的還原。全零 ID 掃描則完全不進 CSR／copy／callback。不能把這個數值模型命名成已證實的 IRQ 控制、原子性或實機指令副作用。

## copy 中止時尚未釋放槽位

指定參考 helper 的第三個目的 byte-store 被合成阻擋時，stack snapshot 只有前兩個 bytes（原 ID），其後仍是初始 canary；原 queue 全槽不變，ID 仍非零。CSR 模型只完成 clear，reference 的 `0x4002420c` 控制 word 仍為零；沒有 slot clear、CSR set、callback 或 caller return。

這和 producer 的部分寫入案例不同，因為 consumer 的清 ID 在 copy 正常返回之後。測試沒有用 finally 補造恢復，也沒有把合成停止當成真實 fault／中斷證據。

## 重現與範圍

```powershell
python analysis/test_v4160_consumer_detach_cpu.py
python -O analysis/test_v4160_consumer_detach_cpu.py
```

需要標準庫、原 APP、既有 V1.31 carrier 與同目錄已發布依賴；可用 `--carrier <path>` 指定相同雜湊的 carrier，不會自動下載。一般與 `-O` 均通過：

```text
PASS: 512 slot/ID/CSR cases; 256 length-byte cases; 5 scan patterns; copy-before-clear-before-callback; interrupted prefix; 2 mutations; installed binding UNPROVED
```

512 組為 32 個唯一佔用槽 × 四個非零 ID × 四個 CSR 初值。256 組長度分配至不同槽位，逐例確認整個 12-byte snapshot。五種掃描模式含全空、全滿、偶數槽、奇數槽、三個分散槽；全滿情境依序建立 32 個 snapshot。每次 callback 邊界比對 queue 全部 bytes、所有參考 copy 事件、clear／copy／清 ID／set 順序及傳入的 snapshot 指標。

**不執行 `0x82d2` 函式體**。為檢查後續掃描，明示合成其正常返回非零，保存 SP／S0–S7／stack、不改 queue／CSR／MMIO，只改寫 caller-saved 暫存器，再執行原 `0x12cb4` 分支及掃描／返回。這些是 callback 的測試假設。返回零後的分類與 handlers 不在允許的 PC 範圍內，未由這批驗證。

逐例核對最終 RA/SP/S0–S7 恢復。兩個記憶體複本負向對照分別把清 ID 的 offset 改成 2，以及把 copy count 12 改成 11，必須被 queue／參數檢查抓出。原 APP／carrier 未變，共享解譯器亦未修改。

本批新增 consumer 前綴證據，沒有增加 C/C++ 重建 bytes 或重算覆蓋率。指定參考 binding、地址有效與無非同步干擾仍是前提；設備 provider、真實 CSR／MMIO、callback 實作及後續 handlers 均未由此證明。前批記錄的舊封存 README drift 也仍保留，未宣稱其重播通過。
