# v4.1.60：完整task registration與hook寫入範圍

本輪補齊`[40080]`的兩版候選函式。它先snapshot count與capacity，以`n<c`判斷是否接受；接受時先寫count byte，再把entry A0寫到`(T+4*n) mod 2^32`。這個index guard不檢查table的範圍，因此不能單憑它排除optional-hook alias。

同時確認APP wrapper對拒絕值255沒有本機分支：存下返回byte後，仍會呼叫constructor。後續fresh reload及尾跳仍有保存條件，不能直接認定它最後一定傳255。

全程只有原bytes、operands、CFG及主機整數／位址區間代數。未執行或模擬目標ISA、registration table、mutable memory、callback、provider或裝置；C重建覆蓋率未增加。

## 完整本體與來源

承接 [optional hook來源鏈](v4160-optional-hook-origin-static.zh-TW.md) 與 [post-config來源](v4160-post-config-static.zh-TW.md)。程式：[check_v4160_task_registration_static.py](check_v4160_task_registration_static.py)。證據：[v4160-task-registration-static.json](v4160-task-registration-static.json)。原APP、candidate、sparse HEX、SDK header及Xwchc參考沿用固定雜湊驗證鏈。

| 候選 | 完整FLASH範圍（右端不含） | bytes／指令 | context base |
|---|---|---:|---|
| V1.31 | `43c4e..43c7e` | 48／16 | `2000319c` |
| V1.40 | `43cda..43d0a` | 48／16 | `200031ec` |

```text
V1.31 SHA-256
be96828519d6ea00886e75e0bc515e41b4c44f1731cb5b7dcf1db6a0fdcf12e1
V1.40 SHA-256
f3ba68eb31ec8f03ec9ac9125f190aa0e903953b96b8dda2673b457e0a98d2bd
```

兩版slot40080均指向上述entry。固定SDK header的`TMOS_ProcessEventRegister`是JT19，數值也對應40080；這是alias與candidate身分證據，不是實機installed provider證據。

每份完整CFG無cuts、無cycles、只有一個RET，沒有nested call或frame。只定義A0／A2／A3／A4／A5；SP／RA／GP／S registers本機未改寫，但dynamic store仍可能透過alias破壞caller frame或其他live data。

## 原指令的讀取與寫入順序

```text
n = fresh U8[context+1]
c = fresh U8[context+2]
if n >= c:
    return 255

T = fresh U32[context+40]
SB n+1, [context+1]
SW entryA0, [(T+4*n) mod 2^32]
return n
```

這段是原dataflow說明，驗證器不執行table／register／memory模型。

| 候選 | count byte | capacity byte | table-pointer來源word | optional-hook word |
|---|---|---|---|---|
| V1.31 | `2000319d` | `2000319e` | `200031c4` | `2000321c` |
| V1.40 | `200031ed` | `200031ee` | `20003214` | `2000326c` |

兩個byte是分開的fresh loads，不是coherent snapshot。T只在接受分支讀取，且先於count store取樣；之後memory改寫T來源word，也不會改變已取進寄存器的本次T。

接受時`0<=n<=254`，因此本次`n+1<=255`，count算術本身不回繞。拒絕分支不讀T，也沒有本機store。接受時存的是原entry A0，並未在此呼叫該pointer。

完整本體沒有table-null、對齊、extent、provenance、callback-null或lifetime guard。存取有效、程式碼保持及無外部GPR干擾，仍是正常返回語意的前提。

## 兩個store不能視為原子更新

第一個SB的固定地址與hook word分離；第二個SW的目的由T決定，未被本機限定到有效table區。它可能與hook、前面剛寫的count byte、table-pointer來源word、caller frame或其他live data重疊。

因此最終memory中的count是否仍為n+1，需要另外的nonalias／無干擾條件；不能因先寫SB就當成永久結果。local reply則由寄存器中的舊n形成，在valid code／accesses與無外部GPR干擾條件下不依賴count的再次讀取。

一般4-byte footprint與4-byte hook word可能部分重疊；若兩者都word-aligned，才可把重疊縮成起址相等。驗證同時檢查含32-bit邊界的部分overlap幾何，沒有假設SW必然對齊或會成功完成。

## 何時可以排除本次hook寫入

以下是充分條件，不是已取得的實機table證明。若接受分支成立，並有：

```text
n < c
T = P + 576                     # 數學加法無回繞
R >= 576 + 4*c
0 <= P，P+R <= 2^32              # allocation區間不回繞
[P,P+R) 與 [hook,hook+4) 分離
```

則：

```text
dynamic word footprint
  = [P+576+4*n, P+580+4*n)
  位於 [P,P+R) 內
```

所以在有效存取、無不利physical alias與外部干擾等條件下，本次SW不能直接碰hook。這個條件只排除hook；若要保證final count或caller frame，還要分別排除它們與table footprint的重疊。

既有post-config形成的是`T=(fresh P′+576) mod 2^32`，早期allocation request為`R0=576+6*N0`。若再能建立`c=N0`、`P′=P`、table word保存，且目前有效allocation extent至少R0並與hook分離，就有`576+4*c<=R0`可接上上述條件。

這些snapshot等值、allocation所有權／extent與保存關係仍未證明；早期request或fill長度不能直接當成目前有效block範圍。前一輪尚未排除的post-init dynamic stores／callees也仍需處理。

## APP如何消費返回值

wrapper19b16在19b2e以fresh40080呼叫，明設A0=`0x1995c`。匹配候選leaf時，正常reply是舊n或255；wrapper把低8寫到then-live GP+388，沒有檢查255，就在19b38呼叫constructor19b56。

constructor返回後，wrapper會fresh讀`U8[then-live S0]`覆蓋A0，再準備40058尾跳參數。若要把registration的255連到這個尾跳，仍要證明該byte與S0等context在中間保持；不能把早期reply當作後續fresh值。

這是本機控制流及參數證據，不把return n命名為硬體或登錄操作成功，也不推定40058的外部行為。

## 重播與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_task_registration_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_task_registration_static.py
```

檢查涵蓋兩份完整原本體96 bytes／32條指令、所有operands／CFG／store／GPR、SDK／40080／APP wrapper／post-init來源接點、65,536組n/c（32,640接受／32,896拒絕）、index與extent不等式、部分word overlap，以及34個operand／branch-signedness變異拒絕。JSON必須逐bytes重播一致。

後續仍需證明實際table範圍與snapshot關係、post-init dynamic stores及其他hook writers的保存、實機40080／400a4／40074綁定，以及非同步writers與frame／payload生命週期。
