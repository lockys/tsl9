# 下一段靜態邊界 / Next static boundaries

來源 / Source: official ID2966 V4.1.60, SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, interpreted at base `0x8000` with bounded RV32 static disassembly. No target execution. These are research notes, not new C reconstruction or hardware evidence.

| 原廠範圍 / Original span | Bytes / instructions | SHA256 |
| --- | --- | --- |
| IRQ adapter `[0x12C24,0x12C58)` | 52 / 17 | `44ab1cdae33f0151e8270b3769d9dca81847154bf88d3f691443d77200ece51a` |
| Queue consumer `[0x12C58,0x12D92)` | 314 / 107 | `89905d7666bbe8295d09c752f1fcd34246847ea86c6428b539406450f8980c0f` |

先重建 52B adapter：包含條件式 32B frame、兩個 direct JAL 及 `0x12C50`／`0x12C54` 的 MRET；不能以普通 C 函式的 RA／RET 代替。它把 ID16、SP22 的 length、SP23 payload 與 tag0 交給 ring。MMIO 寬度與中斷架構 ports 需逐項保留，完整 IRQ 語意仍未知。

Reconstruct the smaller 52B adapter first. Its conditional 32B frame, two direct JALs and MRETs require explicit interrupt ports, rather than ordinary C RA/RET behavior. The ring inputs are ID16, length from SP22, payload at SP23 and tag0. MMIO widths and IRQ architecture remain separate proof obligations.

314B consumer 使用同一個 `0x2000C038`、32×12B 佇列。`0x12C8C` 讀 ID16；ID0 走跳過路徑。`0x12C96`／`0x12CAA` 使用 CSR `0x800` 的 clear／set，不能直接宣稱已證實全域 IRQ lock。resident 呼叫後 `0x12CA6` 只清 slot ID；必須保留當下實體暫存器與後續 dispatch 邊界。唯一 RET 在 `0x12D0C`，後面仍有可達 cold blocks；本機 bounded CFG 並非全域 incoming-xref 證明。

The 314B consumer uses the same 32×12B queue. ID0 follows a skip path after the ID16 load at `0x12C8C`. CSR `0x800` clear/set at `0x12C96`/`0x12CAA` is not proof of a global IRQ lock. After the resident call, `0x12CA6` clears only the slot ID. Preserve then-live registers and later dispatch boundaries. The sole RET at `0x12D0C` precedes reachable cold blocks; bounded local CFG coverage does not establish all global callers.

功能線索 / Feature lead: ring 用 ID0 辨認空槽，而 consumer 也跳過 ID0，存在靜態表示衝突。實際來源是否允許 ID0、resident／非同步寫入與實機結果未證。可考慮未來加離線診斷或明示 occupancy，但本輪未修改原廠 layout、協定或執行行為。

ID0 is both an empty-slot sentinel in ring insertion and skipped by the consumer. This is a static representation conflict. Actual incoming ID0 availability, resident/asynchronous effects and hardware outcomes are unknown. Offline diagnostics or explicit occupancy may be future research options; no original layout, protocol or runtime behavior was changed.
