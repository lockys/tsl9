# B1 完整 RAM query：輸出寫入切集與 SP+12 串接

接續[兩個RAM callbacks](v4160-b1-ram-record-callback-static.zh-TW.md)，完整展開query `0x20001122`，新增 **1,240 bytes／392條指令**。關鍵進展：每條從入口通往普通RET的本機路徑，都先經過至少一個Out word store；在相符implementation及所需保存條件下，這補上兩個caller的SP+12本機寫入來源。它不證明後續callee未覆寫、未保存pointer，或最後內容始終有效。

[Python checker](check_v4160_b1_ram_query_static.py)與[固定JSON ledger](v4160-b1-ram-query-static.json)保存完整operands、hashes、CFG、stores、輸出控制流切集及全部邊的語法證書。全程離線、嚴格sparse HEX，只核對不可變圖與封閉host整數關係；沒有目標執行／模擬、query／frame／clock／heap狀態模型、packet replay、硬體或目標網路分析。C重建覆蓋率不變。

## 完整範圍與共同frame

| 參考carrier | RAM範圍 | FLASH來源 | bytes／指令 |
|---|---|---|---|
| V131 | `[0x20001122,0x2000138e)` | `[0x41392,0x415fe)` | 620／196 |
| V140 | 同上 | `[0x413d2,0x4163e)` | 620／196 |

逐byte核對strict HEX及startup first-copy的完整來源／目的涵蓋，在RAM PC解碼。唯一RET是+0x252；其後到+0x26a的分支仍可達，完整範圍包含它們。

32-byte frame保存RA、S0..S6共八個word。入口P=A0、Out=A1；Out保存在S2，本機只在epilogue恢復原S2。query沒有P或Out的null guard。明示P存取最遠到byte+320，完整路徑需321-byte有效範圍；Out需四-byte可寫範圍。未知callees可能另有需求，這些數值不是實際配置extent證明。

## 五個Out stores與三點控制流切集

全部明示Out word stores為：

| Offset | 作用 |
|---|---|
| +0xca | 重算路徑的中間結果 |
| +0xe0 | 重算路徑的初始調整結果 |
| +0x1fa | mode1 gate失敗的fallback結果 |
| +0x208 | 初始P+11不等於1時，寫入先前捕獲的U32[P+144] |
| +0x1a2 | 迴圈中的後續替換結果 |

checker從完整CFG移除 **`{+0xe0,+0x1fa,+0x208}`** 後，確認入口已無法到達普通RET、最早Out讀取及三個clock call sites。這是一組共同切集，不是聲稱某一個store單獨dominate所有路徑。+0x208使用原A1，該分支store之前沒有child call或A1重新定義；其他stores使用保存Out的S2。

兩個caller都傳入自己的SP+12。query建立32-byte frame後，該位址成為query SP+44，四bytes範圍在query自己的SP+0..31之外。若matching query確實由入口進入、普通存取完成、frame／S registers／code與所需nonalias保存成立，caller正常得到query回覆前已有本機word寫入，不再需要自行preinit SP+12作為這些明示讀取的來源。

這只封閉**發生過本機寫入**的證據。query之後還有間接／直接callees；它們可能觀察then-live暫存器、保存Out、透過alias改變內容或物件存活期。不能推成最後writer一定是query、caller每次fresh observation都相同，或frame pointer沒有escape。較直接的分支在clock呼叫時，A1甚至可能仍保留Out。

## 初始分流與mode1 gates

先讀U8[P+11]，並捕獲B=U32[P+144]。

- P+11不等於1：直接把B寫Out，進共同clock階段。
- P+11等於1：捕獲U16[P+128]、U16[P+60]及K=U16[Q+8]，Q=`0x20003234／0x20003284`。只有P+128<P+60、fresh P+16=1、P+280與P+164 words皆零、P+15=7時進重算；任一gate失敗進fallback。

這些是不同時點的觀察，沒有原子物件snapshot或整體transactional更新保證。

fallback從fresh U16[P+134]和捕獲K形成：

```text
S = floor(low32(U16[P+134]*K + 999999) / 1000000)
若 captured B < S：B′ = low32(B + fresh U32[Q+4])
否則：B′ = B
Out = low32(B′ - S)
```

加999999及單次補償可回繞；不是無條件的數學ceil或完整modulo normalization。之後進共同clock階段。

## 重算、除零與opaque arithmetic回覆

令delta為捕獲P+60−P+128（gate確保1..65535），h=U16[P+58]：

```text
N = low32(h * delta * 1250)
q = DIVU(N, fresh U32[P+148])
t = low16(q + fresh U8[0x20003202／0x20003252])
U16[P+134] = t
```

h×delta本身可放入U32，但再乘1250可回繞。P+148沒有零值guard；RV32 DIVU除零回覆`ffffffff`，再加byte／取low16，結果可以是`ffff`或其他值，不自動等同飽和／錯誤status。

接著用MULHU／MUL形成完整pair K×N，以A3:A2=0:1000000呼叫`0x6df1a／0x6e10a`。重用完整914-byte arithmetic原指令證據；**這次實參域的quotient公式未證明**，保留實際回覆的low／high words。

captured B加回覆low word，SLTU形成carry，再將carry加回覆high word；這個high相加也取low32。依它是否非零及low是否大於等於fresh Q+4，決定只減Q+4一次。+0xca先發布中間Out，之後從held t／K計算縮放量、加2×delta，對中間值再作一次減法或fresh Q+4補償，+0xe0寫Out。兩次stores不是原子發布；helper回覆、carry與一次減法不能單獨建立正常化／物理時間合約。

## Clock、重複更新與返回範圍

共同階段先載入clock slot `0x200031e0／0x20003230`，再捕獲Out word，然後間接呼叫，沒有null guard。若unsigned Out<clock回覆，另讀補償word加一次，再以low32差值做signed比較。

signed差值非負進terminal threshold；負值則再fresh載入clock、再呼叫、再fresh讀Out，依unsigned差值作一次補償，與另一個以U16[P+62]／fresh Q+8計算、可能回繞的threshold比較。較大gap進action分支，否則進更新迴圈。

迴圈會：

1. U16[P+64]加1並截低16位。
2. fresh U8[P+320]=0時呼叫RAM `0x200014c6(P)`；隨後明示重設A0=P，再呼叫`0x56972／0x56ab2(P)`。
3. 第二個child非零回覆直接走強制`ffffffff`出口；零才用fresh P+144／P+140／Q+4作一次加法、carry檢查及一次減法，寫P+144。
4. fresh P+31 byte加1截低8位。fresh P+134與Q+8形成縮放量，補償／減法後寫Out，再呼叫fresh clock slot。
5. 經一次補償與signed差值檢查，負值回到迴圈。

沒有本機timeout或迭代上限。counter會回繞、clock／callee是否更新、pointer是否仍有效都未證明，因此不保證query返回或外層registry遍歷完成。

terminal threshold的兩個入口都要求signed差值非負。若該值unsigned大於fresh U8[0x20003203／0x20003253]，保留差值返回；否則發布P後明示返回0。其他強制失敗出口為`ffffffff`。因此在相符implementation由入口普通返回、所需保存條件成立時：

```text
R ∈ {0, ffffffff} 或 1..7fffffff
```

這將上層selector可選中的普通query回覆從先前一般U32假設縮小至1..`7fffffff`；不建立真實可達值、物理時間或installed provider身分。

## Action與pointer保存來源

large-gap action請求既有完整124-byte threshold `0x568f6／0x56a36(P,8)`，把回覆低8位寫P+43。之後fresh載入hook `0x20003220／0x20003270`，非零才以A0=5、A1=2及其餘then-live參數呼叫；hook回覆被忽略，最後強制`ffffffff`。hook正常返回不提供整條鏈的成功或保存期保證。

terminal零回覆分支則先明示寫：

```text
U32[0x2000345c／0x200034ac] = 保存的入口 P
然後 A0 = 0
```

這就是B+164，也是既有RAM callback `0x20000d50` prefix重新讀取的物件pointer來源。本階段只重驗其完整82-byte prefix，不把prefix當作整個callback。

record caller在query回覆0後會直接請求`0x20000d50`；selector回覆0分支則透過setter發布該literal供後續路由。若global未被其他writer／alias改變，prefix的fresh讀取可接到此次P。相同位址不等於兩次觀察必定相同，也不證明後續cleanup會保留或釋放P、執行順序已成立，或W／P完整生命期已封閉。

這個store是明確pointer保存來源；不能宣稱P只在query期間借用或沒有escape。

## 重播與後續界線

```powershell
python analysis/check_v4160_b1_ram_query_static.py
python -O analysis/check_v4160_b1_ram_query_static.py
```

兩模式核對完整祖先證據、strict HEX及固定ledger。每版218條CFG邊、17條選定語法路徑與輸出切集均有證書。392個逐指令變異、60個typed-load變異必須拒絕；正常／除零／word與counter回繞／opaque回覆carry的host整數檢查明列取樣家族，不冒稱遍歷全部物件／clock或U32輸入狀態。

尚需展開RAM `0x200014c6`、`0x56972／0x56ab2`、`0x436a8／0x43734`及其他optional callees；確認clock／hook綁定與writers、query／cleanup／record物件同一性、消費釋放順序，以及`0x5d006／0x5d14e`等後續流程的完整保存合約。
