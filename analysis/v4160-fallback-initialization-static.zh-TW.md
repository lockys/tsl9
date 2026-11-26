# v4.1.60：fallback word 的啟動與完整設定函式來源鏈

日期：2026-11-26。承接 [allocation core](v4160-allocation-core-static.zh-TW.md)，驗證兩份參考候選的完整 initializer、zero helper 與完整 BLE_LibInit bytes。本輪擴大的是先前停在 copy 後的設定函式範圍及啟動輸入缺口，不宣稱取得實機 callback 身分。全程只有 bytes／operands／條件性 CFG／位址區間代數，沒有執行或模擬 ISA、provider、heap、loader 或 MMIO，C 覆蓋率未增加。

## 六個完整本體

[檢查器](check_v4160_fallback_initialization_static.py) 精確重播 [JSON ledger](v4160-fallback-initialization-static.json)，固定下列完整 body hashes。合計 744 bytes／266 instructions；每版本 initializer 114B／32 instructions、zero helper 30B／9 instructions、設定函式 228B／92 instructions。所有區間終點均不含。

| 候選／本體 | flash range | SHA-256 |
| --- | --- | --- |
| V1.31 initializer | `0x6de0c..0x6de7e` | `7a0cf58801fabb3dcb9d26fcece3d01b2f41276dacce4130daff0e663559927f` |
| V1.40 initializer | `0x6dffc..0x6e06e` | `e5a738246f7b39ca8dc057596acaf0040bb6673935fac8015ef1dba8af84c74e` |
| V1.31 zero helper | `0x40292..0x402b0` | `c07bd6c2683b5aa3db852c523b30438cfff119d8920ba3c577943ebfc7b8ac6a` |
| V1.40 zero helper | `0x402d2..0x402f0` | `b50f930aec0a45c60255bb412cf59ca3ea8fbd89b992cef9569cc43bea1b8cbb` |
| V1.31 config | `0x43c7e..0x43d62` | `dc0cfe70fdbcb5f85158fe44d57780e562607b7182ddfd371bdc05b0e4a754f3` |
| V1.40 config | `0x43d0a..0x43dee` | `4fc5bf263804bbb6e2633b2b5c597bde01b8cefaad605696b3e18b7bd4579d2c` |

原 APP、SDK header、carrier 全檔身分與前輪 core-to-fallback 關係均再檢查。仍明示條件性 LLVM Xwchc profile，並驗證已保存四份 LLVM 欄位／測試來源的 SHA-256、Git blob 與 28 筆 encoding vectors；不把一般 disassembler 的 FLD／FSD 名稱當成實體語義證明。

## 啟動 zero helper：包含 word203，並非已完成 boot 證明

seed source 先保存 18-byte inclusive word-copy helper，緊接 30-byte zero helper；既有 seed loop 的目的範圍為 `[0x20000010,0x20000040)`，故 zero helper 對應 RAM `[0x20000022,0x20000040)`。initializer 恢復原 RA／SP 後，AUIPC/JALR tail 的數值目標也為 `0x20000022`。

zero helper 明確比較 unsigned end≥cursor，包含最後一個 word，每次寫 U32 zero、cursor+=4。

| 候選 | zero start | inclusive last word | end-exclusive | fallback slot |
| --- | --- | --- | --- | --- |
| V1.31 | `0x20002ef8` | `0x20003614` | `0x20003618` | `0x20003220` |
| V1.40 | `0x20002f48` | `0x20003664` | `0x20003668` | `0x20003270` |

各有 456 個對齊 word，fallback 是一開始算第 203 個。這是對完整 operands 與地址區間的檢查，沒有實際寫這些地址。正常完成仍依賴先前 copy、code／live context／有效存取保持所需條件。

**重要輸入限制：initializer 的第二段 copy 來源完全不在此次使用的連續 carrier segment 內。**

| 候選 | 要求 flash source | 要求 RAM destination | bytes | 連續輸入 end-exclusive |
| --- | --- | --- | --- | --- |
| V1.31 | `0x6eaa4..0x6eb30` | `0x20002e70..0x20002efc` | 140 | `0x6ea66` |
| V1.40 | `0x6ec94..0x6ed24` | `0x20002ebc..0x20002f4c` | 144 | `0x6ec56` |

兩份 source start 都比連續檔案尾端再高 62 bytes。檢查器只記錄要求及 coverage=false，沒有補零、讀越界、拼湊其他區域或假設缺失內容。這不判定所有其他原始 sparse 來源是否缺少該資料；只界定本輪輸入可支持的結論。因此不能由本輪連續 BIN 證明整個 initializer／boot 已完成。

此外，依 inclusive copy 操作數，第一與第二段目的區間重疊 4 bytes，第二段與 zero 起點也重疊 4 bytes；ledger 保留這些原始關係，未用一般 end-exclusive 預期改寫指令。

## 後續 writer：64-byte 設定複製

固定 header 的 BLE_LibInit 為 JT28，對應 slot `0x400a4`；兩份槽值分別指向上表完整 config 函式。通過入口欄位檢查與前置 validation callee 後，在 live S0／S1 保持所需值的條件下：

1. S0=`0x20003000`，向 `0x2000039c` 提出目的地清零、byte=0、count=64 的請求；數值 target 等於候選 slot40048。
2. 重新設 count=64、source=live S1，向 `0x20000332` 提出 forward copy；target 等於候選 slot4004c。
3. V1.31 destination=`0x200031ec`，V1.40=`0x2000323c`，其 **+52..55** 正好覆蓋 fallback word。

既有 [callback-review](v4160-allocator-callback-2026-10-22/callback-review/README.md) 已保存這條有界來源及 copy helper 證據。本輪檢查其 entry/call operands，並把整個設定函式後段納入同一 ledger。source 是 live S1，不能無條件等同 entry A0；callback word 是四個依序讀取並寫入的 source bytes，不是原子 U32 快照。

這個 bulk copy 是具體 writer，會在條件成立時重寫啟動零值。找不到相鄰絕對地址 SW，不等於不存在 writer。本輪未做全 ROM 所有 computed／indirect stores 的可達性或寫入缺席證明。

## 完整 copy 後段：直接 stores 不碰 +52，仍有 opaque calls

完整 228-byte config 函式在 copy 返回後，八個預設欄位 store 依序寫 destination 的：

```text
+12 (U16), +14 (U8), +16 (U16), +15 (U8),
+18 (U8), +19 (U8), +20 (U8), +22 (U8)
```

兩個 profile 的每個 store 均逐項驗證，全部與 +52..55 不重疊。最後一項是 **+22**，其判斷讀取的是 live S1+22；沒有用欄位名稱或猜測 layout 取代原 bit 解碼。

之後重新讀 destination+44 的 pointer，非零則呼叫該 target；這是 **+44..47**，與 fallback 的 +52..55 不同。callback 若正常返回，A0 的 low16 寫至 V1.31 `0x200031a4`／V1.40 `0x200031f4`。另一個直接 byte store 位於 `0x200035f5`／`0x20003645`。這些已定位的直接 stores 也不與 fallback word 重疊。

設定函式還會呼叫 V1.31 `0x43b3e`／V1.40 `0x43bca`，然後才在正常後段建立返回值並恢復 frame。因此即使前面的 copy 確實寫入 0，也不能從「defaults 不碰 +52」推論返回時或後續 allocation 時仍為 0。+44 callback、本機 callee、其他 writer／中斷仍沒有完整副作用合約。

CFG 解碼涵蓋完整設定函式，內部無循環；每個 call 的 fallthrough 都只是**明示假設的正常返回邊**。沒有展開未知 callee 的內部 CFG，也不將 saved frame、S／GP／SP、code 或 source／destination 穩定性視為已證。

## APP 零來源的既有前提仍然保留

既有 [failure-slot-origin](v4160-allocator-failure-slot-origin.zh-TW.md)／[config-copy-callers](v4160-config-copy-callers.zh-TW.md) 將 APP 的設定 +52 對應至當時 SP+68..71，並在清零請求確實完成、必要呼叫保存與直接 stores 不覆蓋等條件下，得到當次 source word 為零。

本輪沒有重做整個 APP stack 寫入普查，也沒有將該條件性來源升級為任意時刻 slot 值。即使設定複製後得到零，allocation core 仍使用當次 fresh load 的 fallback word。實際 installed resident、當次 slot target、任何後續更新及真實 callback 提供者都尚未確認。

## 實際重播與反例

需本機固定 APP、六個既有 Python dependency 模組，以及 `analysis/wch-resident-candidate-2026-10-21/` 內 digest 相符的兩份 carrier、SDK header、四份 LLVM 來源／測試參考。候選輸入目錄未隨本次發布；僅 clone repo 不足以重跑。程式不下載、不安裝或啟動服務；預設精確比對 JSON，`--write` 僅能建立不存在的 ledger。

```text
python analysis/check_v4160_fallback_initialization_static.py
python -O analysis/check_v4160_fallback_initialization_static.py
```

兩種模式均實際輸出：

```text
PASS: 2 x 456 zero-word addresses; field+52/word203 relations; 16 disjoint default fields; 10 specified raw mutations
PASS: 6 complete bodies, 744 bytes; full config suffix/conditional CFG; second-copy source gaps retained
PASS: ledger exact replay; installed/full boot/later slot identity UNPROVED; NO ISA/provider/MMIO execution
```

zero-word addresses 與 field overlap 是主機位址代數，沒有建立目標記憶體模型。十個 raw mutations 改 zero branch、zero store 的 source register、second-copy inclusive end、zero tail target、config destination、64-byte fill count、copy target、default store offset、+44 callback load offset、callback target register。每個直接進入推導，要求命中特定 operand／range guard；未以全檔 hash 不符或任意 decoder exception 充作通過。

剩餘工作包括本機 sparse 來源能否支持第二段 copy、+44 callback 與後段 callee 的副作用、其他可達 writer，以及實際 installed 綁定與 allocation 時的 slot 值。本輪保留缺失輸入及 opaque 邊界，沒有假造 callback 或執行結果。
