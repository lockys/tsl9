# ID2966 V4.1.60 runtime-loop source / 執行迴圈來源

## English

This package is bound to the selected original ID2966 V4.1.60 firmware:76,800B, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, retained analysis base `0x8000`. The file header at offset `0x38` also contains `0x8000`; this is a source coordinate, not a physical-device observation. It does not reuse a different firmware's dispatcher ABI.

| Body / 原始範圍 | Bytes / instructions | SHA-256 |
|---|---:|---|
| main `[0x9008,0x901A)` | 18 / 8 | `87dd87b4471d5281a6185185b66e454ac79136553f837e3c9a3c2abdfb85ead5` |
| init `[0x9250,0x9290)` | 64 / 19 | `9c9a241ad1ffb34eab4267c3368c9b5cbd459e1d9f111621eb4716087f8cf60b` |
| loop `[0x8180,0x81AA)` | 42 / 15 | `c440bafcc9fdbe370d24fbcd3bd0c67e8162ceaa776a64ea6f34f1d509b6f72f` |
| dispatcher `[0x901A,0x907A)` | 96 / 38 | `1ca1876ac3f3458d2a170336f9d1598ee7dd62f359f802ceae6739d04fda437f` |

All220B/80 instruction starts are retained with PC, file offset, width, raw bytes and control edges. Fresh bounded radare2 6.2.4 static disassembly matches the original bytes and the existing main plan/core-flow CFG/conditional-dispatcher CFG. The three native C sources and related evidence files are hash-pinned as historical inputs; this task does not recompile them or claim a new native runtime verification. The checker separately decodes source operands and rejects **45 actual in-memory raw mutations**, without executing or emulating RV32.

`contract.json` gives the fixed numeric/live-state C reconstruction interface. Important source behavior:

- **Main:** subtract16 from live SP, save live RA at `SP+12`, call `0x9250`, then `0x8180`. Only if the loop call returns does the source suffix freshly load RA, set A0=0, add16 to then-current SP and RET. The selected loop has no local RET; its observer budget must not manufacture this continuation.
- **Init:** frame16/save RA, then14 direct callees in the exact order recorded in JSON, from `0x9254→0x18834` through `0x9284→0x173A2`. The initializer assigns no argument registers between these calls and tests none of their numeric return values. Every next call gets then-live A0..A7. After14 normal returns, `0x9288` freshly loads RA from then-live `SP+12`, `0x928A` adds16 to current SP, and `0x928C` tails to `0x17BF6` without a new link. Callee effects on SP/GP/registers/stack and nonreturn remain explicit delegated boundaries.
- **Loop prologue:** save old S0 at `0x8182`, assign S0 high part at `0x8184`, then save S1/S2/RA at `0x8186/88/8A`. It sets S2=`0x20000000`, S1=`0x40003000`, S0=`0xAAAA`. Every iteration freshly reads a pointer from **then-live S2** at `0x8198`, attempts the loaded A5 call at `0x819C` even if zero, calls `0x17002`, calls `0x12C58`, writes **then-live S0** to **then-live S1** at `0x81A6`, and jumps back to `0x8198`. There is no local null guard, register restore or RET. The literal write is `0xAAAA→0x40003000` only while the expected S0/S1 values remain preserved. The peripheral's hardware role is not established.
- **Dispatcher selection:** scan indices0..14 for the least set input bit using arithmetic shift of full32-bit A1 and AND1. Bits15..31 do not select a record; no selected low15 bit returns0 even if higher bits are set. Before record access, the source saves full A1 in S1. The PC-relative pair `0x9034/38` produces base `0x2000BE08`; this is not a live-GP lookup. Stride12 is observed, without proving a whole original C object or RAM lifetime.
- **Dispatcher read/call order:** `0x9040` reads callback pointer at record+4; if zero, it skips mode/argument reads, clears and callback. Otherwise `0x9044` samples the unsigned mode byte at record+0 **before** `0x9048` reads the argument word at record+8; `0x904A` masks that already sampled mode afterward. For mode0 only, zero record+4 then record+8 **before** calling the already loaded A3 target at `0x9058`. Nonzero mode skips clearing. A0 is the sampled argument; A1 remains the original full u32 before the call. Target and argument are not refetched after clearing.
- **Dispatcher return:** callback numeric A0 is overwritten. The result is `low16(liveS1 XOR (1u << (liveS0 & 31)))` using **post-callback live S0/S1**, before restoring either register. It removes the originally selected bit only if those expected values remain preserved. RA, S0 and S1 are then freshly read from current SP+12/+8/+4, current SP gains16, and RET uses the fresh RA. No ordinary C callee-save ABI, stable stack or callback lifetime is assumed.

The source CFG includes explicitly conditional call-return edges. In particular the `0x900E→0x9012` edge is an unproved delegated-return alternative, not an exit found in the original loop. Both source entry assumptions (`0x9008` and `0x901A`) are bounded; this package does not prove arbitrary interior entries or the resident's original invocation context. A host observation budget is a model limit, not an original HALT, RET or stack-unwind instruction.

Portable, entirely read-only replay:

```powershell
python -B "<source-package>\inspect-source.py" --check --firmware "<absolute-ID-2966-V4.1.60-decoded.bin>" --source-root "<source-package>"
```

The package contains all selected rows, so replay needs neither radare2 nor an old evidence tree. To additionally verify the historical native/evidence files in the original workspace, append:

```powershell
--verify-historical --workspace "C:\Users\locky\Documents\Codex\2026-10-13\rea-https-github-com-morluto-rea"
```

`--check` regenerates and byte-compares the two JSON reports and checks seal members without writes. `--write` is restricted to this checker's own unsealed scope. No original ISA, network, hardware, provider generation, ROOT/D change or old-seal mutation occurs. Physical RAM/MMIO/resident, original C signatures/ABI, callback lifetimes, IRQ behavior and target readiness remain unproved.

## 繁體中文

本包只對應所選 **original ID2966 V4.1.60**：76,800B，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，分析 base=`0x8000`。檔案 offset`0x38` 的 header 也含`0x8000`，這是來源座標，不是實機量測；沒有套用其他版本的 dispatcher ABI。上方共用表列出四段的精確範圍、大小、指令數與 SHA。

全部 **220B／80個指令起點** 都保留 PC、檔案 offset、寬度、raw bytes 與控制邊。Fresh radare2 6.2.4 有界靜態反組譯與原 BIN、既有 main plan／core-flow CFG／conditional-dispatcher CFG 相符；三份 native C 與相關 evidence 僅保存歷史 hash，沒有在本輪重編或宣稱新的原生執行驗證。Checker 另以 raw 欄位核對並拒絕 **45個實際記憶體內 operand 突變**，沒有執行或仿真 RV32。

`contract.json` 可供固定 C 數值／live-state 流程重建，重點如下：

- **Main：** live SP 減16、把 live RA 存於`SP+12`，先呼叫`0x9250`，再呼叫`0x8180`。只有 loop 真正返回後，來源 suffix 才會 fresh 讀 RA、令 A0=0、對當時 SP 加16並 RET。原 loop 沒有本地 RET，不能把 host observer budget 當成自然返回。
- **Init：** 建立16B frame、保存 RA，依 JSON 記錄的精確順序呼叫14個 callee：從`0x9254→0x18834`到`0x9284→0x173A2`。Init 沒有在 call 之間設定參數暫存器，也不檢查任何數值回傳；下一個 call 使用前一步留下的 live A0..A7。14次正常返回後，`0x9288`才從**當時 live SP+12**重新讀 RA，`0x928A`把當時 SP 加16，再由`0x928C`不建新 link 地 tail 到`0x17BF6`。Callee 改動 SP/GP、暫存器、stack 或不返回，都必須保留為 delegated 邊界。
- **Loop prologue：** `0x8182`先保存舊 S0，`0x8184`才設定 S0 高位，之後才在`0x8186/88/8A`保存 S1/S2/RA。初始 S2=`0x20000000`、S1=`0x40003000`、S0=`0xAAAA`。每輪`0x8198`都從**當時 live S2**重新讀 pointer，`0x819C`即使 pointer 為0也嘗試呼叫載入的 A5；再呼叫`0x17002`、`0x12C58`，於`0x81A6`把**當時 live S0**寫到**當時 live S1**，然後永遠 backedge 到`0x8198`。沒有本地 null guard、restore 或 RET；只有相關 S0/S1 保持預期值時，寫入才等同`0xAAAA→0x40003000`，未證明其硬體周邊角色。
- **Dispatcher 選擇：** 使用完整32-bit A1 做 arithmetic shift 後 AND1，搜尋 index0..14 的最低 set bit。bit15..31不會選 record；若低15位全0，即使高位有值也回0。存取 record 前先把**完整 A1**保存在 S1。`0x9034/38`的 PC-relative pair 得出 base=`0x2000BE08`，不是 live GP lookup；stride12 是原指令事實，不代表已證原始完整 C 物件或 RAM lifetime。
- **Dispatcher 讀取與呼叫順序：** `0x9040`先讀 record+4 的 callback pointer。若為0，會略過 mode／arg 讀取、清除與 callback。否則先在`0x9044`讀 record+0 的 unsigned mode byte，**再**於`0x9048`讀 record+8 的 argument word，之後`0x904A`才對已讀 mode 做 AND255。只有 mode0 才會先清 record+4、再清 record+8，最後`0x9058`呼叫先前載入的 A3；非0 mode 不清除。A0 是已讀 argument，callback 前 A1 仍為原完整 u32；清除後不重新讀 target 或 argument。
- **Dispatcher 返回：** callback 的數值 A0 會被覆蓋。結果是 `low16(liveS1 XOR (1u << (liveS0 & 31)))`，使用 **callback 後當時的 S0/S1**，而且是在 restore 前計算。只有 callee 保持原預期值時，才等同移除原選定 bit。接著才從當時 SP+12/+8/+4 fresh 讀 RA/S0/S1、對當時 SP 加16，並透過 fresh RA 返回；沒有假定普通 C callee-save ABI、stack 穩定或 callback lifetime。

靜態 CFG 的 call-return 邊都有明確條件。尤其`0x900E→0x9012`只是尚未證實的 delegated-return 分支，不是原 loop 裡找到的 exit。分析只涵蓋從`0x9008`或`0x901A`開始的有界入口，未證任意 interior entry 或 resident 的原始呼叫 context。Host budget 是模型觀察限制，不是原程式的 HALT、RET 或自動 stack unwind。

上方共用命令支援可攜唯讀重播：`--check --firmware <原ID2966絕對路徑> --source-root <本包>`；不需要 radare2 或舊 evidence 樹。加`--verify-historical --workspace <W>`可額外核對歷史 native/evidence 檔。`--check`重新計算兩份 JSON、byte-exact 比對並檢查 seal 成員，完全不寫入；`--write`只允許本 checker 自身尚未封存的目錄。

本輪沒有原 ISA 執行／仿真、網路、硬體、provider 生成、ROOT/D 修改或舊 seal 變更；實體 RAM/MMIO/resident、原 C signature／ABI、callback lifetime、IRQ 行為及 target readiness 仍未證實。
