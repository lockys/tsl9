# V1.31 candidate：0x20003538 啟動初始化覆蓋

結論：**有條件的 startup zero writer**，但沒有證明執行時 pointer 的非零 writer、allocation 或可讀容量。以下皆為候選 SDK，不是原機 resident 身分或實際執行證據；區間均為左閉右開。

## 原始 bytes 與範圍

`scripts/check-rf-3538-init.py` 直接讀 `analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.hex`，驗證完整 SHA-256 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`、解析 checksum 與稀疏位址。startup 用既有 raw operand gate 核對 entry、seed、兩次 copy、zero helper 的指令及 inclusive unsigned branch；RF 的 setup/call 原始 bytes 另逐 byte 核對。沒有補洞。

| 操作 | 條件目的範圍 | 與 `20003538..2000353C` |
|---|---|---|
| seed copy | `20000010..20000040` | 不重疊 |
| first copy | `20000040..20002E74` | 不重疊 |
| second copy | `20002E70..20002EFC` | 不重疊 |
| zero helper | `20002EF8..20003618` | **完全包含** |
| RF_Config zero 32、copy 32 | `20003540..20003560` | 不重疊，兩者相距 4 bytes |

seed 從 flash `40280..402B0` 複製 helper 至 RAM `20000010..20000040`。zero helper 的 flash `402A8`（映射 RAM `20000038`）是 `sw zero,0(a5)`；`402A2` 的 unsigned inclusive guard、`402AC` 的 +4 和 loop，連同 `40292..402A2` 設定界限 `20002EF8`、最後 word `20003614`，在正常順序完成下包含對齊 word `20003538` 的一次 zero store。因此這是**條件性的明確初始化 writer，值為零**，不是指向 buffer 的非零初始化證據。已知其他讀取與 direct-pattern 掃描限制見 [原有追查](rf-pointer-3538-bounded.zh-TW.md)。

第二次 copy 要求來源 `6EAA4..6EB30`，但原 HEX 缺 `6EB2C..6EB30`；其最後 READ32 發生在進入 zero 之前。不能以後續 zero 覆蓋目的字來推定此讀取成功、CPU fault 與否或 zero 必然執行。還須 seed 與兩次 copy 正常、RAM code 可見、控制流和記憶體不受干擾等條件；細節見 [copy 順序](resident-copy-order-v131/README.md)。

RF_Config 的 `64BCE..64BF6` 原 bytes 包含 `lui s2,0x20003`、兩次 `a0=s2+0x540`、兩次 `a2=32`、第一次 `a1=0` 和第二次 `a1=s1`，及對應兩個 call。依既有 [函式分析](../experiments/tsl9-resident-callback-registration/README.md) 和其 helper 契約，這是條件式 global zero/copy，目標 `20003540..20003560`，並不包含 target；不是說該函式其他指令、callee 副作用或其他路徑不可能寫 target。若 caller buffer alias target，copy 的**來源讀取**也不等於 target 被寫入，且 overlap 契約仍須另證。

## 重現與限制

原始 SDK HEX 不包含於本次變更；需自行提供至 `analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.hex`，完整 SHA-256 必須與上方一致。沒有此檔時初始化測試無法執行；不要以缺失資料推論執行結果。候選 carrier 則使用 base 已追蹤、hash 相同的 reference-carrier，未新增二進位副本。

```text
python scripts/check-rf-3538-init.py
python -m unittest discover -s tests -p test_rf_3538_init.py -v
```

測試對 copy/zero guard、store、界限、tail 和 RF 長度/call bytes 變異；也測缺失指令 byte、偽造缺失 source byte、HEX 身分和半開區間邊界。變異為 host 資料，非 firmware 執行。此 bounded check 非全程 writer 掃描，亦未封閉間接 store、其他 RAM/ROM code、動態控制流、實際 callback 安裝或記憶體可用性；不操作硬體。
