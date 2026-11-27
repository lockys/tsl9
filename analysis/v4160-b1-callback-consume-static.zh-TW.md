# v4.1.60：RF task、event-4 request 與 APP callback17 消費鏈

本階段以原始 APP 與兩份 resident 候選載體的完整函式位元組，接通前階段已定位的註冊 task、request helper、RF command13 與 APP 重試／完成路徑。全部工作離線；未執行或模擬目標 ISA、provider、timer、queue、heap 或硬體。候選載體不等於裝置上實際 installed provider。

驗證程式：[check_v4160_b1_callback_consume_static.py](check_v4160_b1_callback_consume_static.py)；逐指令與 CFG 證據：[v4160-b1-callback-consume-static.json](v4160-b1-callback-consume-static.json)。前置註冊來源見 [上一階段](v4160-b1-binding-order-static.zh-TW.md)。

## 完整新增範圍

| 函式 | V131 候選 | V140 候選 | 每份大小／指令數 |
|---|---|---|---|
| RF task | `[0x65920,0x65a18)` | `[0x65a0a,0x65b02)` | 248 bytes／81 |
| event-4 request | `[0x657d8,0x65920)` | `[0x658c2,0x65a0a)` | 328 bytes／126 |

合計 **1,152 bytes、414 條指令**，每個範圍均核對原始 sparse HEX 的實際捕獲位元組，不以缺失位元組補零。另重用 APP status/retry/finish/task 共 332 bytes、resident RF command 共 396 bytes，以及 start/stop/lookup 共 940 bytes；這些重用範圍不算新增覆蓋，也不提高既有 C 重建覆蓋率。

## RF task 與兩套 task ID

令 V131 的 `C=0x20003560`、`S=0x20003514`、`F=C-32`；V140 對應值均加 80。前階段 role initializer 註冊上述 RF task，將登記回傳的低 8 位寫入 `C+16`。此 RF task 持有完整入口事件字 E，依 bit mask **1、2、4、8、16** 的順序只處理首個命中項；子函式正常返回後強制回傳 `E XOR mask`，無命中則回傳 0。函式自身只有 frame stores，沒有本機迴圈。

- event 1：首次讀取的 `C+12` bit1 啟用時，請求 timer `(fresh C+16,4,80)`；另一個 fresh flags snapshot 的 bit7 若為 1，delay 改用 `160*fresh F+25`。
- event 2：以 bit2 gate 請求 `(fresh C+16,8,160)`，或依另一 flags snapshot 改用 `160*fresh F+25+40`。
- event 4：直接呼叫完整 request helper。
- event 8：fresh flags bit2 啟用才呼叫 `0x6575a/0x65844`。
- event 16：先呼叫 `0x43edc/0x43f68`，之後 fresh `S+7==8` 才請求 `(fresh C+16,16,1600)`。

所有子回覆均不作 task 的最終回覆。上述 timer 實參只證明請求形狀；未證明計時單位、事件實際交付或中間狀態不變。APP 重試與完成服務重讀 APP task ID **`0x2000c7a0`**；APP task 本體的 priority 是 bit15、bit0、bit1。兩個不同欄位與登記來源不可推成相同 task 或相同 queue。

## request 的分支與等待界線

request 使用 48-byte frame，保存十個 word。fresh `C+12` bit1 為 0 時直接普通返回，沒有強制 A0。其餘情況若 fresh `S+7==3`，恢復 frame 後尾跳 `set_event(fresh C+16,4)`，目標是 `0x4354a/0x435d6`，並非 start_timer。

非 3 分支先呼叫 RF command13，再將外層 counter 設為 8。每個獲准進入的 attempt 呼叫 `0x64794/0x6487e(0,0,128)`。fresh `S+2` bit0 未設時，重新讀取動態指標 slot `R=0x2000353c/0x2000358c` 與其 word+100；word 非零會重新輪詢 status，為零才減 counter。八次減至零後恢復 frame，尾跳 `0x6575a/0x65844`。**counter 只限制完成這些退出條件的次數，不能限制等待時間。**

當 fresh `S+2` bit0 設定時：清 `S+2`，以 fresh `F+0` bits4..5 呼叫 `0x63c54/0x63d3e(bits,255,0)`；再次讀取 flags 後，呼叫 RAM service `0x200026ba/0x20002706(1,bits,255)`，不假設兩次 bits 相等。

接著 fresh `S+3` bit0 若設，會清 `S+3`、呼叫 `0x6440a/0x644f4`，fresh flags OR 0x80 寫回 `C+12`，恢復 frame 並尾跳 set_event `(fresh C+16,1)`。否則同樣先呼叫 `0x6440a/0x644f4`，再進行以下順序：

1. 捕獲 `P0=fresh [R]` 與 `saved=fresh [P0+12]`，寫入 `saved & 0xffffdfff` 至 `P0+12`。
2. 重新捕獲 `P1=fresh [R]`，依序寫入 `P1+8=8192`、`S+4=128`、`P1+100=3986`、`P1+12=saved`。
3. 持續重新讀取 `[R]` 與 word+100，直到零才回到前面的 word+100 判斷。

未證明 P0 與 P1 相等；保存值來自 P0，而最後回寫至 P1。兩條 polling cycle 均無已證明的 timeout 或進展來源。保留的 `0x0100` 指令只作原指令證據，不推定硬體等待語義。

## callback17 至 APP 的條件性串接

重用完整 RF command 的證據：其獨立 fresh `S+7==3` 分支，從 `F+16` 讀取 callback，以 **`(17,0,0)`** 呼叫，沒有非零 callback guard。若實際綁定及保存條件成立，該 slot 可對應 APP `0x174ee`；status17 路徑不解參考 A2，直接尾跳 retry `0x17442`。

request 先前讀取 `S+7!=3`，並不能證明 RF 之後的 fresh snapshot。若另有證據證明兩次值穩定相等，則這條 request 呼叫中的 callback17 反而被排除。B1 core 直接 command13 的 caller 沒有該前置 guard。本階段既不假設狀態改變，也不宣稱觀察到 callback 實際執行。

retry 先讀 fresh byte `old=[0x2000c7a8]`，計算並存回 `(old-1)&255`，再作分支。只有 old=1 進入 finish `0x173ee(1)`；old=0 會變成 255。其他值捕獲 fresh `0x40058`，以原 link 尾跳 timer `(fresh APP task byte,1,2)`；retry 本身沒有 frame，也不修改 SP。

finish 的順序固定為：

1. 透過 fresh `0x4005c` 請求 stop `(fresh APP task byte,2)`；不根據 scalar reply 分支。
2. 依序清除 counter `0x2000c7a8` 與 length `0x2000c7a9`。
3. 捕獲 fresh completion word `0x2000c7a4` 到 T1。null 路徑普通返回當時 A0；nonnull 路徑恢復入口 A0=1 並 reload 保存的 S0／RA，清 completion slot，再恢復 SP 並尾跳捕獲的 `T1(1)`。

APP task 的 bit1 路徑也呼叫 finish(1)，隨後將回覆覆寫為完整 E XOR 2。start/stop/lookup 的候選完整合約已重新核對；stop 不等於已確認取消或釋放 timer。completion 的 capture/clear 非原子操作，slot 清零亦不排除其他 writers 或重入。finish 自身 frame 已恢復時，外層 RF/request frame 仍可能存在。

## 驗證與尚未證明事項

驗證包含完整 operands、typed loads、QingKe 指令標記、frame/tail/call/store 範圍、CFG 路徑及 cycle cuts；拒絕 414 個逐指令 mutation 與 18 個 typed-load mutation。host scalar 檢查涵蓋 65,536 個 RF event 低 16 位值、256 個 retry bytes、256 個 delay/flag bytes，以及八次已完成退出的 counter 算術；未執行 target 狀態模型。一般模式與 `-O` 均必須精確重放同一份 ledger。

所有串接依賴候選 ISA／mapping 與實際 API/callback 綁定、有效 extent、一般 callee 對 S/SP/RA 和保存 frame 的遵守，以及沒有破壞性 alias、wrap、IRQ/DMA 或重入。各次 fresh reads 的相等性須分別證明。未解決的工作是 `0x6575a/0x65844`、`0x64794/0x6487e`、`0x63c54/0x63d3e`、`0x6440a/0x644f4` 及 RAM service 的副作用、flag writers、真實事件順序、provider 綁定與完整借用指標保存期。

```powershell
python analysis/check_v4160_b1_callback_consume_static.py
python -O analysis/check_v4160_b1_callback_consume_static.py
```
