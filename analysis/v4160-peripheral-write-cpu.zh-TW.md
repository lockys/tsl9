# v4.1.60 `0x18ca4` handler 與派送串接

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批執行 `[0x18ca4,0x18d78)` 原指令，資料與 MMIO 均為本機 bytearray，沒有接觸設備。

## bank 選擇與返回值

輸入 A0 是暫存器區基址 T，A1 是 record 指標 P。每一步重新讀 `U32[T+8]`：

1. bit 26 非零，選 bank 0。
2. 否則再讀，bit 27 非零，選 bank 1。
3. 否則再讀，bit 28 非零，選 bank 2。
4. 三次均未命中，返回 A0=4；不讀 P、不寫資料。

穩定 fixture 的優先序為 26→27→28；不是一次 snapshot。測試另外供給 512 組三次讀值序列（每次三個選擇 bit 的全部組合），確認前一次讀值不被當成後一次的值。

正常選中時返回 A0=bank，故 A0=0 也是正常 bank 0 結果。函式沒有 callee 或 stack frame，RA／SP／GP／S／A1 等未用暫存器保持；A0、A2–A6 可被改寫。這不是實體傳輸完成或實際暫存器穩定性的證明。

## 選中後的精確效果

令 B=`T+0x180+16*bank`，所有 word 運算截為 RV32：

| 次序 | 原指令資料讀寫 |
|---|---|
| 1 | 讀 `U32[B]`，寫回 `old&1` |
| 2 | 讀 `F=U8[P+8]`、`R=U8[P+9]` |
| 3a，F=0 | 讀 `U32[P]`，再讀 B，寫 `U32[B]=(ID<<21) OR R OR current_B` |
| 3b，F非零 | 讀 `U32[P+4]`，再讀 B，寫 `U32[B]=(ID<<3) OR R OR F OR current_B` |
| 4 | 讀 `D=U8[P+10]&15`，**寫回 `U8[P+10]=D`** |
| 5 | 讀 `U32[B+4]`，寫回 `old&0xfffffff0`；再讀一次，寫回 `current OR D` |
| 6 | 按 P+12、P+11、P+13、P+14 讀 byte，組成小端 word 寫 B+8 |
| 7 | 按 P+16、P+15、P+17、P+18 讀 byte，組成小端 word 寫 B+12 |
| 8 | 再讀 B，寫回 `current OR 1` |

F 的整個 byte 參與 OR，不能只當成單一 boolean bit。D 是遮罩而非長度上限檢查：P+10 全部 byte 值皆測試；這段不根據 D 限制 payload 讀取。當 B 的初始 bit 0 為一時，最初 stores 也沒有先清除該 bit，不能將此步概括成「先停用」；本報告只描述數值讀寫。

## 串接原 `0x12a08` 派送

由原 dispatcher 執行到 handler 並返回 caller。未知 `0x81aa` 僅接受指定正常返回 0／1；刻意改寫 caller-saved 暫存器，保存 SP／S／GP 與記憶體。copy 槽位綁定到既有 SDK carrier 的 **參考候選** 58-byte body，執行其原指令與既有合成 FENCE／控制 word 模型，不是已安裝 provider 的身分證明。

fixture 固定 gate 可用、tag=0，測 ID=1／`0x123`／`0xffff`、payload 長度 0–8、八種穩定 bank bit 組合，以及兩種 stack canary（0、`0xcc`）：

- probe=0 且 ID≠1 時提前返回，不進 handler；只有 frame 保存的兩項 stores。
- 其餘案例 handler 的 A0=`0x40006400`，P=`entry_SP-48+12`，返回點 `0x12a5e`。
- P+0..3 是零延伸 16-bit ID；P+4..7 未初始化，保留 canary。
- P+8..9 由原 halfword store 清零，所以本條上游路徑 F=0，handler 不讀 P+4..7 的洞。
- P+10 是長度；copy 只填 P+11 起的 length bytes。handler 仍讀完 8 bytes；其餘 `8-length` bytes 保留原 stack canary，不補零。
- handler 返回後繼續執行原 epilogue，核對 caller SP／S0 恢復，以及 A0 保留 bank／4 結果。source row 與 copy 控制 word 保持。

每次 handler 執行比對全部記憶體區域及精確資料存取 trace，包含讀取值、順序、寬度和 stores；未選 bank 的 NULL source fixture 必須不解參考而返回 4。尚未串接完整 consumer 上游，也不推論設備暫存器副作用、IRQ、實際傳輸或其他 handlers。

## 重現

```powershell
python analysis/test_v4160_peripheral_write_cpu.py --standalone-only
python analysis/test_v4160_peripheral_write_cpu.py
python -O analysis/test_v4160_peripheral_write_cpu.py
```

第一條只需標準庫、原 APP 與既有有限 CPU。完整串接另外依賴既有測試模組，以及本機候選 carrier；可以用 `--carrier` 指定路徑。carrier 的長度、SHA-256、槽位值及 body SHA-256 均在執行串接前核對，候選資料不另行上傳。

```text
PASS: standalone selectors/volatile/meta/ID/payload/register cases [240, 512, 2304, 408, 12288, 408]; null-source no-bank; 2 mutations; synthetic MMIO only
PASS: 864 original dispatch routes; 576 handler/caller returns; two stack canaries; candidate-only copy binding
```

16160 組獨立案例包含選擇 bit／無關 bit、變動讀值、三個 metadata byte 全值、兩個 ID word 的零／全一／單 bit、8 個 payload byte 的全值，以及兩個原暫存器 word 的零／全一／單 bit。這是指定 fixture 的覆蓋，不是全部 32-bit 輸入的窮舉。

兩項記憶體複本變異將首個選擇 bit 26 改為 27、nibble mask 15 改為 14，均須被資料存取 oracle 抓出。原 APP 未改。共用 CPU 新增標準 RV32 OR、signed BLT／BGE；仍對未知指令、未映射區域及執行範圍外目標失敗即停。

既有 native C 重建 `src/native/receive/peripheral_write.c` 已涵蓋此段；本批增加條件性執行驗證，沒有新增重建 bytes 或重算覆蓋率。後續仍需追查其他 handlers、狀態消費，以及未知服務實際綁定／保存合約。
