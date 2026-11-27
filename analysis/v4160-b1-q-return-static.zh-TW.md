# v4.1.60：Q 保存延伸至 RF 返回與 role／config 邊界

接續 [Q 初始化來源](v4160-b1-q-source-static.zh-TW.md)與[有界 writer 普查](v4160-b1-q-writers-static.zh-TW.md)。本輪將 **同一次、選定初始化路徑** 的 Q 保存證書由 large 取樣點延伸至 radio parent 正常返回；在原先候選身分、所選分支、有效 context／frame、正常存取／callee 返回／poll 終止、無物理別名及外部干擾等前提下，Q 槽保持 `0x40025000`，RF 回覆仍為：

```text
fresh U32[0x400250d0] & 0xf0ffffff
```

尾段另將 H+7 清為零，不能把最初的 state1 當成後續呼叫仍有的狀態。這不是實際 boot、硬體 readback、全域 Q 不變值、installed provider 或完整保存期的證明。

## 從取樣到 radio parent 返回

兩版 large 從 `+0x160` 的 Q load 起，到 `+0xd32` 的 RET，共有 **908 條可達編碼指令、109 個 store**。此區域沒有 nested call，A5 唯一定義就是起點的 Q load，所有 store 都是四 byte、以 A5 為 base。因此，在 captured Q 為 `0x40025000` 的前提下，這些 stores 的名義目的區間皆避開 T／R／Q／descriptor 四個固定 RAM 槽。

後續 enable／wait／final 三個完整 leaf 合計 **17 個 store**：除 wait 的 `T+100` 外，目的地皆由重新讀取的 Q 作 base。將此部分與 large 及 RF tail 清理的五筆寫入接回前輪四槽保存證書，可在明確前提下持續保存 T、R、Q 與 descriptor。

| 部分 | 每版編碼 store 數 | 重要限制 |
|---|---:|---|
| Large 取樣後至 RET | 109 | 持有 Q；不重建 DIV／packing 的完整數值語意 |
| Enable／wait／final | 17 | 依四槽保存投影；wait 的輪詢必須退出 |
| RF tail 清理 | 5 | 寫 R+0、Q+8、T+80、H+7、control word |
| 合計 | 131 | 指令／區間證書，不是一次執行的寫入次數 |

Wait 可重複執行讀取與分支；本輪沒有證明硬體進展或有界終止。名義 `0x400xxxxx` 的存取必須在實體上不別名到受保護 `0x2000xxxx` RAM；數值區間不重疊本身不提供這項保證。所有必要 context、S／SP／RA、frame、code 與存取條件仍須成立。

RF tail 的 `+0xce` 是對 H+7 的一 byte zero store。這個狀態結果指 **RF parent 的選定主路徑返回時**；不自動外推到稍後的 role 登記或其他事件。

## Role 與 config 的固定目的地

令 `F=0x20003540+80*i`、`C=F+32`、`Q=F+80=C+48`，其中 i=0／1 分別為 V1.31／V1.40。

| 寫入 | 目的範圍／位置 | 與 Q 的關係 |
|---|---|---|
| Role 在 radio parent 返回後 fill | `[C,C+36)` | 終點距 Q 還有 12 bytes |
| Role 的固定 stores | C+0 word、C+16 byte | 不碰 Q |
| Config fill／copy | 各自寫 `[F,F+32)` | 不碰 Q；copy 來源不是目的地 |
| Config 固定 stores | F+1、F+25..29、C+4 word、C+15 byte、C+20 word | 不碰 Q |

檢查器逐筆核對兩個完整 caller 的 12 個 non-frame store 與三個 bulk 目的範圍。C+4 的 zero／allocation-pointer store 是兩個編碼位置；C+20 依原指令是 **四 byte word**。Frame stores 另依有效且不別名 Q／code／其他 live data 的前提處理。

Fill 與 copy 重用完整的 46／58-byte 原指令 guard，並以 first-copy 來源與 strict HEX 接回 runtime 名義入口 `0x2000039c`／`0x20000332`。這是匹配 helper 與其指定目的範圍的條件式合約，沒有證明實機正在使用該映射。Config 來源還必須是有效可讀的普通記憶體，不藉來源讀取引入未封閉的硬體／別名副作用。

Role 仍會呼叫登記函式，因此固定區間分離不足以單獨證明整個 role 保存 Q。若該動態寫入也符合下節排除條件，且其他前提成立，可將 Q 保存延伸至 role 正常返回；role 本身最後將 A0 設為零，不能把其回覆混同於內層 RF masked word。

## 登記表的動態寫入邊界

完整登記 leaf 為兩版 `0x43c4e`／`0x43cda`，48 bytes／16 指令，沒有 nested call 或 frame。它分別取樣 n 與 capacity 的 U8 值，只用 `n < capacity` 決定接受：

- 拒絕時不寫入，也不讀 table pointer。
- 接受時先寫固定 count byte，再對 `D=(T+4*n) mod 2^32` 寫入四 bytes，T 是本次載入並持有的 table pointer。
- 固定 count byte 不碰 Q；動態目的地需要另證，函式本身沒有 Q 別名／table extent／alignment guard。

對指定 n，未假設對齊時，Q 重疊當且僅當 `D` 落在 Q−3..Q+3。若 T 與 Q 都四 byte 對齊，則簡化為 `T=(Q−4*n) mod 2^32`。

遍歷全部 65,536 組 U8 n／capacity，有 32,640 組接受，所有可能接受的 n 為 0..254。對至少一組可接受 n 而言，會重疊 Q 的 **T 數值**聯集為：

```text
未限定對齊： [Q−1019, Q+3]，共 1023 個數值
限定四 byte 對齊： Q−1016, Q−1012, …, Q，共 255 個數值
```

這是地址區間／模數等式，不是實際 table 值、執行路徑或可達性證據；table pointer word 的存放位置也不能當成 T 的值。若另外採用既有首次配置的名義 `T=0x200047f4`，全部放寬後可接受 U8 索引的 store envelope 為 `[0x200047f4,0x20004bf0)`，仍避開兩版 Q。這只排除名義目的地址與 Q 的重疊，**不證明全部放寬索引都在實際配置容量內、T 仍是該值，或存取一定有效**。

## 可封閉的 config 分支族

完整 config 的無迴圈 CFG 有 1538 條語法路徑。其中 **386 條**不經 private release（+0xaa）或 allocator（+0xc6）：兩條早退，以及 384 條使用匹配 fill／copy 的發布路徑。在固定 stores、helpers、普通來源、有效非別名 frame、正常存取／返回及無外部干擾等條件下，這一族可保存入口 Q；不需要猜測 private allocator／release 的副作用。

這是 CFG 路徑分類，不代表 1538／386 種實際可達場景。對完成發布的路徑而言，fresh 舊 C+4 為零可跳過 release，fresh F+0 的 bit0 為零可跳過 allocator。

**既有 APP constructor 提供 flag1，匹配 copy 且該取樣保存時會走 allocator，因此不屬於這個無配置／釋放的發布族。** 本輪也未封閉 role 與較晚 config／postservice 之間的 param774 等中間呼叫，不能據此宣稱整條 APP boot 保持同一 Q。

## 驗證與未完成項

[檢查器](check_v4160_b1_q_return_static.py)與[固定 ledger](v4160-b1-q-return-static.json)重用完整來源／原指令／CFG guards，重新接通 strict HEX、helper 映射與 call sites；另保留每版 131 個尾段目的區間、caller 固定寫入、386 條路徑摘要與登記表別名等式。34 個 caller／bulk／allocator 邊界及 16 個 capture／store／leaf／H+7 原指令位置突變都必須被拒絕。

```powershell
python analysis/check_v4160_b1_q_return_static.py
python -O analysis/check_v4160_b1_q_return_static.py
```

新增原始 byte 覆蓋為 **0**，APP C 重建覆蓋率不變。仍需追查 fresh table／heap 來源、實際 allocator／release 與中間 callees、installed provider／實體映射／IRQ／poll 進展，以及同一物件的 N+12 writer 與完整保留／消費釋放／通知保存期。

全程離線，沒有目標執行、模擬、mutable target model、硬體存取、封包重放或 target network。
