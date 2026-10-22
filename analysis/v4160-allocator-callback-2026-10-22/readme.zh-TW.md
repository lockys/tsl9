# 配置 callback 欄位來源與 OTA 回覆 frame 實驗

[English](readme.en.md)

本輪繼續處理原機相容性所需的指標／callee／記憶體契約。**沒有新 BIN；已發佈的77,824-byte source-wired實驗映像與568-byte元件保持不變，仍未驗證可刷寫。**

## 已確認的進展

| 項目 | 實際證據 | 尚未證明 |
|---|---|---|
| 配置 callback 的 writer | 兩候選114B／41指令 BLE-init prefix，64-byte copy至2000323C／200031EC；+52正好是20003270／20003220 | 呼叫當時的值、後續writer、lifetime、已安裝ROM |
| 候選 SDK 型別 | 兩份實際 header經RV32 C編譯：staCB offset52、readFlash56、writeFlash60、config64 | 原機callback的實際參數／副作用 |
| 原 App 設定 | 實讀308B；32選定欄位、23標準store；SNVAddr數值08077C00、無明示SP68..71 store | 未知call／alias下是否真零、完整NV範圍或free Flash |
| C生命週期實驗 | 568→560→556B；最後188指令／48frame，移除一對S8 spill | 原530B配置與完整ABI |
| 回覆物件 | 最終真獨立SP10/11物件，不與savedS7@12重疊；共同原7個保存位置相同 | 相對entry−38仍不等於原−36；數值差異是否可觀察 |

原caller在14098後只恢復自身RA／S0..S3並返回，沒有自己的S7恢復。因此把回覆直接指向新S7保存槽會讓損壞越過caller，不能當成指標修復；目前沒有採用這種做法。原保存順序與新順序也不同，共同保存位置相同不等於完整frame契約相等。

## 程式與重驗

- [有界 C/C++ 實驗](../../experiments/tsl9-v4160-ota-reply-frame/README.md) 與[實際編譯／replay](implementation/README.md)。只試兩個有依據的 source profile，沒有第三輪旗標掃描、opcode patch、假 size、借用spill物件或新映像連結。
- [獨立 frame／source delta 審查](frame-review/README.md)：實讀舊568與新556，保留caller／UID／指標未知界線與兩個ELF反例。
- [候選 callback writer](callback-review/README.md)：兩候選各114B prefix、30B zero helper、8B initializer tail；每候選12個相鄰讀取pattern、零相鄰直接store仍不排除bulk／computed writer。8個原始欄位反例。
- [原 App／SDK設定欄位](config-review/README.md)：兩個40-byte資料-only layout object與5個只改immediate的有效反例。預設metadata與明示實檔讀取／freshcompile分開。

Python與POSIX shell介面可攜；目前native證據是Windows pinned LLVM，不宣稱Linux／macOS／CI通過。本輪沒有重跑未變的HOST演算法，也沒有RV32／ISA模擬、BLE／UART／CAN／Flash、廠商API或裝置識別資料傳送。

## 後續條件與功能候選

先追查原App config建立途中未知call／間接store的可寫範圍、候選allocator其餘路徑與staCB生命週期；新C尚須安全消除一個保存負擔或合法安排獨立物件，不能把數值指標一致當成全部ABI證明。實體板型、原機ROM／BOOT／RAM／IRQ、Flash／NV所有權與BLE OTA接受／恢復仍待證。

值得增加的是離線更新前檢視工具中的 **NV／ROM條件摘要**：把原碼明示SNV數值、映像增加區域、候選型別來源及尚缺條件同時顯示。這是提案，尚未實作為原機功能，也不能把摘要當成刷寫許可。
