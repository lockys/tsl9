# 324B原生記錄路徑驗證

[English](readme.en.md)

選用`src/record_program.v3.c`，整理副本為`src/native/receive/record_program.c`。v1／v2失敗試作及所有原收據保留。19個private regions依nominal.ld固定原始位址，整段324B與原廠相同；joined.ld只產出2250B診斷ET_REL，並非可執行韌體。

命令需要本機已封存的1926B父物件、舊13來源的嚴格證明、當前來源整理收據／物件、原始BIN，以及已安裝且雜湊相同的LLVM。這些私有建置物件不隨Git發布；缺少即停止，不下載替代資料。

於專案根目錄設定`LLVM_BIN`後：

```sh
"${PYTHON:-python3}" -B experiments/tsl9-record-program/build.py --tool-dir "$LLVM_BIN" --output experiments/tsl9-record-program/build/my-check
for mode in c cpp; do
  "${PYTHON:-python3}" -B experiments/tsl9-record-program/verify-v2.py --tool-dir "$LLVM_BIN" --folder "experiments/tsl9-record-program/build/my-check/$mode" --mode "$mode" --write
done
```

目錄及收據只准新建。正式既有結果位於`build/formal-v1/{c,cpp}`，移除`--write`即唯讀重算並逐位元組核對`verification-v2.json`。v1收據是歷史資料；v2補上nominal FUNC實際所屬區段及範圍檢查。原始檔名與curated檔名的STT_FILE不同，整檔ELF雜湊不可混用；程式碼與原廠的比對才是本文局部結論。

腳本只編譯、連結及讀取資料；不執行HOST行為模型、ISA或硬體。資料、控制、frame與暫存器埠均需要原始配置，不能當作普通C API呼叫。

[分析與限制](../../analysis/record-program-2026-10-23/README.md)
