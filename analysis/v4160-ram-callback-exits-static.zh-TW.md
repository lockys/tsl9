# v4.1.60：callback 出口、三組 frame 恢復與獨立尾段

承接 [callback 更新迴圈](v4160-ram-callback-loop-static.zh-TW.md)，本輪展開原先四個 cuts，驗證 ordinary RET、間接尾跳、direct 尾跳及相應 frame restores。resident 身分仍限兩份**候選**，沒有把數值相符報成實際 installed provider。

新增八個有界片段，340 bytes／128 指令；連同前段共選定 1016 bytes／348 指令。從已驗證 callback entry 出發的 local graph，原四個 cuts 均已接通，只剩 `0x20000ee8` 一個 fallthrough cut。另有 80-byte final tail 以**獨立入口前提**驗證，尚未由該 entry graph 接通，不能據此宣稱整個 callback 已完成。

只讀原 bytes、核對 operands／hash／CFG 與主機端 bit 算術；未執行或模擬目標 ISA、callback、resident、RAM／frame、MMIO 或裝置。既有 C 重建 bytes 未增加。

## 本輪範圍

| 片段 | V1.31 FLASH，end-exclusive | V1.40 FLASH，end-exclusive | 每份 bytes／指令 |
|---|---|---|---:|
| threshold exit | `0x41104..0x41138` | `0x41144..0x41178` | 52／20 |
| completion gate | `0x41146..0x41158` | `0x41186..0x41198` | 18／6 |
| ordinary epilogue | `0x41302..0x41316` | `0x41342..0x41356` | 20／10 |
| independent final tail | `0x41342..0x41392` | `0x41382..0x413d2` | 80／28 |

每片核對完整 operands 與 SHA-256，PC-relative calls／branches 在 FLASH 與 first-copy RAM 座標分別核對。APP 仍為 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；既有候選／SDK／sparse／指令格式來源合約也遞迴重驗。

## threshold exit：普通返回或恢復後 JR T1

先以 A0=then-live S0、A1=8，呼叫 helper `0x568f6`／`0x56a36`。若它正常返回，將返回 A0 的 low8 寫入 `[then-live S0+43]`，再 fresh load T1：

| 候選 | fresh T1 slot |
|---|---|
| V1.31 | `0x20003220` |
| V1.40 | `0x20003270` |

- raw T1=0：轉 ordinary epilogue。SB 不會改 A0 register，因此 epilogue 保留 helper 的完整 A0，而非只保留剛寫下的 byte43；callee 返回後的 A1 內容也不由這段重設。
- raw T1≠0：恢復八個 saved fields，設 A0=5、A1=2、SP+=32，再 JR T1，effective target=`raw T1 & ~1`。這是無新 link 的 tail transfer。

T1 在 helper 返回後才讀取，之後八個 restores 不改 T1。非零判定不等於 target 對齊、可執行、符合 ABI 或 referent 保存期有效；例如只知道 raw 非零仍不足以證明 masked target 非零。

未知 helper 的副作用、then-live S0、SP／saved words、別名與其他 writer 都是前提。尾跳後的行為與是否返回仍未知。

## completion gate：兩個入口共用後續判定

FLASH `0x41146`／`0x41186` 先設 A0=S0，呼叫 mapped local target `0x2000156c`。另一個原 cut `0x4114a`／`0x4118a` 則直接匯入後面的 MV，跳過此 local call。

兩個入口後續都再次設 A0=then-live S0，呼叫 `0x56972`／`0x56ab2`：若正常返回 A0≠0，轉 ordinary epilogue；若 A0=0，落到本輪唯一仍未展開的 cut：

```text
V1.31 FLASH 0x41158
V1.40 FLASH 0x41198
mapped RAM 0x20000ee8
```

這裡沒有根據 helper 名稱推定狀態或物件語意，也沒有假設第一個 call 保留了第二個 call 所需的 S0／frame。

## ordinary epilogue 與三組 restore 對應

ordinary epilogue 恢復 RA@28、S0@24、S1@20、S2@16、S3@12、S4@8、S5@4、S6@0，接著 SP+=32、RET。它本身不改 A0／A1，沒有建立固定 scalar return 值。

threshold 非零尾跳、ordinary epilogue、final-tail 零 flag 分支這三組 restores，都與先前 prefix 的八個 saved fields 逐一對應；部分 restore 的先後順序不同。欄位格式相符不保證 stack words 實際保存，也不證明獨立尾段使用的 frame 曾由目前已驗證的 entry 建立。

## independent final tail：先取 flag，再清 pointer word

兩份尾段映射至 `0x200010d2..0x20001122`。一開始是：

```text
A5 = fresh QK.C.LBU [then-live S1+12]  // raw 0x24dc
SW ZERO,[then-live S3+164]
if A5==0: zero branch
```

flag 在 clear 之前取樣；即使 store 與該 byte 有 alias，也不能將 branch 寫成重新讀取 clear 後的 flag。若 S3 保留先前 nominal base，清除位置為 `0x2000345c`／`0x200034ac`。這是 pointer-word store，不是 object 釋放或保存期結束的證明。

### 非零分支

fresh load A0 來自 `0x200034ec`／`0x2000353c`，然後 linked call `0x43ed2`／`0x43f5e`。只有 call 正常返回且後續存取條件成立，才執行編碼中的 store：

```text
address operand = 0xe000e204
value operand   = 0x02000000
```

接著跳往 ordinary epilogue。檢查器僅核對這些地址與值的原指令來源，沒有進行 MMIO 存取或推定任何硬體副作用。

### 零分支

先從 **then-live S0** 讀 fresh unsigned byte `b=[S0+41]`，然後才恢復 S0 與其他七個 saved fields。原 RV32 register-shift 與兩個 immediate shifts 形成：

```text
A1 = (1 << (b & 31)) & 0xffff
A0 = 0
SP += 32
tail transfer without new link
```

| b | A1 |
|---:|---:|
| 0 | 1 |
| 15 | 32768 |
| 16 | 0 |
| 31 | 0 |
| 32 | 1 |
| 47 | 32768 |
| 255 | 0 |

不能用未限位的 `1<<b` 取代。最後 AUIPC／JALR 的 rd=X0，target 分別為 `0x4354a`／`0x435d6`，保留先前恢復的 RA；它本身不是 ordinary RET，也沒有下游 ABI 或返回證據。

## 合併 CFG 的可達範圍與重播

每份合併 graph 共 174 個 instruction nodes。由原 entry `0x20000d50` 可在 conditional-normal-return CFG 走訪 146 個；另外 28 個 final-tail nodes 需要獨立 root `0x200010d2`。兩個 roots 合起來覆蓋全部選定 nodes，但這不是硬體可達性或實際執行證明。

之前的 41-node 更新 SCC 精確保留；新出口沒有把終止性未知變成已知。唯一 external fallthrough cut 為 `0x20000ee8`；RET 與兩類尾跳明列為 terminal edges，而不冒充本機 linked calls。

[檢查器](check_v4160_ram_callback_exits_static.py) 與 [完整 ledger](v4160-ram-callback-exits-static.json)：

```text
python analysis/check_v4160_ram_callback_exits_static.py
python -O analysis/check_v4160_ram_callback_exits_static.py
```

一般及 `-O` 模式逐 byte 重現 ledger，核對每片 operands／hash、雙座標 targets、三組八欄位 restores、entry 與 independent-tail root 的區分、SCC／唯一 cut、256 個主機端 RV32 mask cases，以及 40 個指定 operand mutations。這些檢查沒有執行 target frame／calls／MMIO。

接續仍需展開 `0x41158`／`0x41198` 後的中段算術與迴圈，建立獨立尾段的實際 incoming paths，追查 callees、完整 config gates／copy 合約、登錄順序及 provider／物件／frame 保存期。
