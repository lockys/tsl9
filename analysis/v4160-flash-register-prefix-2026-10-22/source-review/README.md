# Flash 暫存器與指令邊界的獨立審查

[English](readme.en.md)

本輪獨立讀取最終 C11／C++17 的六個物件、IR 與已連結元件。五個 Flash leaf 函式的 **198 bytes、76 條指令，已逐 byte 等於原始 ID2966 BIN**。外層 `9C0A` 仍是 64 bytes、23 條指令，其中三條堆疊儲存順序與原始不同。合計為 262 bytes、99 條指令；沒有產出完整韌體 BIN，也未執行 RISC-V 指令、模擬器、硬體或網路操作。

最終 C／C++ 元件 SHA-256 相同：`575b2e1009437c77d71081fffeaa32988ff10b23c78decb01e9ad976c5e6c9c7`。本輪證據不能直接把前輪 `de159…` 整體映像升級為新的完整映像證明。

## 原始程式與前輪差異

`baseline.json` 由實際原始 `0ee64183…` 與前輪整體映像 `de159bb3…` 的指定 262 bytes 產生。可攜檢查重新讀取原始 BIN，依已封存解碼器核對全部 99 條指令及 20 個既有原始 byte 負向控制；前輪完整建置封存不在時，明確回報沒有重讀前輪封存。

| 函式 | 原始要求及前輪問題 | 本輪實際結果 |
| --- | --- | --- |
| `18E90`，8 bytes | A5 先取得基址，SW32 狀態值至基址 +12，透過 RA 返回。 | 原先與本輪均完全相同。 |
| `18E98`，30 bytes | A3 高位、A5 基址、A3 低位、A4 高位依序建立；`18EA8` 先寫 key1，`18EAA` 才計算 key2 低位。前輪把基址提前，並改變 key2 建立／第一筆寫入位置。 | 全部 10 條指令及邊界完全相同。 |
| `18EB6`，14 bytes | A4 基址；LW32 CTRL 至 A5；A3=0x8000；A5 OR 後寫回。 | 原先與本輪均完全相同。 |
| `18EC4`，46 bytes | `18EC8` 讀入 A4，`18ECA` 建立 A3 遮罩，`18ECE` 才對齊 A0；RMW 與 busy poll 使用 A4。前輪提早對齊並把部分 RMW／poll 暫存器改為 A3。 | 全部 19 條指令完全相同。 |
| `18EF2`，100 bytes | 首筆 CTRL 讀入 A5；A3 模式遮罩先於 `18EFA` 的 A0 ANDI。前輪讀入 A2 且 `18EFA` 落在另一條 32-bit ANDI 中段，後段 commit／poll 也改用其他暫存器。 | 全部 38 條指令完全相同，包含兩條 ADD 的編碼來源順序。 |
| `9C0A`，64 bytes | 原始依序儲存 S0、S1、RA；既有 C 編譯結果依序儲存 RA、S0、S1。 | 此來源與元件保持不變，仍有 6 個不同 bytes／3 個指令前緣差異。沒有宣稱修復外層逐指令等價。 |

這些不是只有正常返回值的差別。例如第一筆 unlock store 前，key2 是高位還是完整值；program 初次讀取後 A2 是否已被覆寫；busy poll 不退出時 A3／A4 的內容，都可能影響故障或中斷前緣的暫存器觀察。這是依原始指令操作數得到的靜態差異，沒有實際觸發硬體故障或中斷。現在 leaf 原始 bytes 完全一致，是較強的編碼證據，仍不代表已觀察到真實硬體的例外精確度、時序或非同步行為。

恢復 `18EFA` 指令邊界，不表示任意外部程式都能安全從該處跳入；仍需證明當時暫存器、控制流程與呼叫條件。未因此新增假別名或宣稱不存在計算式／編碼式／ROM 內部參照。

## 獨立檢查與重用邊界

`frontier.py` 只解碼單條指令的欄位，不保留或評估 CPU 狀態。它比較每個 PC、長度、opcode、寫入暫存器、來源暫存器、立即值與分支目標。為解釋先前候選，它另有只允許同一目的暫存器之 ADD／AND／OR 來源交換的比較；最終結論使用更嚴格的 198-byte 完全相同檢查。

實際六個部分連結物件各只有一個完整原大小函式配置，寫入 GPR 集合等於原始，五個 leaf 沒有隱藏呼叫或重定位；外層只有原位置的五個 JAL。部分物件與已連結元件僅允許這五個 JAL 的立即值差異。IR 另核對 volatile 32-bit 讀寫、key2 第一筆 store 後的相依 bridge，以及初始讀取／遮罩／A0 對齊的 SSA 順序。

新程式保留可讀 C 的讀寫、poll、迴圈與演算法。原生層使用空的固定暫存器相依 barrier，以及兩個有界的 address ADD primitive，將來源／目的地址依原始 A1/A0 + A5 順序寫入 A3；不是純標準 C。IR 檢查只允許這兩條指定的 leaf ADD 指令，不接受任意 opcode 字串或函式重播。沒有宣稱 IR 文字檢查就是完整形式化語義證明。

最終製作者 C／C++ 收據各 57 個實際檔案、99 個 raw 指令控制及 3 個實際原生編譯控制均已唯讀重播。另有本輪獨立 **12 個實際 ELF 變更與 7 個實際 IR 變更**：11 個順序／暫存器前緣錯誤被拒絕；另一個 ADD 來源交換只被「原始 bytes 完全相同」檢查拒絕，刻意不稱為語義前緣錯誤。IR 控制涵蓋失去 volatile、讀取寬度改變、A5 bridge 變 A2、遮罩錯誤、key2 相依錯誤及 address primitive 操作數／opcode 錯誤。

這 19 個靜態控制的實際元件及 IR bytes 已與最終建置逐一比對一致。控制成品只留在本機 `build/controls`；`independent-controls.json` 是封存紀錄，不會在預設模式假稱重新產生。

來源審查綁定五個最終核心檔案，確認 HOST backend／公開標頭、既有 HOST 巨集與 63 個 provider 表達式順序不變（兩個地址別名還原成既有 `fn_add` 後）。新增 HOST primitive 是 identity、已知常數與原有 unsigned32 加法。兩個 key 的拆分值也按模 2^32 核對。

本輪額外使用原封不動的獨立 `expected-effects.c`，對最終核心重新編譯及執行 C11、C++17，各通過 **12 個合成情境／8964 個檢查**。每個主機執行檔啟動前均經已審查的格式／架構 guard；不執行 RV32。這次沒有重新編譯獨立語義 mutant 矩陣，收據明列新增獨立語義 mutant 數量為 0。舊 oracle bytes／原始證據與 backend 可依確切身分重用；新原生機器碼及新主機正向結果是本輪實際驗證。

## 可攜檢查

只驗證封存、原始 99 條指令／20 個控制及當前來源：

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original-ID2966.bin
```

讀取新建置的六個物件、IR、元件及實際收據，要求五個 leaf 與原始完全相同：

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original-ID2966.bin --receipt /path/to/native-build/c/verification.json --require-exact-leaves
```

也可用 `--candidate-folder` 檢查六個物件、IR 與元件，或用 `--candidate-elf` 只比較已連結指令；它們不宣稱已重播完整收據封存。`check-review.sh` 支援 `PYTHON`／`python3`，Windows 可直接呼叫 Python。重新產生控制或正向 host oracle 應使用新的 `--output-directory`／`--build-root`，不得改寫此封存。

ROM、完整映像整合、外層堆疊逐指令／非同步等價、實體故障前綴、晶片相容性、已安裝 BOOT 與 OTA 接受條件仍未證明。本輪沒有新增使用者功能已實作的宣稱。
