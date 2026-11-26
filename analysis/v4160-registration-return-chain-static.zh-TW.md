# v4.1.60：立即 callback、結果覆寫與 wrapper 返回鏈

本輪接通 [constructor 設定發布](v4160-constructor-publication-chain-static.zh-TW.md) 之後的 registration 與立即 callback，並補齊 callback 所用的一般算術 helper 的控制流與保存合約。符合先前及本輪前提時，可以返回 APP wrapper，在 `19b3a` 重讀 task byte `3`，最後以 `(A0,A1,A2)=(3,8192,192000)` 尾跳 fresh `40058` 服務。

新發現是 **registration 將 callback 的差值回覆寫回 callback 剛更新過的同一個 `ctx+24` word**。因此整個 registration 返回時，該欄位是差值，不一定是 callback 中途的新值 Q。

程式：[check_v4160_registration_return_chain_static.py](check_v4160_registration_return_chain_static.py)。原 bytes／operands／CFG 證據：[v4160-registration-return-chain-static.json](v4160-registration-return-chain-static.json)。只做靜態解碼、圖與封閉純量／區間等式檢查，未執行或模擬 target ISA、callback、算術 helper、RAM、MMIO 或裝置。C 重建覆蓋率不變。

## 完整本體與呼叫關係

| 候選 | registration | 立即 callback | 一般算術 helper |
|---|---|---|---|
| V131 | `43b0a..43b28` | `43d62..43de4` | `6df1a..6e2ac` |
| V140 | `43b96..43bb4` | `43dee..43e70` | `6e10a..6e49c` |

範圍右端不含。每版 registration 為 30 bytes／11 指令；callback 為 130 bytes／46 指令；算術 helper 為 914 bytes／296 指令。算術 helper 兩版 relative bytes 完全相同，SHA-256 為 `f4060bab83e2fde71bb16115cbc831a37ebc925599da24ca2015d5e4805a73b5`，JSON 只保存一份共同的 relative body。

registration 先保存 RA，把入口 A0（前輪形成的 callback address）寫入 callback slot，**立即 JALR A0**。callback 再 fresh 讀取 copied config 的 word0 並間接呼叫；在前輪 copy 與 source 保存條件下，這個值是 APP reader `191c6`。此處讀的是 copied config，並非另一個 service publication slot。

| 項目 | V131 | V140 |
|---|---|---|
| registration 保存 callback 的 slot | `20003230` | `20003280` |
| callback fresh 讀取 reader 的 word | `20003234` | `20003284` |
| callback prior-value／registration 最終結果 word | `200031b4` | `20003204` |

[完整 APP reader](v4160-service-provider-link-static.zh-TW.md) 沒有 frame、store 或 nested call，只定義 A0..A5，但有 fresh halfword 重讀迴圈；實機是否正常返回仍是條件。

## 一般算術 helper 的保存證明

先前 [config 算術證據](v4160-config-arithmetic-static.zh-TW.md) 僅封閉 divisor=1,000,000 的特定輸入路徑，不能套用到這次 callback 的參數。本輪改為解碼完整 914-byte 本體，確認：

- 全 296 節點在本機 CFG 條件性可達，邊界閉合、無環；七個 terminal 都是 `JR RA`。
- 沒有 store、call、frame 或 privileged operation。
- 只有三個 unsigned byte loads；其餘為算術及控制指令。
- 定義的 GPR 僅 T1、A0..A7、T3..T5，未定義 RA／SP／GP／任何 S register。

所有 66 個控制指令及三個 load operands 另有獨立 guard；完整 body SHA 固定其他 bytes。本機圖的有限性不代表所有 memory accesses 或裝置讀取都會成功；仍需有效 lookup 讀取、正確 code／ISA mapping、正常指令完成及無外部干擾等條件。

這足以把 helper 的 A0 回覆當成 opaque U32，同時證明它不由本機指令破壞 caller frame／S／GP。**本輪沒有證明一般 quotient 公式**，也沒有把 host 除法當成目標 helper 執行。

## callback 的三種結果與同址覆寫

令 R 為 reader 回覆，h 為 fresh `U16[copied_config+8]`。callback 用 MULHU／MUL 形成精確 unsigned 64-bit `1600*R`，以 high:low 放入 A1:A0，A2=h、A3=0 呼叫 helper。僅保存返回 A0 為 Q，忽略 helper A1；之後讀 `old=U32[ctx+24]`。

| unsigned 比較 | callback 的局部 word store | callback A0 回覆 |
|---|---|---|
| old=Q | 不寫 ctx+24 | 0 |
| old<Q | 寫 Q 到 ctx+24 | `(Q−old) mod 2^32` |
| old>Q | 寫 Q 到 ctx+24 | `(Q2−old+Q) mod 2^32` |

最後一種先 fresh 讀 `U32[copied_config+4]`，乘 1600 後用相同已保存的 h 呼叫 helper，第二個 opaque A0 回覆記作 Q2。前輪無干擾條件下 copied h 為 16000、word4 為 `ffffffff`，但本輪不推論 helper 的具體數值結果。

callback 普通返回後，registration 無條件 SW callback A0 到上述**同一個** `ctx+24`。所以最終結果是表中的差值回覆：即使 callback 曾寫 Q，也會被覆寫；相等路徑則最後寫 0。然後 registration 強制 A0=0，還原 RA／SP 並 RET。

例如 old=10、Q=13 時，callback 中途可寫 13，但 registration 最後會寫 3。此例僅說明兩次 stores 的不同資料來源，未宣稱實機能產生這組 helper 回覆。

## 保存範圍與返回鏈

令 constructor frame base 為 C：provider SP=C−32，registration SP=C−48，後者保存 RA 於 C−36；callback SP=C−80，保存 RA／S0..S5 的七個 word 位於 `[C−76,C−48)`。reader／一般算術 helper 沒有 frame 或 stores。

這些 stack stores 與 provider frame、constructor config／RA、wrapper saved fields 分離；另逐一驗證兩個全域 word stores 不碰 task byte、count、capacity、table pointer、entry3、allocated header、hook、copied config 或 service publication word。因此在原名義配置、有效非別名 frames／globals／heap、code 與 fresh fields 保存、無不利 MMIO／IRQ／DMA／重入／外部 writers，以及所需正常返回等條件下，可保留 task byte=3、count=4、entry3=`1995c`。

返回的資料流依序是：

1. registration 丟棄 callback delta 作為函式狀態碼，強制回 0；delta 已寫入 ctx+24。
2. config 在成功尾段再次設 A0=0，還原 RA／S0／SP，返回 `19bce`。
3. constructor 還原 RA，SP+=32，RET 至 `19b3a`，不再改 A0。
4. wrapper 在 `19b3a` 以 LBU fresh 讀 `[S0]`，覆寫原本的 0；若 S0／task byte 保持，得到 3。
5. `19b40` 在還原 S1 **之前**，fresh 讀 `[S1+88]` 至 T1。僅在 S1 仍為 `40000` 時，此來源才是 slot `40058`。
6. 還原 wrapper 原 RA／S0／S1／SP，設 A1=8192、A2=192000，`19b54 JR T1` 尾跳，不建立新 link。

候選 slot `40058` 分別為 `43728`／`437b4`；本輪只記錄 slot 身分，沒有呼叫、執行或驗證其本體。尾跳也沒有檢查該服務的結果。constructor 的 stack source 此時已釋放；新 callees 未見直接以原 config-pointer register 為來源的保存 store，但 opaque Q／delta 的數值仍可能恰等於 C。前輪 matching copy 只證 byte 值搬移，不能泛化為所有 provider 都不保存指標，亦不證後續 payload／物件生命期。

## 驗證與後續

一般與 Python `-O` 要求 JSON 逐 bytes 重播一致。檢查包含所有來源身分、完整新本體及既有依賴、全圖閉合／無環、store／GPR／call 清單、frame 與 protected ranges、252 個指定 operand mutations 拒絕、65,536 個乘積分拆等式、U32 高邊界及 4,096 組分支／模數等式。

下一步是 fresh `40058` 服務及返回 setup 的流程。實際 installed provider、GP／slots 全鏈保存、reader／硬體進度、一般算術數值合約與後續保存期仍待釐清。
