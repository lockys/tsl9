# Callback 原生暫存器實作證據

[English](readme.en.md)

本 scope 的正式 producer 是 `verify_native.py`，或 model 的 `verify.py / verify.sh`。它會重新編譯三個來源，以已封存旗標加上唯一的 x26/x27 reservations，再明示呼叫新 `postpass/frame.py`，最後由標準 linker 產生 scratch-address 元件。**正式 C11／C++17 都是 624 bytes、223 指令；完整 ABI／632-byte 原址整合仍未通過。**

```sh
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/pinned/llvm/bin --language both
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/verify_native.py --project-root . --replay /absolute/path/to/ordered/c/verification.json
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/check.py --project-root .
```

工作區的同一資料夾前綴為 `apk-analysis/tsl9-`；正式發佈 checkout 使用 `analysis/`。runner 同時辨識兩者。Windows 可用 `python -B`；POSIX wrapper 可設定 `PYTHON`。目前 pinned 工具是實測 Windows NDK LLVM，尚未宣稱其他平台 compiler 身份／執行結果。

預設新 UUID build，或 `--build-root NEW` 指定此 model/build 下不存在的目錄，拒絕覆寫。輸出：

- `pre/{c,cpp}/probe.json`：五個原始 compiler/resource/IR/link/disassembly 步驟與原始 object/ELF。
- `ordered/{c,cpp}/frame-order.json`：只移動原始 object 兩個 2-byte C.SWSP words，保留每個其他 ELF byte。
- `ordered/{c,cpp}/verification.json`：正式來源、resource header、工具、IR、machine、排序與產物 readback。
- stdout JSON：`passed` 與兩個 `results`，每項含 `mode`（由 selected index 對應）、`receipt`、`sha256`、`native_bytes=624`、`instructions=223` 及明確 false admission flags。

八個工具步驟為七個 LLVM commands 與一個明示 Python 排序 command；外層 Python generator 啟動另有 argv／exit／log／hash 身份。原始 MD 恰好三個 project sources 加一個實際 Clang resource `include/stdint.h`，非廣泛掃描 header。

`results.json` 與 `receipts/*.json` 是 byte-identical 選定正式 metadata，含原本本機絕對位置；發佈並不附 object/ELF/IR/log archives。`check.py` 預設只檢查封存來源、來源變換與 selected metadata，**actual_native_artifacts_read=false**。提供 `--receipt NEW_VERIFICATION` 才讀回明確指定的本機產物；`--require-local-builds` 專供原始 W archive 存在時使用，缺檔會失敗，不假裝重播。Fresh D/P checkout 應先以 producer 新建自己的 receipt。

`probe.py`（656B）、`probe_gp.py` 的 first-gp 診斷與未封存 build 中間成果是歷史探索。`probe_gp.py` 同時是正式 producer 的固定 raw-generation substage，但單獨成功不代表已經執行保存排序或正式驗證。`machine.py` 是 producer 自身 field/coverage gate；獨立 `ABI-review` 的 raw/frame/ordered review 與 `source-review` 分別保留自己的結論與封存，不混為同一項測試。

source3 與 HOST 展開身份已固定；這輪沒有重新跑未變更的 HOST suite。原生沒有 x26/x27、GP writes、SP+0 spill、hidden helper／UND；有六個 live-GP operands、15 個 opaque calls、48B frame 及11對 saves/restores。新 pass 只恢復相對 stack-save 順序，沒有恢復原版 SLLI-before-store 全 prefix、opaque RA/frontiers 或全部 physical GPR residue。原632區段仍有8-byte尾端未建立所有權，沒有補 bytes、沒有 BIN、沒有 fullimage 更新。硬體、ROM preservation、實機 BLE/OTA 皆未驗證。
