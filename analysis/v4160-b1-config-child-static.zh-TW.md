# B1 設定巢狀服務：P+78 推導與四欄位重算

接續[worker 下游驗證](v4160-b1-worker-leaves-static.zh-TW.md)，這次完整展開設定函式呼叫的小函式，以及相鄰的四欄位重算函式。兩份 resident 候選共新增 **852 bytes、264 條指令**的原指令合約。已確認小函式只直接寫 P+78，並釐清重算函式何時清除 P+124、何時重寫四個設定欄位，以及強制返回 0／2 的分支。

[Python checker](check_v4160_b1_config_child_static.py) 與[固定 JSON ledger](v4160-b1-config-child-static.json) 保存完整 operands、hashes、CFG、stores、呼叫串接與路徑憑證。全程只分析本機原始 bytes／strict sparse HEX、不可變 CFG 與封閉的 host 整數關係；未執行或模擬目標、建立可變物件／provider 模型、重播封包、連接硬體或進行目標網路分析。

## 完整範圍與證據界線

| 函式 | V131 FLASH | V140 FLASH | 每份 bytes／指令 | stores／calls |
|---|---|---|---|---|
| P+78 推導 leaf | `[0x55dea,0x55e44)` | `[0x55f2a,0x55f84)` | 90／29 | 1／0 |
| 四欄位重算 | `[0x55e44,0x55f94)` | `[0x55f84,0x560d4)` | 336／103 | 7／2 |

範圍包含普通 RET 之後仍由分支進入的指令。stores 包含重算函式的 RA frame store；兩個 call sites 位於不同分支，每條本機返回路徑只呼叫一次 leaf。

兩份候選的 leaf bytes 相同，重算函式 bytes 也相同；各版 call target 的絕對地址不同。這不等於實際 installed provider 已確認。以下串接都以對應原指令、正常返回、來源可讀、frame／物件不破壞彼此，以及所需欄位保存條件為前提。

## 小函式：有號除法之後才做無號截斷

入口 A0=P。依序讀取 mode byte `P+326`、無號 halfword X=`P+486`；只有 mode 2 才讀無號 halfword H=`P+328`。最後讀取無號 halfword Z=`P+484`。

以 `trunc0(a/d)` 表示向零截斷的有號整數除法，leaf 在截斷為 halfword 前的 scalar q 為：

| 分支 | q | 完整 X=0～65535 的 q 範圍 |
|---|---|---:|
| mode=2，H 非零 | `trunc0((trunc0((X−376)/2)−43)/8)` | −28～4067 |
| mode=2，H=0 | `trunc0((trunc0((X−376)/8)−43)/8)` | −11～1012 |
| mode=1 | `trunc0((X−68)/4)` | −17～16366 |
| 其餘 mode | `trunc0((X−80)/8)` | −10～8181 |

mode 1 從 `+0x52` 直接跳到 `+0x2e` 的共同 DIV，因此只除以 4 **一次**。所有實際除數為正的 2、4、8，沒有本機除零路徑，也沒有 32-bit 有號溢位。

接著先取 `T=low16(q)`，再做無號 `min(Z,T)`，最後僅將低 byte 寫入 **P+78**。負的 q 會在 low16 時轉成接近 65536 的值；選出的正 halfword 大於 255 時，也會在 byte store 再截斷。因此不能改寫成有號 min 或直接將負結果限制為零。

leaf 無 frame、child call、SP／RA／S 暫存器定義，也不定義 A0，普通返回的 A0 仍是入口 P。唯一直接 store 是 P+78 的 scalar byte，沒有將 P 指標寫入其他記憶體；保留入口 A0 作為回覆不等於在外部物件中保存指標。直接存取 extent 至少為 **488 bytes**，沒有本機 null／extent guard，亦未證明實際配置與有效期。

## 接回既有設定 wrapper：關閉已定位 child 的欄位改寫缺口

完整 200-byte 設定 wrapper `0x55f94／0x560d4` 的 `+0x88` 呼叫目標正是此 leaf。wrapper 沿用入口 P 傳入，leaf 只寫 P+78，wrapper 再強制返回 0。

因此在匹配這個 child、沒有其他 writers 或 alias／frame 破壞時，leaf 不會改寫上層剛算出的 **P+482、P+486、P+124**，也沒有額外 nested callback 或 pointer publication。這將前一階段尚未展開 child 的未知副作用，收斂為一個特定 byte store；並未證明整體 provider、其他呼叫或非同步欄位保存期。

若 mode=2 且 wrapper 的 `X>=2704` 限制一路保存到 leaf，q 的下限可收斂為 H 非零時 **140**、H=0 時 **31**，不再為負。仍不能推論 P+78 必為正：Z 可以為零，最後的 byte 截斷也可能回到零。模式與 X 在 child 的 fresh loads 前是否保持，仍是串接前提。

## 四欄位重算：各自取樣的來源與兩種 mode 路徑

重算函式以 fresh 無號 halfwords 取得四組最小值，讀取順序及每個 signed／unsigned branch 都保存在 ledger：

| 名稱 | 來源 | 後續用途 |
|---|---|---|
| A | `min(P+464,P+476)` | low8 寫 P+480，並參與 mode 2 計算 |
| B | `min(P+466,P+478)` | 經限制後寫 P+482 |
| C | `min(P+468,P+472)` | low8 寫 P+484 |
| D | `min(P+470,P+474)` | 經限制後寫 P+486 |

P+480／P+484 雖是 **halfword stores**，寫入值只保留來源最小值的低 8 bits；不是以 byte store 留下舊的高 byte。

B 使用 captured mode `P+327`：恰為 2 時取 `max(B,2704)`；其他 mode 讀 fresh `U32[P+256]`，bit 11 清除時取 `min(B,2120)`，bit 11 設定時保留 B。這個函式在非 mode 2 分支會先讀 P+256，即使 B 沒有超過 2120，也不能借用 wrapper「超過上限才讀」的存取條件。

D 使用之後讀取的 mode `P+326`。非 mode 2 時，另一個 fresh P+256 bit 11 決定保留 D 或限制為 2120；兩次 P+256 讀取不可合併成同一 snapshot。

mode 2 的 D 路徑有更完整的算術：

```text
t = 64 * low8(A)
H = (B > t+975) ? t+1276 : B+300
R = 1250 * fresh_U16[P+58]
D = max(low16(signed_min(D, R-H)), 2704)
```

此處 B 指已完成前述限制的 B。`P+58` 的原始兩 bytes 為 `3a3d`，既有 QK decoder 將其確認為 `qk.c.lhu`；不能使用一般 RISC-V 反組譯器顯示的 `fld` 當作此裝置指令語意。checker 沿用已固定的 QK 來源與向量合約。

t 介於 0～16320，H 介於 **300～17596**，R 介於 **0～81918750**；R−H 不會超過有號 32-bit 範圍。但 R−H 可以為負，指令確實先做 signed min，再 low16，最後才做 unsigned 2704 floor。不能將 floor 移到截斷之前。checker 使用 `signed_min=-300` 的封閉 scalar 例子，得到先 low16 再 floor 為 65236，與錯誤改序的 2704 不同；這只是算術次序證據，未證明存在對應的可達物件或實際資料來源。

## 相等時清 flag；不相等時重寫全部四欄位

算完候選值後，函式依序讀當前 U16[P+480]、P+482、P+484、P+486 並比對，任一不相等即短路離開比較鏈。

| 分支 | 本機寫入與呼叫順序 | 普通返回值 |
|---|---|---:|
| 四欄位全部相等 | 寫 P+124=0 → 呼叫 leaf(P) → 強制 A0=2 | 2 |
| 任一欄位不同 | 寫 P+124=1 → 依序 SH P+480、482、484、486 → 呼叫 leaf(P) → 強制 A0=0 | 0 |

不相等時會重寫全部四欄位，不是只寫那個發現差異的欄位。相等時會**清除** P+124，與前述只在兩 lane 變動時設 1 的 wrapper 不同。

兩個 call sites 都以原入口 P 呼叫已核對的 leaf；leaf 回來後，各分支明確重新定義 A0，因此其入口 P 回覆不會成為重算函式的外部返回值。兩個函式的直接 store 都沒有保存物件指標；重算函式只有 RA frame store 與所列 scalar stores。

leaf 會重新讀 mode、X、H／Z，並不保證看見重算函式先前使用的相同 mode 或來源時點。即使四欄位 writer 已定位，也未證明來源初始化、實際 caller 可達值、物件所有權、非同步更新順序或後續消費／釋放。

## 驗證與剩餘工作

```powershell
python analysis/check_v4160_b1_config_child_static.py
python -O analysis/check_v4160_b1_config_child_static.py
```

checker 重跑祖先驗證、APP／SDK／兩份 candidate 身份與 strict sparse HEX，核對整個函式範圍、QK 指令及固定 ledger。每份 leaf／重算 CFG 分別有 **32／120 條 edges**，每條 edge 都有 entry→edge→RET 語法 walk；兩者本機 CFG 均無環。

逆向追查普通返回前最後一個 A0 定義，確認 leaf 的入口 P 可到達 RET，而重算函式只能由 `+0x10a` 的 2 或 `+0x14c` 的 0 到達 RET。完整 DAG 語法路徑分別為 **8／4400**；重算函式中 880 條通往 2、3520 條通往 0。這些是忽略分支條件可滿足性的圖上計數，不是可執行測資、輸入機率或 runtime observations。

負向驗證逐一修改 **264 個指令位置**，另修改 **40 個 typed-load funct3**，必須全部被拒絕。封閉整數檢查涵蓋四個 leaf 公式各自的全部 65536 個 X，共 **262144** 組，以及 mode byte 分類、halfword 截斷與 clamp 邊界。沒有將可變物件、記憶體、callee 或 provider 建成目標模型。

下一步仍需追查重算函式的實際 callers／來源 writers、`0x5d006／0x5d14e` 等其他巢狀服務、實際 clock／arena／record 綁定，以及 clear 後節點有效期、完整消費與釋放順序。此次只增加條件性原指令合約驗證，**未增加既有 C 重建分子或更新 95.75% 靜態重建快照**，也未宣稱完整可用韌體已經驗證。
