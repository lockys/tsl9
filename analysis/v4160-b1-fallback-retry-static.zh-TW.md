# v4.1.60：Range／retry 正常返回至 entry6 的 fallback 保存

接續 [RF 返回與後續 helpers](v4160-b1-fallback-rf-static.zh-TW.md)，本輪將 gate 零分支從 range helper 呼叫前接過完整 retry 的**條件式正常返回**，再接回 gate／primary 的指標發布及外層 entry6 登記。

檢查器：[check_v4160_b1_fallback_retry_static.py](check_v4160_b1_fallback_retry_static.py)；證據：[JSON ledger](v4160-b1-fallback-retry-static.json)。全程是原始 bytes、CFG／operand／stores、封閉整數與區間／frame 證書，沒有執行韌體、建立可變 target 狀態模型、操作硬體、重播或連線 target。沒有增加 C 重建 bytes 或提高覆蓋百分比。

## 來源槽位與已封閉的呼叫情況

進入本輪時，前階段已在所選路徑下得到 fallback=`0`、gate=`5`、count=`6`。下一個 range helper 的實參是 `(0,16383,6)`；之後 wide range 使用上下界 `(0,0xffffffff)`。

| 槽位 | V1.31 | V1.40 |
|---|---|---|
| Source primary，config64+36 | `0x20003210` | `0x20003260` |
| Source secondary，config64−12 | `0x200031e0` | `0x20003230` |
| Primary clock wrapper 的 callback，config64+68 | `0x20003230` | `0x20003280` |
| Allocator failure fallback，config64+52 | `0x20003220` | `0x20003270` |

Source primary 與 secondary 都不是 allocator failure fallback。Primary 非零時直接呼叫該值；primary 為零時才讀 secondary。本證書涵蓋每次 fresh 綁定符合下列任一已核對情況：

1. Primary／secondary 均為零：不呼叫來源 callback。
2. Primary 為零、secondary=`0x191c6`：使用匹配的 APP reader。
3. Primary 匹配 `0x43520／0x435ac` clock wrapper，wrapper 的 callback 為零。
4. Primary 匹配該 wrapper，callback 匹配 `0x43d62／0x43dee`，且其 fresh copied reader 仍為 `0x191c6`。

這些是獨立的條件式來源情況，不表示所有情況都已從實際 boot 證明可達。未知非零 callback 不在已封閉範圍內；也不因函式名稱或 ABI 就假定它不改 frame 或物件。

Word source 的固定 state 為 `0x20002ec8／0x20002f18`。在所需取樣與保存條件下，本機更新式為 `(214013*s+2531011) mod 2^32`；有 callback 時先存入「callback 回覆＋fresh post-callback state」再進行相同更新。這不證明 uniform、隨機、原子或實體時間特性。

匹配 reader 與完整 arithmetic helper 沒有本機 stores／巢狀呼叫。Primary wrapper 與匹配 callback 的額外 RAM writes 分別落在 `ctx+20` accumulator 與 `ctx+24` result word；兩者地址不同。

## Range 與兩階段 retry

對任意正常返回的 U32 source 值 R，caller 的特化範圍為：

```text
X = floor(16383*R / 2^32)，範圍 0..16382
Y = floor((2^32-1)*R / 2^32)，範圍 0..0xfffffffe
```

X 與 Y 來自不同呼叫，不能視為同一次來源取樣。這些界線排除 caller 中的 all-ones guard，但不能排除 `(X,Y)=(0,0)`。

第一階段重試至 pair 非零，將 Y 寫入 B+244，將 `X | 0xc000` 的 little-endian halfword 寫入 B+248。第二階段取得非零 pair 後，先寫 candidate `LE32(Y) || LE16(X)` 到 B+250..255，再與舊 B+232..237 的六 bytes 比較；相同則重試，任一 halfword 不同才走正常返回。

所有 retry 資料 stores 都在 `[B+244,B+256)`，避開舊 tuple 及先前取樣的 B+193／B+201。Signed LH 載入後的 low16 mask 已由原指令及整數性質核對。

正常 RET 的 A0 是最後一次 Y 的 low16，**可能為零**。例如非零 pair 的 X 可以非零而 Y=0；因此這不是 Boolean 成功碼。Reader 輪詢、零 pair 重試、candidate 等於舊 tuple 時的重試均沒有證明必然退出，也沒有給出嘗試次數上限。

## 接回 gate／primary 與 entry6

如果 retry 正常返回，原始 saved-RA／frame 接點依序接回 gate、primary 與 outer。Gate／primary 不測試 A0 是否非零，接續發布七個固定 callback pointer words。這些是資料安裝，不表示 callback 已被執行。

此路徑先前已登記 entry5；在 fresh count=`6`、capacity=N0、table=`0x200047f4` 保持的條件下，下一個 outer 登記接受 ID `6`：

| 結果 | 值 |
|---|---|
| Entry6 word | `T+24=0x2000480c` |
| Handler | `0x4dbf2／0x4dc8a` |
| 返回 ID | `6` |
| 更新後 count | `7` |
| 下一個 initializer 實參 | `(6,0xffffffff,7)` |
| 本輪截止目標 | `0x4da70／0x4db08` 呼叫前 |

全部 67 個 N0（14..212、間隔 3）均可容納 entry6。A1 的 `0xffffffff` 來自最後一個 wide range，經所選正常返回路徑及匹配 registrar 保持；A2 則是 registrar 建立的 count+1=`7`。這與先前**非零 gate** 替代路徑登記 entry5、傳入 `(5,0,6)` 的情況不同，本輪沒有合併兩條路徑。

## 寫入、frame 與驗證範圍

每版核對十四個範圍包絡：source control、source state、clock accumulator、callback result、retry seed／candidate、七個 gate／primary pointers、count、entry6。包含來源替代情況的保守包絡，不是每次呼叫都執行的 store 次數。

這些區間在數值上避開 allocator fallback、config64／clock 來源 96 bytes、gate／capacity／table pointer、entry0..5、timer head／名義 node、small／remainder／large headers 及兩個 APP task bytes。名義 node 的排除在前階段失敗替代情況下是保守範圍，沒有宣稱節點存在。

所選最深來源鏈為 retry frame32＋range32＋source16＋clock wrapper16＋callback32，共 128 bytes。Reader／arithmetic 沒有自身 frame。正常返回後，retry 重用並釋放先前 initializer 的 saved-RA 位置，gate／primary 再還原各自 frame，最後留下 outer 的 16-byte frame。相對深度不證明絕對 placement／ownership／不別名，保存字有效仍是前提。

兩版各有十二個 resident strict sparse HEX 範圍核對；缺失 bytes 未補零。438 筆原指令變異檢查、range bounds／LH／packing 性質、entry6 全容量界線及 exact-byte ledger 都必須通過：

```powershell
python analysis/check_v4160_b1_fallback_retry_static.py
python -O analysis/check_v4160_b1_fallback_retry_static.py
```

所有前階段 source／RF／timer 條件仍保留，並要求所需 fresh 綁定、匹配 code／ISA／first-copy、正常 range／source／callback／reader 返回、有效且不回繞／不別名的 owned frames／heap／objects、保存字及無不利 MMIO／FENCE／IRQ／DMA／reentry／外部 writer。數值區間分離不等於實體副作用分離。

本輪結論是：若上述來源與正常退出條件成立，fallback 可保持為零至第一個 outer initializer 呼叫前，此時 gate=`5`、count=`7`。尚未執行 `0x4da70／0x4db08`，也未證明之後的登記 IDs、outer tail、實際 installed provider、retry progress 或完整消費／保留／釋放期。
