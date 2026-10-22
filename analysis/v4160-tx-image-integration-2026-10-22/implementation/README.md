# TX 完整映像實作證據

[English](readme.en.md)

正式入口為 `verify_image.py`，或 model 的 `verify.py` / POSIX `verify.sh`。它以封存的 12-region 來源流程為基礎，fresh 編譯 46 個來源單元，明示執行 reply、TX、IRQ/quarter 三個 ABI 排序步驟，再 partial link、嚴格缺 ROM 失敗檢查、數值 ROM witness link 及匯出新離線 BIN。原始 BIN 僅驗證差異，沒有作為生成 fallback。

`prototype.py` 是正式 producer 釘選的實際生成子階段，單獨呼叫只有原型子集檢查；不能用它的 `passed` 取代正式 admission。`tx_order.py` 是新 namespace 的 driver，呼叫 immutable TX 十個已編譯 word 的 transform/policy API，不修改舊腳本，也不生成 opcode。`prepare_manifest.py` 只建立 source ledger，不是 runtime producer。

```sh
python -B PATH/verify_image.py --project-root ROOT --tool-dir LLVM --language both
python -B PATH/verify_image.py --project-root ROOT --replay RECEIPT
```

建置輸出 `BUILD/{c,cpp}/verification.json`；stdout 包含 `passed` 與每種語言的 `receipt`、`sha256`、`image`、`image_sha256`。預設 UUID 新目錄或明確 `--build-root` 都拒絕覆寫；目錄必須位於 model/build。重播拒絕 build-only 選項。`--firmware` 在 build 與 replay 都作同雜湊原始映像定位。

正式檢查核對完整 artifact 集合、67 個 exact chronological recipes、外層 generator/query 及 log/exit、工具和來源前後穩定性、45 個 MD target/primary/forced-include 關聯、實際 compiler resource header、三個 pre/post 排序證據、所有 ELF metadata/provider/RELA 角色與 LOAD/BIN coverage。17 個實際 ELF/重定位/映像 byte 反例及 7 個來源依賴/recipe/排序證據反例必須拒絕。獨立 source/ABI review 另有自己的 oracle 與反例，避免把 producer 自查等同獨立驗證。

實際 inventory：13 regions/930 bytes、15 truthful FUNC providers；691 allocations/678 retained sections；8,246 outside RELA + 12 prior typed JAL + 3 TX RELA = 8,261；53 canonical bindings；29 outside incoming；15 LOAD。canonical TX FUNC280 明確改為真實 FUNC8，後接 LOCAL270/GLOBAL2。原 TX 七個控制標籤與 PCREL anchor 的變更不能混為八個 branch discharge。

新 C/C++ 映像相同，SHA256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`；93 byte 差異全在 TX280，外側完全相同。數值 ROM witness 不證明實際 ROM、硬體、燒錄或 OTA。全 ABI、computed targets、故障/中斷觀察仍保留未確認。

`check.py` 預設只驗封存 source/metadata，不讀歷史 build archives；`--receipt` 才重播指定實體產物。`--require-local-builds` 要求選定的本機 archives，適用保留它們的本機工作區。發佈會保留選定 JSON metadata，不包含 `.o`、`.elf`、`.ll` 或完整 logs/build archives；BIN 另作明示實驗 artifact。
