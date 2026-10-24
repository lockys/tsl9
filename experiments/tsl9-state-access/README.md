# 狀態存取 C/C++ 重建

來源：[state_access.c](../../src/native/receive/state_access.c)。完整原始範圍為 `82A8–82D2`、`10032–10158`，共 336B／108 指令，分為 24 個架構區域；同一份來源以 C11、C++17 實際編譯後，依原始位址計算跳轉的 336B 全部吻合。

這些區域需原位址與相鄰配置，不是可獨立呼叫的一般 C ABI 函式。C 實作記憶體與算術；PC、控制及暫存器交接保留明示架構 port。ROM、索引界限、IRQ、欄位用途與原硬體仍未證明。

- `build-v1.py`：一般編譯／唯讀重驗；`trial-v1` 兩語言皆通過。
- `integrate-v2.py`：真實部分連結與全輸入／符號／relocation 檢查；6038B code＋60B table、485 FUNC、435 RELA、68 UND。
- 485 FUNC 包含一個長度為 0 的 linker alias，指向已證明的 24B 原有 C provider，並非新增實作。第一次檢查預期 alias 長度為 24，失敗的 `integrate-v1.py` 與 `build/graph-v1` 均保留。
- 沒有合成破壞案例、HOST 模型、ISA 執行、硬體操作或新 BIN。

從專案根目錄重驗；`LLVM_BIN` 須指向既有、雜湊吻合的 Windows LLVM 18，未下載工具或驗證其他平台：

```sh
python -B experiments/tsl9-state-access/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-access/build/trial-v1
python -B experiments/tsl9-state-access/integrate-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-access/build/graph-v2
python -B scripts/check-state-access-publication.py
```

[證據與未知事項](../../analysis/state-access-2026-10-23/README.md) · [English](readme.en.md)
