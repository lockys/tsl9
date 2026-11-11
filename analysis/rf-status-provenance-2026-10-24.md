# 0x174EE 註冊與候選 caller：有界靜態追查

## 直接觀察和條件鏈

- APP constructor `0x175E8..0x17666`：`0x17644/0x17648` 以 AUIPC/ADDI 算出 `0x174EE`，`0x1764C` 存到 `SP+16`；`0x17654..0x1765A` 從 `[0x401C4]` 取指標，以 `A0=SP` 間接呼叫。[原始 listing 和核對](../experiments/tsl9-original-RF-bridge/README.md)。候選 carrier slot 指向 `0x64BAE`；header 的 `rfConfig_t` 將 offset 16 命名為 `rfStatusCB`。候選 `RF_Config` 非零 callback 等條件通過後清零並複製 32 bytes 至 `0x20003540`，故在有效、不重疊記憶體及 copy 契約成立下 word `0x20003550` 可取得 APP 值。不是實機已註冊的觀察；入口、ROM 身分、成功路徑和記憶體契約均需成立。[候選設定本體](../experiments/tsl9-resident-callback-registration/README.md)
- 候選 SDK ACK-phase `0x645DC..0x646A8` 是**可能**的 status caller，不是已觀察到的呼叫。`0x645F6` 設 `s0=0x20003514`，`0x645FA` 從 `[s0+36]=[0x20003538]` 取指標，並把它交給 `0x64608/0x6460C` 的 RAM helper；`A2=SP+15`。helper 返回後，在部分路徑 `0x64644..0x64648` 將該 stack byte 寫入重新讀取的指標的 byte 0。`0x6464E` 從 `[0x20003550]` 載入目標，`0x64650` 再從 `[0x20003538]` 讀入 A2，`0x64652` 截 A1 為 byte，`0x64656` 設 A0=2，`0x64658` 間接呼叫。多次讀取是 then-live 值，不保證相同。詳見 [candidate listing](../experiments/tsl9-original-RF-tx-path/evidence-v1.json) 的 `tsl9_candidate_TX_ack_callback_645dc`。
- 上述 helper 的輸出 byte 不可直接認定為有效 buffer 長度或分配容量：其 ABI、來源、成功條件以及 `[0x20003538]` 指標的建立／allocation、可讀範圍尚未在本次封閉。亦未證明此候選 caller 的路徑可到達、callback word 當時為 APP 值或列盡其他 callers。原 APP 的 sender `0x1753A` 提供的是**傳送** buffer／長度，不能自動當成該 RX callback 的 A2 容量；[傳送路徑](../experiments/tsl9-original-RF-tx-path/README.md)。
- APP `0x174EE` 在 A0=2、A1=0 時讀取 A2+1、+2、+3，沒有在此本體檢查 null 或長度，故此路徑的記憶體前提是至少偏移 1..3 可讀（一般描述為有效的至少 4-byte buffer）。**沒有本地檢查不等於短 buffer 能到達這條路徑**：上游可能保證容量、拒絕狀態或使用固定儲存，現有證據尚不能肯定或否定。A1 非零時該分支不讀這三個 bytes；其他 status 路徑亦不得混同。

## 固定 bytes 與覆蓋邊界

`python scripts/verify-rf-status-provenance.py` 固定完整 APP／候選 carrier 的長度與 SHA-256，另對下列 end-exclusive windows 各自固定 SHA-256；這是 bytes 身分檢查，不是反組譯、資料流、可達性或安全性證明。APP 以 `0x8000`、carrier 以 `0x40000` 為檔案偏移基底：

| 範圍 | SHA-256 |
|---|---|
| APP `174EE..1753A` | `8d1fe26ede0b1c74b6c550872c3a3db09c6ce90f8b129501d4d6e50156c974d0` |
| APP `175E8..17666` | `f4a0f1fe856e488853f27ae937fdca1e9e0240a4b705e79b77265675c3513c5e` |
| carrier `401C4..401C8` | `dc55dfbb2d2cbe1162d1469abf1e87506fc55a4b1b2cfb005508cdfd23fe64b0` |
| carrier `645DC..646A8` | `1d6f1e4f8b846f93e35696b266869542744609b60bb6dbaad732a78576174331` |
| carrier `64BAE..64CEC` | `0e73a5cebf069a716f6967b386c8cc9de529e25608933422eda98997a0ec9bf4` |

`python -m unittest discover -s tests -p test_rf_status_provenance.py -v` 對各 window 首尾 byte 翻位、截斷以及 window 外翻位執行 negative；後者刻意證明單獨 window check 不覆蓋全檔，而完整 hash 會拒絕。沒有硬體、目標執行、模擬或動態封包證據。
