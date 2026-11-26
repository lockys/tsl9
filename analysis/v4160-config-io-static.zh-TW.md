# v4.1.60：完整 config-I/O helper、stack 輸出與重讀 buffer 合約

日期：2026-11-26。承接 [post-config callee](v4160-post-config-static.zh-TW.md) 的最後一個 call，核對兩版本完整 `44022/440b6` 本體。[檢查器](check_v4160_config_io_static.py)／[JSON ledger](v4160-config-io-static.json) 保存每條指令、條件性 CFG、store census、callback 參數及返回路徑。沒有執行或模擬 ISA、output buffer、heap、provider 或 MMIO，C 覆蓋率未增加。

## 完整本體與欄位

| 參考候選 | range（終點不含） | bytes／instructions | SHA-256 |
| --- | --- | --- | --- |
| V1.31 | `0x44022..0x440c2` | 160／61 | `72f70ec3ff48430f0b198f914b6bd949fed111707b324a237e5af2f2f3b2ef11` |
| V1.40 | `0x440b6..0x44156` | 160／61 | `4a44bc23e78c7c0b93549c29695e2f889a28e57d8e8f33570300a6f1453fe126` |

| 欄位 | V1.31 | V1.40 |
| --- | --- | --- |
| config base C | `200031ec` | `2000323c` |
| metadata base M | `2000319c` | `200031ec` |
| cached pointer M+32 | `200031bc` | `2000320c` |
| neighbor clear M+36 | `200031c0` | `20003210` |
| initial callback C+56 | `20003224` | `20003274` |
| per-iteration callback C+60 | `20003228` | `20003278` |

表中 C／M 的數值投影要求 live S0／S1 在相應存取時保持所需 base；實際 operands 使用當時的暫存器值。每條 opcode／operand／target 均逐項檢查，三組 AUIPC/JALR pairs 另解算數值 target。沿用固定 APP／SDK header／carrier hashes、已保存 LLVM 欄位與 vectors 的條件性 Xwchc 解讀，以及 RV32I/M/C 規則；實體 profile 與 installed 綁定仍未知。

## 初始 callback：stack word，不是 allocation reply

入口建立 32-byte frame，保存 S0／RA／S1／S2 至當時 SP+24／28／20／16。依序要求 **完整 U32[C+8]、U32[C+56]、U32[C+60] 都非零**；任一缺少便在 encoded 正常返回路徑設 A0=1。

第一個間接 call 的參數是：

```text
target = 較早讀出的 U32[C+56]（JALR target 清 bit0）
A0 = 初次讀到的 U32[C+8]
A1 = 1
A2 = SP_after_frame + 12
```

`[SP+12,SP+16)` 是 output word，與保存 S2 的 `[SP+16,SP+20)` 相鄰但不重疊。完整本體在 call 之前沒有初始化 output word，也沒有檢查 callback 實際寫入多少 bytes。A1=1 是原始參數，不等於本輪已證 provider 的寫入長度。

callback 正常返回後，caller fresh 讀 U32[live S0+8] 與 U32[當時 live SP+12]，比較這兩個 word；相等設 A0=1 返回。**它不檢查 callback 的 scalar A0 reply，也不是把 output 與最初傳入的地址暫存值比較。** 若 SP 未保存，後者甚至不一定是 call 時交出的 output word；S0 的 config 關係也需要保存。callback 不寫、只寫一部分或改變 config／frame 時，不能假造有效 readback。

## mismatch 後的配置與填值

不相等才進入後段：

1. fresh U16[C+12]=L0 作 A0，A1=78，呼叫 allocation core `0x20000040`。
2. **回覆 P 先無條件存到 M+32，再判斷是否為零。** P=0 走 A0=1 返回路徑；沒有在此清除 M+36。
3. P 非零時，fresh U16[C+12]=L1 作 A2，A0 仍為該次 P、A1=255，呼叫 fill `0x2000039c`。

L0／L1 是不同讀取，不能無條件認定相等或認定填值 extent 一定受配置大小保護。S2=0 的指令在 fill call **之前**，所以連「進入 loop 時 S2 為零」也需要該呼叫保存條件。

三個直接 call windows 的 offset 分別是 +72/+76（allocate）、+100/+104（fill）、+118/+122（private free `0x20000110`）。它們與先前已定位的候選 helpers 數值一致；本輪把呼叫邊當成 opaque 正常返回邊界，不以函式名稱推定副作用。

## 迴圈：每輪重新取得指標、長度與 callback

loop head fresh 讀 N=U8[C+14] 與 Pcurrent=U32[M+32]。判斷是 **signed32(S2) < N**；N 為零延伸 byte。繼續時按指令順序：

```text
Li     = fresh U16[C+12]
base_i = fresh U32[C+8]
target = fresh U32[C+60]
A0     = (base_i + Li * old_S2) & 0xffffffff
A1     = Li >> 2
A2     = Pcurrent
S2     = (S2 + 1) & 0xffffffff
U32[Pcurrent] = A0
call target(A0, A1, A2)
```

S2 增量在 callback 之前，address 使用增量前的 index。A1 是除四向下取整，未向上補齊；本輪未證 callback 的具體單位／寫入效果。word store 的目的地是 **Pcurrent 本身**，不是 Pcurrent+4*index，也不是 M+32。

每輪都重讀 C+60，卻沒有再次作非零 guard。入口曾檢查該欄位非零，不代表這次 fresh target 仍非零。每輪 Pcurrent 也可能已改，不能自動沿用 allocation 返回的 P；Li、L1、L0 同樣需要分開。

callback scalar A0 reply 不控制重試或錯誤返回。正常返回只回 loop head 重新取得欄位；沒有以其 reply 證明 NV operation 成功。

### 有條件的 255 輪上界

若 fill 之後 live S2=0，之後各 callback 正常返回並保存 S2，且 code／控制流程／必要 context／reads 有效，每次繼續必有 index≤254，接著加一≤255；fresh N 最大只有 255。因此即使 N 每輪變動，最多仍可進入 255 輪。

這不是無條件終止保證：callback 可以不返回、改 S2／SP／S0／S1 或造成後續 fault。若 S2 被改為帶符號負數，signed BLT 的結果也不能用 unsigned 比較代替。

完整正常返回圖的 loop SCC 有 13 節點，offsets 為 `108,110,112,138,140,142,144,148,150,152,154,156,158`；callee 內部的 successors／loops 不在這張本機圖內。

## cleanup 與返回值

退出 loop 時，以該次 loop head **最後重讀的 Pcurrent** 呼叫 private free，並非必然以最初 P 交回。其 scalar reply 被忽略，之後依序：

```text
A0 = 0
U32[M+32] = 0
U32[M+36] = 0
恢復 frame 並 RET
```

所有 early gates、equal readback、null allocation 路徑則明確返回 1。這些 0／1 是編碼中的 caller 控制流程，不能當作實際 NV 效果或物件已釋放的收據。

接回前輪 post-config callee，在上述正常返回與 context 前提下，其沿用此 helper A0 的路徑可收斂為 {0,1}；更外層 config 函式仍自行返回 0，沒有把這個差異傳給 APP。

每版本有 8 個本機 store 指令：四個保存字、一次 allocation cache store、每輪一次動態 U32[Pcurrent]、兩次 cleanup clears。encoded GPR writes 為 RA／SP／S0／S1／S2／A0／A1／A2／A4／A5。未知 callback／heap stores 可能與 frame、metadata、code 或其他欄位 alias，不能把本機 census 當成全程保存證明。

## 實際重播與反例

```text
python analysis/check_v4160_config_io_static.py
python -O analysis/check_v4160_config_io_static.py
```

兩模式均實際輸出：

```text
PASS: 64 gate shapes; 65536 loop variants; 1024 signed controls; 65536 U16 counts; 40 address cases; 12 specified raw mutations
PASS: 2 complete bodies, 320 bytes/122 instructions; 16 local stores; 10 opaque call sites; stack/cache distinctions
PASS: ledger exact replay; installed/callback output/context integrity UNPROVED; NO ISA/provider/heap/MMIO execution
```

gate、loop variant、signed controls、U16 floor 與地址 cases 都是主機寬度代數，沒有建立 output buffer、provider reply 或 loop memory state。BLT 在共用 CFG 演算法中只用另一個雙 successor branch 標記處理拓撲，signed operands／方向仍另外驗證。

十二個 raw mutations 改 gate field、初始 callback offset、stack output address、output load offset、allocation length offset、cache store、loop cache load、signed branch、stride length、fresh callback offset、counter increment、neighbor clear offset。均直接進入推導並要求命中特定 guard，沒有把完整 hash 不符或任意 exception 當成通過。

重跑需八個已發布 Python dependency 模組，以及本機固定 APP、兩份 carrier、SDK header 與 LLVM 來源／vectors。候選輸入目錄未隨本次發布，僅 clone repo 不足以重現。預設只讀重算並精確比對 JSON；`--write` 僅建立不存在的 ledger。

下一步為 APP 實際提供的 C+56／C+60 callback 身分、輸出 buffer 的寫入／長度與保存條件，以及 provider／installed 綁定。前輪 sparse HEX 的最後一個缺失 source word、實際物件保存期與中斷／外部 writer 也仍未知。
