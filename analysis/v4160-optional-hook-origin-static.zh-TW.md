# v4.1.60：optional hook的field48來源與巢狀frame

找到一條具體、仍有保存前提的來源鏈：APP把code pointer `0x197b8`寫入64-byte設定的+48欄位，候選初始化函式複製到state base+48；後續config入口正好fresh讀這個word作optional hook。若呼叫當下仍是197b8，就會進入已驗證的mode 3 wrapper／callee，其本機寫入不會覆蓋provider保存的config指標或caller的16-byte config。

這個結論不把「初次copy的來源」當成「實機當下的hook」。copy後的callbacks、動態table writes與中間服務仍有保存缺口，也未證明installed provider身分。

全程只做原bytes／operands與欄位、位址、frame區間代數。未執行或模擬韌體、copy、callback、RAM/frame、MMIO或裝置；C重建覆蓋率未增加。

## 證據與重用範圍

承接 [mode 3完整結構／保存合約](v4160-mode3-frame-static.zh-TW.md) 與 [完整config gates](v4160-config-gates-static.zh-TW.md)。程式：[check_v4160_optional_hook_origin_static.py](check_v4160_optional_hook_origin_static.py)。可重播證據：[v4160-optional-hook-origin-static.json](v4160-optional-hook-origin-static.json)。

本輪重用完整APP builder、UID leaf、初始化／zero helper、post-config、config consumer、mode 3及reader原本體驗證，新增的是它們的來源與保存串接。兩個bounded windows合計56 bytes／19條指令：

| window | 範圍（右端不含） | bytes／指令 | cut |
|---|---|---:|---|
| setup順序 | `8e88..8eb0` | 40／14 | 8eb0續行 |
| hook pointer形成／保存 | `19aa4..19ab4` | 16／5 | 19ab4續行 |

只有setup最後的4-byte `8eac CALL19b16`是相對既有bounded prefix新增的接點；不把重用bytes算成新增C進度，也不把windows稱為完整函式。

```text
setup window SHA-256
5cb9c111f8882609ad53a1b67a0b42a60679bf74e99bf0efef7cfe25c47bd2b2
source window SHA-256
0efd74834dd9b3216637be797ac67736e1a9129aa3944ad2d2dd10c565e82fc8
```

setup依序在initial slot fill正常返回後，於8ea8呼叫builder199e2，再於8eac呼叫wrapper19b16。這只建立條件性順序，沒有證明整個startup必然走到這裡或所有calls會返回。

## field48在APP中的確切來源

APP `19aa4 AUIPC A5,0`加上`ADDI A5,A5,-748`，形成`0x197b8`。中間的ADDISP參數與halfword store不改A5；`19ab2 SW A5,64(SP)`保存四個bytes `b8 97 01 00`。

builder傳給400a4的設定指標是C=`then-live SP+16`，因此SP+64對應 **C+48**。這與C+44中的197f0 callback、C+52中的fallback word是三個不同欄位。

在pointer store之後、400a4呼叫之前，只另呼叫完整UID leaf18f56。該leaf無frame／nested call，只寫A0+0..5；此處A0=SP+8。後面的本機六byte迴圈寫SP+40..45。這些範圍與SP+64..67不重疊；完整builder suffix沒有其他本機store覆蓋hook source word。

因此若所需SP／frame與有效存取保存、無不利physical alias／非同步writer，明確pointer store可把197b8帶到初始化呼叫。這個欄位有自己的完整word覆寫，不僅依賴更早的64-byte清零。

## candidate複製目的與consumer是同一個word

| 候選 | `[400a4]`初始化入口 | 64-byte目的state base | hook word=base+48 | `[40074]` consumer |
|---|---|---|---|---|
| V1.31 | `43c7e` | `200031ec` | `2000321c` | `43f46` |
| V1.40 | `43d0a` | `2000323c` | `2000326c` | `43fd2` |

地址均為十六進位。初始化通過前置validation並保持live S0／S1等context時，先要求fill64，再要求copy64，target分別為2000039c／20000332。field48..51因而是四個依序傳送的source bytes；不是原子word publication。來源／目的不利重疊、fill破壞source與外部writer仍須排除。

初始化的八個local defaults只寫+12／14／16／15／18／19／20／22，不碰+48..51。其後兩個fixed direct stores、post-config的fixed stores與fixed fill requests也與hook word分離，均在重播中作區間檢查。

startup zero helper的要求範圍同樣涵蓋hook word：兩版相對起點都是804 bytes，即zero-based index201、**one-based第202個word**。這只識別zero helper完成時可產生的零來源，不表示startup已完成或當下仍為零；也不是所有writers或可能值的窮舉。

## 欄位保存仍有缺口

至少仍需分別處理：

- 初始化copy後呼叫state+44 callback，以及43b3e／43bca。
- post-config的動態table stores與其callees。
- builder返回後，wrapper先呼叫fresh `[40080]`，才進constructor／40074。
- 其他slot writers、interrupt／DMA／reentry或非同步改寫。

固定ranges不碰hook，不能推論全部computed stores都不碰它。所以本輪只證明「若field48來源與保存鏈成立，optional hook可對上197b8」，未證明call當下的fresh word或實機installed slot。

## 匹配197b8時的三層frame

設constructor的當前SP=C，它把16-byte config放在C..C+15。provider入口同樣以SP=C進入，配置32-byte frame後H=C−32：

| 區域 | 相對C的位置 |
|---|---|
| provider frame | `C−32..C−1` |
| provider saved config pointer | `C−20..C−17` |
| provider saved S0 | `C−8..C−5` |
| provider saved RA | `C−4..C−1` |
| hook mode3的13個saved words | `C−84..C−33` |
| hook mode3 scratch word | `C−100..C−97` |
| constructor config | `C..C+15` |

197b8不配置frame，先把incoming A0替換為3，再無新link尾跳1929a。mode callee以SP=H進入，另配置80-byte child frame；它的直接stack writes完全低於provider frame，與saved config pointer及constructor config分離。

既有完整mode3／reader驗證確認：在相符code、有效正常存取、無MMIO physical alias／外部干擾，且內層polls與reader完成的前提下，mode callee恢復SP／RA／S registers且不定義GP。返回後，provider在V1.31 `43f62`／V1.40 `43ff6`由H+12 reload A1，可取回原config指標C；state S0也可保存。hook的A0返回值未拿來決定gates。

這解除的是匹配此hook時的本機frame-clobber疑點，沒有建立poll timeout或外部指標保存期。saved registers或搬移資料本身可能含有pointer值，不能從此宣稱「指標不被保存」。

## 接回gates與生命週期

若constructor來源與本輪hook保存條件都成立，C非零、reload後仍為同一來源，則words191c6／ffffffff與halfwords16000／1000可通過四個必填gates；byte12保留零會跳過state+21 gate。後續copy／arithmetic仍各有原本的正常返回、無干擾與分支條件，不能直接宣稱會寫入22或硬體成功。

hook word保存的是code pointer197b8；builder的64-byte來源frame結束，本身不會使這個數值code pointer失效，但仍依賴正確code、已完成且未被覆寫的copy。這不是其他payload／buffer被外部保留後的生命週期證明。

## 重播與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_optional_hook_origin_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_optional_hook_origin_static.py
```

檢查包括來源pointer／field48／little-endian bytes、UID／local copy extent、64-byte source與destination、startup word202、固定writer區間、fresh consumer load與save/call/reload、三層frame分離，以及35個source／setup／copy／consumer operand變異拒絕。JALR target變異改有效的immediate bit1，沒有把會被mask掉的地址bit0當成不同target。JSON須逐bytes重播一致。

仍需追查中間calls與動態stores是否保存hook word、實際400a4／40074／40080綁定及slot writers、MMIO／poll進度、非同步writers與payload保存期，以及GP+108來源和signed算術合約。
