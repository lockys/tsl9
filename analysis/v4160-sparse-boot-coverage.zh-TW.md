# v4.1.60：完整 sparse HEX 的啟動 copy 來源覆蓋率

日期：2026-11-26。接續 [fallback 初始化來源](v4160-fallback-initialization-static.zh-TW.md)，把來源範圍由主連續 carrier 擴到本機保存的兩份完整 sparse HEX。新 [檢查器](check_v4160_sparse_boot_coverage.py) 與 [JSON ledger](v4160-sparse-boot-coverage.json) 重播 HEX record、sidecar equality 與 copy-request 位址覆蓋率；沒有執行或模擬目標 ISA、copy 狀態、heap、provider、loader 或 MMIO，沒有增加 C 覆蓋率。

**結論：第二段來源的大部分 bytes 在另一個 sparse segment 中；兩版本都只缺最後要求的一個 4-byte word。** 上一輪主連續 BIN 不含該來源的結論仍成立，不能將主段之外的地址一律當成整份 HEX 都缺失。

## 固定原始來源與 reader

| 來源 | bytes／records／captured data | SHA-256 |
| --- | --- | --- |
| V1.31 `original-dec2023/wchble_rom.hex` | 526184／11973／191244 | `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5` |
| V1.40 `original/wchble_rom.hex` | 527568／12005／191744 | `5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23` |

每份各有三個 type02 extended-address records、一個 type03 start record（數值地址 `0x40000`）與一個終止 EOF；data records 分別 11968／12000。新 ledger 保存原 HEX Git blob SHA-1、record type counts、各 segment digest，以及第二段來源對應的原始 line／source-offset／checksum／line hash。

使用既有本機 `carrier/intel_hex.py` 的嚴格 reader，固定其完整 8416 bytes、SHA-256 `727ec4a519e751f72180381ab9129d58e351affd0bc467a99889f1f14e77e5df`、Git blob `680d42832cd6640f34b5a5806375c3b838c8abaf`，並確認另一個已保存 reader bytes 相同。

reader 檢查 syntax、count、checksum、extended address、EOF、start records、offset boundary，且連相同值的重複地址也拒絕，不使用 last-writer-wins。新檢查器另外用 `check()` 重算每行 source byte offset、原始 line hash、換行長度及總來源長度，因此這些完整性條件在 `-O` 仍會執行。

原 APP／SDK header／兩個主 carrier 與前輪 initializer 操作數鏈也重新固定。本輪全數來自既有本機檔案，未下載新來源。

## 所有 34 個既有 sidecars 都與 HEX 相符

每份 HEX 有 17 個 contiguous segments：主段、15 個兩 byte 小段、最後一段 initialized data。檢查器逐一比較現有 sidecar 的完整 bytes，並在 ledger 保存 interval／size／SHA-256；沒有產生新的 segment、拼接檔或填洞影像。

| 候選 | 主段 end-exclusive | 第二段來源開始 | 兩者間 interval |
| --- | --- | --- | --- |
| V1.31 | `0x6ea66` | `0x6eaa4` | 62 bytes，其中 30 bytes 已捕獲、32 bytes 缺失 |
| V1.40 | `0x6ec56` | `0x6ec94` | 同樣 30 已捕獲／32 缺失 |

30 bytes 來自 15 個各兩 byte 的小段，穿插 16 個兩 byte holes。因此 **62 是位址距離，不是 62 個缺失 byte**。資料覆蓋率由 records 的 active extended-address base 加 offset 決定，不能由檔案長度或 bounding interval 推算內容。

## 三種啟動 request 的來源覆蓋

兩版本的 48-byte seed 與第一段 inclusive copy 的全部來源 bytes 都存在，且第一個 sparse segment 與既有主 carrier 完整相同。第二段的精確結果如下，區間終點均不含：

| 候選 | 要求 source | 實際 captured source | 整份 HEX 未提供 |
| --- | --- | --- | --- |
| V1.31 | `0x6eaa4..0x6eb30`，140B | `0x6eaa4..0x6eb2c`，136B | `0x6eb2c..0x6eb30`，4B |
| V1.40 | `0x6ec94..0x6ed24`，144B | `0x6ec94..0x6ed20`，140B | `0x6ed20..0x6ed24`，4B |

V1.31 有 34 個完整來源 word，第 35 個缺全部四 bytes；V1.40 有 35 個完整 word，第 36 個缺全部四 bytes。這只是逐地址 capture-mask 盤點，不模擬 copy 已執行幾次、不建立目的 RAM 狀態，也不預測硬體 fault。

對應的既有 tail sidecars：

| 候選／bytes | SHA-256 | 原 HEX data record lines |
| --- | --- | --- |
| V1.31／136 | `7416a8d7c1d595a759e14b05918b732a9168c6003af658359d8c3f452840b450` | 11963..11971 |
| V1.40／140 | `bc3a261829e7c230061200abb66ef5b3e8e9308e4f93b550d4ebf31db8f9a936` | 11995..12003 |

每筆貢獻 record 的 absolute interval、raw line hash、source byte offset、data digest 與 checksum 均可由 ledger 審閱。不存在的最後四 bytes 沒有值，程式不以零、鄰近資料或其他版本替代。

## 後續清零不能證明先前讀取有效

缺失的最後來源 word 對應 RAM：

- V1.31 `0x20002ef8..0x20002efc`。
- V1.40 `0x20002f48..0x20002f4c`。

它們正是下一個 zero helper 的第一個目的 word；本輪透過既有 initializer 操作數與位址差值驗證此關係。**之後會要求覆寫該目的 word，不等於先前 source read 已成功。** HEX 不含 record 也不代表實體 flash 沒有可讀值或硬體一定 fault。

因此完整 boot、RAM code 可見性、MRET／中斷狀態、實體 ISA 與 installed resident 仍未證明。既有本機 `v131-sparse-startup-copy.zh-TW.md` 使用另一個明示 host copy-state 模型，該文件未隨本次發布；本輪提供純來源／coverage bridge，沒有呼叫或擴張該模型。

## 可重播驗證

```text
python analysis/check_v4160_sparse_boot_coverage.py
python -O analysis/check_v4160_sparse_boot_coverage.py
```

兩模式均實際輸出：

```text
PASS: 3 address semantics; 10 HEX grammar negatives; 2 actual checksum mutations; 16 sparse masks; 8 captured-byte deletions
PASS: 23978 HEX records; 34 source-matched sidecars; both second copies lack exactly the final 4-byte word
PASS: ledger exact replay; full boot/physical read/installed identity UNPROVED; NO ISA/copy-state/provider/MMIO execution
```

測試涵蓋 type02／type04 address semantics、分離 records、十種指定格式負例、兩份真實 HEX 的 checksum 記憶體副本變異、單 word 全部 16 種 byte-presence masks，以及每份來源第一個 captured word 的逐 byte 刪除。它們要求預期的 parser／coverage guard 生效，不以任意 exception 當作通過；沒有為真實來源補上缺失 bytes。

重跑需要七個已發布 Python dependency 模組，以及本機候選目錄中的固定 HEX、reader、34 個原 sidecars、SDK header 與前輪 LLVM 參考。這些本機候選輸入未隨本次發布；僅 clone repo 不足以重現。預設只讀重算並精確比對 JSON；`--write` 只可建立不存在的 ledger。

本次發布不改前輪封存成果。後續仍需追查設定函式之後的 APP `0x197f0`／resident `0x43b3e`（V1.40 對應 `0x43bca`）及其巢狀副作用、其他可達 writer、實際 provider 綁定與物件保存期。來源覆蓋率的收斂不會解除這些未知。
