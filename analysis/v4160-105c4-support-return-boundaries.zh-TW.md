# V4.1.60：105c4 擴充連結的七個支援區段邊界

此有界靜態分析接續 `analysis/v4160-105c4-28-section-provider-local.zh-TW.md`：先前連結比較了 28 個選段、400 bytes，但這些支援區段並不都包含完整函式。這裡只追查七段末端與部分已知後繼；**不是新的 28 段連結、可達性、ABI 或整圖驗證**。

參考 BIN 為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。以下採假設的線性基址 `0x8000`，以離線反組譯檢視指定窗口；解讀以所列位址是指令邊界、路徑實際進入且相關存取成功、不發生例外為前提；`ret` 只表示跳至當時 `ra` 指向的位址，不保證該位址有效或等於原呼叫者的返回位址。

| 選段半開區間 | 段末控制流與邊界 |
|---|---|
| `[0x81aa,0x81b0)` | `lbu a0,167(gp); ret`；不是順序落到 `0x81b0`。`0x12a10` 的直接呼叫正常返回時到未選的 `0x12a14`。 |
| `[0x820c,0x821e)` | `a0` 無號大於 2 時直接返回；否則向 `gp+193+a0` 寫零後返回。不是順序落到 `0x821e`。`0x1075e` 呼叫正常返回時到未選的 `0x10762`。 |
| `[0x9124,0x913a)` | 建立 stack frame 並以 `auipc/addi` 計算 `0x2000be08`；末尾順序進入未選 `0x913a`。 |
| `[0xd272,0xd288)` | 從 `[0x40048]` 載入 `t1`，以 `auipc/addi` 計算 `a0=0x2000bf48`，最後 `jr t1`；不是順序落到 `0xd288`，間接目標未知。 |
| `[0x1074c,0x10758)` | `0x10754` 呼叫 `0xd272`；只有間接目的地最終遵循原返回位址正常返回，才繼續未選的 `0x10758`。 |
| `[0x107c0,0x107c6)` | 設 `a0=0`，以無連結跳轉到已選 `0x1074c`；不是順序落到相鄰的 `0x107c6`。 |
| `[0x12a08,0x12a14)` | `0x12a10` 呼叫已選的 `0x81aa`，正常返回才繼續未選的 `0x12a14`。 |

例如，`0x913a` 的 `39e6` 為 `bnez a2,0x9188`，未跳轉時接 `0x913c`；`0x12a14` 的 `11e5` 為 `bnez a0,0x12a20`，未跳轉時接 `0x12a16`。`0x12a1c` 的 `6311f704` 對 `a4 != a5` 跳至 `0x12a5e`；`0x12a22` 的 `ef50cfff` 呼叫未選的 `0x821e`，若正常返回到 `0x12a26`，其 `05cd` 再依 `a0` 分支。`0x10758` 的 `efa05f9a` 呼叫 `0xb0fc`，後續 `0x1075e` 呼叫 `0x820c`、`0x10762` 呼叫 `0x10032`，均須各次正常返回才能繼續。

對應來源分別見 `src/native/receive/queue_small_providers.c`、`src/native/receive/scheduler.c`、`src/native/receive/callback_providers.c`、`src/native/receive/feature_callback.c` 和 `src/native/receive/record_dispatch.c`。後續選段不能只追 relocation 目的地，還需考慮順序 fallthrough、間接跳轉及返回；PC-relative 固定編碼也依賴選定地址。例如，`0x12a08` 先寫 stack 再由 `0x81aa` 讀 `[gp+167]`，若位址重疊，保存動作可能影響讀值；不能假設兩者獨立。這些觀察不能確定呼叫者完整性、資料 owner、暫存器保存或動態可達性；原 selected-link 丟棄 `.llvm_addrsig` 和部分區段，來源仍含 inline assembly。

本次未執行、模擬或燒錄目標；未改正式來源或正式 guard。上述判讀是條件式靜態證據，不是完整純 C 重建。
