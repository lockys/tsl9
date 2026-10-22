# OTA 命令本體的原始來源契約

[English](readme.en.md)

本範圍是官方 ID2966／V4.1.60 的 `0x9C4A..0x9E5C`，530B、169 條原始指令，SHA256 `693eba9e21b786525b457b538d998a997a601ee46327621a2302ede1b2f274c5`。韌體 base=`0x8000`、完整原檔 SHA256=`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。這裡保留獨立 raw 欄位解碼及實際 LLVM 靜態反組譯；它們逐欄核對，不執行或模擬 RV32。

`contracts.json` 是原始指令契約，`instructions.json` 保留所有169列。它們不把舊 HOST 模型的普通 ABI、記憶體副本或 provider 回覆當成原機證據。`source-reconciliation.json` 另外記錄對最終凍結4個 C/H 檔的獨立閱讀核對與身分；這不是 HOST 執行或 native 編譯證明，也沒有宣稱原始高階程式碼已完整還原。

原始入口以 A0=context、A1=完整32位命令、A2=payload、A3=完整32位長度；A6/A7 沒有任何 body 明示寫入。48B frame 依序保存 S0、S2、RA、S1、S3、S4、S5，slot為40、32、44、36、28、24、20。共用 epilogue 從當下 live SP 重讀 RA／S0..S5，再 liveSP+=48、JR RA。未知 callee 若改 SP／frame，不能保證返回最初 RA 或恢復最初 SP。

| 命令 | 必須保留的原始行為 |
|---|---|
| W | 依序檢查 liveGP+0xA9 active、完整長度1026、BE16頁號與 unsigned位址界線；目的 `0x08001000+page×1024`，原BE16頁號0..27通過。非對齊來源先透過不明 resident copy 搬至較低的4B對齊位址。 |
| W 寫入／回讀 | 原9CFC在9D00 call之前增加 S0=offset+256；返回後以live S0/S5決定是否重複。只有 callee 保存相關 state 的前提才固定四次。9D10先LW Flash，9D16後LW live source，每次比較32位、step4；不符回FF，相符要求頁面回覆。 |
| U | 先將active清0，再92F2(payload+1,(length-1)&255)。raw零結果才通過；UID返回後重讀live S0的mode，只有mode1排兩個callback，其他mode仍可回U byte1。body沒有完整長度必須15的比較。 |
| S | 先讀mode並將它與byte1=1存liveSP+12／13，再UID。成功後重新讀live S0的mode。active成功寫入取**UID後live S1**的低8位，不能在任意callee影響下改稱字面1。reply使用當下liveSP+12，而非自動複製的安全陣列。 |
| R | active、完整長度16、UID14 raw零結果通過後才重新讀BE16頁號；沒有W的頁號0..27限制。 |
| E | active、完整長度15、mode0、UID14 raw零結果；先清active，再要求callback8E18／200，然後99E8／400，最後空E回覆。 |

有12個 direct call site、1個 indirect call site及1個最終JR。所有direct call都寫RA，包括 `0x9DF4` 的半字 `693b`：它是 **RV32 C.JAL rd1→9B8E，RA=9DF6**，不是tail。唯一indirect call是9CEC，目標由新建立的0x40000基址+0x4C讀出A5。各站明示參數與RA在JSON逐一列出；其餘A0..A7是實際live／opaque殘值，未宣稱表格涵蓋全部中間raw GPR。

來源審查發現並在凍結前修正了一項實際橋接差異：W 回覆原本只投影 A0..A2，遺漏原碼9D16留下的A3=最後source word、9D08留下的A4=1024，以及A5=失敗offset／成功1024。最終 C 在W兩個回覆邊界補上這三值與mask63。這是選定邊界的改善；例如R的A5高byte位移殘值仍未投影，不能提升為完整raw8等價。native response[2]也不是原liveSP+12/13的位址／alias證明。HOST return-address欄位只做saved-data bookkeeping，沒有執行或完整重現原機JR／改變返回目標。

51項owned RELA核對31個內部控制邊、12個外部直接call與4組HI/LO。唯一記錄的outside direct incoming是14094 JAL rd1→9C4A、link14098；不能由此排除未記錄／computed entries。`owner-addresses.json`只是實際LLVM carrier的驗證資料，不產生provider或numeric alias。

```sh
python3 -B check-source.py --project-root ROOT --firmware OFFICIAL_BIN
python3 -B check-source.py --project-root ROOT --firmware OFFICIAL_BIN \
  --original-object ACTUAL_SOURCE_INTEGRATED_OBJECT
```

預設仍實際讀取官方BIN、重解169列並拒絕8個新consumer相關的單欄位operand反例。只有明確給object才宣稱重新讀取該carrier；預設不依賴舊W build。沒有重跑舊OTA大型HOST矩陣。原碼的overlap copy、ROM、GP/S/SP保存、回覆是否送達、實體硬體、BOOT身分與可刷寫性均未獲證明。這是Runtime寫BOOT區的原始流程，不能當成已證明能把新Runtime刷進自己；逐word回讀也不是整份映像CRC／簽章驗證。
