# 原始 ADC 設定與 callback 相依閉合

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

這份來源分析只讀原始 ID2966 V4.1.60 與既有來源 ELF。新範圍合計 386 bytes／148 列，另重讀既有 callback 364 bytes，以及上一輪 `0x188E2/0x19160` 的 106 bytes。沒有執行韌體、CPU／ISA／ESIL 模擬、HOST／MMIO 測試、編譯、連結、BIN 或網路操作。

`ledger.json` 保留完整位元組與操作數。解碼器沿用封存來源，僅增加實際遇到的標準 32-bit ORI／SLL／AND／SLTU 欄位；其編碼由同 case 的官方 `riscv-opcodes` 三份節錄支持，MUL 沿用既有解碼。節錄 hash 不是完整檔案 hash，也不是不可變 commit。保留的 radare2 靜態反組譯文字經另一個 parser 逐欄核對全部 148 列；未保存或使用其 ESIL 字串，沒有生成 opcode。

| 原始入口 | 右界不含 | bytes／列 | 邊界依據 |
|---|---|---:|---|
| 1892E | 18986 | 88／37 | 直線區段至 18984 RET |
| 18986 | 18996 | 16／7 | 兩條分支匯入 1898E store、18990 RET |
| 18996 | 189AE | 24／10 | 兩條分支匯入 189A0 store、189A2 RET |
| 189AE | 18A66 | 184／64 | 兩條 channel 分支與三條 sequence 分支，RET 189FC／18A44／18A64 |
| 18A66 | 18A6E | 8／4 | READ32、兩次 shift、18A6C RET |
| 18A6E | 18A8E | 32／12 | 兩條分支匯入 18A80 store、18A82 RET |
| 18A8E | 18A98 | 10／4 | READ32、AND、非零布林化、18A96 RET |
| 18A98 | 18AB0 | 24／10 | 兩條分支匯入 18AA2 store、18AA4 RET |

每個範圍的所有列都可由入口到達，分支目的均在本範圍，沒有呼叫、未知間接跳躍或控制流程迴圈。向前／向後的匯合跳躍不是循環。邊界由實際 CFG／RET 得出，不以「下一符號」或原 FUNC 大小盲截。可選 ELF 只核對這八個位元組子集；不代表全 ELF 或已安裝韌體的來源證明。

`0x1892E` 的 14 次存取順序如下。B 是入口 A0，C 是入口 A1；W 是 READ32，U8 是 READ8。每個讀取都是當時的新值，不先快照整個 config，也不提前合併讀取：

1. W(B+4)，W(C+24)，W(C+0)，W(C+28)，W(C+4)，WRITE32(B+4)。
2. W(B+8)，W(C+12)，W(C+16)，W(C+8)，WRITE32(B+8)。
3. W(B+44)，U8(C+20)，WRITE32(B+44)。

三個寫值按 32-bit 截斷：`(old4 & E0F0FEFF) | C24 | C0 | C28 | (C4 << 8)`；`(old8 & FFF1F7FD) | C12 | C16 | (C8 << 1)`；`(old44 & FF0FFFFF) | (((U8(C20)-1) & FF) << 20)`。config word 沒有另加欄位遮罩；高位元不可任意丟棄。byte20 先減一、再遮罩 FF、最後左移 20；例如零會變成 FF 再左移，不能把它當成只有四個位元的數量欄位。B/C 重疊時，前面的 store 可能改變後續新讀取；這個來源順序必須保留。

實際 caller `0x19896` 傳入 A0=`0x40012400`、A1=當前 SP+32。舊 0x8520 限定清零路徑先清 32 bytes；caller 再令 config words 0／4／8／16=0，12=`E0000`，byte20=1，24／28 保持零。這依賴舊清零路徑的對齊、存取及無別名前提，並非單憑 C 型別或推測 offsetof。對應三次寫值為 `old4 & E0F0FEFF`、`(old8 & FFF1F7FD) | E0000`、`old44 & FF0FFFFF`。

其餘 helpers 的來源效果：18986 對 B+8 設／清 bit0；18996 對 B+8 設／清 `00500000`；18A98 對 B+4 設／清 `04000000`；18A6E 固定對 `40012408` 設／清 `00800000`；18A8E 回傳 `(READ32(B)&A1)!=0`；18A66 做 **32-bit** 的 B+76 新讀取，再取低 16 位。189AE 的實際 caller 已重設 channel16／sequence1／sample7，選到 B+12 的 shift18 讀改寫與 B+52 的低五位改為16。通用其他分支的原始列與 CFG 均保留，沒有聲稱任意越界 channel／sequence 的實體行為已驗證。

至此原 callback 的 13 個直接呼叫皆有有界來源契約，包含舊 8520 的特定路徑、兩個 RCC helpers、188E2／19160 及本次八個 leaves。這些 leaves 都不寫 RA／SP／S0–S11／GP／TP。若原入口 SP 對齊、整個 144-byte 區間（128-byte callback 加最深 16-byte 子 frame）有效且不 wrap、不與 code／MMIO／需保存的 config word52 別名，存取正常完成且沒有非同步暫存器／堆疊／code／config 更動，則 **正常返回路徑** 會還原入口 SP、RA、S、GP、TP。poll `198C6..198D6` 沒有 timeout；還需某次狀態讀取觀察到遮罩 `0x2` 非零，才能推出有限次返回。

不能宣稱完整暫存器或 MMIO 還原：189BE 會寫 A6，值是 `4001240C` 修改前的新讀取，之後沒有覆蓋它。RCC `4002100C` 的 mask200 被兩次 reset-like 呼叫清除，callback 並未快照／還原此位置；它只快照／還原 RCC+4 與 +18。原 A7 則在整個 callback 與全部受限相依都沒有讀／寫，正常出口保持入口值。

針對新 1892E native 候選可能多出的 A2／A6／A7 clobber，來源只支持有限的 caller 證據：從 1989A 到 198B2 前，含介入的 18986／18A98／18A6E，沒有 A2／A6／A7 讀取。198B2 先把 A2 寫為1，之後 189DA 才使用；實際 channel16 路徑 189BE 先寫 A6，189CC 才讀。因此早期 A2／A6 clobber 在這個 caller、無非同步暫存器觀察的條件下會被覆寫。A7 沒有後續覆寫，新 clobber 會逃逸至原 callback 出口。這不是 PSABI 推測、全 ABI 證明或 102-byte 候選的 promotion。

同樣有界檢查原 A3／A4／A5 scratch 的出口差異：A5 在 18986 先做新 LW，1898A 才讀；A4 在較早 18986 不被讀，實際 A1=1 的路徑於 18A9C 先 LUI，18AA0 才讀；A3 在 18986／18A98 不被讀，實際 A0=1 的路徑於 18A7A 先 LUI，18A7E 才讀，且 caller 198B0 又令 A3=7。A0／A1 也先在 1989C／1989A 重設。因此只就這個 caller 的正常、無非同步觀察路徑，1892E 出口 A0–A6 的數值差異會在使用前被覆寫；不允許改變該 callee 內部的存取或寫值。

不能忽略 T 暫存器：完整受限來源中 T0／T2／T3／T4／T5／T6 都不被讀／寫，正常出口保留入口值。T1 僅在 8520 寫為15、8524 用於早期比較，之後沒有讀／寫，正常出口值仍是15。新 native 候選即使修正 A7，也必須另行檢查所有逃逸的 T 值；這些資料不能讓編譯器任意改寫 T0 等暫存器。

config word52 也只能得到本次 callback 的條件式不變：該完整 word 須與上述 144-byte 堆疊與固定 MMIO 寫入集合分離，且沒有其他干擾。這不提供其入口值，不證明整個初始化／後續 runtime 生命期，亦不識別已安裝 resident。暫存器位址與既有官方 WCH header 可支持 ADC／溫度路徑的語意候選；板上晶片、外設實際副作用、BOOT、BLE OTA 與可刷寫性仍未證明。

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin --image-elf /absolute/ADDRESS-WITNESS-ONLY.elf
```

預設僅中繼資料，actual FW／ELF flags 皆為 false。明示 FW 時核對整檔 76800 bytes 與 SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，重讀原始列，並拒絕六個只改單一操作數的實際位元組反例：mask、config byte 位移、byte 減一、左移20、channel 分支目的、非零比較來源。還檢查缺少 FW 的 ELF 模式及錯誤 FW 會被拒絕。舊 94-case 矩陣不重跑。所有結論都是靜態來源證據，不是實體執行結果。
