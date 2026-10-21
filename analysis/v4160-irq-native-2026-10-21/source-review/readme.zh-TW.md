# Branch-first IRQ C 核心：獨立 host 審查

本輪使用 `TSL9_IRQ_REGISTERS_HOST_TEST=1`，測試凍結的 `experiments/tsl9-v4160-irq-native/src/interrupt_registers.c` 與 `native_io.h`。公開標頭及 void callback 沿用 `tsl9-v4160-interrupt-registers`。這是 C／C++ 行為審查，不另造韌體解碼器，也不代表原生暫存器證明。

獨立合成 oracle **原樣沿用**前一輪 placement code review 的 `independent-tests.c`，SHA-256 是 `e40f4b8e986e705d6c8c29a34c793ce74d7c37a506e0ddedfecd80a1e2b783b4`，其封存為 `4757434b52178f0394efe252688340c1be19f43a16708e1b70b4e1d0b453dce9`。Runner 先核對舊 seal 及全部成員，再以同一套獨立 fixture 檢查新核心，避免複製或暗改舊證據；新來源／標頭也各自固定雜湊。

## Host 測試證明的範圍

每種語言通過 4 組／3820 案例／138312 斷言。Helper 矩陣涵蓋四個 RCC 位址、完整 32 位元資料／遮罩／enabled。2、3、0x100、0x7FFFFFFF、0x80000000、0xFFFFFFFF 等非零值均走啟用分支，A1 觀察保留完整位元。啟用輸出為 `(before|mask, enabled, 0x40021000, before)`，停用輸出為 `(before&~mask, enabled, before, 0x40021000)`，不能把基址改成個別周邊完整位址。

主流程刻意提供六個不同的新讀取值，逐項核對二十個外部效果的順序與原始寬度：CSR clear、六組 READ32／WRITE32、六次 PFIC 寫入及 CSR set；另檢查六次 helper 與一次最終輸出觀察。最終 A0 來自最後清除讀取，A1=0、A4=128、A5=0xE000E000。操作間的合成 CSR 漂移檢查「設定當時位元」，不能誤當恢復入口快照。所有 callback 都先檢查邊界，只將周邊位址當作數值。

每種語言實際編譯並由斷言拒絕二十二種修改，C11／C++17 合計 44 個已編譯負向案例，包含真假判斷與 enabled 位元、基址／完整位址、取樣／改寫值殘留、OR／清除語意、helper offset、動態遮罩截斷、快取分支讀取、先寫後讀、錯誤寬度、主輸出 A0／A1／A4／A5、CSR 遮罩／順序及漏 PFIC 寫入。其中兩個 host-header 修改保持 callback 輸出正確，卻改壞 RCC／主流程回傳值，確保回傳檢查不是重複輸出觀察。編譯失敗不算行為拒絕。

在本正常數值 I/O／輸出／回傳介面內，未發現來源語意不符。`receipts/` 在排除的 `build/` 外保存位元組相同的 JSON metadata；實際 EXE、object、日誌及變異來源留在本機歷史工作產物，不當作發布內容。

## 限制與重播

Host macro 會替換基址、常數、記憶體、CSR 與 returned-A0 bridge，因此測試**不能**驗證 production 組合語言、原生 `+r` bridge、實際 A0／A1／A4／A5、A2／A3 保存、堆疊／RA／IRQ、編譯器 outliner、原始放置或硬體／OTA。四個 helper 的原生相等與主流程結構，由另外的原生審查負責，不從 host 通過推論。

```sh
sh verify.sh --project-root /絕對路徑/project --language c
sh verify.sh --project-root /絕對路徑/project --language cpp
# Windows 亦可直接呼叫 backend：
python3 run-review.py --project-root /絕對路徑/project --language c
```

需要 Python 3.10+ 及已安裝編譯器，沿用 `scripts/portable_verify.py` 定位。Runner 支援工作目錄 `apk-analysis/tsl9-...` 與發布後 `analysis/v4160-...` 的 peer 結構。本次實際執行 Windows／MSVC；shell 是可攜入口，不宣稱本機 WSL／Git Bash 或 Linux／macOS 已執行。不連網、不碰硬體、不執行 RV32、不模擬指令集。

`python3 check-review.py --project-root <project>` 只核對凍結輸入、不可變 peer seal 與 selected receipt 雜湊，不重跑編譯器／host 測試，也不產生新的原生證據。
