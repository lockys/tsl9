# TX 候選的 OTA 頁面證據

[English](readme.en.md)

[檢查器](check.py)只讀取原廠 ID2966 V4.1.60 與 TX 整合候選各自的第 3 個 1 KiB 頁，即從 0 開始的頁面 index 2、名目位址 `[0x8800,0x8C00)`；不讀取其他頁或 APP 排除區。該頁有 93 個差異，全部位於已審查 TX 範圍 `[0x8A56,0x8B6E)`，首尾差異分別在 `0x8A7F`、`0x8B6B`。

原廠頁面 SHA-256 為 `d835e10c8861c681e9c371f7ba99e885ca4d8db33a435d1f03555ce36d41347f`；候選頁面為 `72d7f81f1d65031c55869b541b90e76d22b85d5ca340aaf46acc5346fcf2350e`。這些是 1024-byte payload 雜湊，不含 OTA 頁面 index。其他頁是否一致依據[既有完整映像靜態審查](../../analysis/v4160-tx-image-integration-2026-10-22/README.md)，不是本檢查器新讀取的結果。

Morphe 的 RAW 解析使用 1024-byte payload 和兩個大端序 index bytes；選檔 debug log 會記錄整檔及傳輸 payload SHA-256。日後若有候選檔選取雜湊及 page 2 讀回成功的可信紀錄，可縮小「傳送了哪個候選」的不確定性，但仍不能證明開機後執行、所有功能、ROM 相容或安全性。本檢查不執行韌體、不刷寫、不產生新 BIN。

獨立的[允許區域檢查器](check-allowed-windows.py)另比較每份 APP 的 73,672 bytes：`[0x8000,0x14056)`、`[0x14C8A,0x1A69C)`、`[0x1A6A0,0x1AC00)`。這些區域中只有同一 93 bytes 不同，全部在 TX 範圍；被排除的 3,128 bytes 沒有讀取，所以本次不能證明整檔其他部分一致或硬體相容。各區間的預期雜湊固定在檢查器中。
