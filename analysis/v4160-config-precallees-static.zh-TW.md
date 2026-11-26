# v4.1.60：config 前12個call sites的本機保存與輪詢合約

接續 [APP config 建立來源](v4160-app-config-source-static.zh-TW.md)，本輪補齊constructor前12個call sites所依賴的本機函式，將原本籠統的callee保存前提收斂到明確的MMIO、子frame與輪詢條件。若這12次呼叫均正常完成、程式碼與所需context保存、存取有效且沒有不利別名／外部干擾，原config bytes12..15的零值可以保留到最後一次 `0x197b8` 呼叫入口。

最後的 `0x197b8 → 0x1929a` 尚未封閉，不能把這個保存結論延伸至provider call，也不能宣稱實機輪詢會返回。

全程僅原bytes、operands、CFG與主機整數／區間代數；未執行或模擬韌體、MMIO、輪詢、RAM/frame或裝置。C重建覆蓋率未增加。

## 本輪完整本體

程式：[check_v4160_config_precallees_static.py](check_v4160_config_precallees_static.py)。證據：[v4160-config-precallees-static.json](v4160-config-precallees-static.json)。來源APP、兩個candidate、sparse HEX與Xwchc參考沿用既有雜湊固定驗證鏈。

| 原APP範圍（右端不含） | bytes／指令 | 本機行為 |
|---|---:|---|
| `19076..1908c` | 22／8 | word bit8依A0清／設 |
| `1909e..190c6` | 40／13 | 兩次zero byte store，另有模式分支 |
| `190c6..190da` | 20／8 | word bit0依A0清／設 |
| `190da..190e6` | 12／5 | fresh word OR A0 |
| `190e6..19106` | 32／14 | word bit15依A0清／設 |
| `1919c..191ae` | 18／5 | fresh halfword設bit4 |
| `191ae..191c6` | 24／9 | fresh halfword清bit4 |
| `19220..19248` | 40／14 | 保存參數，寫一組halfwords，尾跳clear leaf |
| `19248..19272` | 42／15 | 保存參數，寫另一組halfwords，尾跳clear leaf |
| `19272..19282` | 16／5 | fresh halfword測bit5，未置位就重讀 |

新增10個完整本體，共266 bytes／96條指令。另重用 [既有19142完整leaf](v4160-irq-setup-stack-sources-static.zh-TW.md) 的30 bytes／12條指令，未重複計入新增code bytes；各body SHA-256、完整instruction bytes與operand、CFG、stores與GPR定義清單都記錄於JSON。

constructor前12處direct calls依序為：

```text
19142,19076,190c6,1909e,190da,190e6,
19272,19272,19248,19272,19220,19272
```

相依本體集合封閉：只有19220／19248有nested call至1919c，最後restore RA/SP並以JAL X0尾跳191ae；該leaf普通RET才返回constructor續行處。其他涵蓋函式沒有nested calls或未知間接tail。constructor第13處197b8及其1929a目標仍明列為未完成部分。

## MMIO只按原指令描述

| 本體 | encoded有效地址／寬度 | constructor實參對應行為 |
|---|---|---|
| 19142 | `4002101c` word | fresh snapshot OR `18000000`後寫入 |
| 19076 | `40007000` word | fresh snapshot OR `100`後寫入 |
| 190c6 | `40021024` word | fresh snapshot OR1後寫入 |
| 1909e | `40021020` byte | **依序兩次SB0**；A0=0無第三次store |
| 190da | `40021020` word | fresh snapshot OR512後寫入 |
| 190e6 | `40021020` word | fresh snapshot OR `8000`後寫入 |
| 1919c | `40002804` halfword | fresh unsigned snapshot OR16後寫入 |
| 191ae | `40002804` halfword | fresh unsigned snapshot AND `ffef`後寫入 |
| 19248 | `40002808`、`4000280c` halfwords | 原A0=1，依序寫0、1 |
| 19220 | `40002818`、`4000281c` halfwords | 原A0=0，依序寫0、0 |
| 19272 | `40002804` unsigned halfword讀取 | fresh結果測mask32 |

地址均為十六進位。這不指定clock／timer等硬體語意，也不代表相鄰access可合併。特別是1909e的兩次byte零寫入必須保留為兩次；一般A0=1還會第三次SB1，A0=4則第三次SB5，但constructor此處使用A0=0。

19220把原A0高16／低16分別寫入兩個halfwords；19248的高半部先再取低4 bits。兩者都先呼叫1919c，寫完後尾跳191ae。這只是原指令的位元及順序合約，未保證硬體凍結、提交或狀態復原。

## 子frame與GPR保存

只有19220／19248建立32-byte子frame，保存原RA於child SP+28、原A0於child SP+12。相對constructor當前frame base C，直接stack stores是：

```text
C−20 .. C−17：保存原A0
C−4  .. C−1 ：保存RA
```

這些整數offset區間與constructor config `[C,C+16)`、保存RA `[C+28,C+32)`不重疊。nested1919c不改SP／RA且無stack stores；wrapper重載參數與RA、恢復SP後尾跳191ae，該leaf也不改SP／RA。

涵蓋的9個unique direct callees及兩個nested leaves均不定義GP或S registers。無frame leaves直接保持SP／RA；有frame的兩者在保存words有效等條件下恢復SP／RA。其他本機stores均是表列的固定MMIO寫入。

因此，在有效accesses、無MMIO／stack不利physical alias或副作用、無interrupt／DMA／reentry／外部writer等條件下，這前12次呼叫不會由本機直接寫入constructor的16-byte config，且正常返回會保住所需SP／RA／S／GP。這是有條件的局部保存合約，不把GPR不變當作硬體或frame生命週期證明。

## 四次輪詢與實參傳遞

19272完整圖只有一個3-node SCC：LHU、ANDI32、BEQZ回到load。它沒有store、nested call、timeout或retry counter，只有bit5非零時才能續行RET。每次讀取都是fresh值；四次call中的任一次都可能持續讀取，沒有建立eventual return或硬體時間保證。

在已驗證callee語意、有效存取及無外部GPR干擾下，四次19272入口A0依序可收斂為 `1,1,1,0`：190e6保持明設的A0=1，poll本身僅定義A4/A5；19248(1)返回低16值1，19220(0)返回0，clear leaf不改A0。這是前一輪then-live實參未知項目的局部補足，並不讓輪詢使用A0作為固定readiness值。

## 保存結論停止在哪裡

若以上12個call sites正常完成，且符合存取／映射／保存／無干擾條件，constructor在最初寫下的四個zero words仍可保留到197b8入口，SP也可回到C。但197b8接著強制A0=3尾跳1929a，後者的完整副作用尚未在此驗證；再後面的config optional hook也可能修改來源。

因此本輪未無條件宣稱最終config byte12必為零、state gate必被跳過、provider必成功或實際installed slot已確認。

## 重播與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_config_precallees_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_config_precallees_static.py
```

驗證包含完整operands／CFG、精確poll回邊、calls／tails閉合、12個constructor接點、frame／MMIO／GPR清單、65,536個halfword mask／poll代數、子frame區間，以及96個operand加3個unsigned-load變異拒絕；JSON必須逐bytes重播一致。

後續仍需展開1929a的mode3路徑及callees、追查實際provider／slot writers、MMIO外部副作用與別名／非同步writers，以及frame／payload保存期和其他算術實參域。
