# V4.1.60 clock query and derived outputs / 時鐘查詢與衍生輸出

## English

This is a bounded, offline source proof for the selected ID2966 V4.1.60 Runtime. It describes original instruction effects suitable for a fixed C/C++ dataflow model; it does not recover an original C prototype or validate physical clocks, RAM, MMIO, a chip SKU, or an installed resident.

The firmware is 76,800 bytes, analysis base `0x8000`, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.

| Original range | Bytes / instructions | SHA-256 |
| --- | --- | --- |
| `18834..188E2` | 174 / 58 | `1fe76c3ddc25809287b5ebaf84cd508bcffeebc7b442eac36b33a38ab2f81e1e` |
| `1973C..19764` | 40 / 11 | `54981bbd3ffcfe30f15091ac55558d66f221f32712e54ac53e33f9ff2c2afb43` |

The 214-byte, 69-instruction frontier is complete under its two entry conditions: decoded branches and jumps stay inside it, and each body ends at its actual `RET`. Neither body calls another function or operates on SP. Fresh static radare2 rows match the retained historical entry rows byte for byte. The checker decodes raw operands independently, verifies all source bytes and CFG successors, and rejects 50 raw mutations. No original instruction is executed or emulated.

`18834` first samples nominal `0x40021004` and masks with 12. Masked value 4 selects 32,000,000, value 8 selects the multiplier path, and values 0/12 select 8,000,000. The multiplier path uses **two further, distinct reads**: bits 18..21 plus 2, with 17 replaced by 18, and then source bit 16. Source bit 0 reads nominal `0x40023800`: bit 4 selects 4,000,000 or 8,000,000. Source bit 1 performs another fresh config read; bits 22..23 equal 3 select 16,000,000. Otherwise a further fresh read is shifted left 14 with 32-bit wrap and tested with signed `BGEZ`; under that register flow, original bit 17 selects 8,000,000 or 4,000,000. `MUL` retains the low 32 bits.

At `18850`, the provisional value is written to live GP+108 **before** the prescaler reads. A fresh config sample supplies index 0..15. The table byte is read live from the base formed from then-live GP+64. The scalar is then read afresh from an address formed from then-live GP+108, shifted with logical `SRL` using the byte's low five bits, and stored to then-live GP+108. Do not replace the scalar read with the provisional value or the table read with an embedded array. Each memory request forms its address from the pre-read register state; the read response then replaces its destination register.

`1973C` freshly reads GP+108, applies unsigned `DIVU` by 8,000,000, masks with 255, writes a byte at live GP+382, multiplies the held masked quotient by 1,000, and writes its low halfword at live GP+380. It does not reload the stored byte. The units of these outputs are unproved. Both functions return through then-live RA and do not assign A0/A1, GP or RA explicitly. An unknown read, branch result, HALT or TRANSFER must remain unknown or stop the model; it is not a zero/default-path success.

The caller invokes `18834` at `9254`, opaque provider `9A42` at `9258`, and `1973C` at `925C`. The intervening provider can change GP/global/context, so neither GP nor the first function's result may be cached across it. Normal provider returns and preservation of registers expected by original code are model conditions, not an established original C ABI.

The auxiliary 52-byte reset slice only proves a conditional source mapping: a completed original 128-byte word copy maps `1AB60..1ABE0` to GP `20004000`. The 16 source bytes for GP+64 are at `1ABA0..1ABB0`, SHA-256 `81387c7ef90dc35a7440aff79bf63bc9c233dbe35110bbf209b92caef131b844`, values `[0,0,0,0,0,0,0,0,1,2,3,4,6,7,8,9]`. This does not prove current RAM values or immutability; resident, IRQ or other writers may change them.

## 繁體中文

這份成果是所選 ID2966 V4.1.60 Runtime 的有限、離線原始指令證據，可供固定流程的 C/C++ 資料流模型使用。它沒有還原原始 C 函式原型，也沒有驗證實體時鐘、RAM、MMIO、晶片型號或已安裝 resident。韌體大小、分析基址、兩個原始範圍及雜湊如上表；兩個函式合計 214 bytes、69 條指令。

所有可達分支與跳轉都留在這兩個有限範圍內，各自到達真正的 `RET`；兩者沒有呼叫其他函式，也沒有操作 SP。新取得的 radare2 靜態指令列與既有來源逐 byte 相同。檢查器另以原始位元解碼參數、驗證完整控制圖，並拒絕 50 個原始位元突變；過程沒有執行或模擬原始指令。

`18834` 的初次設定值以 12 遮罩：4 選 32,000,000，8 進入倍率分支，0 或 12 選 8,000,000。倍率與來源旗標來自後續兩次獨立的即時讀取。倍率為 bits18..21 加 2，17 再改為 18。來源 bit16 為 0 時讀 `40023800`，以 bit4 選 4,000,000 或 8,000,000；為 1 時再讀設定，bits22..23 等於 3 則選 16,000,000，否則再讀一次、左移 14 並保留低 32 bits，以有號 `BGEZ` 判斷，在該暫存器流程下等價於以原 bit17 選 8,000,000 或 4,000,000。乘法保留低 32 bits，不能把多次讀取合併為單一快照。

`18850` 先將暫時計算值寫到當時 GP+108，之後才讀 prescaler 設定、GP+64 表格 byte，以及重新讀取 GP+108 的 scalar。表格索引是 0..15；表格值必須即時讀取，以其低 5 bits 作邏輯右移，最後寫到當時 GP+108。每次位址形成均使用該時間點的暫存器；讀取的回應才覆寫目的暫存器。不能用暫存結果取代第二次 scalar 讀取，也不能假定整個函式的 GP 固定。

`1973C` 重新讀 GP+108，以無號 `DIVU` 除以 8,000,000，再遮罩 255；先寫 byte 到當時 GP+382，再把手上遮罩後的商乘 1,000，將低 16 bits 寫到當時 GP+380，沒有重新讀剛寫入的 byte。這些輸出的單位尚未證明。兩者使用當時 RA 返回，沒有明確指定 A0/A1、GP 或 RA；未知讀值、分支、HALT、TRANSFER 都必須保留，不能視為 0 或成功返回。

初始化的呼叫順序是 `9254→18834`、`9258→9A42`、`925C→1973C`。中間的未知 provider 可以修改 GP、global 或 context，故不能跨它快取 GP 或前次結果。正常返回以及原程式預期的暫存器保存只是模型條件，不代表已證明原始 C ABI。

附帶的 52-byte reset 片段只證明條件式映射：原始 128-byte 複製正常完成時，`1AB60..1ABE0` 對應 GP `20004000`。GP+64 的 16-byte 初值來源與雜湊列於英文段落。這不是即時 RAM 擷取，也不是不可變表格證明；resident、IRQ 或其他寫入者仍可能改變內容。

## Portable verification / 可攜唯讀驗證

Use explicit absolute paths; no historical tree, radare2, package download or target execution is required. / 使用明確絕對路徑，不需要歷史目錄、radare2、套件下載或執行目標。

```powershell
python -B <source>/inspect-source.py --check --firmware <absolute-ID2966-bin> --source-root <absolute-source>
```

The optional `--verify-historical --workspace <W>` also checks the seven retained historical source pins. `--check` regenerates the two JSON documents in memory, compares exact bytes and checks sealed members without writing. `--write` is restricted to this unsealed source scope and refuses conflicting output. / 可選的 `--verify-historical --workspace <W>` 另核七份歷史來源雜湊。`--check` 只在記憶體重算兩份 JSON、逐 byte 比較並驗證封存成員，不寫入檔案；`--write` 僅限本未封存目錄且拒絕相異輸出。
