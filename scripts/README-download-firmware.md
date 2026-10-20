# POST 下載已回傳的韌體 BIN

在 `C:\Users\locky\Documents\projects\re-tsl9` 執行：

```powershell
pwsh -NoProfile -File .\scripts\download-tsl-firmware.ps1 -FirmwareId 2966
```

需要 PowerShell 7.2 以上。腳本會以隱藏輸入取得你自己裝置的24位十六進位UID，不接受UID命令列參數，也不將UID、請求body或任意伺服器錯誤文字寫進檔案／日誌。

腳本讀取本機實際 `GetVerInfo` 回傳清單，要求指定FirmwareID恰好在清單中；預設清單已位於 `firmware-downloads/legacy-options-2026-10-20/evidence/server-options-receipt.json`。要用另一份已授權、實際取得的同格式清單，可指定 `-OptionsReceipt <路徑>`；不猜測ID、不自動向外查清單。

唯一正式請求為：

```text
POST https://www.iffrc.com/ffkj/user/?Temp=<1..9999>
Content-Type: application/x-www-form-urlencoded
action=GetFirmware&f_UID=<隱藏輸入>&f_FirmwareID=<指定ID>&ver=30
```

`ver=30`是舊官方更新器的客戶端版本欄位；`Temp`是cache-buster，兩者都不是韌體版號或驗證憑證。腳本只嘗試一次，不跟隨重導、不自動重試；遇401／403／429等非200狀態立即停止。TLS憑證使用正常系統驗證，不停用檢查。timeout30秒，回覆上限256KiB，允許1..96個1024B hex rows；格式不符就停止。

預設輸出到 `firmware-downloads/manual/ID-<ID>-<唯一GUID>/`，也能用 `-OutputRoot <目錄>` 指定。所有檔案用CreateNew新增，不覆寫既有下載。完成後終端機顯示BIN路徑、大小與SHA256。

| 檔案 | 內容 |
|---|---|
| `ID-<ID>-<標籤>-decoded.bin` | hex轉bytes後逐byte XOR 0xB7的第一階段候選映像 |
| `server-encoded.dat` | 未XOR的server bytes |
| `download.hex` | 嚴格驗證並正規化的CRLF hex |
| `http-response.txt` | 已驗證為hex加唯一末尾「接收OK」的原始回覆bytes |
| `receipt.json` | 請求嘗試次數、HTTP狀態、來源清單hash與各輸出SHA256；無UID |

完整產品適用性與內部編譯版本尚未獨立證明；檔名版本僅來自本機清單。解碼BIN不是已確認的原機OTA封包或可燒錄韌體。腳本不連接BLE、不寫硬體、不呼叫更新完成／重啟功能。

本機測試入口是 `scripts/tests/test-download-firmware.py`。14項loopback HTTP測試已通過，包含POST欄位、有效解碼、重導／403／429停止、格式／大小限制與未知ID零請求；測試用固定合成UID，未呼叫廠商端點。隱藏測試參數MockUri只接受HTTP literal loopback IP並強制合成UID，不傳送真實UID。
