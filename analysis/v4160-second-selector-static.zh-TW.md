# v4.1.60：第二個完整 selector、byte 內位元反轉與 ordinal 掃描

承接 [第一個 local selector 與 shift leaf](v4160-local-selector-static.zh-TW.md)，本輪展開 callback 的另一個 mapped target `0x2000156c`。兩份 resident **候選**的第二 selector，各 618 bytes／222 指令，已完整核對原 operands、CFG、兩處 leaf joins、frame 與唯一 object store。

此 selector 的三輪轉換使用**每個 byte 內的 bit reversal，保留 byte 位置**，不是整個16-bit字的反轉。初始候選固定在0..36；fallback 最多37輪、總 probe 最多38次的結論，依賴已驗證 leaf、有效 frame／object 存取及無外部干擾等前提，不保證耗盡時選到 set bit，也不證明上層 callback 終止。

只做原 bytes／operands／CFG 與主機端 permutation、整數及 ranking 算術。沒有執行或模擬目標 ISA、callback、resident、RAM／frame、MMIO 或裝置。既有 C 重建 bytes 未增加。

## 兩個完整本體

| 候選 | FLASH，end-exclusive | first-copy RAM | SHA-256 |
|---|---|---|---|
| V1.31 | `0x417dc..0x41a46` | `0x2000156c..0x200017d6` | `2690bd6dd6452573835de2af9c1799cd1adfcd73aa68f937703ccd91498b39c9` |
| V1.40 | `0x4181c..0x41a86` | 同上 | `109d36e174f53e18be4a41283ea4e677405fcefc1cad75e4700609d0458b865d` |

合計新增原本體 1236 bytes／444 指令。先前 44-byte shift leaf 原樣沿用，不重報為新增分析量。不能在較早的 RET 停止：RET 後還有 `MV S6,S7; J completion` 的 out-of-line 選擇分支，屬於完整本體且局部可達。

先前 callback 的 call site `0x41148`／`0x41188`，立即之前明確 MV A0,S0；經 mapping 精確指向本 selector。兩個 probe call sites 則各指向已驗證的 `0x6dec2`／`0x6e0b2` leaf。V1.40 的 AUIPC upper／JALR low 分別釘原 bytes，沒有假設與 V1.31 只差固定 immediate。

APP 仍為 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。既有 APP／候選／SDK／sparse／指令格式來源合約遞迴重驗。

## 單一 word snapshot 與三輪轉換

入口先取一次 W=`U32[object+152]`，另取 counter=`U16[object+64]`。令：

```text
F = low16(W ^ (W>>16))
x = counter ^ F
B(x) = reverse8(x&255) | (reverse8(x>>8)<<8)
x1 = low16(17*B(x)+F)
x2 = low16(17*B(x1)+F)
x3 = low16(17*B(x2)+F)
seed = x3 ^ F
candidate = seed % 37
```

F 的 high／low operands 來自同一個已載入的 W，沒有重讀 word152。第三輪原指令在 XOR 後才取 low16；就保留的低16bits而言，與上式等價。

每個 B(x) 都保留兩個 bytes 的位置。例如 B(`0x0001`)=`0x0080`，不是整個16-bit reversal 的`0x8000`。24條標準 SRAI 的 input 都在這些已形成的非負16-bit／8-bit domain；所有 `17*B(x)+F` 的中間值最多1179630，可放入 U32。

檢查器將三組 low-byte expansions 與三組 high-byte expansions 分別寫成固定 expected-operand templates，保留原排程差異。特別是第三個 low-byte expansion 的最後 OR 寫回 A5，而前兩個的目的 register 不同，沒有為了高階公式而抹去原 register 流程。

## captured pair 與第一次 probe

本體 fresh 讀 words `[object+312]`／`[object+316]` 到 S4／S5，之後兩處 probe 都以 A0=S4、A1=S5。這是分開取樣後保存在 registers 的 pair，不是外部來源必然同時一致的 snapshot。

第一個 A2 是 candidate=`seed%37`；除數是原指令的固定非零37，因此 candidate 一定在0..36。和第一個 selector 不同，本 selector 的所有 probe counts 都落在已驗證 leaf 的一般 unsigned 64-bit right-shift domain。

probe 後 AND1 測試 A0：非零直接保留初始 candidate；零才進 fallback。沒有 call target 的實際 installed 身分或 runtime execution 證明；本輪只把候選原指令接到同一份已驗證 leaf。

## rank、fallback 與條件性步數上限

fallback fresh 讀 d=`U8[then-live S0+301]`，以仍保留的16-bit seed 形成：

```text
rank = (d*seed)>>16
index = 0
ordinal = 0
limit = 37
```

product 最多16711425，可放入 U32；rank在0..254，d=0會給rank=0，這裡不是 divisor-zero 分支。

每輪以 index=0..36 呼叫 leaf，並將 index 的 low8 存入 S7。若返回 bit0 為1且 ordinal=rank，跳往 RET 之後的 out-of-line `MV S6,S7`，選擇該 index。若 bit0為1但 ordinal不符，ordinal++後 AND255；bit0為0則不增加 ordinal。每輪最後 index++，到37退出。

精確13-node scan SCC不包含 out-of-line 選擇分支，也不包含 initial probe。已驗證 leaf 只定義 A0／A1／A2／A5，不改 index S2、limit S8 或其他 S registers；所以在其 code／mapping／存取與無干擾前提下，fallback最多37次、加上initial最多38次。這不等於上層 callback 的終止證據。

初始 candidate 若未被選中的 index 取代，耗盡會保留它。fallback 的進入條件正是初始 probe bit為0，因此不能保證耗盡後的 byte310 對應 set bit。rank與 captured pair 的 set-bit 數是否匹配，目前未有欄位來源證據。

## frame、寫入與返回值

frame是48 bytes，保存／恢復十個 fields：RA@44、S0@40、S1@36、S2@32、S3@28、S4@24、S5@20、S6@16、S7@12、S8@8。stores分散在不同轉換階段，但都在對應 register 修改或 nested call 之前；restores在普通 RET 前完成。

唯一 direct non-stack store 是 SB S6→`[object+310]`；此 selector 沒有 byte311 store。byte310一定是0..36的初始候選或掃描 index，但「範圍內」不代表有效 bit、選擇成功或裝置語意成立。

A0保留最後 probe 的 AND1結果，不能當成固定 success flag。物件與 frame aliases、外部 writers／interrupts／reentry、saved words保存期、真正 installed code與callee映射都仍是前提。

## 重播與下一步

[檢查器](check_v4160_second_selector_static.py) 與 [完整 ledger](v4160-second-selector-static.json)：

```text
python analysis/check_v4160_second_selector_static.py
python -O analysis/check_v4160_second_selector_static.py
```

一般及 `-O` 模式逐 byte 重現 ledger，核對全部222條 expected operands／整段hash／local CFG、十個 frame fields、唯一 object store、caller及leaf joins、精確13-node SCC與ranking definitions，並拒絕40個指定operand mutations。

主機算術另外窮舉65536個16-bit words，比對每byte bit-reversal的獨立 oracle及involution；對每個seed檢查d=0／1／255三個界線，共196608個rank cases，另核對round中間值與最後low16/XOR等價。這些不是 target register／memory loop 模擬，也沒有宣稱窮舉所有欄位組合或證明實際值可達。

接續仍需展開 arithmetic word-pair service與其他callees、完整config gates／copy合約及實際provider綁定，並追查object/global producers、欄位關係、callback整體進度與frame／payload保存期。
