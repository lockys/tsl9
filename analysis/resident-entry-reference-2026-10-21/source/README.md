# V1.31 resident entry/init reference source

This package uses only the already captured December2023 V1.31 SDK candidate. The main segment `[0x40000,0x6EA66)` is 191,078B, SHA-256 `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22`; the originating IntelHEX is `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`, official commit `ec059e0b18046b111ee850e44f105fcd095e775c`. The actual retained marker is `CH32V20x_BLE_LIB_V1.31`. Nothing from V1.40 or a V1.30 XWCHC profile is substituted.

The complete bounded source is230B/66 instructions, plus the4B entry jump:

| Range | Bytes / instructions | SHA-256 |
|---|---:|---|
| `0x40000..0x40004` header jump | 4 / 1 | `2bb4f21801aa29d43c20f8806e6d805fe9975d9bdf699df17862efbdb371124a` |
| `0x6DE7E..0x6DEC2` entry | 68 / 18 | `98fe32a0b24638e9f678c2112dbae4fa05ad6e45d2a9fb84bedb67c3831880b0` |
| `0x6DE0C..0x6DE7E` initializer | 114 / 32 | `7a0cf58801fabb3dcb9d26fcece3d01b2f41276dacce4130daff0e663559927f` |
| `0x40280..0x402B0` seed helpers | 48 / 16 | `1b443f8c3926fac2d65fda618f0ead0c9d2f50cafe5b0ff9c72eb030c13fd5a8` |

`source-map.json` checks all67 instruction starts and234B, their raw widths/operands and71 static CFG edges, including explicitly conditional RAM-code/normal-return edges. It also records35 actual in-memory operand mutations rejected by the same raw gates. `contract.json` gives the ordered numeric/live-state C reconstruction interface. No instruction stream is executed or emulated.

The implementable fixed flow is:

1. Header `0x40000` jumps to `0x6DE7E`. AUIPC/ADDI pairs set GP=`0x20004000`, SP=`0x20010000`, and the48B seed arguments `(0x40280,0x20000010,0x20000040 end-exclusive)`. The guard at `0x6DEA6` can skip both seed and initializer straight to MRET; the literal normal arguments make that guard false. The loop reads32, writes32, advances source then destination, and repeats while destination is unsigned-less-than the end. Twelve word requests represent the seed.
2. JAL `0x6DEBA` enters `0x6DE0C` with nominal RA=`0x6DEBE`. The initializer subtracts16 from **live SP**, saves **live RA** at then-current `SP+12`, then writes the three low-RAM words `0x200007D0`, `0x2000251C`, `0x20002E34` at numeric offsets0/4/8.
3. Both copy calls target numeric RAM `0x20000010`. The first requests source `0x402B0`, destination `0x20000040`, inclusive last-word address `0x20002E70`: **2,957 words /11,828B**. The second requests source `0x6EAA4`, destination `0x20002E70`, inclusive last `0x20002EF8`: **35 words /140B**. These are last-word addresses, not byte counts or exclusive ends.
4. Only after both calls return to their expected links does `0x6DE72` freshly read RA from **then-live `SP+12`**. `0x6DE74` adds16 to then-live SP; `0x6DE7A` tails without a new link to RAM `0x20000022`. It does not force SP/GP or the saved stack word back to their earlier values. The default stack address `0x2000FFFC` and restored RA=`0x6DEBE` require unchanged context and memory.
5. Under matching installed seed bytes, RAM `0x20000010` corresponds to the18B/7-instruction word helper at `0x40280`: if unsigned `last>=current destination`, READ32 source first, advance destination, advance source, WRITE32 at advanced destination minus4, and repeat. RAM `0x20000022` corresponds to the30B/9-instruction zero helper at `0x40292`: it sets its own start `0x20002EF8` and inclusive last `0x20003614`, then writes **456 words /1,824B**, ending at `0x20003618`. Its RET uses the live restored RA.
6. Return to `0x6DEBE` reaches raw `73002030` **MRET**. MRET is not RET/JALR through the saved RA. These bounded bytes contain no explicit MEPC/MTVEC write; that does not prove global, trap or IRQ preservation, an APP return address, or vendor privilege/CSR semantics.

The seed bytes embedded in the carrier are **not automatically installed executable RAM**. A captured helper provider must condition execution on completed seed writes, instruction fetch seeing those exact bytes, executable/valid RAM and matching ISA/privilege, no alias/IRQ/DMA replacement, and the required control return. Default numeric RAM targets remain delegated. An unproved callee can affect live SP/GP/RA or fail to return; continuation is not inferred merely from a numeric return status.

The exact missing-source boundary uses the **complete historical captured segment inventory**, including the136B tail segment `[0x6EAA4,0x6EB2C)`, SHA-256 `7416a8d7c1d595a759e14b05918b732a9168c6003af658359d8c3f452840b450`. A strict source provider must actually possess and validate that tail file; the compact ledger is not its payload. With that inventory and normal fixed helper behavior,34 second-copy words can complete, then the35th request is:

```text
instruction source 0x40286 / conditional RAM 0x20000016
READ32 source 0x6EB2C, width4
current source a0=0x6EB2C; pending destination a1=0x20002EF8
inclusive last destination a2=0x20002EF8
```

`[0x6EB2C,0x6EB30)` is absent from the captured sources. The strict captured-only provider stops before the increments/write. It has not reached zero, fresh RA reload or MRET. A provider backed by **only the main segment** stops earlier, at the first second-copy READ32(`0x6EAA4`); it cannot silently borrow the136B ledger. Source absence does not prove a physical unmapped address or hardware fault. An explicitly unknown external-memory backend is a separate unproved contract. Later zeroing never justifies fabricating the missing read as zero/FF or skipping it.

Portable source replay needs only the main code carrier and this package:

```powershell
python -B "<source-package>\inspect-source.py" --check --carrier "<absolute-REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin>" --source-root "<source-package>"
```

This rechecks raw code, mathematical mapping and the pinned inventory-based boundary; it is not a source-memory provider and does not execute either copy. To additionally recheck all historical carrier/handoff sealed members, append:

```powershell
--verify-historical --workspace "C:\Users\locky\Documents\Codex\2026-10-13\rea-https-github-com-morluto-rea"
```

`--check` is entirely read-only and byte-compares generated JSON. `--write` is limited to the checker's own unsealed directory. The package proves reference source flow, not installed resident identity, original ABI, startup success, physical RAM/MMIO, IRQ behavior or flash readiness. It generates no provider, fills no holes, executes no original ISA, performs no network/hardware operation, and changes neither ROOT/D nor old seals.

## 繁體中文

本包只使用先前已保存的 **Dec2023 V1.31 公開 SDK 參考候選**，不是從使用者 TSL9 讀回的 resident。主段範圍為 `[0x40000,0x6EA66)`、191,078B，SHA-256 為 `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22`；原 IntelHEX 為 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`，官方 commit 為 `ec059e0b18046b111ee850e44f105fcd095e775c`。實際保存的版本字串是 `CH32V20x_BLE_LIB_V1.31`，未套用 V1.40 常數或 V1.30 XWCHC 解碼設定。

上方共用表格列出每段精確 SHA：entry68B/18指令、initializer114B/32指令、seed helpers48B/16指令，共230B/66指令，另含4B/1指令的 header 跳轉。`source-map.json` 逐一核對全部67個指令起點、234B原始 bytes 與71條靜態控制邊；35個記憶體內 raw operand 突變均由同一組原始欄位檢查拒絕。這是靜態來源核對，沒有執行或模擬原 ISA。

可重建的固定 C 流程與條件如下：

1. `0x40000` 跳到 `0x6DE7E`，設定 GP=`0x20004000`、SP=`0x20010000`，並把48B seed 從 `0x40280` 複製到 `[0x20000010,0x20000040)`。正常固定參數下共12次 READ32→WRITE32，之後先增加來源再增加目的位址。`0x6DEA6` 的 unsigned guard 若成立，會同時跳過 seed 與 initializer，直接到 MRET；原始固定參數使該 guard 不成立。
2. `0x6DEBA` 呼叫 initializer，正常 link RA 為 `0x6DEBE`。`0x6DE0C` 從**當時 live SP** 減16，`0x6DE12` 把**當時 live RA** 寫到 `SP+12`；再把 `0x200007D0`、`0x2000251C`、`0x20002E34` 寫至數值 RAM 位址0/4/8。
3. 兩次 copy 都呼叫數值 RAM 位址 `0x20000010`。第一次來源 `0x402B0`、目的 `0x20000040`、**含最後一個 word** 的目的位址 `0x20002E70`，共2,957words/11,828B。第二次來源 `0x6EAA4`、目的 `0x20002E70`、含最後 word 位址 `0x20002EF8`，共35words/140B。第三參數不是 byte 數，也不是 exclusive end。
4. 只有兩次 call 都正常返回指定 link，才會在 `0x6DE72` 從**返回後當時 live SP+12** 重新讀 RA，再把當時 SP 加16。`0x6DE7A` 不建立新 link，直接 tail 到 RAM `0x20000022`。原程式沒有自動復原 callee 改過的 SP/GP 或 stack 內容；預設 stack 位址 `0x2000FFFC` 與讀回 RA=`0x6DEBE` 都有記憶體／context 未改動的條件。
5. 在 seed 指令確實保留於可執行 RAM 的條件下，RAM `0x20000010` 對應來源 `0x40280` 的18B/7指令 word helper。它先用 unsigned `last>=current destination` 判斷，**先 READ32，再增加目的、增加來源，最後寫 advanced destination−4**。RAM `0x20000022` 對應來源 `0x40292` 的30B/9指令 zero helper；它自行設定 `[0x20002EF8,0x20003618)`，含最後 word `0x20003614`，共456words/1,824B。其 RET 使用 initializer 剛重新讀回的 live RA。
6. 只有返回 `0x6DEBE` 才到 raw `73002030` 的 **MRET**。MRET 不是透過 saved RA 的 RET/JALR。這些有界原始 bytes 沒有明確寫 MEPC/MTVEC，但不能推成全域、IRQ 或 trap 保持不變，也未證明 APP 交接位址或廠商 CSR／權限語義。

**檔案內有 seed，不等於 RAM 已安裝該指令。** 若 C 模型選擇 captured helper provider，必須明列：12次 seed 讀寫都完成且保留正確 bytes、instruction fetch 真正看到相同 RAM bytes、RAM 可執行／有效、ISA／權限解碼相容、沒有 alias／IRQ／DMA 改寫，以及控制流正常返回。數值 RAM 位址本身不是 provider。未知 callee 對 live SP/GP/RA 的影響、HALT／TRANSFER 或返回別處，均不可強制當作正常 continuation。

精確缺口使用的是**完整歷史 captured segment 集合**，包含136B tail 檔 `[0x6EAA4,0x6EB2C)`，SHA-256 為 `7416a8d7c1d595a759e14b05918b732a9168c6003af658359d8c3f452840b450`。source provider 必須實際持有並驗證該檔，不能把 ledger 當成 payload。有該完整來源且固定 helper 正常執行時，第二次 copy 完成前34個 word 後，第35次是來源指令 `0x40286`／條件式 RAM PC `0x20000016` 的 **READ32(`0x6EB2C`)**，待寫目的為 `0x20002EF8`。缺少的 `[0x6EB2C,0x6EB30)` 不能補 zero/FF；嚴格 captured-only provider 應在增加指標、store、zero、fresh RA reload、MRET 之前停止。

如果 backend **只有主段**，第二次 copy 的第一個 READ32(`0x6EAA4`) 就沒有來源，必須更早停止。本機來源缺失不代表實體位址一定未映射或必然 fault；允許未知外部記憶體的 backend 是另一個尚未證實的契約。後來的 zero 動作不能消除先前讀取的義務。

上方共用 PowerShell 命令可攜重播：`--check --carrier <原主段絕對路徑> --source-root <本包>`。它只核對 raw code、數學映射、已 pin 的 inventory 邊界及 JSON byte-exact 結果，**不是記憶體 provider，也不執行 copy**；不需要舊報告樹或 radare2。另加 `--verify-historical --workspace <W>` 可檢查既有歷史 seal 成員。`--check` 完全唯讀，`--write` 只容許本 checker 自身尚未封存的目錄。

本成果不證明實機 resident 身分、原 C ABI、啟動完成、實體 RAM／MMIO、IRQ 或燒錄相容性；沒有生成 provider、補洞、原 ISA 執行／仿真、網路／硬體操作，也沒有修改 ROOT、D 或舊 seal。
