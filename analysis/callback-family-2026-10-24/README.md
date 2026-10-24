# 回呼表與取消路徑

[English](readme.en.md)

新增 [C/C++ 原始碼](../../src/native/receive/callback_table.c)：原廠 `901A–9124` 共 **266B／102 指令／20 架構區塊**。C11／C++17 的 244 個非控制 bytes 與 8 個具型別控制轉移，經純資料原位址編碼後與原 BIN 全部相同。[原生核對](evidence/standalone-trial.json)

## 已確認的靜態行為

- `9070` 是跳回 `9026` 的共用迴圈，並非獨立函式；frame 入口為 `901A`、`907A`、`90B0`。
- 原 `9034/908C/90B2` 的 AUIPC 表達式同指 `2000BE08`；槽距 12B、掃描上限 15。
- `901A` 依事件位元挑槽，讀取 callback 與 payload。flag 為零時先清除槽位 +4／+8，再透過 A3 呼叫；保留原 frame、共用還原出口與 then-live S1 運算。
- `907A` 以值 0／長度 180B 參數呼叫表項 `40048`，將原 `901A` 位址傳給表項 `40080`，把回傳 A0 低 byte 存入 GP+166。
- `90B0` 找第一個 callback 相符槽；payload 非零時呼叫表項 `40068`，清除槽位 +4／+8，再以 GP+166 和 16-bit 事件遮罩經 `4005C` 間接尾跳。無相符槽的路徑回傳 A0=1。

## 推論與限制

以上配置與 WCH SDK 的 memset／task registration／message deallocation／stop-task 預設表項相符，因此推論為 **15 槽回呼事件表、初始化與取消處理**。表項位址不是函式入口；沒有取得實機指標、installed ROM 身分或 ABI 證據。[對照](rom-profile-correspondence.json)

`17C38` 的真實未解析參照已綁到 `90B0` 的原 22B 入口；完整 266B 區域一起連入。新部分連結元件為 **2616B code＋456B data，244 個非零 FUNC、9 個入口 alias、225 RELA、17 個直接 UND**；所有前一階段 2350B code／456B data 與 62 個非零向量綁定保留。[證據](evidence/native-c.json) · [依賴清單](pending-providers.json)

目前 `src/` 有 87 個 C/H；原始與整理版 code 來源比對 120 組／240 物件，指標資料另有 2 組／4 物件，共 **122 組／244 物件**。這是來源投影及原始指令證據，不是完整韌體行為驗證。元件仍為 VMA0 ET_REL，原始 AUIPC 配置、完整啟動／IRQ、硬體／記憶體／ROM 與 BLE OTA 尚未證明。

## 後續與功能候選

下一個直接依賴為 `1798A`；保存的 [有界反組譯](next-1798a-frontier.json) 包含 `1787C` 呼叫。最後一列只剩 2B 卻標示 4B，已排除並記錄；不把其後另一個 frame 當作同一函式。值得探索的新功能是唯讀回呼佇列診斷：槽位占用、待處理事件遮罩與取消狀態。尚未加入韌體，須先證明記憶體 ownership、穩定快照與 resident ABI。

本輪不執行目標／HOST model／ISA 模擬，不操作硬體、不產生 BIN、不 commit／push。[完整建置收據](evidence/integration-build.json) · [匯出來源](publication-provenance.json)
