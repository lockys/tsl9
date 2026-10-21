# V4.1.60 Flash 入口次序與自然 100-byte 程式

本輪六個可讀 C11／C++17 函式均以原有 LLVM 參數實際編譯、嚴格連結於原始入口：
quarter／status／unlock／lock／erase／program 為 64／8／30／14／46／100 bytes，
合計 262 bytes／99 指令。兩種語言的 component ELF SHA-256：
`aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d`。
沒有 padding、人工補指令、物件位元組修改或旗標搜尋；不執行 RV32，也不產生 BIN。

與前一輪相比，program 首次 CTRL 讀取後的 A0 對齊由固定暫存器值相依關係約束，
在首次 CTRL 寫入之前完成；前兩個輪詢後重新建立原始 A4 base，輪詢 AND 結果固定於 A5。
這些是原始指令／暫存器站點的表達，不是任意填補。HOST 宏保留原本相同的 AND 值語意。
`source-diff.json`／`check.py` 核對只有兩個核心檔案及主機 runner 的模型路徑改動；
host provider、測試、API 與編譯參數均未改。

三個有界實驗均保留實際 C／C++ 收據：

| 變體 | program bytes | 結果 |
|---|---:|---|
| 單一 fixed-A0 bridge | 94 | ANDI 可被移到首次讀取前，未關閉缺口 |
| 相依 A0 bridge＋兩次 fresh A4 | 102 | A0 記憶體事件次序改善，但超出原始 2 bytes |
| 再表達兩個原始 A5 輪詢結果 | 100 | 自然消除額外 LI A5,0，恰佔原始函式範圍 |

可直接使用的入口（Python 3.9+，本機已安裝編譯器）：

```sh
python3 -B experiments/tsl9-v4160-flash-entry-order/verify.py --project-root . --language both
python3 -B analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --replay /path/to/native/c/verification.json
```

原始工作目錄將 `analysis/v4160-` 換為 `apk-analysis/tsl9-v4160-`。
主機與原生 CLI 都支援全新 `--build-root` 及唯讀 `--replay`；shell wrapper 接受相同參數。
原生工具可由 `--clang`／`--linker`／`--objdump`／`--firmware` 指定。
`--firmware` 同時適用於編譯與 archive replay；使用其他位置的相同固定韌體時，
replay 須明確提供同一個 `--firmware` 路徑。`--language` 選擇 fresh 建置語言；replay 使用收據語言。
`probe_native.py` 是保留三次 Windows 診斷的入口，正式可攜入口是 `verify_native.py`。

主機每種語言實際通過 5 組／481 案例／247191 檢查及 6 個編譯語意負例。
每次正／負主機程式啟動前都檢查 PE／ELF／thin Mach-O 架構與寬度，以目前 Python 自身
標頭及執行期指標寬度辨識架構，拒絕 RISC-V ELF243；replay 重新解析七個程式。
macOS 要求 thin Mach-O Python，拒絕 universal／fat Python；本輪僅在 Windows 實際執行，
不宣稱 POSIX shell、Linux 或 macOS 已執行。

正式原生 CLI 固定前輪已封存的 compiler／ELF／disassembly 工具函式和旗標來源，
以新獨立 100-byte pattern checker 驗證 program，其他五函式沿用不可變的既有 pattern。
未修改或放寬前輪 94-byte 專用完整檢查器。每個物件完整 raw byte 覆蓋、CFG、GPR、
32-bit volatile IR、無隱藏配置／helper／UND、原始入口與五個 JAL 修補均另行檢查。
新 program checker 拒絕 12 個 raw 機器碼與 3 個 IR 反例，正式 CLI 另拒絕六函式各一個 raw 反例。
`-MMD` 清單是非系統專案來源閉包，不包含 compiler resource headers。

100-byte 型別程式已佔滿個別原始函式區段，原先 6-byte 尾端缺口消失；
這還不是完整映像整合通過。五個 program 內部輪詢／copy 入口對應偏移
10／1A／28／38／52，但原始偏移 8 的指令邊界已不同。
首次 CTRL RMW 使用 A2 而非原始 A5，ANDI／mask-LUI 次序也不同；
逐指令、完整 scratch GPR 前綴、非同步及中斷等價仍為 false。
wrapper 保存次序差異維持不變。正常契約有條件：存取完成、輪詢最終清除、無未建模非同步干擾。

主機 unknown／HALT／TRANSFER／診斷輪詢上限只保存外部效果前綴，不補做 cleanup，
也不把診斷上限當成原生 timeout。正常暫存器輸出與未證明的非返回 GPR 狀態分開。
A0 仍是對齊目的地而非成功旗標，A2 不是輸入長度，未新增 helper 位址範圍限制。

下一步必須獨立完成完整區段／符號／RELA／interior-role／LOAD 儲存驗證及來源整合。
本輪沒有整合完整映像、改寫前輪 BIN 或操作硬體。晶片／ROM／Flash 容量、時序、電源失敗、
開機、實體相容與 OTA 仍未證明。build 留本機，發布只保留選定收據與來源；
`check.py` 明確列出缺少的本機 archives，不將收據閱讀冒充 fresh 建置或產物重驗。
