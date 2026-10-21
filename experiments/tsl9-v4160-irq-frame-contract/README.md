# 原 ID2966 的兩種軟體中斷框架

本工程將原 `8448..8496` 與 `8498..851E` 的兩個有限本體重建成可讀 C11／C++17。它是自己的合成框架資料模型，不是 CPU stepper、一般 ISA 模擬器、真正的硬體 ISR 或可刷寫原生替代品。原 native 工程的相同指令儲存體保留不變。

原始 ID2966 V4.1.60 的 SHA256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；兩個有限來源視窗、29 個 register／offset 與控制操作均綁定獨立 raw-operand proof，並在每次編譯前驗證原檔與 sealed members。

`iq_restore_8448` 不建框架。它先把 a1 設32，以 CSRRS 對 `804` OR32，再從 live SP+0 讀 word 到 a1 並寫 MEPC，之後依序從 SP+4..116 讀29個 word，最後 SP+=128，停在 MRET 邊界。框架的產生者及實體 CSR804／中斷語義尚未證明。

`iq_irq_8498` 先 SP-=128，再依序保存29個 GPR。它以 live `gp+384` 取指標到 a0，將 a1 設為該 slot 地址；原 `84DA JALR` 沒有 NULL guard，link為 `84DE`，控制目標清除 bit0，a0 則保留原指標值。只有明確的合成 callback provider 回傳 RETURNED 才接續恢復；每個 word 都是 callback 後重新從當時 live SP 讀取，沒有使用 entry 快照或把 SP 強行重設。最後 SP+=128，停在 MRET 邊界。本體沒有讀寫 MEPC 或 MSTATUS，也沒有保存 gp。

兩者共同的29-register順序為 `ra,tp,t0,t1,t2,s0,s1,a0,a1,a2,a3,a4,a5,a6,a7,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,t3,t4,t5,t6`，offset4起每項加4。x0、SP、GP不在這個保存序列內；8498沒有明示讀寫offset0／120／124。這不證明原128B框架的完整物件邊界或硬體產生方式。

所有 target 地址保持 uint32 整數，不轉為 host 指標。read／write／CSR／callback／MRET 均由使用者明示的合成 backend 記錄；未提供 backend、未知地址或未能確定的 callback 目標會停止。JALR 的 bit0 即使原本未知也會清零，不能因此錯誤拒絕已知的控制目標。read32 的 partial-known 值可以按 known mask 傳遞到 GPR／MEPC，沒有捏造未知資料。

callback 可變更 GPR1..31、CSR觀測與合成記憶體，必須保持 gpr0 的零值，不能變更模型 backend／counters／budget 等引擎控制資料。這是明示的自身模型介面，不是原 C prototype 或硬體 callee-preserved ABI。callback 改 frame word、SP、GP 或 MEPC 的效果不會被模型回滾。外部 provider 的 HALT／TRANSFER 及未確認的效果保留已發生的前綴。

觀察預算只計 provider observations，不計純位址算術與暫存器資料賦值。因此停止在第一個 store 前仍可能已有 SP-=128；停止在 callback observation 前已可有 RA=84DE。這是有限觀測的分界，不是原韌體的指令配額或實體執行中止機制。MRET observation 的成功確認仍只導致 `IQ_TRANSFER/IQ_MRET_BOUNDARY`，不執行 privilege／IRQ return 或宣稱硬體接受。

```powershell
.\verify.ps1
.\verify.ps1 -Cpp
```

以 MSVC `/W4 /WX` 編譯並執行16組自己的 host 合成情境：兩種框架／CSR順序、live-frame mutation、替換SP、未保存GP、callback transfer／halt、已寫入後失敗、部分已知資料、NULL與bit0未知目標、未知GP／SP、uint32 wrap、預算及8498不恢復MEPC。這些只驗證 C/C++ 契約模型；沒有執行原／重建RV32、沒有ISA模擬、沒有網路或硬體I/O，`physical_IRQ_ABI_proved=false`、`OTA_ready=false`。

獨立來源 audit 還保留其他原中斷入口的完整有限 CFG，包括第一個 MRET／RET 後仍可達的 cold paths。不能拿這兩個 wrapper 的保存方式推廣到所有 IRQ。歷史 V1.31 resident 的 entry／copy／zero／MRET 條件另外列於本輪 `resident-handoff` 證據；reference 的身分、來源洞及先前可能 fault 的 load 均不能由這個模型補證。
