# 主機執行檔檢查補充審查

[English](readme.en.md)

本補充審查取代先前審查對「目前主機 runner」的入口檢查。舊審查 17 個檔案完整保留，seal 為 `f5cec050e258486cb7205c2354742e197ed7632fa5f943cc3a0a2bf9760c92f6`。舊審查固定的 runner 是 `d1f470a8539eb9815eaa65230a6da974f7dd21b2c009950516e0e3d250cc377e`；它拒絕後來改變的 runner 是正確行為。歷史結果沒有改標成新的執行成果。

編譯器選擇 helper 接受明確指定的編譯器；交叉編譯成功並不代表輸出是主機執行檔，也可能是 RV32。修正後的 runner 在每個正常／行為突變測試啟動前，先讀取並檢查執行檔格式及 machine，明確拒絕 RISC-V ELF machine 243，不依賴作業系統啟動失敗來保護邊界。這是自有測試產物的格式檢查，不是任意不可信程式的沙盒，也不能單靠檔頭證明程式行為。

前一版檢查曾因本 Shell 的 `platform.machine()` 是空字串而安全停止。最終版改由目前執行中的 `sys.executable` 標頭、作業系統、編碼與 Python 指標寬度判定主機架構，不讓待測產物決定主機架構。獨立測試確認空白 `platform.machine()` 不影響判定。本次實際驗證 Windows PE；Linux ELF 與 thin Mach-O 支援僅有來源審查，並非實體平台執行證據。不支援的直譯器格式會拒絕通過，例如 macOS universal 直譯器不符合本版要求的 thin 標頭。

新的受保護 C11、C++17 主機執行結果，各維持精確的 5 組、481 案例、247191 項檢查及六個實際編譯行為控制。`review.json` 綁定最終 runner、保留結果與獨立觀察。獨立審查核對最終程式中的檢查順序，並讀取真正的主機 PE 與 RV32 元件；測試 RV32 拒絕路徑時攔截程序啟動，從未啟動該元件。格式拒絕與已編譯測試的語意斷言失敗分開記錄。

所有 C／標頭／測試輸入及原生檢查工具與先前版本相同，因此沿用原先獨立預期效果測試（每語言 12 情境、8964 斷言及十二個編譯控制）與六個原生函式共 256 位元組、98 指令的歷史證據。舊 `run-effects.py` 保持封存原樣，沒有新格式檢查，也不重新執行。本次僅改主機 runner，不重跑原生編譯與整套歷史效果矩陣。

先前限制仍成立：program 對齊時點、包裝函式儲存順序不同，未證實未返回時的實體暫存器前綴或非同步等價；program 剩餘六位元組仍未建立所有權。本次沒有新 BIN、完整映像整合、硬體／Flash／ROM／OTA 驗證或產品功能實作。

於專案根目錄執行：

```sh
python apk-analysis/tsl9-v4160-flash-native-2026-10-22/review-v2/check-review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin
```

發布目錄對應入口為 `analysis/v4160-flash-native-2026-10-22/review-v2/check-review.py`。此命令唯讀核對封存證據、目前輸入雜湊及原始位元組，並重驗 20 個來源位元組控制，不執行指令。未明確提供保留 v2 主機產物的 `--archive-root` 時，會回報 `actual_archived_artifacts_replayed:false`；保留的結果 JSON 不能代替缺少的執行檔或編譯器封存。歷史絕對 Windows 路徑代表實際執行環境，新跑可使用有格式檢查的模型 `verify.py`，明確指定專案／輸出路徑。本審查不執行原始或重建的 RV32 程式。
