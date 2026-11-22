# 初始化第四、五個呼叫：第一個常駐程式邊界

接續 [前三個呼叫](v4160-irq39-first-init-csr.zh-TW.md)。原 APP 的 `0x9260 → 0x9f4c` 是 15 條指令的葉函式。令 B=`0x40003000`；五次 32-bit store 依序是 `(B,0x5555)`、`(B+4,3)`、`(B+8,1500)`、`(B,0xaaaa)`、`(B,0xcccc)`，然後返回。沒有 CSR 指令或子呼叫；不能因此保證外設沒有作用。

下一個 `0x9264 → 0x131c2` 先讀取 slot `0x4004c`，在 `0x131e0` 間接呼叫，參數 `(0x2000c29c,0x08077a00,112)`。APP 本身不能證明 slot 指向何處。[V1.31 參考 copy](rf-copy-helper-provenance.zh-TW.md) 在已核對的映射下，目的為 `[0x2000c29c,0x2000c30c)`；另有暫寫再恢復 `0x4002420c` 及 `FENCE.I`，沒有寫 `mstatus` 或 `mtvec` 的指令。未證實機常駐程式、來源資料或外設效果。

返回後 `0x131f6` 起從目的緩衝區的 +12 至 +15 依序讀 byte。每個 byte 通過 `(byte-32)&255 <= 94` 才前進，所以四個都在 `0x20..0x7e` 就到 `0x13208`；首個不合格者即走 `0x13204 → 0x1316a`。這不是對 112 bytes 全部做字串驗證。檢查器固定 APP SHA、核對地址與 guard 位元組，再對四個位置各測 256 個 byte；並非 CPU 或實機測試。

重現：`python analysis/check_v4160_init_first_config_guard.py <APP BIN>`；`python scripts/check-rf-copy-provenance.py`。後續從 `0x1316a` 的分支和 `0x13208` 的下一次 slot 載入接續，不預設兩次讀到相同目標。
