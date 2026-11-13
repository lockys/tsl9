# F030 路徑的原始 stack 保存槽與固定 store：有界位址分析

這是 `analysis/v4160-f030-continuation-bounded.zh-TW.md` 的算術補充，不是執行軌跡或純 C ABI 證明。參考 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，假設線性 base `0x8000`。本機核對了 `0xf016:4111`、`0xf018:22c4`、`0xf022:06c6`、`0xf024:26c2`、`0xf026:a304b400`、`0xf030:23059400`、`0xf03a:2300f500`、`0xf03e:2244`、`0xf040:b240`、`0xf042:9244`；其餘指令與條件見前篇。假設指定起點和指令邊界，不能據此證明路徑可達或存取成功。

令 `S` 為 `0xf016` 入口的 32-bit `sp`，位址算術模 `2^32`。先前指令所保存的 `s1`、`s0`、`ra` 分別佔 `[S-12,S-9]`、`[S-8,S-5]`、`[S-4,S-1]` 四個 byte。此處以每個 byte 環繞計算；不假設未對齊 word 存取會成功。F026 固定寫 `0x2000bf8d`；F030 寫 `0x2000bf8e` 的前提是 EE9A 返回時仍有 `s0=0x2000bf84`；BD46 按前篇正常返回後 F03A 固定寫 `0x2000bf11`。

## 單一 byte store 對原始保存槽的所有算術交集

表格每格是與該槽至少一 byte 重疊的入口 `S`，包含兩個端點。其公式為 `S = T + d - j (mod 2^32)`，其中 `T` 是 store 位址，`d=12/8/4` 分別對應 s1/s0/ra，`j=0..3` 為 byte lane。

| store / T | s1 保存槽 | s0 保存槽 | ra 保存槽 |
|---|---|---|---|
| F026 / `0x2000bf8d` | `0x2000bf96..0x2000bf99` | `0x2000bf92..0x2000bf95` | `0x2000bf8e..0x2000bf91` |
| F030 / `0x2000bf8e` | `0x2000bf97..0x2000bf9a` | `0x2000bf93..0x2000bf96` | `0x2000bf8f..0x2000bf92` |
| F03A / `0x2000bf11` | `0x2000bf1a..0x2000bf1d` | `0x2000bf16..0x2000bf19` | `0x2000bf12..0x2000bf15` |

三個固定地址的聯集有 25 個不同 `S`；F026 和 F030 兩者均重疊原槽的交集有 11 個，F03A 與前兩者的交集為空。若額外假設入口 4-byte aligned，聯集只剩 `0x2000bf14`、`0x2000bf18`、`0x2000bf1c`、`0x2000bf90`、`0x2000bf94`、`0x2000bf98`；若額外假設 16-byte aligned，只剩 `0x2000bf90`。這些只是篩選條件，不證明入口 alignment 或這些記憶體可用。

例如假設 little-endian、`S=0x2000bf90`、原始 `ra=0x11223344`，F026 寫 `0xaa`，EE9A 正常返回且保留必要的 `s0/s1/sp`、F030 寫 `0xbb`，中間沒有其他寫入原 ra 槽，則保存槽由 `44 33 22 11` 變成 `44 aa bb 11`，F040 成功載入時得到 `0x11bbaa44`。如果寫入值恰好與槽中的 byte 相同，重疊未必改變值。呼叫鏈也可能不返回或修改槽；若返回時 `sp` 已改，F03E/F040/F042 讀取的是新的 `sp` 相對槽，不必是上表原槽。若 `s0` 已改，F030 的地址也不一定是 `0x2000bf8e`。

可用下列只做整數集合運算的 Python 片段獨立重算；它不執行或模擬韌體，也不檢查其他寫入者：

```python
mask = (1 << 32) - 1
stores = (0x2000bf8d, 0x2000bf8e, 0x2000bf11)
slots = (12, 8, 4)
sets = [{(t + d - lane) & mask for d in slots for lane in range(4)}
        for t in stores]
print(len(set.union(*sets)), len(sets[0] & sets[1]),
      len(sets[2] & (sets[0] | sets[1])))  # 25 11 0
```

這些結果只處理三個指定位址與原槽，不涵蓋 EE9A、BD46 外的寫入、fault、中斷、別名映射、其他入口或完整 caller。原始正式 source 仍有 inline assembly，不能把這個算術結果當成 RV32 runtime、完整 ABI 或完整 BIN 驗收。
