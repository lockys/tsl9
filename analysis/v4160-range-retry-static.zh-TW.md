# v4.1.60：範圍 helper、來源 callback 與完整重試尾段

接續 [initializer 後段搬移](v4160-initializer-post-radio-static.zh-TW.md)，本輪核對兩個範圍helper、共同word來源及完整276-byte重試函式。兩個呼叫域可排除全1值的拒絕分支，但不證明取樣或重試會完成。正常RET的A0是最後候選word的低16位，合法返回也可能是0。

程式：[check_v4160_range_retry_static.py](check_v4160_range_retry_static.py)。證據：[v4160-range-retry-static.json](v4160-range-retry-static.json)。只檢查原bytes、operands／CFG／frame與整數／byte等式；沒有執行或模擬ISA、callback、RNG、RAM、MMIO或裝置。C重建覆蓋率不變。

## 完整本體與解碼

| 項目 | V131起點 | V140起點 | bytes／指令 |
|---|---|---|---:|
| signed range | `43e8e` | `43f1a` | 36／16 |
| unsigned range | `43eb2` | `43f3e` | 32／14 |
| word source | `433a8` | `43434` | 108／37 |
| retry tail | `53868` | `53916` | 276／94 |

每版452 bytes／161指令全部另有operand guards。本輪只在新checker中加入strict標準signed LH及MULHSU解碼，沒有修改既有decoder。原APP reader `191c6..19220` 的90-byte合約重用既有證據。

尾段五個LH都以S0為B基址，offsets為232、252、234、254、236，之後AND `ffff`，所以比較的是16-bit位元值；不能將它們誤解為unsigned load，或把符號擴展帶入最終比較。

## 範圍 helper 的實際呼叫域

兩個wrapper都配置32-byte frame，保存S0／RA及入口上界A1，呼叫同一word source，返回後載回上界。令source返回的unsigned word為R，D為`(upper−lower) mod 2^32`：

* signed wrapper取signed D × unsigned R的high32，加lower，再保留低16位。
* unsigned wrapper取unsigned D × unsigned R的high32，加lower，沒有最後的16-bit縮窄。

以上是原指令算式，不表示任意上下界都形成合法區間。本輪caller實參足以給出更強界線：

| 實參lower／upper | 結果 |
|---|---|
| `0／3fff` | X=`floor(16383*R/2^32)`，範圍`0..3ffe` |
| `0／ffffffff` | Y=0若R=0，否則R−1，範圍`0..fffffffe` |

signed wrapper在此使用的D是正數16383，低16縮窄無損。X與Y來自兩次source呼叫，不是同一次word取樣。只要wrapper與來源按所需保存條件正常返回，範圍就對任意R成立，不需要假定R均勻、隨機或獨立。

## word source 的callback界線

候選固定槽`40038`分別指向`433a8／43434`。source先保存RA／S0／S1於16-byte frame，fresh讀`4002420c`到S1，CPU SW0及FENCE.I，然後選擇來源：

| 分支 | V131欄位 | V140欄位 | 行為 |
|---|---|---|---|
| primary非零 | `20003210` | `20003260` | 呼叫該次fresh pointer |
| primary為零、fallback非零 | `200031e0` | `20003230` | 呼叫fresh fallback |
| 兩者為零 | 同上 | 同上 | 略過callback，仍更新state |

state地址是 **`20002ec8／20002f18`**。有callback時，先把callback回覆加上callback之後fresh讀取的state，mod32存回。共同段再執行`state*343fd+269ec3`的低32位，即係數214013與2531011，存回state。最後CPU寫回S1 snapshot，再fresh讀state到A0。

這些是條件式資料流，不證明統計隨機性、原子snapshot或硬體效果。若沒有callback，且所需state保留／正常存取條件成立，算式是`(214013*s+2531011) mod 2^32`；有callback時的輸入則還包含它的回覆與fresh post-callback state。

未知callback必須正常返回、保存source正在使用的S0／S1、SP、frame words及其他live caller S registers，尤其尾段的S2／S3，並保存所需GP、物件與global內容。這些義務不能只由ABI名稱推定。

若實際選中的pointer保持前輪APP reader `191c6`，其既有本機合約可提供S／frame非寫入證據；但它的配對halfword讀取仍有四個retry edges，正常完成仍是額外前提。固定候選slot或先前publication都不能自動證明目前fresh pointer相同。

## 第一階段：非零seed

前輪copy6已提供B+232..237的舊值。重試函式先依序產生X、Y；兩者都是0便重試。原code另拒絕全1值組合，但Y永遠不是`ffffffff`、X也不是`3fff`，因此該拒絕分支不可達。

通過後寫：

| 目的 | 資料 |
|---|---|
| B+244 word | Y |
| B+248 byte | low8(X) |
| B+249 byte | low8((X>>8) OR `ffffffc0`) |

後兩個bytes合成little-endian `X OR c000`。此階段不比較舊六個bytes，也沒有要求後面的候選必須與這個seed不同。

## 第二階段：與舊值不同的非零候選

函式從offset122再次依序取X、Y。零pair會重試；這裡的全1值拒絕分支也不可達。接著把`LE32(Y) || LE16(X)`寫到B+250..255，其中X高兩位為0。

它按三個16-bit blocks，與先前copy的B+232..237比較。任一block不相同就到epilogue；三者全相同便重試。因此正常退出條件是：**候選六個bytes非全零，且不同於舊值**。

完整raw CFG有兩個循環SCC，大小14／37。使用本輪helper範圍固定兩個BNE後，92個nodes可達；兩個全1值BEQ不可達，SCC縮成12／36。剩餘零pair／相同候選重試未被範圍證據排除，沒有硬性嘗試次數或source公平性／完成保證。這也不是對任何特定callback序列可達性或無限執行的證明。

## 返回值與保存條件

candidate比較前，code將A0的低16位符號擴展再AND `ffff`；其後RET suffix不再定義A0。因此普通返回是 **`A0=Y & ffff`**，不是完整Y，也不是Boolean成功碼。

例如X=1、Y=0、舊六個bytes全零，候選非零且與舊值不同，可以正常退出，但A0仍為0。此例只驗證值域與退出條件相容，沒有宣稱實際source一定產生它。

尾段直接stores只有五個frame saves、三個seed stores及五個candidate stores；直接物件寫入都在B+244..255，不碰舊六個bytes、B+193／B+201。來源自身的固定state word也與既有B／ctx metadata／table／node／task區間分離；未知callback的額外寫入仍需另行保存義務。

符合所需helper正常返回、live S／frame／物件保存及無不利MMIO／非同步干擾前提時，epilogue載回RA／S0／S1／S2／S3、SP加32後普通RET。這提供條件式返回鏈，不證明實際重試已完成或initializer已回到gate／primary publication。

## 可重現檢查與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_range_retry_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_range_retry_static.py
```

一般與`-O`要求ledger逐bytes一致；320個operand mutations與2個非本輪支援的FENCE.I編碼變體均被拒絕。另檢查完整CFG／SCC、131072個range輸入樣本及邊界等式、65536個LH正規化值、seed／candidate packing、零返回例，以及LH／LHU與MULHSU／MULHU區分。非支援編碼不等同架構上非法。

下一步追查實際primary／fallback binding與state保存，並接通普通返回之後的gate／primary發布；重試終止、setter執行順序與實際installed provider仍待釐清。
