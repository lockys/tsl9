# Compact OTA handler producer 與證據

[English](readme.en.md)

正式 `verify_native.py` 直接編譯新 model C/C++ 來源，保留 9 個真 UND；不 link、不輸出 BIN。最後實測 568B／193 instructions／frame48／20 RELA（12 JAL＋4 HI20＋4 LO12）。原530B仍超出38B，完整ABI／placement／硬體OTA為false。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/check.py --project-root .
```

發布版路徑使用 analysis/v4160-ota-handler-compact-2026-10-22。fresh預設新UUID scope，可指定model/build內尚不存在的 --build-root。source/tool/header皆before/after pin，產生的logs/artifacts則完整列hash；四exact recipes與完整raw ELF／LLVM bytes、MD三project sources＋實際stdint.h可replay。沒有新增flags／fixed-register profile，未編譯原始BIN作模板。

`check.py` 預設只驗來源、seal、metadata，actual flags false；只有明示 `--host-receipt PATH`／`--native-receipt PATH` 才唯讀重驗實體archives。四份selected receipt metadata在receipts/，results.json含工作樹實體位置及hash，該位置不構成發布預設依賴。

唯一無效假設為no-unroll：實際payload與baseline776完全同hash。兩個有效source調整是response object分離和原shared reply labels恢復。hypotheses.json保留實際776→592→568的證據身份；歷史build及source snapshots留W、不發布、不宣稱預設archive replay。最終HOST每語言10/8292＋3 compiled negatives。

ABI-review承擔新source-delta／effects／獨立HOST與native審查；callee-review是有界callee候選證據，不能冒充新原始rawsourceconsumer review。原530B raw169rows證據沿用上一輪封存source-review。兩候選resident leaf或App callee不代表已裝ROM，不能用來移除八暫存器橋。

保留私有C response及一般callee保存條件；不宣稱原始SP、pointeralias、rawGPR、RA、async完整等價。frame大小相同不足以提升admission。沒有執行RISC-V／模擬／網路／硬體／UID或VIN存取，也未改舊fullimage。
