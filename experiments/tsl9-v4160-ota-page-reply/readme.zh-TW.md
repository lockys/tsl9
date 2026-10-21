# OTA 頁面回覆：可讀 C / C++ 元件

[English](readme.en.md)

本元件重建 ID2966 V4.1.60 的 `9B8E..9C0A`：配置 1026 bytes、寫入頁面索引的兩個位元組、透過即時函式槽要求複製 1024 bytes、呼叫 TX，最後以尾端轉移交給釋放函式。配置為零時只還原框架並返回。這是部分可讀重建，未完整還原原始專案。

`src/page_reply.c` 是主要演算法；`reply_io.h` 的原生分支提供窄範圍暫存器約束、volatile 存取、真實 JAL/JALR 呼叫與 `musttail`。不含整函式組合語言或原始 BIN 指令模板。索引保持完整 32 bits；只有標頭截取低 16 bits，複製來源使用 `u32((0x20004 + liveS1) << 10)`。

實際 C11 與 C++17 編譯皆產生 124 bytes / 50 條指令。單純編譯器輸出仍有兩段 ABI 順序差異；另行記錄的 `reply-abi-order/order.py` 僅重排這次編譯出的指令，改動 ELF 中 28 bytes，保留全部中繼資料與重定位。排序後在 `9B8E` 連結的元件與原版 124 bytes 完全一致。這個結果應稱為「C/C++ 編譯 + 明確 ABI 排序」，不能稱為編譯器直接輸出原版順序。

原生驗證先確認缺少 `__tsl9v4160_call_8a56` 時嚴格連結失敗，再使用數值 `8A56` 產生 `ADDRESS-WITNESS-ONLY.elf`。該見證沒有 TX 提供者內容，不是可執行完整韌體；本里程碑不輸出 BIN，也沒有改動既有完整映像。

## 離線驗證

在專案根目錄執行，`LLVM` 指向本機已驗證的 LLVM NDK 工具目錄：

```sh
sh experiments/tsl9-v4160-ota-page-reply/verify.sh --language both
sh experiments/tsl9-v4160-ota-page-reply/verify_native.sh --tool-dir "$LLVM" --language both
```

Shell 包裝器使用 `PYTHON` 環境變數，否則選 `python3` / `python`。也可直接使用 Python：

```sh
python -B experiments/tsl9-v4160-ota-page-reply/verify_host.py --project-root . --language both
python -B experiments/tsl9-v4160-ota-page-reply/verify_native.py --project-root . --tool-dir "$LLVM" --language both
```

兩個 CLI 都接受 `--build-root`，必須為專案內尚不存在的目錄；`--replay RECEIPT` 只讀取實際輸出並重新驗證，不重新編譯或執行測試。原生 CLI 支援發布後的 `analysis/` 與工作區的 `apk-analysis/` 路徑。它會檢查精確 LLVM 檔案雜湊；目前驗證使用 Windows NDK 27.1.12297006，未聲稱其他平台 LLVM 已通過同一原生編譯證據。

HOST 每種語言通過 3 組 / 87 案例 / 3634 斷言及 6 個實際編譯的錯誤版本。涵蓋完整索引、精確效果順序、即時函式槽、回呼改變 S 暫存器／SP／保存框架、未知或不返回的效果前綴、原始與 JALR 遮罩後的目標，以及不把釋放結果正規化為成功碼。每次 HOST 執行前皆檢查執行檔格式與目前 Python 的主機架構；拒絕 RISC-V ELF。支援 PE、ELF 與 thin Mach-O 的檢查程式碼；目前實測是 Windows 主機，macOS universal/fat Python 不支援。

## 證據界線

HOST 是具名演算法／框架模型，不是 CPU 模擬器。READ/WRITE 回呼可改變合成記憶體與流程；正常返回時若改動暫存器或其已知遮罩，模型會停止並標記 UNKNOWN。只有具名外部呼叫邊界允許任意暫存器、SP 與框架變更。成功釋放保留原始與遮罩後的呼叫者連結，回傳值由不透明提供者決定；不返回路徑的斷言限於已提交的外部效果前綴。

HOST 的廣泛回呼變動測試不證明原生 C ABI 可容忍任意 SP／callee-saved 破壞。排序後原生區段的逐位元組一致性、原生 C 的條件性 ABI、合成 HOST 行為是三種不同證據。未知駐留提供者、計算出的內部入口、非同步／例外行為、實體硬體、ROM、BLE、Flash 與 OTA 適用性均未驗證。沒有執行 RV32、ISA 模擬、網路或裝置操作。

完整來源、獨立原始證據、原生 ABI 與 HOST 評閱及選定收據位於對應的 `analysis/v4160-ota-page-reply-2026-10-22/`（工作區為 `apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/`）。編譯產物與日誌保留於本機忽略的 `build/`；發布的收據中繼資料不代表這些檔案已隨專案發布。
