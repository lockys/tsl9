# 與原始 bytes 一致的 IRQ／Flash 完整離線整合

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

C11 與 C++17 的實際生成鏈各新編譯 42 個單元，匯出相同的 76,800-byte BIN。SHA-256 與官方 ID2966 V4.1.60 相同：`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。11 個函式共 526 bytes 來自可讀重建來源，其餘仍為原始承載資料。這是部分來源重建，**尚未驗證可刷寫**。

## 實際生成與核對

34 個原始承載、兩個 IRQ／RCC 與六個 Flash 單元經編譯及部分連結，先產生 `compiler-integrated.o`。明確的 ABI 處理只重新排列兩個函式既有的堆疊保存指令，產生 `source-integrated.o`；兩者只差 14 bytes，metadata、符號與全部 RELA 保持相同。最後再連結、匯出，不以原始 BIN 填補或貼回函式。原始 BIN 只作參考核對；保留的原始承載則有各自來源與重定位身分。

每語言 57 個實際命令、42 份精確依賴規則與 201 個成品均可重驗。嚴格核對 691 個配置、680 段保留儲存、8,270 筆 RELA、53 個相對綁定、二十個外部入口及十個已明確消去的原始分支。全部匯出 bytes 由實際區段與 15 個 LOAD 支持，沒有 padding、RAM NOBITS 或 ROM bytes 匯出。嚴格連結在 ROM 缺少實作時仍失敗，成功連結僅提供數值位址 witness。

生成流程各拒絕 23 個實際 ELF／重定位／映像反例、三個依賴規則反例及四個排程收據反例。[來源獨立審查](source-review/README.md)另外核對 42 個實際來源／依賴與編譯配方；[ABI 獨立審查](ABI-review/README.md)核對實際保存順序、函式機器碼、進入／返回邊界及完整映像。封存 metadata 預設檢查與當次實際產物重驗會分開標示。

## 重建與唯讀重驗

```sh
python3 -B analysis/v4160-register-image-integration-2026-10-22/implementation/verify_image.py \
  --project-root /absolute/project --tool-dir /absolute/LLVM/bin --language both \
  --firmware /absolute/project/firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin

python3 -B analysis/v4160-register-image-integration-2026-10-22/implementation/verify_image.py \
  --project-root /absolute/project --replay /absolute/project/path/to/verification.json \
  --firmware /absolute/project/firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

需要 Python 3.10 以上與符合既有身分要求的 LLVM。生成產物寫入新的專案內 `build/`；不執行或模擬 RV32。模型入口與完整說明位於[實驗目錄](../../experiments/tsl9-v4160-register-image-integration/README.md)，獨立保存順序工具位於[另一模型](../../experiments/tsl9-v4160-frame-schedule/README.md)。

## 尚未證明

原機 ROM、確切晶片／板子、已安裝 BOOT、實體中斷／Flash 行為、BLE 更新接受性與失敗復原仍未證明。相同 bytes 不是完整高階來源還原，也不是實機測試。沒有接觸 BLE、UART、CAN 或實體 Flash，沒有呼叫廠商 API，沒有新增硬體功能。Windows Python／LLVM 證據不能擴張成 Linux、macOS、shell 或 CI 通過；完整目標保持未完成。
