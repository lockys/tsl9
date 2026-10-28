# 傳送呼叫、buffer 交接與條件式回收

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_transmit_handlers.c)

新增三個完整候選 SDK 本體，合計 **3,576 CODE bytes／1,173 指令**。C11／C++17 的原指令、控制重定位與完整 CFG 相符；沒有新增 DATA、假 provider 或執行 target。

|原始範圍（尾端不含）|靜態確認|
|---|---|
|5774E..5784A，252B／78 指令|分別清理 queue head+280、+288；非空 buffer 才呼叫釋放，fresh-read head、恢復 tag 高 byte、推進 next；另清理 frame buffer、可選 slot 與 controller record|
|59042..595B8，1,398B／442 指令|三處遠呼叫指向 RAM20000AC6，均保留原始 incoming record 作 A0；prepared state1 選 queue buffer，其他狀態選 record.frame buffer|
|595B8..59D3E，1,926B／653 指令|保留狀態／helper／head／prepared／marker 條件、buffer 釋放、counter 與 queue-head 更新；正常出口是恢復 frame 後 tail 到567BE，不新增 return|

三處遠呼叫為 **59212、59284、59594 → 20000AC6**。在590BA／590C4或591A2／591AA寫入 record+12與+21的兩個 header bytes，再於590D4將 buffer 指標寫至 global2000353C所指 context 的 word+112。這解釋先前首個完整片段沒有 copy 的路徑；**尚未證明此指標交接的 MMIO／DMA／無線意義**。

條件式 queue 消費路徑在5983C更新 head+280。完整 CFG 確認以下條件支配該更新：status byte2000351A的bit0清除、560B2回0、head非空、prepared非0、node.marker低bit清除；並先在59822寫入 `uint16(tag | 0xff00)`，59828把**當前 node.buffer**交給20000110。fresh-read head後讀 next，另遞增record+68 halfword，條件式遞減record+420 word。這些是數值與資料流事實，**不是實體 ACK／CRC 成功證據**。split由marker81變01仍保留低bit1；whole marker0也必須符合其他條件才可走此路徑。

清理函式5774E會分別處理兩個 queue，沒有明確清零 tail；slot39／38／40／41僅在不等於255時釋放。回收傳入當前 buffer 值，**自訂 allocator／buffer 生命週期仍待證明，不能直接改成假定的標準 free**。

新單元有54個普通匯入：12個由真實既有本體解析，**42個保留為真實 UND**，另有599F6／59BEC兩個間接 callback 未閉合。相同的 C/C++ 部分連結含 **48,720 CODE＋412 DATA bytes／16,883 指令**、3,595正大小FUNC、2,913重定位；原父 bytes、globals、重定位角色保留且無重複原始 CODE。未完成 readonly／RAM／MMIO／callback 與實體事件綁定。

APP正式來源仍 **162份、73,478／76,800B（95.67% 靜態 byte 覆蓋）**，不是功能完成率。本候選尚未納入正式 src、連入 APP 或最終原位址配置；既有4B啟動來源缺口保留。**沒有新 BIN；尚未證明原硬體 ROM／RAM／IRQ／Flash／OTA 相容性**。沒有 target、HOST model、ISA、硬體執行或廠商 API 存取。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的診斷候選](feature-candidates.json)

固定本機輸入與 LLVM 齊備時，唯讀重播：

```sh
python3 experiments/tsl9-resident-transmit-handlers/verify-v1.py --tool-dir "$LLVM_BIN"
```
