# V4.1.60 `0x10402` 的 GP 相對寫入候選

針對固定 V4.1.60 BIN（76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`、映射基址 `0x8000`）的原始 bytes，逐 2 bytes 掃描完整 4-byte 視窗。只篩選 RV32I `SB`、`SH`、`SW` 且 base 為 x3（GP），其 S-immediate 指定的 byte 範圍與 `GP+0x50..GP+0x51` 相交。不預設指令邊界：資料和指令中間位置均被掃描。

限定模式有一筆候選：`0x102b2` bytes `23 98 81 04`，解碼 `sh s0,80(gp)`；附近連續反組譯提供指令邊界旁證，不能證明可達或寫入成功。C.SW 只能以 x8..x15 為 base，C.SWSP 則以 SP 為 base，不屬此直接 GP 模式。

`0x10402` bytes `03 d5 01 05 82 80` 解碼 `lhu a0,80(gp); ret`。Reset `0x186aa` 指令算術得到 GP `0x20004000`；若該初始化完成且 GP 未變，讀取地址為 `0x20004050`。Reset 的 copy 從 `[0x1ab60,0x1abe0)` 複製到 `[GP,GP+128)`；來源 `0x1abb0..0x1abb1` 為 `00 00`。這只支持 copy 完成後的條件式初值，不代表 leaf 執行時 RAM 為零。

已辨識 writer 的局部路徑自輸入 `p[6]` 與 `p[7]` bit 0 組合 `raw = p[6] | ((p[7] & 1) << 8)`，將 `0x1ff` 轉為零；若不同於舊半字，`0x102b2` 寫入該值。因此此路徑值域為 `0..0x1fe`，不是全部 writer 的值域。

限定模式不涵蓋經其他暫存器的 GP 別名、間接寫入、bulk copy、其他映像、resident 或非同步干擾；不證實際 GP、記憶體狀態、可達性或全域 writer 完備。`global_writers_complete` 固定為 false。

```sh
python -I -S -B experiments/v4160-10402-gp-store-survey/scan.py
python -I -S -B experiments/v4160-10402-gp-store-survey/test_scan.py
python -I -S -B -O experiments/v4160-10402-gp-store-survey/test_scan.py
```
