# v4.1.60 TX 尾段 selector 選擇與返回合約

2026-11-26。原廠 APP `ID-2966-V4.1.60-decoded.bin`：76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。接續[本機 fill／header 投影驗證](v4160-tx-header-roundtrip.zh-TW.md)，本次離線執行 `0x16bfa..0x16c6c` 的原指令；不執行外設、未知 provider 或真實傳送。

## 原指令結果

尾段依序從 stack `sp+12..14` 讀 selector。入口先前寫入的三個 byte 為 `0x30、0x40、0x50`；本測試合成保留這些值，不假設未知 provider 必定保存它們。

1. `0x16c02..0x16c12`：以當時的 row `+11` byte 與 selector 呼叫 `0x16994`。返回 bit 3 設定時才嘗試下一個 selector；三個皆設定位則返回 4。
2. 第一個 bit 3 清零者，在 `0x16c14..0x16c2c` 重新讀 row `+2` 的長度及 `+11` 的 tag，再呼叫 `0x168de(tag,(selector+1)&255,sp+16,(length+5)&255)`。
3. `0x16c30..0x16c3a` 再讀 tag，呼叫 `0x1693e(tag,selector,8,8)`。
4. `0x16c3e..0x16c50` 再讀 tag，呼叫 `0x16994(tag,selector)`，最後返回 `(result & 0x70) != 0 ? 4 : 0`。

找到第一個可用 selector 後只有這一輪，不會因最終 mask 非零再試其他 selector，也沒有在這個尾段等待 ACK 的迴圈。上述兩個中間呼叫的返回 A0 被後續 row load 覆蓋；最終返回值由最後一次查詢決定。返回 0 不等於硬體傳送或 ACK 成功。

`0x16c52..0x16c60` 從既有 64-byte frame 恢復 RA、S0–S3 和 SP 再返回。這與既有 [tagged_dispatch.c](../src/native/receive/tagged_dispatch.c) 一致；本批補上原指令的行為檢查，沒有宣稱新重建函式。

## live row 不是入口 snapshot

tag 在每次呼叫前重讀；長度在選到 selector 後重讀。入口原本的 0–8 檢查不能在未證明 row 穩定時，無條件約束這個較晚的值。

新增的 6 個合成 callee-side row 改寫案例，在查詢返回後更改 tag／長度，之後再次改變 tag，確認後續原指令使用新值。長度 probe 為 0、8、9、250、251、255，對應傳入 `0x168de` 的第四參數 5、13、14、255、0、4。這只是指定記憶體變動下的數值合約，不證明真實 caller、provider 或中斷會造成這些變動，也不執行這些長度的傳送。

## 重現與測試範圍

```powershell
python analysis/test_v4160_tx_tail_cpu.py
python -O analysis/test_v4160_tx_tail_cpu.py
```

需要 Python 標準庫、原 BIN 與已發布的同目錄 `test_v4160_zero_id_queue_cpu.py`。新腳本從自身位置定位 BIN，可從其他工作目錄執行。

```text
PASS: 4096 busy/final/tag combinations; 27 length/selector boundaries; 6 live-row changes; 2 mask mutations; restored caller state
```

4,096 組為三個 selector 的 bit 3 設定組合（8）× 最終狀態低 byte（256）× tag（2）。另有 3 個首可用 selector × 長度 0–8，共 27 個邊界案例。狀態的額外高位只是 mask 邊界 probe，不主張被呼叫函式實際可返回這些值。

測試起點是未知 copy provider 返回後，row 指標、frame、selector bytes 與保存的暫存器皆為合成 fixture。每個直接呼叫在進入目標位址前停止；測試核對目標和完整參數，再指定返回值並刻意改寫 caller-saved 暫存器，保存 SP／S0–S3／stack。因此沒有執行 `0x16994`、`0x168de`、`0x1693e` 的函式體，也不把它們稱為未知 resident provider。

逐例檢查精確呼叫順序、次數、返回值、RA/SP、S0–S3 恢復，以及除明示合成 row 變動外無記憶體寫入。所有情境均需正常返回、SP／S0–S3／frame 保持有效；這些不是實機 ABI 或中斷安全證據。

共享有限 CPU 增加本切片所需的 LBU、ANDI、C.ANDI、C.ADDI4SPN、SLTU 與 JAL 解碼，預設 queue PC 範圍不變；新子類只允許本 TX 尾段。兩個記憶體複本負向對照改錯 bit 3 檢查與最終 `0x70` mask，必須被呼叫紀錄／返回檢查抓出。一般與 `-O` 通過；既有 queue、TX header、transfer-chain、ingress、NV caller 測試也重新通過，原 BIN 未變。

本批沒有增加 C/C++ 重建 bytes 或重算覆蓋率。接續可離線串接本尾段的直接 callees，區分它們的傳輸等待與此處的 selector 選擇；provider 身分和實機效果仍待證。
