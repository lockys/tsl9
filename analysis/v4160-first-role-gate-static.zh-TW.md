# v4.1.60：401a0 角色入口、條件式登記與 gate 寫回

本輪接續 [timer 與第二次 task 登記](v4160-timer-start-setup-static.zh-TW.md)，驗證兩版 `401a0` 候選入口及其前置 gate。前輪 `(A0,A1,A2)=(4,0,5)` **不是此角色的固定 task ID**：程式會先建立 handler address，再由 registration fresh 讀取 count 決定回覆。

若 fresh gate 為零且前輪 count=5 等保存條件成立，內層 registration 返回5、count 寫6、entry5 收到 handler。initializer 的已封閉前綴會保存回覆、完成清零，再把 byte5 寫回該 gate。證據止於 initializer 前綴結束，沒有宣稱整個 initializer 或角色入口會返回。

程式：[check_v4160_first_role_gate_static.py](check_v4160_first_role_gate_static.py)。原指令與分支證據：[v4160-first-role-gate-static.json](v4160-first-role-gate-static.json)。全程僅靜態解碼、CFG、欄位及 frame 區間等式；未執行或模擬韌體、registration、fill、callback、MMIO 或裝置。C 重建覆蓋率不變。

## 完整原碼與 bounded prefix

| 本體 | V131 範圍 | V140 範圍 | bytes／指令 |
|---|---|---|---:|
| 401a0 角色入口 | `6dd16..6dd86` | `6df06..6df76` | 112／30 |
| primary publisher | `61b1c..61b5a` | `61c06..61c44` | 62／18 |
| gate 函式 | `55bde..55c32` | `55d1e..55d72` | 84／26 |
| initializer 前綴 | `5362e..5366c` | `536dc..5371a` | 62／20 |
| setter 0 | `55bd4..55bde` | `55d14..55d1e` | 10／3 |
| setter 1 | `55c48..55c52` | `55d88..55d92` | 10／3 |

範圍右端不含；只有 initializer 是未完成的 bounded prefix。每版共340 bytes／100指令，primary publisher 重用 [既有來源驗證](v4160-loaded-hook-sources-static.zh-TW.md)。全部 instruction operands、whole-window hashes、calls／stores 清單及 conditional-normal-return CFG 均重驗。

角色入口先呼叫 primary，primary 再呼叫 gate。角色本身有13個 linked calls，最後還原 RA／SP，尾跳 `6d572／6d75e`；沒有 ordinary RET 或固定成功返回碼。解碼完整本機 body，不代表13個 callee 或尾跳已全數封閉。

## gate 與 count 是不同欄位

| 欄位 | V131 | V140 |
|---|---|---|
| fresh gate，ctx+3 | `2000319f` | `200031ef` |
| count，ctx+1 | `2000319d` | `200031ed` |
| capacity，ctx+2 | `2000319e` | `200031ee` |

gate 非零會跳過內層 registration 與 initializer；為零才呼叫它們。以前的 context clear 是零值來源見證，沒有建立所有中間 writers 的完整保存證明，所以本輪分別附加 fresh gate=0 或1..255的條件，不自行選定實機分支。

在 count=5、capacity≥14、owned T=`200047f4` 保持時，兩種分支的第一個新登記都能受理，但 handler 不同：

| fresh gate | 第一個新 handler V131／V140 | 回覆／count | 本輪截止點 |
|---|---|---|---|
| 0 | `5352c／535da`（gate 內層） | 5／6 | initializer `5366c／5371a`，已寫 gate5 |
| 1..255 | `4dbf2／4dc8a`（外層首筆） | 5／6 | 呼叫 `4da70／4db08` 之前 |

兩路均寫 entry5=`T+20=20004808`，word 終點 `2000480c` 位於最小 table 終點 `2000482c` 之前。登記 handler pointer 不等於同步執行 handler。

## 零分支：從回覆 ID 到 gate5

內層 registration 的普通返回 A0=5 隨即傳給 `5362e／536dc`，不是傳入口4。前綴依序：

1. SP−=16，保存 S0／S1／S2／RA；以 S0 保存入口 A0=5。
2. 明設 A2=296、A1=0、A0=`200033b8／20003408`；因此入口 A2=5 不作為 fill 長度。
3. 先清 word `200034e4／20003534`，再透過 mapped `2000039c` 完成296-byte fill。
4. 兩個完整 setter leaves 各以 A0=0 清 word：V131 `200034e0／200034e8`；V140 `20003530／20003538`。
5. matching fill 僅定義 A0／A4／A5，setters 僅定義 A5，因此 S0 仍是5；`53668／53716` 將 low8(S0)=5 寫回 ctx+3。

fill 加上三個 word stores 合計清除連續308 bytes，但它們不是一次原子清零。在正常完成、source/code/slots 保存、無不利 alias 或 MMIO／FENCE.I／非同步副作用等條件下，前綴截止點可得 S0=5、gate=5、A0=0、A1=0、A2=296、count=6。此時 frames 仍活躍，後續原指令尚未展開。

## 非零分支與 callback words 的順序

若 fresh gate 非零，gate 不呼叫內層 registration 或 initializer；局部不改 A0／A1／A2，因此返回 primary 時可保存 `(4,0,5)`。在有效 saved frames 與無干擾等條件下，gate／primary 共發布七個固定 code-pointer words，再返回角色入口。外層隨即重設 A0 為自己的第一個 handler，matching registration 得5、count6；到下一 initializer 前，條件式實參是 `(5,0,6)`。

| publisher | V131 目的範圍／word | V140 目的範圍／word |
|---|---|---|
| gate，四個 word | `20003420..2000342f` | `20003470..2000347f` |
| primary，前兩個 word | `20003470／20003474` | `200034c0／200034c4` |
| primary，第三個 word | `200034fc` | `2000354c` |

這些是保存函式位址，不是在此呼叫它們。零分支的296-byte fill 會覆蓋上表前六個目的 word，但各 publisher **只有在 initializer 返回後才寫入**。因此不能把完整 body 內後面的 pointer stores 當成零分支前綴截止時已發生的事。

## frame 與尚未封閉的範圍

以401a0入口 SP=S：外層、primary、gate 的 RA 分別存於 S−4、S−20、S−36；initializer SP=S−64，S2／S1／S0／RA 存於 S−64／−60／−56／−52。fill 與兩個 setters 沒有自己的 frame，這些 saved words 互不重疊。零分支截止時四層 frame 仍在，不宣稱已還原至 setup。

固定清零與 pointer stores 另核對不碰 count、capacity、table pointer、APP task bytes、已有 table entries 或前輪名義 timer node。這些數值區間證明仍以實體非 alias、有效非回繞 frames／globals／heap、無 IRQ／DMA／重入／外部 writers 等條件為限。

完整外層雖有六次明確 registration，後續 initializer 的效果尚未封閉，不能將其實際 ID 直接指定為5..10或6..11，也不能從局部無分支推定它必定進入下一個 setup slot `401ac`。

## 驗證與後續

一般與 Python `-O` 均要求 ledger 逐 bytes 重播一致。驗證涵蓋原檔身分、兩版slot、六個視窗的全部 operands／CFG、fill／registration 接點、兩類分支截止點、256個 gate 值、全部256種前輪 capacity layout、四層 saved-word 區間，以及200個逐指令 operand mutations 拒絕。

下一步是 `5366c／5371a` 之後的 initializer 寫入與返回，或非零分支的 `4da70／4db08`。實際 fresh gate、provider 綁定、其餘 initializer／tail、副作用及物件保存期仍待釐清。
