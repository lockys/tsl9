# V4.1.60 原始內容一致的來源整合映像

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本輪從 42 個來源翻譯單元重新編譯 C11 與 C++17：34 個 raw carrier、2 個 IRQ typed TU、
6 個 Flash typed TU。11 個可讀函式合計 526 bytes，其餘 680 個區段仍由既有 raw carrier 保留。
這是部分可讀重建，不代表整個韌體已還原成原始 C/C++。

兩份實際輸出均為 76,800 bytes，SHA-256 完全等於原始 ID2966 V4.1.60：

`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`

原始內容差異為 0；相較前一份 de159...68be1 整合映像，70 個 byte 差異已消除；
相較較早的 IRQ-only 映像，8 個差異消除。完整輸出名稱仍是
`NOT-FLASH-VALIDATED-register-scheduled.bin`。儲存內容一致尚未驗證實體燒錄或 OTA。

實際流程保留每一層產物：

```text
42 fresh source TUs
  → raw-carriers.o + typed-providers.o
  → compiler-integrated.o
  → explicit Python ABI frame scheduling
  → source-integrated.o + frame-scheduling.json
  → strict missing-ROM rejection
  → numeric-ROM ADDRESS-WITNESS-ONLY.elf
  → NOT-FLASH-VALIDATED-register-scheduled.bin
```

編譯器原始輸出中的 IRQ 與 quarter 保存次序，由獨立的來源政策調整。
排序工具只重排新編譯所得的既有 C.SWSP words：IRQ 8 bytes、quarter 6 bytes，共 14 個
file byte 值變動。沒有製造 opcode、padding、讀取原始 BIN 來產生程式碼，或修改最終 BIN。
前後整個 ELF 的區段 metadata、符號與 RELA 完全相同；兩個物件與完整收據均保留。
最終流程明確是「C/C++ 編譯＋已驗證 ABI 保存次序調整」，不宣稱 stock compiler 單獨產生
最終保存次序。原始 BIN 僅作固定的離線驗證參考。

排序工具固定 `schedule.py` SHA
`dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d`，
政策 SHA
`2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d`，
全部 10 個排序模型檔案在使用前後核對。11 個最終連結函式皆與原始內容完全相同；
其中五個 Flash 葉函式早在排序前已由編譯器產生原始相同位元組。

固定入口（Python 3.9+ 與已安裝本機 LLVM；不下載工具）：

```sh
python3 -B experiments/tsl9-v4160-register-image-integration/verify.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B experiments/tsl9-v4160-register-image-integration/verify.py --project-root . --replay /path/to/c/verification.json
python3 -B analysis/v4160-register-image-integration-2026-10-22/implementation/check_image.py --project-root . --require-local-builds
```

工作目錄使用 `apk-analysis/tsl9-v4160-...`，發布目錄使用 `analysis/v4160-...`。
.sh wrapper 接受相同參數，可用 PYTHON 指定 Python。只在 Windows 實際驗證；
沒有宣稱 POSIX shell、Linux／macOS 已實跑。
CLI 支援新的 `--build-root`、`--clang`／`--linker`／`--objcopy`，
只採用目前 Python 執行排序步驟。該步驟明確加入 -B，runner 也禁止 Python bytecode cache。
`--firmware` 轉交 build 與 replay 的所有依賴 context，且必須是同一固定 SHA 的離線檔；
不同位置的參考檔須在 replay 提供相同路徑。明確 replay 語言須與收據一致；
工具／build override 僅供 fresh build，replay 拒絕忽略這類參數。
正確 C／C++ replay、明確韌體路徑、錯誤語言／override 拒絕皆有實際 CLI 檢查；
alternate-location 僅另做 context 轉交測試，沒有重跑另一份完整映像編譯。

每種語言的實際證據：

| 項目 | 結果 |
|---|---|
| 來源 recipes | 57：56 次 LLVM＋1 次明確 Python 排序 |
| MMD | 42 條逐條 target／primary source／adapter 核對 |
| 非系統 native 依賴 | 72 個既有檔＋12 個生成 filter／adapter |
| 原始配置／保留儲存區段 | 691／680 |
| RELA | 8270＝8259 個區段外完整角色＋11 個 owned JAL |
| canonical 相對 bindings／外部入口參考 | 53／20 |
| 私有 branch discharge | 10 個精確舊角色：4 IRQ＋6 Flash |
| LOAD | 15 個，file payload／記憶體範圍／權限與區段完全覆蓋 |
| 原始內容／前後排序 | 全映像 0 差異／僅 14 bytes 重排 |
| 實際負例 | 23 個 ELF／RELA／映像＋3 個 MMD＋4 個排序收據 |
| 本機產物 | 每種語言 201 個，全部 hash 後唯讀重驗 |

680 個 retained hash 比對的是原始 partial-object 儲存內容；linked section／LOAD／BIN
另行比對，沒有把 relocation 前的資料誤當最終 BIN。
舊私有 branch 只在確認原始 site/type/target/bytes 與無已記錄外部參考後 discharge；
沒有建立假的 numeric alias/provider。metadata 的 FILE、SECTION、mapping 角色另行精確核對。
所有11個函式入口、526個程式 byte、全部 LOAD payload 都由實際來源編譯／連結產物供應，
沒有 holes、舊 BIN fallback、NOBITS/RAM 匯出或 ROM bytes。

嚴格連結仍因唯一缺少的 ROM provider 拒絕；數值 0x40000 只供位址 witness。
這不提供 ROM 內容或執行證據。全映像 byte identity 是靜態儲存事實；
完整 GPR／非同步／interrupt／fault 語意、computed interior entry 假設、ROM、實體晶片／板卡、
Flash 容量、電源失敗、開機與 OTA 相容仍未證明。沒有執行 RV32、ISA 模擬、裝置 I/O 或網路操作。

原始歷史 layout 保留既有 CRLF bytes（SHA `651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b`），
其餘新報告／來源／文件均為 UTF-8 LF。prepare_manifest.py 是建置驗證 ledger 的歷史 bootstrap，
需要明確本機元件；正常 verify.py 使用發布的固定 ledger，不依賴 W-only 舊 build 或 exports。
首次尚未編譯即被來源 hash 拒絕的舊 ledger，與早期 provisional build 留在本機 build 診斷中。

發布僅包含來源、固定 ledger、分語言文件與選定收據 metadata；完整 build／log archives 留本機。
check_image.py 預設明列缺少的 archives；`--require-local-builds` 要求實際前後物件、收據、ELF、
BIN、log、依賴與負例可讀，才回報重驗通過。閱讀 metadata 不等於 fresh build 或硬體驗證。
