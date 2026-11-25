# v4.1.60 佇列呼叫點：欄位寬度與返回合約

2026-11-25，僅分析本機原廠 `ID-2966-V4.1.60-decoded.bin`，76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。未執行韌體、未連接設備。GitHub 僅用於發布文字成果。

## 原指令與結果

以 radare2 RV32 離線解碼並以小型 RV32IMC 指令解譯器重跑 `0x12bc8..0x12c24`：

| 位址 | 指令 | 可確認的合約 |
|---|---|---|
| `0x12be8..0x12bf2` | `lhu a6,0(s0)` 與非零分支 | 依首 halfword 判斷槽位佔用，掃描 32 個 12-byte 槽位 |
| `0x12bf6` | `sh a0,0(s0)` | ID 只儲存低 16 位；`0x10000` 和 `0xffff0000` 都留下零標記 |
| `0x12bfa` | `sb a2,2(s0)` | metadata 只儲存長度低 8 位 |
| `0x12c02..0x12c0c` | 讀取 `[0x4004c]` 並 `jalr a5` | A0 是槽位 `+3`，A1 原值不變，A2 保持完整 32 位；長度 `0x100` 的 metadata 是 0，但呼叫點 A2 仍為 256 |
| `0x12c06`、`0x12c0e` | `mv s1,a3`、`sb s1,11(s0)` | tag 在 provider 返回後才寫入，使用返回時的實體 S0/S1 |
| `0x12c12..0x12c1a` | 恢復堆疊與 `ret` | 在 SP、堆疊內容及 S0/S1 被保留的條件下，caller-saved 暫存器被改寫仍能正確寫入 tag 及返回 |

這些寬度在既有 [`ring_insert.c`](../src/native/receive/ring_insert.c) 已有表達；本次新增的是直接針對原 BIN 的邊界驗證，沒有增加重建 bytes 或提高覆蓋率。

## 重現與驗證範圍

```powershell
python analysis/test_v4160_zero_id_queue_cpu.py
python analysis/test_v4160_queue_call_contract.py
python -O analysis/test_v4160_queue_call_contract.py
```

新增腳本枚舉全部 32 個首空槽，搭配 7 種 ID 和 7 種長度（0、1、8、255、256、257、`0xffffffff`），共 1568 個呼叫點案例。每例在合成 provider 位址停下，確認所有 queue bytes、A0/A1/A2、返回位址及 tag 尚未寫入；不執行 provider，也不依大長度進行複製。

另有 224 個合成返回案例：不模擬 provider 記憶體副作用，保留 SP、S0/S1 和堆疊，刻意改寫全部 caller-saved 暫存器，再從 `0x12c0e` 執行原指令，檢查 tag、整個 queue、SP 與呼叫者的 S0/S1 恢復。49 個滿佇列案例確認直接返回且未寫 queue。記憶體中的負向對照把 `sb a2` 改成 `sb a1`，必須被 metadata 檢查抓出；原始 BIN 不變。

一併發布既有 `test_v4160_zero_id_queue_cpu.py` 作為自包含依賴；其原有 32 組零 ID、消費 guard、重用、滿佇列與分支變異檢查也通過。該解譯器只支援本切片所需指令，遇到未支援指令或未映射存取即失敗；不是完整 CPU 或周邊模擬器。

限制：provider 的實際身份、長度解讀、返回與暫存器保留、副作用及中斷競爭仍未知。合成返回不證明真實 provider 遵守 ABI。任意 32-bit 參數只驗證此函式邊界，不證明實際上游能產生那些值；不能據此推論實機越界或功能成功。下一步可把實際接收入口的長度 guard 與此呼叫點連接驗證，進一步區分上游可達值與單函式邊界值。
