# v4.1.60：APP config 建立來源與外層返回流程

APP `0x19b56` 會在32-byte frame內建立16-byte config，經13個前置呼叫後，寫入 reader `0x191c6`、`0xffffffff` 與 `0x03e83e80`，再以 A0=then-live SP 呼叫 fresh `[0x40074]`。後者拆出的 halfwords 是16000／1000；若內容、copy及相關分支保存，已驗證算術結果為22。

這個來源不是無條件的執行時設定快照。bytes12..15的零值在13個呼叫前寫入，之後未本機重寫；optional hook也可能在gates前改動來源。外層wrapper在constructor返回後fresh讀另一個byte，沒有檢查constructor返回值。

本輪只做原bytes、operand、CFG與常數代數核對，未執行或模擬韌體、RAM/frame、provider、callback、MMIO或裝置。C重建覆蓋率未增加。

## 原始證據

承接 [config gates](v4160-config-gates-static.zh-TW.md) 與 [config 算術／copy合約](v4160-config-arithmetic-static.zh-TW.md)。程式為 [check_v4160_app_config_source_static.py](check_v4160_app_config_source_static.py)，證據為 [v4160-app-config-source-static.json](v4160-app-config-source-static.json)。來源APP、兩個candidate、sparse HEX、SDK header與Xwchc參考沿用固定雜湊驗證鏈。

| 本體 | 完整APP範圍（右端不含） | bytes／指令 |
|---|---|---:|
| config constructor | `0x19b56..0x19bd4` | 126／43 |
| 外層wrapper | `0x19b16..0x19b56` | 64／22 |
| mode tail wrapper | `0x197b8..0x197be` | 6／2 |

```text
constructor SHA-256
b5717eca817e1845094b27eca434f7827b15f3b331148c1ba0491eca9bf14940
wrapper SHA-256
db9229526342b615e61627737672782a6620c99170d608bb956f9d10356884ab
mode tail SHA-256
781acefb45e65f1dbc986de7f9ae09da680c11d5d1416f460b706c9c5d1bede0
```

三個本機圖都是順序有限圖，明列所有call與tail。普通call只連接條件性正常返回邊，沒有宣稱所有callee返回、保存ABI或完成初始化。

## constructor：清零早於13個呼叫

入口SP減32，保存RA於SP+28；四個SW0初始化SP+0、+4、+8、+12。接著13個direct call依序為：

```text
19142,19076,190c6,1909e,190da,190e6,
19272,19272,19248,19272,19220,19272,197b8
```

第一處明設A0=`0x18000000`、A1=1。後續明設的A0分別包括19076=1、190c6=1、1909e=0、190da=512、190e6=1、19248=1、19220=0；四個19272呼叫前沒有重新指定A0，不能把先前的值當成其固定實參。

197b8小wrapper僅有 `LI A0,3; JAL X0,0x1929a`，沒有新link或frame；1929a若正常經原RA返回，才會續行constructor的19bac。此wrapper本身沒有讀取40058。

這13個callee的完整副作用不在本輪封閉範圍。它們需要正常返回、保存所需SP／frame與其他live context，才能把清零區和後續設定視為同一個物件。

## 前置呼叫後的三個word

最後一個前置呼叫返回後，constructor在沒有另一個nested call的區間內寫入：

| 相對then-live SP | 寫入值 | 原指令形成方式 |
|---|---|---|
| +4 | `0xffffffff` | LI −1，SW |
| +8 | `0x03e83e80` | `0x03e84000−384`，SW |
| +0 | `0x191c6` | `0x19bba+0xfffff000+1548`取U32，SW |

little-endian下，word+8拆為 `U16[+8]=16000`、`U16[+10]=1000`。bytes0..11由這個呼叫後區間覆寫；bytes12..15則只有更早的清零，沒有再次本機寫入。將它們的零值帶到最終input需要SP身分保持、該區間未遭callee／外部writer改寫。

然後fresh讀`U32[0x40074]`、設A0=SP並間接call，沒有本機null guard。A1/A2在這個呼叫點未重新建立，不能宣稱為初始化時的常數。candidate中的40074目標仍與既有config入口相符，但不代表實機installed slot已確認。

## 與gates／copy／算術的條件串接

串接非空config分支時，需要then-live SP非零，optional hook重載後的C仍對應該來源，並有相符candidate、有效accesses、SP／input保存且hook未破壞所需欄位等條件。constructor本身未設SP／null guard。在這些前提下：

- word0、word4、halfword8、halfword10均非零，通過四個必填gates。
- 若最初byte12的零值仍在，會跳過state byte+21的額外gate；並非檢查該state必在允許集合。
- 若既有copy leaf正常完成、無不利別名／writers，目的區halfword h可接成16000。
- 只有fresh state byte+23為零而執行算術分支時，輸出才為 `floor(7×16000/5000)=22`；略過分支時會保留既有byte。

optional hook發生在gates之前，可能改動來源、saved pointer或globals。因此上述串接不能當作實際執行結果，也不證明成功或實際provider身分。

constructor的provider返回後，本機只restore RA、釋放32-byte frame並RET，A0未再定義，所以在正常存取／frame保存前提下會把provider的A0回傳。此時stack config的active frame已結束；指標是否被外部保留仍未知。`0x191c6`是來源中建立的code pointer，不是該stack buffer本身。

## 外層wrapper不以config返回值決定尾跳

wrapper配置16-byte frame，保存S1／RA／S0。以fresh `[0x40080]`呼叫，A0形成`0x1995c`，沒有本機null guard。正常返回後，建立S0=then-live GP+388，把返回A0低8存到該處，再direct call constructor。

constructor返回後，下一條指令fresh `LBU A0,[then-live S0]`，覆蓋constructor返回A0；沒有本機分支測試config的狀態值。這個fresh byte也不能無條件等同稍早寫入值。

其後T1=fresh `U32[then-live S1+88]`；只有S1仍為`0x40000`時才可稱為slot40058。wrapper恢復S0／RA／S1，設A1=`0x2000`、A2=`0x2ee00`（192000），釋放frame並 `JR T1`，不寫入新link。

這只界定本機尾跳ABI。target有效性、實際slot40058／40080綁定、GP／S0／S1保存、後續參數消費與返回行為仍未知；沒有單憑數值指定服務名稱。

## 重播與下一步

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_app_config_source_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_app_config_source_static.py
```

檢查涵蓋196 bytes／67條原指令的完整operands／本機CFG、所有call／tail、frame與field stores、provider／算術連接、paired-halfword及尾跳常數代數、逐指令67個operand變異和1個unsigned-byte變異拒絕，以及JSON逐bytes重播。

仍需展開13個前置callee與1929a、釐清初始bytes12..15的保存與其他writers、實際provider綁定、optional hook／registration副作用，以及frame／物件保存期與其他算術實參域。
