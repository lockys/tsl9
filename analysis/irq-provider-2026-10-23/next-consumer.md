# 下一段：佇列消費與 dispatch

[English](next-consumer.en.md) · [逐指令證據](next-consumer.json)

`[0x12C58,0x12D92)` 共314B／107指令，SHA256 `89905d7666bbe8295d09c752f1fcd34246847ea86c6428b539406450f8980c0f`，尚未重建為可讀C。不能在`0x12D0C`的RET處截斷：後面仍有由區域分支到達的cold blocks。

下一輪須保留80B frame與S0..S7／RA、fresh slot讀取與清除、CSR `0x800` clear／set、opaque provider前後的then-live實體暫存器，以及後續dispatch／direct和indirect call邊界。不得把CSR操作直接稱為已證實的全域IRQ lock，或把resident指標直接假設成標準memcpy。

ID0同時作為空槽與consumer跳過條件，是值得加離線診斷的表示衝突線索；實際ID0可達性、同步／resident效果及硬體掉包未證。先重建原始行為，再討論明示occupancy或計數器；本輪未改layout／協定／硬體行為。完整caller、IRQ、記憶體與晶片仍未知，未執行target／ISA／MMIO。
