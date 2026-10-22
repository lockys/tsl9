# 狀態讀取與旗標更新：16FB6

[English](readme.en.md)

官方 ID2966 V4.1.60 的 `[0x16FB6,0x17002)` 是76B／21指令；捕捉到的向量表 slot39 存放 `0x16FB6`。目前可讀 C 的核心操作是：

1. 即時讀取 `0x40010414` 的32-bit值；若 bit64 非零，向同址寫入64，再以當時 GP 讀取 `GP+360` 的 byte、OR1後寫回。
2. 重新讀取 `0x40010414`；若 bit128 非零，向同址寫入128，再重新讀取當時 `GP+360` 的 byte、OR2後寫回。
3. 以最小架構 port 執行 MRET。

兩次讀取不合併，兩個 flag byte 操作不共用快照；MMIO 與 flag byte 存取使用真正的 volatile。C 保留所有運算／條件，空 A4／A5／GP port 固定原始 register boundary，沒有 opcode carrier。正常 MRET 前若第二bit未設，A4=0／A5=`0x40010400`；若已設，A4=128／A5=當次新讀byte OR2。只自行寫入 A4／A5，沒有額外 frame、GP／SP／RA 寫入或 call。

## 證據與限制

初版因需要已保留的 SP 而編譯失敗；調整等價 C 資料流後的本機 `build/probe-v1` 是74B／20指令，仍未通過全文比對，該來源快照與收據保留。明確固定原始base形成／branch順序後，`build/probe-v2` 的C11／C++17物件完整等同原76B／21指令。

正式元件使用 `rv32imac_zicsr`；整理後 `src/` 使用另外實測的 `rv32imac_zicsr_zifencei` profile。兩者都只允許 A4／A5 配置並使用 `-Oz`，函式碼錨點相同，不宣稱其整個 ELF 或旗標相同。來源與工具鏈固定雜湊，不搜尋旗標或下載依賴。

整理後來源可用專案根目錄的 `python3 scripts/verify-curated-source.py` 核對；Windows 可用 `py -3`。本機正式收據及公開資料另見 [分析摘要](../../analysis/init-write-sequence-2026-10-23/summary.json)。

正式本機收據為 `build/verified-v3/{c,cpp}/verification.json`，每語言23項負例；四個實際ELF保留完整76B。原收據CRLF與雜湊保留本機，公開收據以明示LF wrapper保存全部JSON，不能冒充byte-exact原收據。UND／ABS provider為零，local FILE／mapping ABS metadata另列。

```sh
python3 experiments/tsl9-irq-flag-leaf/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --build-root experiments/tsl9-irq-flag-leaf/build/my-run
python3 experiments/tsl9-irq-flag-leaf/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --replay experiments/tsl9-irq-flag-leaf/build/my-run/c/verification.json
```

MRET 是特權返回，不是普通 C return；它的狀態作用、向量模式、IRQ保存上下文、周邊身分、實體RAM／ROM及完整APP／OTA相容性仍未證。捕捉到的82-word向量視圖不等於已確認IRQ數量。**這不是可刷寫BIN；未執行／模擬RV32／MMIO，也沒有操作硬體或網路。**
