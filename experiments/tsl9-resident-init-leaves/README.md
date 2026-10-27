# 必要 initializer 的三個 leaf providers

[English](readme.en.md) · [原 caller initializer](../tsl9-resident-init-5362e/README.md) · [NVM layout](../tsl9-NVM-record-layout/README.md)

新增 [C/C++](resident_init_leaves.c)，三個完整本體共 **90 CODE bytes／28 指令**，實際 C11／C++17 物件相同，10 個正尺寸 FUNC、6 筆 direct-branch relocations 與原始 SDK bytes 全部吻合。三者皆無自身 frame、callee 或 CSR 指令，本輪沒有 custom 指令；保留原始暫存器與控制 ports，不是恢復出的原廠 C 原始碼。

| 本體 | 完整範圍 | Bytes／指令 | 原始作用 |
| --- | --- | --- | --- |
| `0x43E24` | `0x43E24..0x43E6A` | 70／22 | Fresh LHU `0x2000323E`，返回0..7數值級距 |
| `0x55BD4` | `0x55BD4..0x55BDE` | 10／3 | incoming A0 word → `0x200034E0` |
| `0x55C48` | `0x55C48..0x55C52` | 10／3 | incoming A0 word → `0x200034E8` |

相鄰的 registration／search 函式沒有選入。兩個 setter 不強制清零，A0 亦不被改寫；只有原 initializer 的特定 calls 明確傳0。

## Unsigned halfword 的完整數值分區

原始 LHU 一次讀取 unsigned16 input；6 個 unsigned branches 與最後 SLTIU 的 operand、常數與 CFG 均已獨立解碼：

| Input（含兩端） | A0 result |
| --- | --- |
| 0..20 | 7 |
| 21..30 | 6 |
| 31..50 | 5 |
| 51..75 | 4 |
| 76..100 | 3 |
| 101..150 | 2 |
| 151..250 | 1 |
| 251..65535 | 0 |

這是由原指令導出的完整、不重疊 unsigned16 數學分區，沒有執行 HOST model／ISA 或產生測試輸入。source halfword 的物理單位與協議欄位名稱仍未證明。

原 caller `0x5362E` 在 `0x536FE` 呼叫 classifier，之後沒有改寫 A0，於 `0x53718` 使用原 `qk.c.sb a0,3(s0)` 將結果存至 state `0x200033BB`。在 ROM／callee／memory／IRQ／alias 等契約成立時，此 byte 的值域為0..7；沒有觀測實機值，也不把它當作初始化成功或硬體相容性的判定。

## 相鄰308 bytes 的條件零值請求

前輪已核對 initializer 的296-byte memset request、獨立 zero word，以及兩個 calls 的順序。本輪明確補上 calls `0x5365A`／`0x53660` 所傳 A0=0 的真實 providers：

| 原始請求 | 數值區間（半開） |
| --- | --- |
| memset0／296 | `[0x200033B8,0x200034E0)` |
| `0x55BD4` 的 word store（此 caller 傳0） | `[0x200034E0,0x200034E4)` |
| initializer 原有 zero word | `[0x200034E4,0x200034E8)` |
| `0x55C48` 的 word store（此 caller 傳0） | `[0x200034E8,0x200034EC)` |

這些請求數值上連續涵蓋 **308 bytes**；兩個 setter 保留 SP／GP／RA／saved registers，沒有其他 calls 或 CSR effects。仍需要有效記憶體、原 ROM／callee 契約、無 fault／非同步干擾與 alias 等條件。initializer 後續的非零 fields／callback stores 完整保留，**沒有宣稱返回時308 bytes全為0，也未證明 RAM 所有權、初始化原子性或 binding 前無 dispatch**。

[leaves_abi.c](leaves_abi.c) 的 RV32 word／halfword／pointer 與308-byte數值範圍 assertions 已以 C11／C++17 編譯；物件相同且沒有 allocated bytes、provider、import 或 executable entry。

## 部分連結與使用

實際 C／C++ 非載入 ET_REL 組合為 **21,006 CODE＋256 DATA／7,191 指令**，1,350 個正尺寸 FUNC、1,017 relocations；所有 input bytes／symbols／relocations 保留，原始 CODE 位址不重複，兩個獨立 ELF reader 一致。三個原缺口均有真實本體、無新增 code imports，因此具名依賴由15降為 **12**，沒有 stub。這不封閉其他間接呼叫與 runtime memory effects。

[證據](evidence-v1.json) · [收據](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-init-leaves/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機 APP／SDK、前輪 native artifacts 與 Windows NDK LLVM；不下載依賴，其他平台未驗證。APP維持159 C/H、95.54%位元組覆蓋率（不是功能完成率）。4-byte啟動來源缺口、設定writer額外144／123-byte來源初始化、NVM映射及 ROM／RAM／ISA／IRQ／Flash／OTA 相容性仍開放。

未連入 APP、未產生新 BIN，沒有目標／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。後續唯讀診斷候選為 raw bucket 與初始化 request span 顯示，尚未實作 UI，不修改 live fields 或 RF／IRQ 設定。
