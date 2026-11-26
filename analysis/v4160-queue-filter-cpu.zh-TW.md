# v4.1.60 `0x82d2`：組包條件與非零返回的差別

2026-11-26。原廠 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本次離線執行 `0x82d2..0x838e` 原指令，使用已固定的 SDK copy reference；不操作設備、不證明 installed binding。對照既有 [queue_filter.c](../src/native/receive/queue_filter.c)，本批新增的是行為驗證，沒有新增 C 重建函式。

## 不是「非零即已轉送」

函式查看名義表基址 `0x2000c794` 的兩個位置，索引 stride 4。每個位置讀取 `+2` halfword handle、`+5` kind、`+4` flag。handle=`0xfffe`、kind 不等於 2、或 flag 為零就跳過。

通過這三個檢查時，`0x832c` **先把完整非零 flag 保存到 S4，再檢查 snapshot 長度**。長度大於 8 時不 copy、不呼叫 `0x8a56`，但 S4 已是非零；第二位置若不合格，也不會清掉第一位置留下的 S4。兩個位置走完後返回 S4，不是回傳 request 的成功狀態。

因此本機合成案例可確認：length=9、至少一個合格非零 flag 時，沒有任何 request 仍返回非零。接回 consumer 的原 `0x12cb4` 分支後，該值會跳下一槽，略過後續 snapshot 分類。不能把非零解讀為已轉送、傳送或 ACK 成功。

## 有效長度的組包

長度 0–8 時，原指令建立：

```text
packet[0] = ((ID >> 8) | (tag << 4)) & 255
packet[1] = ID & 255
packet[2..] = snapshot[3..3+length]
```

指定 SDK helper 以原指令將 payload 複製到 filter 新 frame 的 `sp+6`，前兩個 header bytes 位於 `sp+4/+5`。然後重新讀 snapshot 長度與 table handle，透過原 RV32 C.JAL 呼叫：

```text
0x8a56(handle, 0xc0, sp+4, fresh_length+2)
```

原指令的 `length+2` 沒有再截成 byte；本批固定 snapshot／table 內容，實際測到的 request 長度為 2–10，沒有聲稱已驗證非同步改寫後的值。兩個位置都合格時可提出兩次 request。`0x8a56` 的返回 A0 不決定 filter 結果；測試指定返回 0、1、`0xffffffff` 時，仍返回最後一個通過前三條檢查的 flag。

表 fixture 保留實際 stride 與欄位位移，使用覆蓋兩位置讀取範圍的 10-byte 視窗，沒有把它誤建成兩個互不重疊的 6-byte record。

## 接回 consumer

256 個組合先執行[消費端的原始快照／清 ID 流程](v4160-consumer-detach-cpu.zh-TW.md)，再真正執行 `0x82d2`，不再指定其返回值：

- 非零結果接回原分支、繼續掃描並驗證 caller RA/SP/S0–S7 恢復。
- 零結果只走到 `0x12cb6` 分類入口便停止；分類 handlers 尚未執行。
- 在兩種結果下，queue ID 都已在 filter 之前清除，snapshot 仍供此函式讀取。

仍**不執行 `0x8a56` 本體**：在入口核對完整參數及 packet bytes，再指定正常返回並刻意改寫 caller-saved 暫存器，保留 SP／所有 S 暫存器、stack、table、snapshot、queue、CSR／MMIO。這些是明示測試假設，不是該函式 ABI 或副作用的證明。

## 重現

```powershell
python analysis/test_v4160_queue_filter_cpu.py
python -O analysis/test_v4160_queue_filter_cpu.py
```

只需標準庫、原 APP、既有 V1.31 carrier 與已發布的同目錄依賴；可用 `--carrier <path>` 指定相同身分的檔案，不自動下載。

```text
PASS: 16384 table/length cases; 512 full-flag cases; 75 header/return probes; 256 consumer compositions; sticky nonzero without request; 2 mutations; installed binding UNPROVED
```

16,384 組為兩個位置各八種 handle/kind/flag 通過組合 × 256 種長度。另有完整 flag byte × 長度 8／9 的 512 組、5 個 ID × 5 個 tag × 3 個 request 返回值的 75 組，以及 64 種表格狀態 × 4 種長度的 256 組 consumer 串接。這不是所有欄位數值或實機狀態的全枚舉。

每例比對精確 packet／request 順序、copy 參數、copy 事件數、來源與控制 word 保留、完整 flag 返回與 RA/SP/S0–S9 恢復。記憶體複本分別把長度上界 8 改成 9、把 S4 的預先賦值移除，必須被 request／返回檢查抓出。原 APP／carrier 未變。

共享有限 CPU 增加本函式需要的 RV32 C.JAL、C.OR、標準 SLLI，預設 queue PC 範圍不變。一般與 `-O`、前批 consumer／RX／copy／TX header 檢查均通過。FENCE／CSR 仍採前批明示觀察模型；沒有硬體、中斷、installed provider 或舊封存 README drift 已解的證據。

本批沒有增加 C/C++ 重建 bytes 或重算覆蓋率。接續可追查 `0x8a56` 的本機流程，或零返回後的分類入口；不能將目前的 packet 組裝結果當作設備傳送成功。
