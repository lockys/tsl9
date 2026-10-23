# 原排程器的離線 C/C++ 重建

[English](readme.en.md)

完整 `9124–9250`，共300B、115指令、28個架構區段。相同 [C 來源](src/scheduler.v1.c) 已實際編譯為 C11／C++17；11筆真實控制重定位做純資料原位址編碼後，300B全部與官方 ID2966 V4.1.60 BIN 相同。

- 15個工作槽，基底2000BE08、stride12；byte flag／callback word／argument word位於0／4／8。
- 零A2初始掃描滿15槽後，仍進入一般搜尋路徑，沒有自行改為提早失敗。
- 保留先取低32bit的乘1000，再做unsigned除625；不能據此宣稱時間單位。
- C中的可變位移明確取count低5bit；保留low16 mask。跨resident後重新使用實體S-register，不假設索引仍有界。
- 保留40068／40058兩次間接呼叫、40050／4022C兩個tail。其指向與ABI尚未證明。

C負責自由暫存器的常數、運算、遮罩及一般記憶體。SP／S0–S4、含保留暫存器的運算與存取、PC及控制為明確架構介面；不是普通 C ABI 或完整語義證明。

```sh
python3 experiments/tsl9-scheduler/build-v1.py --tool-dir "$LLVM_BIN" --trial YOUR_NEW_TRIAL
python3 experiments/tsl9-scheduler/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-scheduler/build/trial-v1
```

使用既有、釘選的本機工具鏈及官方BIN，不下載依賴。無網路、硬體、HOST模型、ISA或目標程式執行；未新增畸形輸入／負例矩陣。中斷、並行修改、記憶體界限、resident行為、啟動／實體硬體與OTA相容性仍未證明，不能當作可燒錄韌體。

值得考慮的後續功能：被動顯示15個工作槽的佔用率、滿槽次數及註冊／更新結果。這些只是提案，尚未實作或實機驗證。

## 真實物件整合與參考庫關聯

兩種語言實際部分連結5702B程式＋60B表、460 FUNC／423 RELA。原本的 `tsl9_callback_external_9124` 已有真實定義，仍有74個未解析符號。VMA保持0，沒有可執行載入配置或韌體BIN。

100組來源比較／200物件通過；原98組與589個artifact記錄不變。父元件核對精確增加一檔／一單元及其餘producer輸入，不冒稱舊全域manifest收據原樣重播。

```sh
python3 experiments/tsl9-scheduler/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-scheduler/build/graph-v1
python3 scripts/check-scheduler-resident-references.py
```

[本機保留的參考庫關聯](../../analysis/scheduler-2026-10-23/resident-reference-association.json) 對照歷史header的事件設定、工作啟動、週期工作與訊息釋放宣告。V1.31／V1.40候選映像的實際指標值不同；名稱與prototype只屬參考級候選。重建沒有綁入候選地址或實作。參考核對需要保留的本機WCH資料；實機ROM／library身分與resident ABI仍未知。
