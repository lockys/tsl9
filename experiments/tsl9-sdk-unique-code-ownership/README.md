# SDK 原始位址 CODE 去重

[English](readme.en.md) · [前輪 RF 銜接](../tsl9-original-RF-bridge/README.md)

修正同一個完整 SDK 本體 `0x63C54..0x63D6A` 被兩個名稱重複收錄的問題。保留較早且已有實體 bytes 的 `tsl9_candidate_register_config_63c54`；重新產生三個依賴本體的 C/C++，共 840 bytes／289 指令。沒有新增獨特 CODE，也未加入 stub 或 ABS 函式。

## 已驗證

- 舊組合的實際回歸檢查失敗：278 個原始位址 bytes 各有兩份配置；16 對 FUNC 區段的 bytes 與位址化 relocation 相同。原因是舊檢查僅確認 section／symbol 名稱唯一。
- 新組合通過唯一性檢查：**12,658 CODE＋256 DATA bytes／4,412 指令**，1,037 個 FUNC 區段、781 個 relocation、19 個未提供的具名依賴。FUNC 區段數不是邏輯函式數。
- 去重前後的完整原始 PC → native byte map、typed relocation 關係集合、DATA bytes／屬性／alignment 及未提供依賴完全相同。減少的 278 bytes／95 指令／9 relocation 是重複配置，不能計為新重建進度。
- C11／C++17 物件完全一致；三個完整 CFG 的自身 frame 平衡、逐輸入 bytes／symbols／relocations 與兩個 ELF readers 通過。先前完整靜態驗證鏈亦重新通過。

舊來源與收據保留；先前 12,936 CODE bytes 是當時實際配置量，包含上述重複。新檢查的「原始 PC」是來源契約，並非已完成實體原址連結。

APP 仍為 159 個 C/H、95.54% 位元組覆蓋率；不是功能完成率。未產生新 BIN、未整合進 APP、未執行目標或模型、未連接硬體。4-byte 啟動來源缺口、實機 ROM／RAM／ISA／IRQ、全程 stack／alias、Flash 與 OTA 相容性仍未確認；**尚未成功重建可用替代韌體**。

[C/C++](unique_dispatch.c) · [回歸檢查](verify-ownership-v1.py) · [完整收據](audit-result-v1.json) · [摘要](summary.json)

## 重現

需備齊 spec 固定的本機輸入、先前 native artifacts、Windows NDK LLVM 與 trap 驗證的官方 header；不會自動下載缺少的輸入。

```sh
python experiments/tsl9-sdk-unique-code-ownership/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-sdk-unique-code-ownership/build/native-v1
python experiments/tsl9-sdk-unique-code-ownership/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
python experiments/tsl9-sdk-unique-code-ownership/verify-ownership-v1.py --object experiments/tsl9-sdk-unique-code-ownership/build/composition-v1/c/candidate.o
```

建立新產物時，第一行用 `--trial` 取代 `--replay`，第二行加 `--link-trial`，名稱均須未存在。工具 pins 為 Windows LLVM；跨平台編譯未驗證。
