# 完整 clock 與 reset 狀態的條件式保留

[English](readme.en.md) · [前輪 reset／bootstrap](../tsl9-reset-state-bootstrap-contract/README.md) · [目前正式重建](../tsl9-event-word-table-integration/README.md)

已核對 `boot_original.c` 中 `0x1874A..0x18834` 的完整 **234B／93 指令**，包含 `0x18830` cold-path store 與 `0x18832` 回跳。全部原始 bytes 與目前 C11／C++17 原位址 ELF 一致，整個 CFG 可達、16-byte frame 在正常 return 還原。舊 `clock_init.c` 的 232B 診斷版本屬歷史來源，這份證據使用完整原廠路徑。

## CPU 存取與返回契約

使用有限 CFG 常數資料流分析，保留所有分支、將每次記憶體讀回值視為未知，沒有讀取 MMIO／RAM 值或模擬目標執行。22 次 word load、21 次 word store 的有效位址全部可證明為以下五個數值：

| 區域角色 | 位址 |
| --- | --- |
| 暫定 MMIO | `0x40021000`、`0x40021004`、`0x40021008` |
| 原始自身 frame | `0x2000FFF8`、`0x2000FFFC` |

上述角色仍依原始有效、非 alias 記憶體配置為條件，不代表已驗證實體周邊或 SRAM 映射。

- 全部明確 CPU store 均避開前輪四組、十個 counter／sequence／mode bytes。
- `0x18830` 原始 `SW zero,12(SP)` 寫到 `0x2000FFFC`，cold store 與回跳均納入證據。
- 函式沒有其他 callee、CSR 或 GP／RA 寫入。由 caller 的 GP=`0x20004000`、SP=`0x20010000`、RA=`0x18724` 進入時，唯一正常 return `0x1882E` 保留相同 GP／SP／RA。
- 第一次 MMIO load `0x1874E` 仍早於 `0x18754` 的 frame allocation，沒有把這項存取順序移動到 frame 之後。

## 對啟動狀態的意義

前輪已證明正常 reset 清零流程到 `0x186F8` 時，四組狀態為零，且候選 bootstrap 的明確寫入範圍避開它們。本輪補上中間 clock 的明確 CPU store 與正常返回契約。因此，在下列條件成立時，可將零值保留的條件式推論延伸經 clock 至已知 bootstrap／MRET 路徑：

1. 原始位址、進入暫存器與指令語義相符，所有存取有效且正常完成。
2. MMIO／SRAM 非 alias，沒有 IRQ／DMA、MMIO 引發的間接寫入、fault 或重入干擾。
3. clock 輪詢抵達正常 return；候選 resident code 與來源記憶體相符，包含仍未提供的 SDK 第二次 copy 來源四個 bytes。

**這不是實機啟動完成、實際 MRET 值或第一次查表值的證明。** clock 的周邊副作用、輪詢 liveness、頻率、IRQ 狀態、installed ROM、後續寫入與 callback 順序仍未封閉。原始輪詢／cold path 均保留，不強制成功，也沒有以這些條件宣告全域 mode／counter 值域。

## 重播

保留固定的本機 native 產物與 LLVM 時，在 repo 根目錄執行：

```sh
python3 experiments/tsl9-clock-reset-noninterference/check-v1.py --tool-dir "$LLVM_BIN"
```

[輸入](inputs-v1.json) · [完整位址／暫存器收據](verification-v1.json) · [待實作診斷構想](feature-candidates.json)

正式 APP 來源與 native 產物未變，仍是 **164 個 C/H、95.75% 靜態位元組覆蓋率、六個未解析 source provider**。沒有新韌體 CODE／DATA、BIN、target／HOST model／ISA 執行、硬體或第三方 API 操作。
