# v4.1.60：完整 callback 原指令與局部 CFG 閉合

承接 [callback 中段與等待分支](v4160-ram-callback-middle-static.zh-TW.md)，本輪補齊最後缺口與兩條 MULHU。兩份 resident **候選**的對應 callback，各 **978 bytes／321 指令**，現在具備完整 byte interval、逐指令 operands 與 conditional-normal-return local CFG 的閉合驗證。

閉合的範圍是原本體：沒有未接通的 local continuation，所有指令 nodes 可由 entry 做局部圖走訪，保留精確 3／41-node SCCs 與三個 terminal instructions。這不等於 transitive callees、實際執行、終止、硬體副作用或 installed provider 合約已完成。

全程只解碼原 bytes、比對 operands／hash／CFG 與主機端乘積代數。未執行或模擬目標 ISA、callback、resident、RAM／frame、copy、MMIO、FENCE.I 或裝置。既有 C 重建 bytes 未增加。

## 兩個完整原本體

| 候選 | FLASH 範圍，end-exclusive | first-copy RAM 範圍 | 完整 SHA-256 |
|---|---|---|---|
| V1.31 | `0x40fc0..0x41392` | `0x20000d50..0x20001122` | `b353bc4b279cf6f978caa0b230d7959a5376661d62929c6b77004863849bc0e5` |
| V1.40 | `0x41000..0x413d2` | `0x20000d50..0x20001122` | `957eb61b592d6c4481b4bff30bcb6c7e9bcf1638f54a418e43f4acde383b1990` |

總計 1956 bytes／642 指令。本輪閉合的缺口合計 504 bytes／158 指令，其中新釘選算術及 footer 為 380 bytes／118 指令；另外 124 bytes／40 指令沿用先前 loaded-source 三片段的 operands 規格，沒有把它們重報為新增獨立分析量。

| 缺口片段 | V1.31 FLASH，end-exclusive | V1.40 FLASH，end-exclusive | 每份 bytes／指令 |
|---|---|---|---:|
| 算術與 MULHU | `0x41222..0x412ae` | `0x41262..0x412ee` | 140／41 |
| 已驗證 selector | `0x412ae..0x412d0` | `0x412ee..0x41310` | 34／11 |
| pointer footer | `0x412d0..0x41302` | `0x41310..0x41342` | 50／18 |
| 已驗證 alternative | `0x41326..0x41336` | `0x41366..0x41376` | 16／5 |
| 已驗證 bypass | `0x41336..0x41342` | `0x41376..0x41382` | 12／4 |

所有片段都在原 FLASH 及 mapped RAM 座標分別核對。完整 decoder 的所有 instruction starts 與 CFG edges，必須恰等於先前釘選片段與本輪片段的聯集；整段 hash、978 bytes 覆蓋與 321 nodes 也另行確認。

APP 仍為 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；既有候選／SDK／sparse／指令格式來源合約遞迴重驗。

## 進入 MULHU 前的條件界線

算術段重新載入 b=`U16[then-live S1+8]`、a=`U16[then-live S0+134]`，形成 S2=`1000000` 及先前相同的回繞 quotient：

```text
Q = ((a*b+999999) modulo 2^32) unsigned_div 1000000
G = fresh U8[0x20003203 / 0x20003253]
threshold = Q+G
if unsigned threshold < incoming A0: jump final tail
```

Q≤4294、G≤255，因此最後這次加法不溢位、threshold≤4549。若沿先前非零差值的 fallthrough 到達此段並繼續，incoming A0 在 1..4549；這是有條件的 operand 界線，不是已觀察輸入值。

factor b 沒有 local zero guard。word-pair call pattern 不能取代 callee 對零值、例外、保存或返回行為的證據。

## 兩條 MULHU 與三個 arithmetic call sites

新增 decoder 只擴充標準 unsigned MULHU：`word & 0xfe00707f == 0x02003033`。兩個原 forms 分別為 MULHU A1,A0,S2 與 MULHU A5,A0,S2；原 bytes 為 `b3352503`、`b3372503`。

第一組 MULHU／MUL 形成 unsigned incomingA0×S2 的完整 `(A1:A0)` pair；此時 S2=1000000、A2=b、A3=0。另在 call 前把 fresh `U16[object+34]` 放入 S4。

三個 arithmetic call sites 的 mapped target 都是 V1.31 `0x6df1a`／V1.40 `0x6e10a`。它們的 operands 如下，保存條件均不能省略：

1. 第一次接收上述完整 product pair。返回後 S6=low32(then-live S4+returned A0)，沒有把 returned A1 加入這個 S6。
2. 第二次接收 A0=low32(then-live S4*S5)、A1=0、A2=1000000、A3=0。
3. **只有第二次返回 A0 非零**，才形成其 `(A1:A0)` pair×then-live S2 的低 64 bits，再以 A2=then-live S5、A3=0 呼叫第三處。

第三處之前的 pair 算術是：

```text
newLow  = low32(S2*returnedA0)
newHigh = low32(S2*returnedA1 + high32(returnedA0*S2))
```

這個乘積代數成立，仍不證明 division64、四捨五入、copy、ownership 或 return ABI。第二次若 returned A0=0，會跳過第三處與後續 field34 store，即使 returned A1 非零也一樣。

第三處正常返回後，原指令做 low32(then-live S4-returned A0)，再以 QK.C.SH（`0xb02a`）僅將 low16 寫到 `[then-live S0+34]`。所有跨 call 的 S0／S2／S4／S5／S6 與 frame 保存都保持前提。

接著設 A0=13，呼叫另一個 mapped helper `0x63eda`／`0x63fc4`，才進入先前驗證的 loaded-hook selector。這些地址只標識呼叫目標，沒有賦予未查證的服務名稱。

## pointer footer：兩次 fresh pointer 與原始未遮罩值

selector 的兩種登錄路徑匯入 footer 後，原指令順序為：

```text
P1 = fresh U32[0x2000353c / 0x2000358c]
SB5 [0x2000351b / 0x2000356b]
V = fresh U32[P1+12]
SW (V & 0xffffdfff),[P1+12]
FENCE.I
P2 = fresh U32[same pointer-source word]
S6 = low32(then-live S6<<1)
SW 0x2000,[P2+8]
SW S6,[P2+100]
SW V,[P2+12]
```

`0xffffdfff` 清 bit13，但最後一個 store 使用原始**未遮罩**的 V。P1／P2 是分開讀取，不能推定相同；即使相同，最後 store 也不保證 field12 一直維持清 bit13 的值。

FENCE.I 與所有 pointer stores 都只按原編碼記錄。沒有執行它、賦予同步／硬體效果、認定所指 object 類型，或排除 aliases、interrupts、重新進入與其他 writers。

## 本體閉合與仍保留的外部前提

每份完整 local graph：

- 978-byte 原區間、321 個指令 nodes，entry 可做局部走訪，沒有 unresolved local continuation cuts。
- 兩個精確 SCC，分別為 3-node 等待與 41-node 更新區；終止性仍未證明。
- 三個 terminal instructions：JR T1、ordinary RET、AUIPC／JALR rd=X0 的直接尾跳。各自的 downstream 行為與保存合約仍未知。

所有 linked calls 在這份 CFG 只採**條件性正常返回邊**，不是已證明的 callee summary。完整原本體驗證因此不會自動解除 transitive callees、實際路徑可行性、frame／payload 保存期或 installed 身分的未知。

[檢查器](check_v4160_ram_callback_closure_static.py) 與 [完整 ledger](v4160-ram-callback-closure-static.json)：

```text
python analysis/check_v4160_ram_callback_closure_static.py
python -O analysis/check_v4160_ram_callback_closure_static.py
```

一般與 `-O` 模式逐 byte 重現 ledger，驗證整段 hash／byte coverage、所有釘選 operands、完整 CFG／SCC／terminals 與 42 個指定原指令 mutations。主機乘積檢查用獨立 16-bit limb oracle 對照 4145 個 unsigned product cases，另檢查 4549 個受條件限制的 million-product cases、pair×word modulo2^64 代數與 QK field34 store。沒有執行 target MULHU、helper 或 callback。

接續可針對已列出的 local helpers 與 word-pair service 展開，並補完整 config gates／copy 合約、實際綁定、object/global 寫入來源、硬體與保存期證據。
