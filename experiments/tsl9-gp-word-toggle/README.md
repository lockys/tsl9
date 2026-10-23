# 9B36 原生 C/C++ 靜態驗證

[English](readme.en.md)

選用 `src/toggle.v2.c`：24B／7 指令與原廠完全相同；`toggle.v1.c` 是26B early-return 試作，未選用。來源使用普通 C 條件與 volatile 記憶體存取；空 asm 僅綁定 then-live GP／A4／A5。不能當成一般 C ABI 函式呼叫或在 HOST 執行。

以下命令依賴本機已封存的1902B parent物件、當前來源整理收據／物件及原始BIN；這些私有建置產物不隨Git發布。缺少時立即停止，不會下載或重建替代證據。

於專案根目錄設定 `LLVM_BIN` 為已安裝的 LLVM bin 路徑。以下命令只編譯、連結及讀取檔案，不下載套件或執行產物：

```sh
"${PYTHON:-python3}" -B experiments/tsl9-gp-word-toggle/build.py --tool-dir "$LLVM_BIN" --output experiments/tsl9-gp-word-toggle/build/my-check
for mode in c cpp; do
  "${PYTHON:-python3}" -B experiments/tsl9-gp-word-toggle/verify-v3.py --tool-dir "$LLVM_BIN" --folder "experiments/tsl9-gp-word-toggle/build/my-check/$mode" --mode "$mode" --write
done
```

輸出目錄及收據只准新建。正式既有產物可把 folder 指向 `build/formal-v1/c` 或 `cpp` 並移除 `--write`，逐位元組核對 `verification-v3.json`。這是當前來源／依賴及固定工具鏈的唯讀核對，不會重新編譯。工具與 stdint 雜湊不符即停止。

`LEAF-ONLY-NOT-FIRMWARE.elf` 僅把24B leaf 放在原位。`UNRESOLVED-FULL-PLUS-LEAF.o` 是1926B診斷部分連結，保留97個待解析控制 relocation與三個UND，沒有可用韌體入口。兩者均不得轉成可刷韌體宣稱。

`spec.json` 的 `native_ELF_sha256` 是原始檔名 `toggle.v2.c` 的 probe 物件；正式 curated 物件的檔名／STT_FILE 為 `gp_word_toggle.c`，其整檔雜湊另由 v3 固定。機器碼均為 `3629ae9c699510146a50485e475c373cdf2ea385d086633b70f1cfc43a88fb79`。

v1／v2收據保留作歷史證據；最新v3補上完整命令、實際依賴、LLVM讀回位元組、UND metadata、固定IR body及唯讀收據比對。不要用舊檢查器的1985負例宣稱已涵蓋獨立審查找出的六個漏檢。

[分析與限制](../../analysis/gp-word-toggle-2026-10-23/README.md)
