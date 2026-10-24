# 狀態組裝與通知 C/C++ 重建

目前選用 [state_events.c](../../src/native/receive/state_events.c)，來源為 `src/state_events.v2.c`。它需原位址、區段相鄰與原機暫存器契約；不是一般可獨立呼叫的 C API，也不是可燒錄 BIN。

| 原始範圍（結尾不含） | bytes | 指令 |
|---|---:|---:|
| `137C0–13B4C` | 908 | 314 |
| `13B4C–13BA6` | 90 | 42 |
| `13BA6–13BD2` | 44 | 14 |
| `13BD2–13C4E` | 124 | 46 |
| `13C4E–13CDC` | 142 | 45 |

同一份來源以 C11／C++17 實際編譯，1308B／461指令在依原始位址計算控制及函式指標重定位後全部吻合。C 實作 free-bank 位元、常數與一般記憶體操作；SP／GP／S 暫存器、frame、PC 與控制保留明示架構 port。每個 opaque call 結束一個區域，後續重新取當時的實體暫存器。

- `author-v2.py` 只做固定範圍的靜態來源轉寫；不模擬暫存器／記憶體、不執行目標。
- v1 正常產物為1752B，因 LLVM 加入 SP／GP 搬移而未通過原始碼比對；舊來源、checker 與產物均保留，沒有放入目前的 `src/`。
- `integrate-v1.py` 實際部分連結為7346B code＋60B table，676 FUNC／498 RELA／93 UND；接通2舊入口並揭露27新getter。FUNC是架構區域符號數，包含既有零長度alias，不代表676項功能。
- 既有81B0完整26B C實作重用；每筆global／local重定位的符號、區段與位置均檢查。沒有新ABS provider或alias替代實作。

從專案根目錄重驗；`LLVM_BIN` 為既有且雜湊吻合的 Windows LLVM18。其他主機／工具鏈尚未驗證；原始產物保留本機：

```sh
python -B experiments/tsl9-state-events/build-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-events/build/trial-v2
python -B experiments/tsl9-state-events/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-events/build/graph-v1
python -B scripts/check-state-events-publication.py
```

沒有 HOST／ISA／硬體執行、合成破壞案例、新 BIN 或推送。[證據與未知事項](../../analysis/state-events-2026-10-23/README.md) · [English](readme.en.md)
