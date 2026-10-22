# ADC 配置 C/C++ 與原始 callback 相依閉合

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

以同一份可讀 C 演算法重建原始 `0x1892E..0x18986` 的配置效果，並用實際 C11／C++17 編譯與合成 IO 驗證。新增的 native adapter 使用真實 volatile IO，僅編譯及靜態檢查，沒有執行。**沒有新的重建韌體 BIN，沒有替換既有元件，也尚未證明原機可刷寫性。**

另保留88-byte原始來源切片供證據核對；它不是重建韌體或編譯器的opcode輸入。原始配置函式為88 bytes／37指令，依序有14次存取：三組 fresh read／修改／write32，穿插讀取配置中的完整32-bit欄位與一個byte。三個遮罩為 `0xE0F0FEFF`、`0xFFF1F7FD`、`0xFF0FFFFF`；最後欄位使用 `((byte-1)&255)<<20`。重建保留讀取順序、uint32回繞、alias回饋及高位元，沒有自行把配置值縮成布林或較窄欄位。

| 實測項目 | 結果 | 限制 |
| --- | --- | --- |
| 實作 HOST C／C++ | 各80案例、6864檢查、3個實際語意反例 | 合成 typed IO，未執行原始韌體 |
| 獨立 HOST C／C++ | 各74案例、2904檢查、3個實際語意反例 | 包含alias、動態讀值及14步中止前綴 |
| 選定 native 入口 | 102 bytes／38指令，無call或frame | 比原始多14 bytes |
| 完整 native 物件 | 5個真實global FUNC，254 bytes／93指令，UND／RELA為零 | 包含4個未選函式，未連結成映像 |

native入口在正常完成時保留A0／A1，但額外寫入A2／A6／A7；原始只寫A3／A4／A5。特定caller後續會覆寫A2／A6，這只降低該正常路徑的部分差異；原callback保存A7，新A7改寫仍可能逃逸。完整暫存器、fault／非同步前綴與extent契約未通過，不將正常效果相符當成原機ABI相容。[實作](implementation/README.md)；[獨立驗證與原生差異](model-review/README.md)。

來源分析新增8個函式範圍，共386 bytes／148列，並重讀364-byte callback及上一輪106-byte相依。所有13個直接呼叫點的受限相依已閉合；在有效、不與MMIO／code／配置重疊的144-byte stack、正常存取、無不利非同步修改，且輪詢在有限次讀取內遇到狀態bit1等前提下，可推導正常返回保存SP／RA／S／GP／TP。這不是保證終止：原始輪詢沒有timeout。A6原本會被通道設定改寫，不能宣稱callback保存所有GPR。

callback選擇channel16、sequence1、sample7，正常結果是fresh READ32(`0x4001244C`)的低16位元；沒有證據把它直接當成攝氏溫度。`0x4002100C` 的reset bit9會清除，callback未備份此字，因此不是整體MMIO快照還原。config word52只有在與已列stack／MMIO寫入集合不重疊等前提下才可延伸保存，整段初始化生命期與installed身分仍未知。[完整來源、前提與反例](source-review/README.md)。

既有官方CH32V20x參考標頭的ADC1／ADC2位址及CTLR1／CTLR2／RSQR1欄位順序與這些操作相符，僅支持家族候選，不能確認板上晶片或封裝。摘錄、完整原始header hash與取得來源見 [hardware-reference.json](hardware-reference.json)。新增的標準指令欄位只使用 [官方RISC-V來源節錄](instruction-reference/README.md)，沒有opcode生成或CPU／ISA執行。

值得新增的功能提案：離線ADC配置／讀取報告可顯示原始raw16值、channel與取樣設定、未完成校準或輪詢的診斷狀態；需要實際硬體與校準證據才能顯示實體溫度。這是提案，沒有新增原機功能或改動原始輪詢行為。

預設checker只核對來源與封存metadata，實際FW／ELF／物件須明示路徑。原生adapter、RV32、MMIO及硬體均未執行；既有550-byte元件與77,824-byte NOT-FLASH-VALIDATED映像維持不變。Python入口已測；Git Bash先前因 `NtCreateDirectoryObject 0xC0000022` 無法啟動，這輪不重試或改通道，shell runtime仍未驗證。
