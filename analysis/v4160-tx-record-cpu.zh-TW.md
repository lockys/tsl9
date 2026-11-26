# v4.1.60 TX 記錄選擇、byte23 與 A=0 的 transport 邊界

2026-11-26。原decoded APP為76800 bytes，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。延續 [13346入口驗證](v4160-tx13346-prefix-cpu.zh-TW.md)，本批展開有效記錄的兩條路徑：A非零的前三個getter與byte23，以及A=0的清除請求至原8A56 lookup入口。

全部離線合成記憶體；沿用前批明示copy/fill正常返回與目的資料效果，不讀真實來源、不執行provider或設備。既有C對應 `src/native/receive/callback_flow.c` 等來源；本批未重建C、未改共享CPU或原BIN，不增加C覆蓋百分比。

## 原記錄選擇

令F為144-byte TX frame基址，R=`0x2000c794`。每次迴圈以i=0/1，依序讀：

1. H=`U16[R+4*i+2]`，FFFE直接跳過，不讀M/A。
2. M=`U8[R+4*i+5]`，非零直接跳過，不讀A。
3. A=`U8[R+4*i+4]`，先寫 `F[23]=1`，才依A零／非零分流。

A=0也已寫狀態byte，不能把它視為整筆完全跳過。腳本由原TX入口及本機包裝函式抵達迴圈，接續最後19-byte copy的明示返回，沒有憑空設定迴圈S暫存器。

## A非零：直接執行原getter

| 原函式（右界不含） | 結果 |
|---|---|
| `fa2a..fa30` | A0=`U8[GP+278]` |
| `b1b0..b1b6` | A0=`U8[GP+196]` |
| `fa36..fa3c` | A0=`U8[GP+279]` |
| `a968..a976` | A0=`U8[0x2000bed1]!=0` |

前三個回傳完整byte，不是布林。它們不建frame、不寫記憶體，只改A0；本批執行其原指令，沒有替這些getter假造返回。

每個返回後，caller重新讀F+23再OR及SB。若中途沒有外部寫入，令X/Y/Z為前三個byte、G=`U8[GP+357]`：

```text
F[23] = low8(1 | (X<<1) | (Y<<2) | (Z<<3) | (G<<4))
```

GP+357是在FA36返回後才讀。X/Y/Z沒有單bit mask，高位可重疊；例如X=8與G=1都能設bit4。SB只截斷儲存byte，不把暫存器一律截成byte：第一、二段的A0仍保留完整移位OR結果；第三段用A5組合store，A0則保留Z<<3。

24組明示hook在各getter返回後更改F+23，並於最後改G，確認原caller重新讀取這些值；它們是fixture的外部狀態變更，不是getter本身的副作用。

接著直接執行A968，將其布林結果存F+38，停在下一個getter `0xd314` 入口。後續byte38/39等欄位**本批尚未完成**，不宣稱已完成A非零的整個TX payload。

## A=0：兩個16-byte清除請求

原 `0x135ca`：先SH寫 `F+38..39=0`，讀 `[40048]`，呼叫 `(F+44,0,16)`，RA=`135d8`。正常返回後再次讀40048，呼叫 `(F+79,0,16)`，RA=`135e4`。

測試分別採「明示寫零16 bytes」或「不寫資料、只返回」。APP本身沒有實作fill；未寫區域保持原stack內容。完整144-byte frame另與預期逐byte比對，確認沒有多清其他欄位。

明示返回保存S暫存器、GP/SP及saved frame，破壞A/T。另一組fixture在兩次呼叫之間替換slot，驗證第二次確實載入新target；不是觀測到resident provider會更換自身。

兩次請求只覆蓋F+44..59與F+79..94。這條分支不直接清F+40..43或F+95；不能把這些欄位無條件當成0，它們仍取決於先前76-byte fill及其他資料效果。

## 重新讀handle，再進原8A56

清除請求返回後，原指令將S1與R相加，再**重新讀 `U16[R+4*i+2]`**，以：

```text
A0 = 新handle
A1 = 160
A2 = F+20
A3 = 76
RA = 135ac
```

呼叫 `0x8a56`。若fixture在先前檢查與清除後將handle改成FFFE，caller仍傳這個新值；沒有重跑記錄eligibility判斷。本批2組在8A56入口核對此邊界，沒有繼續假裝lookup成功。

另外128組合成狀態令transport第一筆handle匹配且不等FFFE，實際執行原8A56至 `[4013c]` lookup服務入口：

- 原8A56建立32-byte frame，保存S0/S1/S2/S3/RA。
- A0=handle，A1=`GP+128`，RA=`8a90`。
- live S0=76、S1=F+20、S2=handle、S3=160；來源payload仍位於caller的TX frame。

lookup provider未執行，未作admission、未組transport輸出frame或送出event。既有 [transport framing驗證](v4160-transport-frame-cpu.zh-TW.md) 可作後續串接依據，但不由本批128組自動證明實際送出。

## 驗證

[test_v4160_tx_record_cpu.py](test_v4160_tx_record_cpu.py) 使用 `check()`，一般模式與 `-O` 同樣保留檢查：

```text
python analysis/test_v4160_tx_record_cpu.py
python -O analysis/test_v4160_tx_record_cpu.py
```

```text
PASS: 4096 actual getter/byte23 chains; 24 explicit live stack/G hooks; actual A968 boolean and byte38 first store
PASS: 128 zero-record-to-8a56/lookup chains; 2 fresh FFFE handle boundaries; 4 mutations
PASS: exact frame/store/argument order; source/fill return premises explicit; remaining getters and provider bodies NOT executed
```

4096組為X/Y/Z/G逐欄位完整256值 × 其他欄位基值0/255 × 兩筆記錄位置；不是四欄位全部2^32組合。A968來源也涵蓋完整byte值。128組覆蓋位置、handle={0,1,FFFD,FFFF}、先前fill有／無、本次fill有／無、slot固定／替換、handle保持／變更。

四個記憶體副本mutation：X左移1改2、FA2A讀GP278改279、首個清除請求16改17、transport長度76改77。皆由指定的存取／參數檢查拒絕，不把解碼或unmapped失敗當作偵測。原BIN未修改，所有步驟核對實際存取、stores、frame及返回／入口暫存器。

原區段SHA-256（右界不含）：

| 範圍 | SHA-256 |
|---|---|
| `133b4..13434` | `925709e704981d655f6e997431c9cbddd7fd9cc61e70cb887d402d3bfbb8b5cd` |
| `fa2a..fa30` | `da2e85b5ca5217427e6d99b61a1e37687c2759098944ccee39ef3a8f59248092` |
| `b1b0..b1b6` | `9fc541b3c45072c8aec6db57a785687e8d2b06bc8f49554df2064fb324cbc5b7` |
| `fa36..fa3c` | `9d67c46a8c4d66684441bc514cfdaf72e263010057947402ea50eafb000f319e` |
| `a968..a976` | `5e14b606d619fad6b32fe4e5b137cfe9aa65904bdf178c97afe18772bdc8c1c0` |
| `13598..135ac` | `0b915cdff7ad94fdb5c37b2ed8b4e039fc64ce7d5f053c787279d493f85e09cd` |
| `135ca..135e6` | `9d91b0df442625052b57997487502f0bc9861406c29e13c3265dbc5108b18d4c` |
| `8a56..8a90` | `d5c5f73471230f6bac84dc37c7e609aa0b4fb9768dcbaeb1cf76fa81313f1bda` |

後續仍需完成A非零的byte38/39、其他getter與資料copy，串接transport admission及回到記錄迴圈，並釐清實際provider綁定／保存與payload生命週期。本批未執行未知provider、設備或實際傳輸。
