# NV read callback 的獨立原生審查

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

本審查直接讀 C11／C++17 的 ET_REL、全部 symbol／section／RELA、原始指令欄位、LLVM 靜態文字、IR、成功 log 及完整 `-MD` 閉包。沒有以 producer 的 replay 當作獨立結論，也沒有執行 native、MMIO、CPU／ISA／ESIL、HOST 矩陣或硬體。

兩語言均有一個真實 global FUNC：32 bytes／14 指令，無未用函式，UND／RELA／ABS 皆零。函式 bytes 完全相同，SHA256 `be3e03eacb688e38d8dbebdd509b900520385a2a2084136c4bdbfdd5f5caad3c`。原入口為 30 bytes／13 指令，因此不能就地塞入原範圍。

機器碼的完整 operand 契約及 IR 的完整 def-use 鏈各自核對：新鮮 READ32(0x4004C) 的值成為唯一間接呼叫目標，參數依序為 entry A2、entry A0、uint32(entry A1 左移 2)，忽略 callee 回值，正常返回 A0=0。這是條件式實體暫存器投影介面，不是恢復出原始 C prototype。IR 的 tail 標記沒有被誤認為機器碼 tail jump；實際 JALR 寫 RA，之後仍執行回傳零與 epilogue。

新函式有 16-byte frame、SP+12 的 RA 保存／還原。自有寫入為 RA／SP／A0..A5，比原 wrapper 額外寫 A3；沒有自有 T／A6／A7／S／GP／TP 寫入。callee 的寫入並不包含在這個自有清單。新增 A3 可能在 copy 不迴圈等路徑逃逸，因此未證明 resident caller 或完整原 callee ABI 可替換。

原始 slot load 先於 frame 建立；新編譯結果先調整 SP 並保存 RA，才讀 slot。這個順序差異使 fault／IRQ 前綴等價未通過。正常投影仍要求有效對齊且分離的私有 frame、正常存取、無非同步干擾，以及 fresh slot 確實符合已審查的 copy 暫存器與正常返回契約。不能從標準 C 間接呼叫語法推定實體 ROM 已符合這些條件。

每語言拒絕八個實際反例：五個保持指令形式、只改一個 operand 的 raw byte 反例，涵蓋 slot、word shift、source 參數、RA 保存位置與 call 變 tail jump；另有三個 IR 反例，涵蓋移除 volatile、錯誤長度與互換來源／目的。這些只做有限靜態解析，不執行突變程式。

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --folder /actual/build/c --receipt /new/review.json
python -B check.py --project-root /absolute/project/root --replay /existing/review.json
```

預設僅 metadata；actual 與 replay 均重新讀實物並拒絕反例，不編譯、連結或產生 BIN。`verify.sh` 接受相同參數；因既有 Git Bash 啟動拒絕未重試，shell runtime 尚未驗證。沒有新 provider 身分、Flash ownership、實機更新或可刷寫性證明。
