# v4.1.60：config+44 完整呼叫範圍、8520 清零邊界與周邊寫入

日期：2026-11-26。承接 [完整 callback 與 low16 返回鏈](v4160-app44-callback-static.zh-TW.md)，展開其餘十個直接 callee，另追入 reset wrapper 的 `19160`。本輪補齊這個 callback 的軟體呼叫範圍，並釐清 `8520` 的兩個計算跳轉。[檢查器](check_v4160_app44_closure_static.py)／[ledger](v4160-app44-closure-static.json) 保存完整指令、獨立 operand guards、帶呼叫 context 的靜態圖與條件。

**在有效、不回繞且保存完整的 stack/code 等前提下，8520 可支持 callback 的 32-byte 清零請求；已展開的軟體 callees 沒有留下未知 call target。** 實際 provider、MMIO 映射與副作用、外部 writer、物件保存期及輪詢終止性仍未證。硬體也不能說完全恢復：reset word `4002100c` 不在前輪 16 組 snapshot 中。

全程只做離線讀檔、反組譯、靜態圖與主機整數代數，沒有執行或模擬 target ISA、暫存器、buffer、callback、provider 或 MMIO。C 重建覆蓋率沒有增加。

## 新增完整本體

下表 range 終點不含；每份完整 SHA-256 均固定於 checker／ledger。

| range | bytes／instructions | 靜態 store 位置數 | 用途依編碼描述 |
| --- | --- | ---: | --- |
| `8520..85c8` | 168／55 | 19 | 對齊、word bulk、byte prefix／tail fill |
| `188e2..1892e` | 76／25 | 1 | 兩種 pointer 判斷與 reset set／clear 呼叫 |
| `1892e..18986` | 88／37 | 3 | 依設定來源更新 base+4/+8/+44 |
| `18986..18996` | 16／7 | 1 | base+8 bit0 set／clear |
| `18996..189ae` | 24／10 | 1 | base+8 mask00500000 set／clear |
| `189ae..18a66` | 184／64 | 5 | selector／position 的 register shifts 與兩次 RMW |
| `18a6e..18a8e` | 32／12 | 1 | 固定 word40012408 的 mask00800000 |
| `18a98..18ab0` | 24／10 | 1 | base+4 mask04000000 set／clear |
| `1908c..1909e` | 18／8 | 1 | 固定 word40021004 的 mask／OR |
| `19124..19142` | 30／12 | 2 | 固定 word40021018 set／clear |
| `19160..1917e` | 30／12 | 2 | 固定 word4002100c set／clear |

本輪合計 **690 bytes／252 instructions／37 static store sites**。與前輪 callback／poll／result 三個互不重疊本體合計 **14 個完整本體、1072 bytes／390 instructions／79 store sites**。互斥分支的 store 分別計數；一個 store 在 loop 重複執行不另增加靜態位置數。

252 條新增指令均逐項核對 opcode／operands／targets，並另核對完整 hash、store census、GPR write set 及完整 CFG 邊界。新增標準 SUB／SLL／AND 與 compressed SUB 解碼。沿用固定 APP／SDK header／carrier、LLVM source hashes／Git blobs 與 28 vectors 的條件性 ISA 解讀；不以本機工具能解碼代替實體 profile 識別。

## 8520 的寫入分段

完整本體 SHA-256：

```text
50232f532bf996f5d738050c60480fab6069d6ef4cb842cfc582170e351630c6
```

入口 A0=D、A1=V、A2=N。A0 本身沒有被任何指令定義，正常回覆因此保持 D；SP／GP／S registers 也沒有明確寫入。

1. N≤15 直接前往 byte tail。
2. N>15 且 D 未對齊16，先寫到下一個16-byte 邊界。這個 prefix 長度是 `16-(D&15)`，不是16。
3. 將 low8(V) 擴展成四個相同 byte 的 word，處理每16 bytes的四個 SW。
4. 剩餘0..15 bytes由 byte tail完成。

prefix／tail 內部的 SB 順序是**由高 offset 到低 offset**。bulk 的 SW offsets為0、4、8、12；迴圈用 unsigned pointer 比較，不是剩餘計數比較。

因此「恰寫 N bytes」需要有效存取、不破壞 code/context，並明確要求 **`D+N ≤ 0xffffffff`**，使 one-past end 也不回繞。即使最後一個資料 byte 尚未越界，end pointer 回繞仍可能改變原 BLTU 行為；本輪沒有把任意 U32 輸入都視為正確或必然終止。

### 兩個計算跳轉的有限 targets

| transfer | 來源域與算式 | target 範圍 |
| --- | --- | --- |
| `8556`，JALR rd=0 | r=剩餘0..15；`8550 + 4*(15-r) + 10` | `8596-4*r`，16 個位置 |
| `85b6`，JALR rd=1 | m=D&15，分支保證1..15；`85ae + 4*m - 88` | `8556+4*m`，15 個位置 |

所有 target 都是同一個已捕獲 body 的指令邊界。r=0 直接落在 `8596` RET；其餘落在對應 SB。prefix JALR 將 link設為 `85ba`，此前把原 RA 存到 T0；byte序列不改T0，內部RET後由 `85ba` 將RA還原。

這裡不能把 `8596` 一律當作退出，也不能把兩個 JALR 都當成普通 call fallthrough。checker 的靜態圖只用兩種呼叫 context：

- outer：55 個指令節點。
- prefix：15個SB加一個RET，共16節點；其RET連到 outer的85ba。

總共71個圖節點。context只表達固定的內部 return 關係，不包含 target 暫存器值、記憶體、provider reply 或指令執行模型。圖保留分支的雙 successor，沒有宣稱所有組合路徑都可行。

### 接回 callback 的 32-byte clear

前輪已核對 `19814→8520`，參數為 callback live SP+32、0、32。對任一 D&15：

```text
prefix = 16-(D&15)  if D不對齊且N>15 else0
left   = N-prefix
bulk   = left//16
tail   = left%16
prefix + 16*bulk + tail = N
```

只在上述有效／end不回繞／code-context前提下，這支持把 `[SP+32,SP+64)` 寫成32個零。原 clear reply 保持D；caller隨後自行使用 S registers與明示參數，不依賴未知回覆來判斷是否清零。

## reset wrapper 的跨函式尾跳

`188e2` 建立16-byte frame，把RA保存到新SP+12，即其caller SP−4。

| 入口 pointer | 正常編碼路徑 |
| --- | --- |
| `40012400` | call19160(512,1)，重設參數，再tail19160(512,0) |
| `40012800` | call19160(1024,1)，重設參數，再tail19160(1024,0) |
| 其他 | 還原RA/SP後RET；A0保留原pointer |

`18906` 是 **JAL rd=0 →19160** 的跨函式尾跳；本機CFG將它標成terminal transfer，另外記錄callee連結。它沒有 fallthrough 到1890a。tail之前已恢復原caller RA／SP，19160自身不寫RA/SP，正常RET才可回到原caller。

19160對 `4002100c` fresh讀取再寫入：A1非零則 old OR entryA0，否則 old AND ~entryA0。第二次clear是另一次fresh RMW，並非還原第一次讀出的word。19124形狀相同，目的word改為 `40021018`。

callback正常context中兩次呼叫188e2，都選512路徑，因此共有四次對4002100c的RMW。此word**不在前輪16個snapshot地址之中**；末次操作投影為 fresh word AND `fffffdff`。這足以否定「配對restore表示所有硬體狀態不變」的推論，仍未賦予實體bit語義。

## 設定與 bitfield helpers

令B為相應callee入口A0，所有word load依原順序fresh進行，不視為atomic snapshot。

| nominal caller參數 | 可見word更新 |
| --- | --- |
| 19124(512,1) | `[40021018] ← old OR00000200` |
| 1908c(c000) | `[40021004] ← (old ANDffff3fff) OR0000c000` |
| 18986(B,1) | `[B+8] ← old OR1` |
| 18a98(B,1) | `[B+4] ← old OR04000000` |
| 18a6e(1) | `[40012408] ← old OR00800000` |
| 18996(B,1) | `[B+8] ← old OR00500000` |

零參數分支使用相應補數mask清bits。一般的1908c入口A0沒有先縮限到被清除的bits，不能把任意輸入都描述成只改兩個bits。

### 1892e的三次按序stores

令C為入口A1的config pointer：

```text
[B+4]  ← (old AND e0f0feff)
          OR U32[C+24] OR U32[C] OR U32[C+28] OR(U32[C+4]<<8)
[B+8]  ← (old AND fff1f7fd)
          OR U32[C+12] OR U32[C+16] OR(U32[C+8]<<1)
[B+44] ← (old AND ff0fffff)
          OR(((U8[C+20]-1)&255)<<20)
```

input words沒有被額外限制到特定位域。callback的32-byte clear成功、六個明示設定stores完成且未被介入改寫時，三者才簡化為 `old ANDe0f0feff`、`(old ANDfff1f7fd) OR000e0000`、`old ANDff0fffff`。

### 189ae的兩組selector／position

generic selector≤9選B+16，否則選B+12；shift分別是`3*selector`或`3*(selector-10)`。position≤6選B+52，7..12選B+48，其餘選B+44；shift分別是`5*(position-1)`、`5*(position-7)`、`5*(position-13)`。

branch為unsigned，register SLL的shift取low5 bits。position=0沒有被拒絕，其shift為27；輸入value沒有先AND7，selector沒有先AND31。所有算術按RV32截斷，因此不能將generic函式擅自改成已驗證參數的欄位setter。

本callback明示selector=16、position=1、value=7，才得到：

```text
[B+12] ← (old AND ffe3ffff) OR001c0000
[B+52] ← (old AND ffffffe0) OR00000010
```

十個peripheral bodies的CFG均無循環；189ae雖有一個backward jump，仍不形成cycle。這只涵蓋編碼中的控制流與存取；沒有執行任何RMW。

## 現在能支持的保存結論

前輪13個direct-call sites的所有target都已展開，reset wrapper額外指向19160也有完整body；8520的間接transfers均限於其內部byte序列。這個軟體呼叫範圍不再保留未知callee。

peripheral leaf與8520均不明確寫S registers／SP／GP。188e2的唯一額外frame有RA成對保存／恢復；最深nominal stack depth為callback入口以下144 bytes（128+16）。在明示base保持的投影下，RAM stores可界定為callback本機frame、其中32-byte clear區段、以及reset wrapper位於callback SP−4的RA spill；其餘stores投影到MMIO。

要把這些證據用於config length/count/cache保存，仍須明確要求：

- 相符的APP bytes／ISA語義，所有必要accesses與code有效。
- 不回繞的有效stack，callback／reset frames及clear範圍與欲保存的config/cache/heap物件不重疊。
- 投影MMIO與RAM/config/cache/frame分離，硬體副作用不破壞所需內容。
- 無中斷、外部writer或alias破壞控制／保存字；poll最終完成。

因此可以移除這個callback內「未知軟體callee可能寫欄位」的未解析邊界，**不能移除硬體／映射／alias／外部干擾前提，也不能證明實際installed provider或heap ownership**。前輪low16結果經SP+28保存、重讀再返回的合約仍有相同有效性前提。

## 重播與實際輸出

```text
python analysis/check_v4160_app44_closure_static.py
python -O analysis/check_v4160_app44_closure_static.py
```

兩模式均實際輸出：

```text
PASS: 4096 size/alignment partitions; 31 computed transfer targets; 256 byte-replication cases; 12 specified raw mutations
PASS: 11 new complete bodies, 690 bytes/252 instructions/37 stores; combined closure14 bodies/1072 bytes
PASS: exact ledger replay; computed memset edges bounded; software callees expanded; physical binding/effects UNPROVED; NO target execution
```

4096 cases是N=0..255×16種alignment的寬度分段，不是所有U32輸入或記憶體執行。31個target是靜態operand算術；byte replication及selected masks也只算主機整數。十二個raw mutations改bulk mask、computed tail／prefix位移、SB offset、RA恢復來源、reset tail target、設定讀取offset、selector shift／position增減、RMW store offsets與set/clear branch，均要求命中特定semantic guard，不能以完整hash不符或任意exception代替。

預設只讀重算並精確比對JSON；`--write`僅建立不存在的ledger。重播需十二個已發布Python dependency模組與本機固定APP、兩份carrier、SDK header、LLVM來源／vectors；candidate輸入未隨本次發布，僅clone repo不足以重跑。

接續仍需釐清實際provider綁定、真實MMIO／初始NV內容、外部writer與更廣的config-I/O／heap物件保存期。此checkpoint不代表整份v4.1.60已完成反組譯。
