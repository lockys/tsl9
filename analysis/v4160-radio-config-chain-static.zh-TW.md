# v4.1.60：設定 callees、固定計數迴圈與尾跳截止點

接續 [initializer 欄位驗證](v4160-role-initializer-fields-static.zh-TW.md)，本輪封閉 `64298／64382` 本體、三個直接 callee 及其中一個巢狀 leaf，並把保存條件推到尾跳後第一個 RF call 前。這仍是兩份 resident **候選映像**的條件式合約，沒有證明實際 installed provider。

程式：[check_v4160_radio_config_chain_static.py](check_v4160_radio_config_chain_static.py)。證據：[v4160-radio-config-chain-static.json](v4160-radio-config-chain-static.json)。只解碼原 bytes、核對 operands／CFG／讀寫及定義集合、驗證整數與區間等式；不執行或模擬目標 ISA、RAM、MMIO、FENCE.I、callback 或裝置。既有 C 重建覆蓋率不變。

## 本輪範圍

| 項目 | V131 起點 | V140 起點 | bytes／指令 |
|---|---|---|---:|
| parent | `64298` | `64382` | 118／34 |
| registers leaf | `6430e` | `643f8` | 60／23 |
| bulk | `660ce` | `6620c` | 372／140 |
| bulk 呼叫的 pulse leaf | `66098` | `661d6` | 54／20 |
| bits leaf | `638ea` | `639d4` | 90／31 |
| 尾跳目的的前綴 | `641b0` | `6429a` | 76／25 |

每版合計五個完整本體 694 bytes／248 指令，加上有界尾段前綴 76 bytes／25 指令。parent 最後尾跳，不能當作已返回 initializer。四個 callees 有普通 RET。除 pulse 的兩個計數迴圈，其餘所列局部 CFG 無環。

bulk 的完整 372-byte 身分、全部指令邊界、GPR 定義集合、全部 30 loads／30 stores 及控制指令均核對；其中 65 個指令另有獨立 operand guards。其餘算術由完整 bytes 雜湊固定，本輪沒有逐一建立所有 RMW 算式或硬體最後狀態。其餘五個列項逐指令核對 operands。

## parent 發布的資料

下表 V140 RAM 地址一律為 V131 加 `0x50`。令 F 為前輪外層設定基址，X 為此處 fresh `U32[F+0]`。

| V131 CPU 地址 | 寬度 | 寫入資料 |
|---|---|---|
| `20003510` | byte | 0 |
| `2000350c` | word | 0 |
| `20003504` | word | `40024300` |
| `2000353c` | word | `40024200` |
| `20003590` | word | `40025000` |
| `20003508` | word | `40024100` |
| `2000351b` | byte | 1，使用 Xwchc 窄 store |
| `20003538` | word | X |
| `20003534` | word | `(X+272) mod 2^32` |

X 和 X+272 在這個封閉範圍是寫入資料，不被當成 CPU 存取基址或呼叫目標。只有在早期來源及所有中途保存前提都成立時，才可分別替換為名義值 `2000418c`／`2000429c`；本輪不據此指定 heap／DMA 用途或物件保存期。

parent 使用 16-byte frame，只保存 RA；三個 linked calls 後還原 RA／SP，再尾跳 `641b0／6429a`。這保留的是 initializer 的返回鏈，並未在尾跳點完成返回。

## 四個 callees 的 CPU 存取合約

這些地址僅在各次 fresh pointer loads 保持 parent 發布值時成立；CPU 地址區分不能取代 MMIO 物理副作用證據。

* registers leaf：fresh 取 `2000353c／2000358c`，對 `40024200` 的 offsets `20,28,36,44,52,60,68,76,116,8,12` 依序寫入 11 個 words。資料依序為 `140,108,140,60,140,60,140,108,X,65535,61455`。最後值是 **`0000f00f`**，是直接寫入，不是還原較早的硬體 snapshot。
* pulse leaf：三次 fresh 讀 `20003590／200035e0`，依序對 base+12 寫 `1101,0,1101`。兩段各為 LI 20、NOP、減一、BNEZ 的固定計數迴圈；正常指令完成且 GPR 無干擾時各 20 次。迴圈沒有硬體狀態讀取，不能稱為 ready polling，也沒有可證的時間單位。
* bulk：唯一巢狀 call 是 pulse；之後 fresh 取同一 base 到 A5，直到返回均無其他 A5 定義。29 個非 frame word stores 均使用該 base，offset 集合是 `40,44,48,56,60,72,76,80,84`，保持 ledger 中的原始順序及 fresh reads；另有自己的 RA frame save／restore。不能把多次 RMW 合成單一一致的硬體 snapshot。
* bits leaf：fresh 取 `20003508／20003558`，依序對 `40024100` offsets `0,0,52,44,44,32` 寫 6 個 words；另 fresh 讀一次 `U8[F+20]` 作位元來源，沒有寫回來源 byte。

四者共有 49 個條件式 MMIO word-store 指令位置。這是靜態位置數，不是裝置事件計數。三個 leaf 無 frame、巢狀 call，亦無 RA／SP／GP／S registers 定義；bulk 有自己的 16-byte RA frame，沒有 GP／S registers 定義。

## 保存到尾段 RF call 前

parent 的固定 RAM stores 均與前輪 B 的 296-byte 範圍、count／capacity／ctx gate、table pointer、最大 212-entry table、名義 node 及 APP task bytes 分離。封閉 callees 的 stores 則只落在自己的 RA frame 或條件式 MMIO 基址。

沿用前輪 gate-zero／來源／mapping 前提，並要求有效非別名 frames 與 globals、保存 frame words、所需正常完成、無不利 MMIO／FENCE.I／IRQ／DMA／重入或外部 writers 時，ctx gate5、count6 與上述欄位可保存到本輪截止點；parent 自寫的 state byte1 亦可保存到尾段兩次 fresh reads。

尾段先建立 **32-byte frame**，保存 S0、RA、S1..S5。兩次 state reads 都與4比較；state1 時跳過兩個 early exits。接著 fresh pointer 與 `40024300` 比較，若仍是 parent 發布值便通過。任何 fresh 值不符合前提，均不能直接沿用這條選定路徑。

通過後，原指令依序：讀 `4002420c` 到 S4、SW 0 到同地址、FENCE.I、設 A0=13。驗證截止在 linked call **之前**：

| 截止 call PC | 目標 | 狀態 |
|---|---|---|
| V131 `641f8` | `63eda` | A0=13；32-byte 尾段 frame 仍存在 |
| V140 `642e2` | `63fc4` | 同上 |

此時只證明 CPU 曾保存 snapshot 到 S4 並出現清零／FENCE.I 指令，**尚未證明 control 已還原**。RF call、其後其他 calls、整個尾段返回、initializer 返回與物件後續保存期都未封閉。

## 可重現檢查

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_radio_config_chain_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_radio_config_chain_static.py
```

檢查原 APP、SDK header、兩份候選及既有來源身分，逐 bytes 重建 ledger；兩版合計拒絕 390 個 operand mutations 與 6 個非本輪支援的 NOP／FENCE.I 編碼變體，另核對 20-step ranking、32-bit 加法回繞及固定 scalar 等式。非支援編碼不等同宣稱架構上非法。

下一步展開 `63eda／63fc4` 與尾段後續 calls，確認 control snapshot 的消費及返回條件；實際 provider 綁定、fresh 資料與物理效果仍待釐清。
