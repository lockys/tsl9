# v4.1.60：callback 回覆的局部保存期與後續覆寫

日期：2026-11-26。承接 [config+44 完整呼叫範圍](v4160-app44-closure-static.zh-TW.md)，追查 `197f0` 的回覆在 reference resident 正常返回路徑如何被保存及覆寫。[檢查器](check_v4160_callback_reply_lifetime_static.py)／[ledger](v4160-callback-reply-lifetime-static.json) 保存兩版本 continuation windows、完整 fill body 與來源串接。

**所追蹤的 A0 與 metadata M+8 半字，不會沿這條選定正常路徑保留到 heap-init：A0先被LUI取代，M+8半字稍後被40-byte fill覆寫為零。** 這不構成全域dead-store證明，也不表示硬體值、callback舊stack或其他副本皆已消失。

全程離線讀取原檔、解碼與主機寬度／區間代數，沒有執行或模擬 target ISA、buffer、fill、callback、provider 或 MMIO。原 BIN 與既有分析保持不變，C重建覆蓋率未增加。

## 證據範圍與呼叫串接

每版本核對config的20-byte／6-instruction窗口、post入口74-byte／22-instruction窗口；兩版本共 **188 bytes／56 instructions**。另重用各自映射到RAM `2000039c` 的完整46-byte／14-instruction fill。這些是既有本體的新跨函式性質驗證，不另算新增C函式覆蓋。

完整APP callback範圍、兩個read leaves與所有軟體callees仍由前輪checker重新驗證；兩份完整228-byte config／272-byte post本體亦核對原hash。所有本輪窗口指令都有獨立operand guards；兩個AUIPC/JALR pairs另外解算target。

| 步驟 | V1.31 | V1.40 |
| --- | --- | --- |
| metadata M | `2000319c` | `200031ec` |
| callback回覆SH | `43d3e → 200031a4..31a5` | `43dca → 200031f4..31f5` |
| 不相鄰的byte store | `43d48 → 200035f5` | `43dd4 → 20003645` |
| 呼叫post | `43d4c → 43b3e` | `43dd8 → 43bca` |
| post的A0覆寫 | `43b46` | `43bd2` |
| fill20 transfer | `43b72` | `43bfe` |
| fill40 transfer | `43b84` | `43c10` |
| fill40返回位置／heap-init call | `43b88` | `43c14` |

窗口範圍（終點不含）：

```text
V1.31 config: 43d3a..43d4e   post:43b3e..43b88
V1.40 config: 43dc6..43dda   post:43bca..43c14
```

本輪窗口在heap-init call本身之前結束，不將該callee之後的讀寫包含進局部結論。hash、全部原bytes與operand細節在ledger保存。仍沿用固定APP／SDK header／carrier與已保存LLVM來源／vectors的條件性ISA解讀；實際installed provider與最終RAM bytes未知。

## A0與A4的register路徑

前輪已核對callback在保存字/context完整時，正常返回硬體U32讀值的low16。設這次回覆為R；caller以SH將low16(A0)寫到M+8。

SH之後，caller只建立A5、將A4設為−1、寫不相鄰的global byte，再JAL到post。post前兩條指令為LUI A5與SW zero；entry+8執行 **LUI A0,20003000**。這段被guard的原指令沒有在SH之後、A0覆寫之前以rs1/rs2消費A0。

所以R雖以live A0進入post，並未由這個register路徑送入後續fill或作本機判斷。callback返回時A4也曾保有R，但caller的LI A4,−1會較早覆寫它；不是只追A0便宣稱其他暫存器皆無副本。

## metadata半字先保存，後被fill40覆寫

post依序提出兩個直接fill請求：

| 請求 | 目的區間（終點不含） | byte／count | 與M+8..9的關係 |
| --- | --- | --- | --- |
| fill20 | `[M+44,M+64)` | 0／20 | 不重疊 |
| fill40 | `[M,M+40)` | 0／40 | 包含兩個bytes |

填值前的其他明示fixed stores為zero至M+76、M+148、M+68，以及上表不相鄰global byte；三個post frame保存字也需在不alias結果欄位的前提下看待。

config窗口與post窗口都沒有本機load指令。兩個fill的完整body沒有nested call，唯一明示load是投影控制word `4002420c`；資料loop只有store。故在code/context、有效且不回繞的存取、MMIO/RAM分離及無外部介入等前提下，**這條路徑在覆寫前沒有對metadata結果的明示軟體重讀**。

兩版本相同的46-byte fill本體SHA-256：

```text
d67147a681aca68d4d082eebf74ab6214f61f43253be91e932eebd5c3e3d05a3
```

first-copy source為V1.31 `4060c`／V1.40 `4064c`。直接call數值target與slot40048的候選值均為 `2000039c`，但沒有因此宣稱實機一定安裝該內容。

其loop先A0+=1，再SB low8(A1)至A0−1，正常完成時依序寫offsets0..count−1。因此fill40的：

- 第9次資料SB寫M+8，先覆寫low byte。
- 第10次資料SB寫M+9，再覆寫high byte。
- 完整正常返回時，所追蹤半字為0；A0則是M+40的one-past end，並非R或原M。

這是兩次byte store，不是atomic halfword clear。中間fault、非返回、觀察者或外部writer可能看到部分更新，或使正常路徑前提不成立。僅提出40-byte請求本身不足以推到清零完成。

fill的encoded writes只包括A0／A4／A5，沒有SP／S0／RA定義；這與post在第一次fill前建立S0的指令一起，支持第二次目的base的條件性投影。saved frame、dynamic stores、物理mapping與外部副作用仍不能由nonwrite集合單獨保證。

## 舊callback stack不在這個清除結論內

令S為callback入口SP，且正常返回後保持同一SP。callback本體SP-=128，保存結果在新SP+28，所以該word投影為 **S−100..S−97**。post的16-byte frame保存S1／S0／RA則位於 **S−12..S−1**，兩個區間不重疊。

本輪選定continuation沒有明示清除舊callback結果word。stack返回後的真實內容、是否被其他路徑重用，以及所有副本的保存期都未證；沒有把metadata清零稱為完整資料抹除。硬體原word也不因RAM半字被覆寫而消失。

同樣不能因這次沒有找到局部consumer就刪掉callback：前輪已發現它有硬體RMW，且reset word `4002100c` 不在16組snapshot恢復範圍。這次未修改或執行任何韌體。

## 結論適用的前提

本輪只針對callback已正常返回並進入選定continuation的情況，要求：

- 相符的原APP／reference bytes與所需ISA語義，callback回覆保存鏈及後續code有效。
- config/global/SP/S0與保存字在相應存取時有效，frame／code／物件不作不利alias。
- first-copy fill內容與當時RAM target相符，兩次fill都完成有效且不回繞的寫入。
- 控制word4002420c與metadata分離，沒有中斷、外部writer或硬體效果破壞所需關係。

在此範圍可把「A0與M+8會繼續保存本次回覆」縮小為明確的覆寫位置。這**不是**全ROM讀寫普查、全域dead-store證明、實機觀測、任意時刻值為零或無條件終止保證。

## 重播與實際輸出

```text
python analysis/check_v4160_callback_reply_lifetime_static.py
python -O analysis/check_v4160_callback_reply_lifetime_static.py
```

兩模式均實際輸出：

```text
PASS: 65536 halfword mask cases; 41 span cases; 2 profile interval identities; 12 specified raw mutations
PASS: 4 continuation windows, 188 bytes/56 instructions; 2 complete46B fill bodies; scalar kill + conditional halfword clear
PASS: exact ledger replay; no explicit local read before overwrite; global/physical lifetime UNPROVED; NO target execution
```

halfword masks窮舉全部U16，只做主機整數關係；span cases為count0..40覆蓋offsets8/9的區間關係，沒有建立target buffer。十二個raw mutations改回覆store offset／width、global byte store、A0覆寫register、兩個fill目的／長度／byte、fill40 target、fill loop store offset／來源，均需命中特定semantic guard，不以完整hash不符或任意exception當成通過。

預設只讀重算並精確比對JSON；`--write`只建立不存在的ledger。重播需十三個已發布Python dependency模組、本機固定APP、兩份carrier、SDK header與LLVM來源／vectors；candidate輸入未隨本次發布，僅clone repo不足以重跑。

後續仍需追查實際provider／mapping、更廣的metadata消費者、config-I/O與heap物件保存期，以及外部writer與硬體副作用；本輪沒有把局部覆寫提升成這些問題已解決。
