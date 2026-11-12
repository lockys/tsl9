# V4.1.60 TX 差異來源：固定全圖靜態稽核

此實驗只讀取兩個固定完整影像，不執行或模擬 target、不編譯、不連網、不接觸硬體，也不輸出影像或可燒錄產物。全圖讀取包含 TX 以外的所有區域；這不同於只讀有限窗口、且有排除區的 [TX guard 比較](../tsl9-tx-guard-compare/README.md)。

* 原廠標示：`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。
* 固定候選：`artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin`，SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。

兩者均為 76800 bytes；雜湊只固定本機檔案身分，非來源認證。映像 offset 0 對應地址 `0x8000`。核對 93 個差異位於五個不連續半開區間 `[0x8a7f,0x8a81)`、`[0x8ad3,0x8ad5)`、`[0x8b11,0x8b12)`、`[0x8b13,0x8b5c)`、`[0x8b5d,0x8b6c)`，均在 TX `[0x8a56,0x8b6e)`。另外直接比較 TX 前後記憶體，並在記憶體中兩向替換完整 280 bytes，各自與另一全圖逐 byte 比較；不寫出替換結果。

## 來源與界線

候選的**歷史 producer**不是現在的正式 owner：候選 [provenance.json](../../artifacts/offline-images/ID2966-V4.1.60-tx-integrated/provenance.json) 記錄歷史 C/C++ receipt 與映像雜湊；[歷史整合說明](../tsl9-v4160-tx-image-integration/README.md) 描述來源載體、ABI 排序及產出，其 [source-manifest.json](../tsl9-v4160-tx-image-integration/source-manifest.json) 指向 [entry.S](../tsl9-v4160-tx-image-integration/adapter/entry.S) 與 [valid_body.c](../tsl9-v4160-tx-register-abi/adapter/valid_body.c)。這是記錄的 producer 脈絡，非本次重建驗證。

目前 `src` 正式原座標 owner 是 [transport_frame.c](../../src/native/receive/transport_frame.c)，明載 private ABI、S 暫存器、frame、opaque calls 與 inline asm；不應把它誤稱為上述固定候選當年的 producer。[src/native/tx_candidate/valid_body.c](../../src/native/tx_candidate/valid_body.c)、[entry.c](../../src/native/tx_candidate/entry.c) 和 [tx_io.h](../../src/native/tx_candidate/tx_io.h) 另保存候選式邏輯與明示暫存器／inline asm ports。歷史 producer 和現行 owner 均不能因檔名或相似邏輯而視為同一建置。此處沒有重新編譯，沒有證明現行來源產生該固定候選或完成純 C 重建；將原廠 raw bytes 替換進候選只是位元組恆等的對照，不等於還原來源。

既有 guard、迴圈及尾端比較只在明示前提下支持有限局部對照，不能推出整體行為等價、ABI、例外／中斷、ROM、裝置相容或可燒錄性。本稽核不增加這些行為證據。

## 執行

從 repository 根目錄：

```sh
python -B experiments/v4160-tx-difference-provenance/audit.py
python -B experiments/v4160-tx-difference-provenance/test_audit.py
python -B -O experiments/v4160-tx-difference-provenance/audit.py
python -B -O experiments/v4160-tx-difference-provenance/test_audit.py
```

測試獨立檢查函數對影像長度／雜湊、差異地址、範圍／TX 外，以及兩個方向 swap 的負例。無 `assert`；最佳化模式仍執行檢查。兩個影像缺失或 pin 不符即失敗。
