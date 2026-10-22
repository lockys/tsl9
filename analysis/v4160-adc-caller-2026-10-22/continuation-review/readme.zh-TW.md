# Callback 返回後的兩份 resident 初始化來源

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本次只做靜態來源讀取，從已封存的 228-byte initializer 繼續追查 `entry+CE`：V1.40 的 `43DD8→43BCA`、V1.31 的 `43D4C→43B3E`。每份候選均保留 **8 個完整有界函式、1,056 bytes／359 列**，不是先前的 96-byte 前綴。既有原始 HEX、slot400A4 與 startup copy mapping 是候選來源證據，不能證明硬體已安裝這份 resident。

| 用途候選 | V1.40 範圍（右界不含） | V1.31 範圍 | bytes／列 |
|---|---|---|---:|
| post-init 主流程 | 43BCA..43CDA | 43B3E..43C4E | 272／87 |
| heap 初始化 | 43190..43200 | 43104..43174 | 112／36 |
| heap list 掃描 | 4316C..43190 | 430E0..43104 | 36／13 |
| 固定 word 清零 leaf | 43326..43330 | 4329A..432A4 | 10／3 |
| table 初始化 | 440B6..44156 | 44022..440C2 | 160／61 |
| 配置器 core RAM view | 20000040..20000110 | 相同數字 view | 208／72 |
| byte fill RAM view | 2000039C..200003CA | 相同數字 view | 46／14 |
| free RAM view | 20000110..200001E4 | 相同數字 view | 212／73 |

所有列都能由其入口在「巢狀呼叫正常返回」的 CFG 上到達；直接分支都在該 body 內，所有直接呼叫均落入表中已讀來源。多條返回路徑與回邊皆保留。heap list、配置／free 與 table 流程有迴圈；未知記憶體、list 形狀或 callback 不允許宣稱必然終止。邊界由實際 CFG／RET 得出，不使用下一個符號大小盲截。

`ledger.json` 保留每列 raw bytes／操作數及 view→原始 flash 地址。新 RAM view 來源為 `402F0→20000040`、11,904 bytes；舊版為 `402B0→20000040`、11,828 bytes，數量由既有 inclusive word copy contract 算出。actual 模式讀完整已 pin HEX，使用既有嚴格 parser 驗證 checksum 與 segment，不補洞；每個請求範圍都必須完整存在。兩份 slot400A4 分別為43D0A／43C7E，配置基底分別為2000323C／200031EC；亦重讀舊 initializer 全部456 bytes 核對來源連接。

全部718列的位元組及界線另與有界 radare2 靜態輸出核對；646列標準指令的每個操作數由獨立文字 parser 比對。72列條件式 Xwchc QK load/store 使用已 pin 的官方 TableGen 格式；radare2 對它們顯示的 FLD／FSD 名稱沒有被當成語意依據。本次沒有新的解碼格式，也沒有執行／保存 ESIL 字串、CPU 模擬、opcode 生成、編譯、連結、HOST 矩陣、硬體或網路操作。

令 C 為候選配置基底。主流程先清 C−4、C+68、C−12 三個 word，byte fill 清 `[C−36,C−16)` 的20 bytes 與 `[C−80,C−40)` 的40 bytes，之後建立 heap metadata。它只讀一次 config+21 的 byte x，計算 `n=(3*((x>>2)+(x&3))+14)&255`，存 byte 至 state+2，再以 A0=`6*n+576`、A1=1 呼叫配置器，將結果寫 C+64。零結果直接返回 epilogue；因此外層 initializer 的正常回傳0不代表配置成功或所有功能可用。

非零配置結果的後續 fill **重新讀 live S0+2** 計算大小，不能把它折疊成先前 n；配置／callback／別名可能使兩次讀取不同。它再建立 pool/table 指標，呼叫小型清零 leaf 與 table initializer，並將 code 位址數值43330／433B2／433B2（舊432A4／43326／43326）寫入動態 table；函式指標用途是脈絡推論。這些常數是 store 的值，**不是向這些 flash 位址寫入**。table 位置依 fresh index 與動態 pointer 計算，須另證明 heap／table／config／stack 不互相覆蓋。

byte fill 完整來源會讀取數字位置4002420C、寫零、經過 `fence.i` 指令列，在目的地與 count 非零時逐 byte 寫入，最後寫回先前讀值。正常非零路徑的 A0 成為 end pointer，不能直接套用標準 C `memset` 的返回 ABI。這只是指令與數值位址的來源契約，不代表外設副作用或實體中斷控制已驗證。

尚未閉合的三個 computed call frontier：

| Frontier | V1.40／V1.31 call PC | 原始指標來源與參數 |
|---|---|---|
| 配置失敗通知候選 | RAM200000A0／相同 | fresh READ32(C+52)；A0=1，A1=live A1 OR `(rounded16 size<<16)`；A2 在所有可到達此呼叫的來源路徑均未先寫，仍是 ambient entry A2 |
| 第一個 table callback | 440EA／44056 | fresh READ32(C+56)；A0 來自 C+8，A1=1，A2=live SP+12 的可寫輸出 word |
| 迴圈 table callback | 44152／440BE | fresh READ32(live S0+60)；只有先前 callback／呼叫保存 S0 才能把它化成 C+60；A0/A1/A2 來自其後的新讀取與索引 |

配置器在 C+52 為零時跳過該 callback。table initializer 先測 C+8、+56、+60；其中任一為零可走 early return，但不能假設它們的實際值。第一個 callback 可寫 SP+12，也可能改變未知記憶體／暫存器；其後任何以 live S0/S1 算出的位址都須保留保存條件。沒有執行這些 callback，也沒有用 SDK 欄位名稱替代實際 ABI 證據。

所有讀到的 body 都沒有自有 GP 寫入。主流程保存／還原 RA、S0、S1；table body 保存／還原 RA、S0、S1、S2；配置器保存／還原 RA、S0；heap-init 保存／還原 RA。這些是來源內的 store/load 關係，整段 SP／S／GP 保存仍需要 computed callbacks 的返回、stack／register 契約、正常存取及無干擾。已讀的 post-callback 巢狀 frame 最深需要主流程入口下64 bytes，或 initializer 入口下80 bytes；這不包括已返回的 ADC callback，也不是未知 callback 的堆疊上限。

已識別固定寫入並不直接寫 C+52；但 heap metadata、allocation fill、table stores、callback 輸出及 callback 本身都是動態寫入來源。因此只能在它們與整個 C+52..55 word 分離、callback 不修改該 word、沒有其他非同步干擾時，條件式延伸這一段的「入口值不變」。這不證明其入口為零、整個初始化或後續 runtime 生命期，更不證明已安裝 resident、完整 ABI、OTA、BOOT 或可刷寫性。

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --candidate-root /absolute/wch-resident-candidate-2026-10-21
```

預設僅中繼資料，actual HEX／body read flags 皆為零。明示 candidate root 才讀兩份原始 HEX、16個新 body 及兩個舊 initializer，並拒絕每候選五個實際單一操作數反例：fill count20、state 位址、config+52 load 位移、config+56 load 位移、SP 還原量。checker 不寫檔，D／P root 皆可解析；可共用既有 D reference 目錄，不複製或補齊來源。Git Bash 先前的沙箱拒絕沒有重試。
