# OTA handler 正式編譯與證據

[English](readme.en.md)

本 scope 的 `verify_native.py` 是正式 native producer；共享來源與 HOST 入口位於 `experiments/tsl9-v4160-ota-handler`。原始 530B／169 指令，本輪真實 C11/C++17 各為 776B／285 指令、frame112，9 真 UND、23 RELA。沒有 link、BIN、target execution 或硬體驗證。原始完整 ABI／placement 均 false。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/check.py --project-root .
```

發布版將 `apk-analysis/...` 對應為 `analysis/v4160-ota-handler-2026-10-22`。shell wrappers 以 `PYTHON` 選擇 Python，預設 python3。fresh CLI 支援 `--build-root NEW`，拒絕覆寫且限 model/build；replay 拒絕 fresh flags，不啟動 compiler。

`check.py` 預設只驗 seal、目前來源及選定 metadata，不宣稱讀取 local build。明示 `--host-receipt PATH`／`--native-receipt PATH` 才重讀實際產物，可重複指定。`results.json` 保留工作樹實體 receipt 位置及其 metadata copy；這些位置不是發布環境依賴，缺 build 不影響 metadata-only 檢查。

四個正式 native recipes 包含 resource-dir query、-MD object、LLVM IR、完整 RV32M/A/C/Zicsr 反組譯。replay 核對 exact argv、工具／來源／resource header、所有檔案集合、MD 三來源與 stdint.h、全部機器 bytes。原始 BIN 沒有參與產碼，沒有 fake provider；真正 UND 留待未來實際 section-backed callee 整合。

正式 HOST 每語言 1 group／10 cases／8292 checks，3 compiled negatives；獨立 HOST 16 narratives／18 dispatches／898 checks，4 compiled negatives。HOST 只證明 defined argument subset、live named values 與合成 effects，不證 native full raw8／physical frame／callee S/SP 保存。W 選定 reply 的 A3/A4/A5 修補不是其他站的完整 scratch residue 證明。

`probe.py`／first-native 是 source 修補前的 752B 歷史診斷，不選入正式 receipts。正式 selected metadata 是 `receipts/` 四份；build archives、object、IR、exe 與 logs 不發布。source-review 封存原始 530B169rows／8 raw controls；ABI-review 對 final native 與獨立 HOST 另作審查。完整目標仍未完成，本輪不替換既有 full image。
