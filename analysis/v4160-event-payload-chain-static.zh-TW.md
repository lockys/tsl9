# v4.1.60：event consumer、payload 複製與 callback 保存邊界

日期：2026-11-26。承接 [APP callback records](v4160-app-callback-records-static.zh-TW.md)，完整展開 `1753a`、`176f8`、`1787c`，並把共同的 completion `17666` 及兩份候選 copy leaf 接上同一條證據鏈。[檢查器](check_v4160_event_payload_chain_static.py)／[ledger](v4160-event-payload-chain-static.json) 固定全部原指令、操作數、完整 hashes、條件性 CFG、stores、呼叫實參與來源映射。

**來源 pointer 與 callback word 的證據不同：`1753a` 直接保存 callback word，來源 pointer 則交給 copy 服務。候選 copy body 能支持「在 helper 返回前逐 byte 複製」的條件性合約，但尚未證明實際綁定、後續目的資料保持或 delivery。**

全程本機讀檔、解碼與主機位元算術，沒有執行或模擬 target ISA、event queue、copy state、provider、payload、callback 或 MMIO。原 BIN、舊 ledger 與 C 原始碼未改寫，C 重建覆蓋率不增加。

## 六個完整本體

地址為十六進位；range 終點不含。

| 本體 | 執行範圍／來源 | bytes／instructions／stores | SHA-256 |
| --- | --- | --- | --- |
| submit | APP `1753a..175e8` | 174／59／9 | `35b5fa1a5d028d10cb4b5bae27f3b458192eac49ac58a1aedac44cc7a3eb39f9` |
| complete | APP `17666..176a0` | 58／22／3 | `f1cbcf44c139aae19dc96b5c5b7ef6f40f3b6820265947a29987167fdfdffd8a` |
| consume | APP `176f8..1787c` | 388／135／13 | `1bd864d85cd82d9253370ea168691d98e1929d40ba4f6d64a6fa42320c278592` |
| enqueue | APP `1787c..178f8` | 124／43／5 | `d6bf7526927fd47af6e6ae487b36a176eb7dc85a2ee33e275971b2dd589d6990` |
| V1.31 copy | RAM `20000332..2000036c`，source `405a2..405dc` | 58／18／3 | `558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36` |
| V1.40 copy | 同一 RAM range，source `405e2..4061c` | 58／18／3 | 同上 |

APP 四個本體合計744B／259 instructions／30 stores；加上兩個 mapped copy 本體，合計 **860B／295 instructions／36個靜態 store 位址**。這是不同來源 body 的計數，含 frame／MMIO／loop store 位址，不是執行次數或新的 C 覆蓋率。

全部 boundaries／opcode／operand／target 逐項固定。新增普通 RV32 OR 與 RV32M signed REM 的欄位解碼，不以一般 disassembler 名稱代替語義。APP 本機圖皆無循環；copy leaf 有明確 byte-loop。所有 call fallthrough 都只是正常返回前提，queue 的 external tail 另列。

## `1753a`：header、callback publication 早於 copy 請求

入口 A0..A5 暫稱 H、channel、kind、source、length、callback。先讀 U8[`2000c7a9`]，非零就直接返回1，不建 frame、無本機 stores／calls。零路徑依序：

1. fresh U8[GP+366]，seq=(old+1)&15，寫回該 byte。
2. SH `low16((H>>8)|(H<<8))` 到 `2000c7aa`；一般完整 H 未先截16位，不能無條件稱 low16 byte-swap。具體 H=`b562` 才可得 `62b5`。
3. SB `low8(kind|(seq<<4))` 到 `2000c7ac`；kind 沒有先 mask 成低4位。
4. 建16-byte frame、保存所需 context；SB50 到 `2000c7a8`，SB low8(length+3) 到 **同一 gate address `2000c7a9`**。
5. **SW 入口 callback word 到 `2000c7a4`**。
6. 透過 fresh `[4004c]`，提出 `(A0=2000c7ad,A1=入口source,A2=完整length)`。
7. fresh `[40200]`，A0=保存的 channel；再 fresh `[40058](fresh task,2,320)`、fresh `[40050](另一個 fresh task,1)`。
8. 正常返回恢復 frame，最後明確 A0=0；不檢查任何 provider scalar reply。

raw SDK header 把 `40200` 對應 JT115 `RF_SetChannel`，兩個候選 target 為 `65f94`／`6607e`。名稱／槽位不是實體無線操作或 installed identity 證據，本輪沒有操作硬體。

兩次 task 均讀 `2000c7a0`，但時間不同，不自動視為同一值。header／length／callback 都在 copy call 前發布；不構成 atomic publication。length 沒有本機上界 guard，low8(length+3) 也會回繞，例如253變成0，因此不能把 gate 提升為通用 busy lock。

本體**沒有把入口 source pointer 直接寫成持久 field**；但未知 copy/provider/callees 仍可能保存它。callback pointer 的直接 store 已有具體來源，卻尚未證明誰從該欄位取出並呼叫它、何時呼叫或值保存多久。正常返回0也不是 copy、設定、排程或 delivery 成功的收據。

## reference copy：能證明的條件性進展

兩版 slot `4004c` 去除 bit0 都對上完整 RAM leaf `20000332`，first-copy source mapping 及58-byte身分重驗。原指令先讀/保存 `4002420c`、寫零、FENCE.I，再檢查 destination/source 是否為零及 length 是否為零；任一條件不允許複製時，恢復控制 word 並 RET。

非零路徑 i=0，逐筆：

```text
fresh U8[source+i] -> byte
SB byte -> destination+i
i++
until i == full length
restore control word; RET
```

完整 leaf 無巢狀 call，encoded GPR writes 只有 A3..A6；不寫 A0/A1/A2、GP、S、SP、RA，也沒有保存 source pointer 的 field store。這支持以下**附帶前提的串接**：

- 實際 slot／RAM bytes 確實匹配 reference、ISA 適用。
- source/destination/code/MMIO 存取有效，且沒有不利 alias、外部 writer、IRQ 或重入破壞。
- source／destination 非零，length 適用，且必要 context 保持。

成立時，前輪 `176a0` 的2-byte stack payload，或 `178f8` 的7-byte stack payload，可在這個 **copy helper 返回前**逐 byte 複製到相應 destination。這不是 target copy-state 模型，也不是實測完成。

不利重疊可能改變後續 fresh source 讀值；null source/destination 則可不複製就返回。即使 helper 已複製，`1753a` 後面仍有未知 provider calls，不能據此證明它最終返回時目的資料未改、原 pointer 不被其他 callee 保留或實際送達。

## `1787c`：queue admission 與兩個 count snapshots

queue 名義 base B=`2000c8ac`，read index=+0、write index=+1、count=+2，payload=B+3+7*i。前輪 init fill request 是115 bytes，即3+16*7；這只是名義 layout，不是任意執行狀態的有效 extent 證明。

enqueue 先把第一次 fresh count 存在 S1，接著再讀一次 count：

- **第二次 count<=15**：取完整 U8[B+1] 作 I，提出 fresh `[4004c](B+3+7*I,入口source,7)`。初始 I 沒有本機 mask／bounds guard。call 正常返回後，重讀 write index 寫 `(i+1)&15`，重讀 count 寫 low8(c+1)，不測 scalar reply。
- **第二次 count>15**：略過 copy 與兩個 queue byte 更新。
- 最後卻由**第一次保存的 count**決定：非零則退框 RET，沒有固定 A0；零則退框、A0=255、tail→`17666`。

因此第一次 count=0、第二次 count拒絕copy的局部條件式可同時出現，仍會發出 completion tail；不能用「enqueue曾被呼叫」推斷已入佇列。index 在 copy 後才 mask，也不能回頭保證此次 destination 落在16筆名義範圍。

source pointer 在本體只作 copy 實參，沒有直接 pointer field store。真正 copy 完成、queue ownership、copy 前後 S0/S1／indices/count 保存與原 stack pointer 保存期仍需相應前提。

## `176f8`：bit0優先，bit1其次，否則返回0

完整入口 E=A1 保存到 S0。bit0 路徑正常返回 E XOR1，**不再處理 bit1**；沒有bit0才看bit1，該路正常返回 E XOR2。兩位都沒設時，本體返回 **0**，不保留所有高位事件。

### bit0：queue 來源與更新身分分開

fresh U8[`2000c8ae`] 非零才讀完整 U8[B+0] 作 I，呼叫：

```text
1753a(b562,21 decimal,0,B+3+7*I,7,17666)
```

I 沒有先 mask／bounds check。只有 full scalar reply=0，才 fresh 重讀 read index 並寫 `(i+1)&15`，再 fresh 重讀 count 寫 low8(c−1)。前置 count、呼叫用 index、更新 index、更新 count 都是不同讀值，不能用原 snapshot 代替。

count為零或 submit回非零仍正常返回 E XOR1；這是本機事件回覆規則，不是 payload 已送達或已消費的證據。

### bit1：copy 到 stack、分類，再交付 stack pointer

保存完整入口 A0 作後續排程 task。第一次 fresh `[4004c]` 請求 `(SP+8,fresh U32[GP+104]+7*fresh U8[GP+376],7)`。返回後再讀 mode；只有它非零且 U8[SP+9]&fc=0，才清 GP+376，然後重讀 slot／來源 pointer，再請求 `(SP+8,fresh U32[GP+104],7)`。不檢查 copy 回覆。

接著依 SP+9 bit1 與 U32[SP+8] bits10..15 分類：

- 分類1，且 U8[SP+14]&7c 非零：GP+369 XOR1 並寫回；結果非零才把1f00 OR進 SP+12 halfword。排程 operand=`160*((fresh U32[SP+12]>>18)&31)`。
- 分類2：完整 U8[GP+370] 先從 `1aae8+4*i` 讀 word，改 stack 欄位，**之後**才以 `(i+1) signed REM7` 更新 index。排程 operand=`800*(1+((fresh U32[SP+12]>>18)&31))`。

兩種排程共用 `1782e`，fresh `[40058]` 收到 `(保存的完整入口task,2,operand)`；**傳 stack pointer 的是後續 `C776(SP+8)`，不是這個排程 call**。C776 的解析／copy／ownership／retention 合約仍未展開。

名義7-byte copy只涵蓋 SP+8..14；LW SP+12會讀到SP+15，但兩種 delay遮罩都只取 word bits18..22，不使用SP+15。這不表示該 byte 必然未初始化，也不能把7-byte copy說成已初始化整個word。時間 operand 未指定物理單位。

名義7個 literal words 為 `ff,7dff,ffff,ff00,ffff00,ff0000,ff00ff`；28 bytes 的 SHA-256=`8c0a5db057c85d9429201e95f2c0e099d305794e4b8aee2585b707769a88bb5b`。首次 table read 沒有 i<7 guard，後面的 REM 不會回頭限制該次讀取；本輪只保存這28個捕獲 bytes，不替其他 index 補值。

## `17666`：先請求排程，再看入口回覆與 flag

先保存完整入口 A0，無條件提出 fresh `[40058](fresh U8[GP+379],1,2)`，不測 scalar reply。只有保存入口 A0=0，且 fresh U8[GP+378]=0，才呼叫 `90b0(176a0)`；正常返回後不管 cancel reply，直接寫 GP+378=1。

queue 的 tail 明確傳255，因此在這條正常局部路徑不會進 cancel／flag-update 分支，仍已提出前述排程請求。這不是「callback從2000c7a4確實被取出並呼叫」的證明，也沒有統一 completion status。

## 重播與下一個邊界

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_event_payload_chain_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_event_payload_chain_static.py
```

兩模式精確重播同一 JSON；RuntimeError guards 不因 `-O` 關閉。主機驗證含65536個 event/opcode cases、65536個 delay-field cases、256個 byte-index cases，以及19個指定原指令單 bit 變異於預期 guard 失敗。沒有建立 event queue、target registers、copy state 或 mutable payload memory 模型。

發布前核對23個 transitive Python dependencies 與 GitHub main blob identity。完整重播仍需固定 APP、本機候選 carriers／HEX、34個 sidecars、saved reader、raw SDK header 與 LLVM Xwchc sources/vectors；只有 clone repo 不足以完整重播。無下載、安裝、服務啟動或候選來源上傳。

本輪只發布新 checker、ledger、本文，保留原 BIN、舊分析與本機 Git index。下一個缺口是 `C776` 的 stack payload 合約、保存 callback word 的真正 consumers／transport task、global queue與length欄位其他 writers，以及實際 provider 綁定、資料保持、重入與 ownership。
