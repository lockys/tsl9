# TX 完整離線映像整合

[English](readme.en.md)

這個實驗從來源 fresh 編譯與連結完整 76,800-byte 映像。13 個原始程式區域共 930 bytes 由可讀 C/C++ 與明示 ABI 層提供，對應 15 個真實 FUNC provider；其餘 678 個區段保留來源載體。這仍是部分可讀重建。

TX 的 canonical `__tsl9v4160_call_8a56` 是真實配置的 FUNC8 入口，後接 LOCAL FUNC270 C 主體與 GLOBAL FUNC2 C 返回葉節點。沒有偽造 FUNC280、ABS 函式 provider 或原始 BIN fallback。入口用標準 assembler mnemonic 與 `R_RISCV_BRANCH`；linker 編碼真實目標位移。另一步僅移動新編譯產物中已存在的五個 SWSP 與五個 LWSP words，還原已證實的堆疊觀察順序。原有 reply、IRQ/quarter 排序工具保持封存不變。

實際 C11/C++17 流程有 46 個來源單元：34 個載體 C/C++、11 個 typed C/C++、1 個不經預處理的組合語言入口。67 個內部工具命令包含 64 次 LLVM 與 3 次明示 Python ABI 排序；外層資源查詢及 producer 啟動另行記錄。45 個 `-MD` 規則實際觀測 78 個既有專案輸入、14 個產生的來源/adapter，以及一個 Clang `stdint.h`。入口 `.S` 以直接來源雜湊核對；85 個 ledger pins 不代表 85 個檔案全部參與編譯。

```sh
python -B experiments/tsl9-v4160-tx-image-integration/verify.py \
  --project-root /path/to/project --tool-dir /path/to/LLVM --language both
```

也可用 `sh experiments/tsl9-v4160-tx-image-integration/verify.sh ...`，以 `PYTHON=/path/to/python` 指定 Python。`--firmware` 可指定相同雜湊的原始 ID2966 BIN，僅作驗證。預設建立 UUID build；`--build-root` 必須是這個 model 的 `build/` 內尚不存在的新路徑。禁止覆寫。Python/sh 入口可跨平台；目前實測工具為已釘選的 Windows NDK LLVM，沒有宣稱實測其他作業系統的工具鏈。

每種語言的輸出位於 `BUILD/{c,cpp}/`，包括新編譯 objects、11 份 IR、45 份 `.d`、三個排序證據、partial ELF、`ADDRESS-WITNESS-ONLY.elf`、`NOT-FLASH-VALIDATED-tx-integrated.bin` 與 `verification.json`。所有 BIN bytes 必須有實際 section/LOAD 來源；不得混入 RAM NOBITS、ROM、padding 或舊 BIN bytes。原始 BIN 只參與差異驗證，不出現在編譯/連結/匯出輸入中。

```sh
python -B experiments/tsl9-v4160-tx-image-integration/verify.py \
  --project-root /path/to/project --replay /path/to/verification.json
```

重播只讀實體產物、來源、工具雜湊與實際命令/依賴/排序證據，不重新編譯、不執行目標。保留的 JSON metadata 與 build archives 是不同證據層級；發佈來源不包含完整編譯 archives。重新 fresh build 可產生自己的實體證據。

已驗證外側 76,520 bytes 與原始映像相同；TX 範圍內有 93 個 byte 差異。新映像 SHA256 為 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。完整配置為 691 個區段、8,261 個 RELA（8,246 outside、12 個原 typed JAL、3 個 TX）、53 個 canonical 相對綁定、29 個 outside incoming references、15 個 LOAD。七個原 TX 控制標籤與一個 PCREL anchor 的變更分開記錄。

嚴格連結仍會因缺少真實 ROM provider 而失敗；數值 `0x40000` witness 不提供 ROM 程式。全原始 ABI、任意 computed targets、故障/中斷時序、實體晶片相容性、裝置燒錄及 OTA 相容性尚未確認。不要把這個實驗 BIN 當成已驗證可燒錄韌體。
