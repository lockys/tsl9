# v4.1.60：設定返回前的 resident 初始化 callee 完整靜態合約

日期：2026-11-26。承接 [fallback 初始化](v4160-fallback-initialization-static.zh-TW.md) 的最後一個直接 call，展開兩個完整 272-byte callee。原先分散的 V1.31 前綴／寫址說明，在本輪加入兩版本全部 operands、條件性 CFG、完整本體 hash、直接 stores census 與反例重播。未執行或模擬任何目標 ISA、heap、provider 或 MMIO，C 還原覆蓋率沒有增加。

## 完整來源與呼叫邊

| 參考候選 | callee range（終點不含） | bytes／instructions | SHA-256 |
| --- | --- | --- | --- |
| V1.31 | `0x43b3e..0x43c4e` | 272／87 | `3093ac8a6c0596e6c6b2afaa1f4480c76b6dfb7e39f6df5d3e121d4007c456d6` |
| V1.40 | `0x43bca..0x43cda` | 272／87 | `970669cbefbaf5eac23456590dd1b4d5769bddddf02f0f8e25c72f872251cf24` |

[檢查器](check_v4160_post_config_static.py) 重新核對外層設定函式的 target 關係、完整本體與每個 operand；四個 AUIPC/JALR pairs 另解算數值 target、transfer PC 與 link。[JSON ledger](v4160-post-config-static.json) 保存完整解碼、stores、calls 與條件性正常返回圖。template 正規化只涵蓋已另外檢查的 relocation／RAM operand。

沿用固定 APP／header／carrier 身分及已保存 LLVM 欄位與 vectors 的條件性 Xwchc profile；本輪新增的 MUL 依條件性 RV32M integer semantics 解讀。實體 I／M／C／Xwchc 支援、installed resident、最終執行 bytes 和 RAM 值仍不是實測證據。

| 角色 | V1.31 call window | V1.40 call window | 數值 target |
| --- | --- | --- | --- |
| 清除 20 bytes | `43b6e/43b72` | `43bfa/43bfe` | `2000039c` |
| 清除 40 bytes | `43b80/43b84` | `43c0c/43c10` | `2000039c` |
| heap 初始化 callee | `43b88` | `43c14` | `43104 / 43190` |
| allocation core | `43bbe/43bc2` | `43c4a/43c4e` | `20000040` |
| 清除 allocation reply | `43bda/43bde` | `43c66/43c6a` | `2000039c` |
| 後段 callee | `43c00` | `43c8c` | `4329a / 43326` |
| 後段 compressed call | `43c04` | `43c90` | `44022 / 440b6` |

每個版本七個巢狀 call；本輪均作為 opaque 邊界。CFG 的 fallthrough 只表示明示假設的正常返回，不代表 callee 終止、保存 context 或沒有記憶體副作用。

## 固定寫入與欄位地址

以下數值地址要求對應 live base registers 保持本體所需值。它們描述直接指令及提出的 fill 請求，不能把 request 當成已完成的 store 範圍。

| 欄位／請求 | V1.31 | V1.40 |
| --- | --- | --- |
| 前三個 zero word | `200031e8,20003230,200031e0` | `20003238,20003280,20003230` |
| fill20 start | `200031c8` | `20003218` |
| fill40 start／metadata base B | `2000319c` | `200031ec` |
| 配置 input byte c | `20003201` | `20003251` |
| capacity byte | `2000319e` | `200031ee` |
| allocation reply slot | `2000322c` | `2000327c` |
| table pointer slot | `200031c4` | `20003214` |
| event table pointer slot | `200031e4` | `20003234` |
| count byte | `2000319d` | `200031ed` |

每個完整本體有 **14 個直接 store**：8 個帶 live-base 前提的固定欄位、3 個 SP-relative 保存字、3 個動態表項 word。表項不是額外的第四個 count store；count byte 已包含於上述固定欄位。

8 個固定欄位及兩個固定 fill 請求，數值區間皆與 fallback `20003220/20003270` 不重疊。這不是整條函式的寫入缺席證明：stack、未知 reply 指標、重讀表基址、各 callee 或非同步 writer 仍可能與 fallback／saved frame／code alias。

## 配置前容量與 request：只適用該次讀值

heap 初始化 callee 正常返回後，讀 c=U8[配置副本+21]，本體計算：

```text
N0 = (14 + 3*((c >> 2) + (c & 3))) & 255
allocation A0 = 576 + 6*N0
allocation A1 = 1
```

全部 256 個 c 的算式可收斂為 67 個容量值：14、17、…、212；此 byte 域內的容量算式本身不回繞。request 範圍為 **660..1848**。接前輪 core rounding 算式，這些 request 全部大於 52，會選 large head；仍不證明實際配置成功或取得有效空間。

allocation 回覆 A0=P **先無條件存至 reply slot，再 BEQZ P**。若 P=0，直接進 epilogue、正常返回 0；先前 globals／capacity stores 不回滾。

## 保存不同的 reload 身分

不能把後續讀值都命名為原來的 N0／P：

1. P 非零時，重新讀 capacity byte 得 N1，以 A0=P、A1=0、A2=`576+6*N1` 提出 fill。N1 只有 U8 寬度界，長度為 576..2106；本輪未證 N1=N0，也不能宣稱這一定落在原 allocation extent 內。
2. fill 正常返回後，再讀 reply slot 得 P′，再讀 capacity 得 N2。建立 `T=(P′+576)&0xffffffff`，另建立 event pointer=`(T+4*N2)&0xffffffff`。不直接沿用 fill 的 A0 reply 或先前 P。
3. 後兩個 opaque callee 返回後，再讀 count n=U8[B+1]，並重新讀 table pointer slot 得 T′。最後三筆函式表寫入使用這個 n／T′ 快照，而非無條件使用前面建立的 T。

N0、N1、N2、P、P′、T、T′ 的相等性需要額外保存、有效存取、穩定資料與非 alias 證據。正常 call 返回本身不足以提供這些條件。

## 三筆表項與 count 的實際順序

| 候選 | literal0 | literal1 |
| --- | --- | --- |
| V1.31 | `0x432a4` | `0x43326` |
| V1.40 | `0x43330` | `0x433b2` |

本體依序執行（地址均為 RV32 模數加法）：

```text
U32[T′ + 4*n]                = literal0
U32[T′ + 4*((n+1)&255)]      = literal1
U8[B+1]                     = (n+3)&255
U32[T′ + 4*((n+2)&255)]      = literal1
```

沒有本機 capacity check 保護這三筆 store；任意 byte n 的三個 indices 彼此不同，但不代表在已配置表容量之內。n 接近 byte 尾端時 indices／count 都可能回繞。

**count store 在第三筆 table store 之前。** 若未知 T′ 指向 count、saved frame 或 code，不能從局部賦值式推論最終 count 或 caller 狀態；表／欄位不重疊與 code 穩定仍是必要前提。檢查器的 modulo 地址代數不會用這些值去讀寫任何目標記憶體。

## 返回、CFG 與保存限制

完整本體的本機 CFG 無循環，唯一條件分支是 allocation-null；各 callee 的循環／例外／非返回均未由此排除。本體用 16-byte frame 保存 RA／S0／S1，最後從 frame 重載。encoded GPR writes 為 RA、SP、S0、S1、A0..A5；沒有把其他暫存器的直接 non-write 當成 opaque callees 的 ABI 保證。

非零 allocation 路徑在最後一個 callee 返回後，剩餘 encoded suffix **未再寫 A0**，因此返回該 callee 的 A0 回覆，並非本體強制返回 0。外層設定函式則在這個 callee 正常返回後自行設定返回 0；其 0 不是三筆登記皆成功、extent 合法或 callback 已綁定的收據。

## 實際重播與反例

```text
python analysis/check_v4160_post_config_static.py
python -O analysis/check_v4160_post_config_static.py
```

兩模式均實際輸出：

```text
PASS: 256 capacity/request/core-head cases; 256 fresh-capacity ranges; 1024 modulo table cases; 10 specified raw mutations
PASS: 2 complete bodies, 544 bytes/174 instructions; 28 local stores; 14 opaque call edges; conditional CFG
PASS: ledger exact replay; installed/nested effects/pointer stability UNPROVED; NO ISA/provider/heap/MMIO execution
```

capacity/request 與 fresh-capacity cases 是主機代數；1024 cases 為全部 byte n × 四個 T′ 地址樣本（含會回繞者），只檢查三個 word 的模數位址集合，未證資料所有權、容量或合法存取。

十個 raw mutations 改 input-byte offset、容量 mask、容量 store offset、allocation-reply slot、null branch 方向、fresh capacity offset、fresh pointer slot、fresh table slot、registration index mask、count store offset。直接進入推導並要求指定 operand guard 拒絕，不以完整檔案 hash 不符或任意 decoder exception 充作通過。

重跑需七個已發布 Python dependency 模組，以及本機固定 APP、兩份 carrier、SDK header、前輪 LLVM 參考。候選輸入目錄未隨本次發布；僅 clone repo 不足以重現。預設只讀重算並精確比對 JSON；`--write` 僅能建立不存在的 ledger。

下一步仍需展開本輪七個邊界中的 heap 初始化與後段 callee，追查它們對 fallback、capacity、reply／table pointer 及 saved frame 的副作用，並維持實際 installed 綁定未知。前輪完整 sparse HEX 的最後 4-byte source 缺口也未由本輪補齊。
