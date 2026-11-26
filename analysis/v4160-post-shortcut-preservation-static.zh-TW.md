# v4.1.60：reset／config-I/O shortcut至table發布的保存合約

本輪把 [首次配置範圍](v4160-initial-table-extent-static.zh-TW.md) 的截止點向後延伸，涵蓋reset、config-I/O的三條gate-fail與一條readback-equal shortcut，再接回三筆builtin table stores及post-config返回。在明列條件下，table／capacity／配置區塊可保存，count從0成為3，post-config回傳A0=1。

這只涵蓋這些shortcut，不代表NV內容已知、NV操作成功或一般config-I/O路徑已封閉。mismatch後的配置、迴圈callback與free仍另待驗證。

全程僅原bytes／operands／CFG與frame、地址、bitfield等式。未建立NV／heap／table可變記憶體模型，未執行或模擬目標ISA、copy、callback、MMIO或裝置。完整原本體重用，C重建覆蓋率未增加。

## 原始證據與call接點

承接 [config-I/O完整本體](v4160-config-io-static.zh-TW.md)。程式：[check_v4160_post_shortcut_preservation_static.py](check_v4160_post_shortcut_preservation_static.py)。證據：[v4160-post-shortcut-preservation-static.json](v4160-post-shortcut-preservation-static.json)。原APP／candidate／sparse HEX／SDK／Xwchc及全部來源body hashes沿用固定身分驗證鏈。

| 候選 | post+194 reset | post+198 config-I/O |
|---|---|---|
| V1.31 | `4329a`，完整10 bytes | `44022`，完整160 bytes／61條指令 |
| V1.40 | `43326`，完整10 bytes | `440b6`，完整160 bytes／61條指令 |

reset只有LUI、SW zero至context−4、RET；不改A0／SP／RA／S／GP。該固定word與table、capacity、count及hook欄位分離。

config-I/O的完整原本體重新核對所有operands／直接call pairs與hash，再於CFG上選出四條有限鏈。所有選定鏈都包含普通RET，不經allocate／fill／free、allocation cache stores／clears或per-write callback。

## 四條shortcut

| 分支條件 | 本機指令數 | initial read callback | 回覆 |
|---|---:|---|---:|
| U32[config+8]=0 | 16 | 無 | 1 |
| +8非零、U32[config+56]=0 | 19 | 無 | 1 |
| +8/+56非零、U32[config+60]=0 | 21 | 無 | 1 |
| 三個gates通過，readback相等 | 27 | 一次 | 1 |

gates都是完整U32檢查。相等分支比較的是**fresh U32[config+8]與當時SP+12輸出字**，不是callback的scalar A0 reply。

原APP提供的read callback來源是1979a。對equal shortcut，本輪使用以下充分條件：呼叫當下target仍匹配1979a，fresh4004c仍匹配copy20000332，來源／非零輸出指標與frame有效，copy完成四個byte傳送，且組成的LE輸出值等於fresh config+8。

這沒有斷言實際NV來源值。copy是四次LBU／SB，不是atomic word read；可以用來源四byte穩定／一致等條件支持結果，也可直接把這次完成傳送的四byte結果相等列為分支條件，不能假造已量測的NV word。

## matching read wrapper與copy的寫入範圍

完整APP read wrapper `1979a..197b8`為30 bytes／13條指令：將入口num=1左移2，形成4-byte copy要求，source為入口A0，destination為入口A2。wrapper配置16-byte child frame並保存RA，正常返回前強制A0=0；config-I/O不使用此scalar reply作比較。

匹配的58-byte copy leaf本機只定義A3／A4／A5／A6，正常4-byte路徑只寫輸出四byte及encoded控制word4002420c；其中MMIO讀／清零／FENCE.I／saved-word寫回的順序沿用原合約，未實際執行，也不保證硬體無副作用。

以config-I/O配置後SP=I表示：

| 區域 | 相對I位置 |
|---|---|
| config-I/O輸出word | `I+12..I+15` |
| config-I/O四個saved fields | `I+16..I+31` |
| APP read wrapper保存RA | `I−4..I−1` |

三者不重疊。還需要它們與caller frame、code、globals、owned heap及MMIO effects沒有不利physical alias，以及沒有interrupt／DMA／reentry／外部writer干擾。僅有frame layout或GPR nonwrites，不能當成這些前提已驗證。

## count0與table保存到post suffix

post-config更早的fill40會清context+0..39，包含count byte+1。前輪名義首次配置路徑的heap bootstrap／core accounting／payload fill，在其有效frame、無alias／無干擾等前提下不改count、table與capacity。

本輪reset只清context−4。選定config-I/O shortcut的本機stores只有四個saved fields；equal case的唯一callback由上述matching read／copy封閉。因此在同樣前提下，可以把：

```text
count = 0
P = 200045b4
T = 200047f4
capacity = N0，N0 ∈ {14,17,…,212}
```

帶到post+200。這條路徑沒有free該P，也沒有重新配置或填寫payload。

## 三筆builtin publication與返回

post suffix fresh讀n=count及T′=table；在此case得到n=0、T′=T。原指令依序寫：

| word地址 | V1.31值 | V1.40值 |
|---|---|---|
| `200047f4` | `432a4` | `43330` |
| `200047f8` | `43326` | `433b2` |
| `200047fc` | `43326` | `433b2` |

count byte先寫成3，再寫第三個word。這些table words與count、hook、header及有效frame分離；N0最小14，所以三個word均位於callback table內，也位於前輪推導的allocated payload內。表內這些literal只識別寫入值，本輪不呼叫它們或推定其外部行為。

config-I/O shortcut強制A0=1，post suffix沒有再次定義A0，因此正常post RET的A0仍為1。這不是NV／硬體成功值，也不是外層initializer返回值的證明；外層及APP continuation另需串接。

## 範圍與未解項

在前輪fresh名義H/L、matching code、有效且分離的frames／headers／globals／heap、正常存取與無外部干擾前提，加上本輪選定shortcut條件後，可將table／capacity／count3／未free的P保存到post RET。

以下仍未涵蓋：mismatch後的allocator／fill／per-write callbacks／private free、outer initializer、APP19106與其他中間服務、實際source內容／fresh callback與slot綁定、一般allocation所有權與lifetime，以及MMIO／非同步副作用。

## 重播

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_post_shortcut_preservation_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_post_shortcut_preservation_static.py
```

驗證涵蓋每profile四條選定CFG chains、完整reset／I/O／APP read／copy／post接點、frame／LE／count／layout代數、三筆table store的範圍與51個I/O／reset／read operand變異拒絕；JSON須逐bytes重播一致。
