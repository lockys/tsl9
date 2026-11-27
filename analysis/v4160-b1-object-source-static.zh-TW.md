# v4.1.60 callback 物件來源與發布後服務

接續[callback 槽位消費與清零](v4160-b1-setup-event-static.zh-TW.md)。本輪將 creator 的 `B+88` 發布、bit0 的 `B+100` 發布與 callback／bit1 的獨立讀取接起來，並新增完整核對發布後呼叫的 `0x43edc／0x43f68`。兩版仍是 resident **參考候選**，不據此認定實際 installed provider 或事件順序。

新服務每版 **106 bytes／42 instructions**：V131 `[0x43edc,0x43f46)`，V140 `[0x43f68,0x43fd2)`，合計新增完整護欄 **212 bytes／84 instructions**。它的唯一非 frame store 是另一個固定 halfword，沒有直接寫 B+88 或 B+100；但它會呼叫兩個未知指標服務與 RF callee，尚不能證明發布指標跨過所有子呼叫後仍有效。APP C 重建覆蓋率沒有增加。

## 指標來源鏈及條件

`B=0x200033b8／0x20003408`。重用[完整 creator](check_v4160_list_origin_static.py)、[bit0／bit1](check_v4160_list_direct_callbacks_static.py)及[完整 hook callback](check_v4160_callback_dispatch_static.py)；每個本體與保留的 sparse HEX 完整逐 byte 比對，缺口不以零補齊。

| 原指令位置 | V131 | V140 | 意義 |
|---|---|---|---|
| creator 入口 | `0x5397c` | `0x53a2a` | 各 194 bytes／69 instructions |
| creator `+0x62` | `0x539de` | `0x53a8c` | fresh head=0 時，將持有 N 寫入 B+88 |
| bit0 `+0x0e` | `0x558b6` | `0x559ee` | 捕獲 fresh U32[B+88] |
| bit0 `+0x70` | `0x55918` | `0x55a50` | 將持有 N 寫入 B+100 |
| bit0 `+0x7c` | `0x55924` | `0x55a5c` | 有條件呼叫本輪新服務 |
| hook callback `+0x0e` | `0x5548e` | `0x5556c` | 另讀 fresh U32[B+100] |
| bit1 `+0x0c` | `0x550d8` | `0x551a2` | 另一個獨立 B+100 讀取者 |

Creator 通過 fresh count／capacity byte 比較後，請求 allocator `(192,577)`。非零回覆捕獲為 N，再請求 `fill(N,0,192)`；原指標由 S0 保存，依賴 fill 正常返回及必要的 register／frame 保存條件。

只有 **fresh U32[B+92]==0** 的第一節點路徑寫 B+88=N，接著寫 head／tail、N.next=0 與 count。判斷的不是 B+88 是否為零。Append 路徑透過 fresh oldtail 連結 N、更新 tail／count，不在本體中更新 B+88。這些 stores 發生在其他 N defaults 與後續服務之前，沒有證明對外發布時物件已完成初始化，或所有 list invariants 都成立。

Bit0 的 fresh B+88 必須非零，fresh U8[N+12] 必須恰為 1，且三個分開取樣的 global byte gate 都未走 early tail，才能到達 B+100 發布。發布使用入口捕獲的 S0=N，沒有重新讀 B+88；位置在第一個 post-gate linked call `+0x7c` **之前**。若走該 call，正常返回後才清 B+0。

Hook callback 與 bit1 則各自重新讀 B+100；沒有證明兩者取得同一個值。只有在發布先於讀取、槽位未被其他 writer 改寫、對象仍有效且 alias／frame／callee 保存條件成立時，才能把這些讀取關聯到同一個 creator N。這條條件鏈不需要、也沒有證明 setup 入口 P 就是 N。

## 尚未補上的 N+12=1 writer

Creator 的明確 N stores 不涵蓋 byte12。**若匹配的 fill 確實清零 192 bytes，且 N+12 後續未被改寫，creator 留下的 N+12 為 0，無法通過 bit0 的 N+12==1 gate。** 因此 allocator／fill 的存在與 B+88 發布，不能直接推出 bit0 一定發布 B+100；仍需定位適用於同一物件的其他 writer 及其順序。

這是有前提的缺口分析，沒有假設實際 fill/provider 綁定、沒有執行填零，也沒有建立 target 物件模型。現有其他 N+12 寫入證據也不能只因欄位偏移相同，就認定操作同一個 N。

## 新增完整服務：先讀指標，再有條件配置 frame

下列偏移相對本輪新服務入口。令 `G=0x20003000`，`K=G+492／G+572`，`M=G+412／G+492`：

```text
provider = fresh U32[K+44]       // 0x20003218 / 0x20003268
若 provider==0：直接 RET，沒有配置 frame，保留入口 A0
否則：配置 16-byte frame，保存 S0、S1、S2、RA
透過捕獲的 provider 呼叫
L = fresh U16[M+8]              // 取樣在 provider 返回之後
X = 完整 U32 A0 回覆，保存於 S0  // 上一筆 LHU 不改寫 A0
```

呼叫 provider 前沒有把 A0 設成 0；從此 bit0 callsite 來時，它仍是 bit0 的入口 A0，不能宣稱為 zero-argument ABI。新服務也沒有將傳入 A0 當作 N 使用。

新本體 `+0x24` 的原始 `1a27` 是 QingKe LHU，`+0x5a` 的 `82a4` 是 SH；一般 radare2 顯示成浮點指令的這兩處沒有照字面採用，而是按既有 WCH 解碼、raw bytes 與 operands 核對。兩版全部 106 bytes 都與 strict sparse HEX 一致。

## 差值不是一般的 U16 絕對差

若 L=0，直接跳過後面的兩組服務及 halfword store。L 非零時，原指令先用完整 U32 作 unsigned max／min 選取，**再各取低 16 位相減**：

```text
D = low16(max_unsigned32(X,L)) - low16(min_unsigned32(X,L))
只有 signed D > 20 才進入後續服務
```

D 的範圍是 −65535～65535，不會在這次減法發生 32-bit signed overflow。只有 X 本身也落在 U16 域時，D 才等於一般 `abs(X-L)`。例如 `X=0x10000,L=100` 時 D=−100，會略過服務；不能用 `abs(low16(X)-L)=100` 代替。嚴格門檻也保留：D=20 會略過，並非 `>=20`。

## 後續服務、snapshot 寫回與返回

條件通過後，`+0x4e` 另讀 fresh U32[K+48]（`0x2000321c／0x2000326c`）；非零才於 `+0x54` 間接呼叫。兩條分支都接到 `+0x56` 的 **linked call** `0x641b0／0x6429a`，不是尾跳。這個 RF 本體已有完整原指令 guard，但其實際 state、nested callee、IRQ 與返回進展仍有前提。

只有上述必要呼叫正常返回後，`+0x5a` 才把 **保存的 low16(X)** 寫入 M+8（`0x200031a4／0x200031f4`）。寫入的不是最後 RF callee 的回覆。這是四筆 frame saves 以外，完整本體唯一的 local store；固定地址與 B+88、B+100 的 word 不重疊。不過未知 provider／optional hook／RF callees 可能有其他寫入或副作用，不能由本機 store 清單推出發布物件完整保存。

兩個 RET 分別在 `+0x66` 與 `+0x68`。非零 provider 路徑的 S0／S1／S2／RA saves／restores 與 SP−16／SP+16 成對，空 provider 路徑完全略過 frame。A0 返回合約為：

- provider 為零：保留入口 A0。
- L=0 或 D≤20：保留第一個 provider 的完整回覆 X。
- D>20 且必要子呼叫返回：保留最後 RF callee 的 then-live A0；沒有固定 success 值。

完整 CFG 有 42 nodes、14 條語法上的正常返回路徑，沒有 local loop。這些有限路徑不證明分支實際可達或任一 nested call 必定返回。

## 驗證

[檢查器](check_v4160_b1_object_source_static.py)與[固定 ledger](v4160-b1-object-source-static.json)保留新服務全部 operands／hash／CFG、14 條路徑、QingKe encodings、frame／def-use 證書、固定 store 位址排除，以及既有 creator／bit0／bit1 guard 的引用與來源鏈。本輪新增部分拒絕 **84 個逐指令突變、2 個 word-load 型別突變**；589824 個 host 整數邊界組合核對 signed 差值，並保留完整 U32 回覆與 U16 絕對差不等價的反例。

```powershell
python analysis/check_v4160_b1_object_source_static.py
python -O analysis/check_v4160_b1_object_source_static.py
```

全程沒有執行或模擬目標韌體、硬體存取、封包重放或 target network。尚需追查 provider／optional hook 實際綁定與副作用、同一物件的 N+12=1 writer、B+88／B+100 的其他寫入者、實際事件順序、配置與保留條件，以及完整消費釋放與 notification 指標保存期。
