# v4.1.60 `0x8a56`：bank 選擇、frame 與事件尾跳

2026-11-26。只使用本機原廠 APP（76800 bytes；SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`），離線解碼並執行 `0x8a56..0x8b6e` 有限原指令切片。不操作設備，不執行未知服務。對照既有 [transport_frame.c](../src/native/receive/transport_frame.c)，新增行為證據而非新增重建 bytes。

## 選擇條件與非固定返回值

入口參數為 `(handle, command, source, length)`。長度以完整無號 A3 比較；大於 1039 就直接 RET，不建立 frame、不讀 GP 資料或槽位、不寫記憶體，A0 保持入口 handle。

有效長度先讀 `U16[gp+150]`，與**完整入口 A0** 比較，且不得為 `0xfffe`。符合才當次讀 `[0x4013c]`，呼叫所載 target，A0=handle、A1=`gp+128`。返回值**精確等於 1** 才選 bank 0。

未選 bank 0 時重新讀 `U16[gp+154]`，同樣比較／排除 sentinel，再重新讀槽位、呼叫服務；返回 1 才選 bank 1。合成 probe 在第一個服務返回失敗後改寫第二個 handle，原指令確實使用新值。

兩個 bank 都未選中時，恢復 frame 並返回當時 A0：若沒有呼叫服務，是入口 handle；否則是最後一次服務返回值。不是固定錯誤碼，也沒有在此處證明 lookup／admission 的真實語意。

## 固定 frame 配置

名義 buffer base=`0x2000b18c`，bank stride=1062。以下 B=`base+1062*bank`：

| 位址 | 原指令寫入 |
|---|---|
| `B+6..7` | marker halfword `0x7f55`，little-endian `55 7f` |
| `B+8` | command 低 byte |
| `B+9`、`B+10` | length 高、低 byte |
| `B+11` 起 | source payload，逐 byte live-read／write |
| `B+11+length` | `(command + length_hi + length_lo + sum(payload)) & 255` |
| `B+2..3` | descriptor halfword `length+6` |
| `B+4..5` | descriptor halfword 0 |

marker 不列入 checksum。測試比對原始 store 順序：先 marker／長度低 byte／長度高 byte／command，再 payload、checksum，最後兩個 descriptor stores；整個兩-bank buffer 其他 bytes 必須保留 canary。

完成後恢復 RA/SP/S0–S3，讀 `[0x40050]` 至 T1，再讀 `U8[gp+148+4*bank]` 至 A0，A1=1，尾跳所載 target。A2 此時是 `gp+148+4*bank` 的地址，不是 bank 索引或 packet 指標。這是事件服務的參數邊界，不是已觀察到的資料發送或 handler 執行。

## 重現與測試

```powershell
python analysis/test_v4160_transport_frame_cpu.py
python -O analysis/test_v4160_transport_frame_cpu.py
```

只需 Python 標準庫、原 APP 與同目錄已發布的有限 CPU；不需要 SDK carrier。一般與 `-O` 均通過：

```text
PASS: 896 handle/admission cases; 1040 admitted lengths; 4 oversized lengths; 5 command probes; fresh secondary lookup; 2 mutations; unknown services NOT executed
```

- 896 組為 7 個完整 handle × 4 種儲存 handle 匹配組合 × 兩服務各 4 種返回值 × 長度 0／8。涵蓋 0、sentinel、`0xffff`、高位不為零的 handle，不把 word load 與完整 A0 比較誤當 halfword 比較。
- 全部 0–1039 的長度都走到組包／尾跳邊界，交替選兩個 bank，核對完整 buffer、checksum、來源逐 byte 讀取與 stores。
- 1040、`0xffff`、`0x10000`、`0xffffffff` 確認裸返回；另有五個 command 寬度 probe 與第二 handle 的 fresh-read probe。

每例核對 lookup 次數、入口參數、返回 PC、GP／槽位／payload 的完整資料讀取順序、caller 保存狀態與尾跳參數。兩個記憶體複本對照分別改錯 marker XORI immediate，以及把第一 bank 的判斷常數 1 改成 2，必須被 frame／返回檢查抓出。原 APP 未改。

## 明確保留的假設

`[0x4013c]` 是指定合成 target；測試停在其入口，供應返回值，刻意改寫 caller-saved 暫存器，保存 SP／S／GP、stack、buffer 與 source。除宣告的第二 handle 改寫 probe 外，服務沒有其他記憶體副作用。入口的 1039 限制只有在這些保存前提下才約束後續 live S0；不能無條件套用到未知實際服務。

`[0x40050]` 僅停在尾跳 target，不執行或替它產生成功返回。沒有真實位址映射、installed slot、IRQ、事件 handler、傳送或 ACK 的證據。本次也沒有將此函式接入 filter；[前批 `0x82d2` 的 request](v4160-queue-filter-cpu.zh-TW.md) 在這個階段仍是兩個分開驗證的邊界。

共享有限 CPU 只新增 XORI 解碼，預設 PC 範圍不變。既有 filter／TX header 等檢查也重跑通過。沒有增加 C/C++ 重建 bytes 或重算覆蓋率；可接續在明示 lookup／event 邊界下串接 filter，或追查 consumer 零返回後的分類流程。
