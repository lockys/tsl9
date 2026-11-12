# V4.1.60 `0xb0b0` 隔離純 C 候選

`leaf.c` 為普通可返回函式：將 `uint32_t` 參數低 8 位轉為 `uint8_t`，經 volatile byte lvalue 寫入 `0x2000beeb`。僅提出此局部語意；不是正式 source，也不包含 inline asm 或 opaque。絕對位址轉指標及該處可寫性依目標實作及環境而定，勿在主機上直接呼叫預設版本。

只讀參考映像 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 `0x12c00`、載入基址 `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。位於 `0xb0b0` 的十 bytes 為 `97 17 00 20 a3 8d a7 e2 82 80`；既有靜態解讀為 AUIPC、SB、ret，其位址算術及 caller 的限定證據見 `experiments/v4160-b0b0-direct-edge-evidence/README.md`。此處不推斷硬體行為或完整 caller。

`verify.py` 固定檢查映像長度、全檔 hash、原始十 bytes，以及 `leaf.c` SHA-256 `81dde947df04c123617fa2fa326ca7f2a78544b461fabbb8ba64ae5a1cd74a4a`。測試也直接對窗口逐 byte 突變與截斷，避免全檔 hash 遮蔽窗口檢查。這些是資料身分檢查，不是 C 行為證明；沒有以 Python 模型代替 C。

`host_harness.c` 是僅供主機的未執行測試設計，將 `B0B0_DESTINATION` 強制注入三 byte host stub 的中央 volatile lvalue，不使用候選預設絕對位址。覆蓋 0..255、兩組每個低 byte 的高位截斷及前後 sentinel。替換 stub 時，可設定 `HOST_B0B0_STUB_HEADER` 為標頭名稱；標頭須定義 `HOST_B0B0_MEMORY` 為至少三個 volatile `uint8_t` 元素的主機記憶體陣列，絕不可映射真實目標位址。harness 與候選需在同一 translation unit，勿另外連結第二份 `leaf.c`。測試注入不是正式介面，也不代表目標硬體。

從 repo 根目錄執行純 Python 資料檢查：

```text
python -B experiments/v4160-b0b0-pure-c-candidate/verify.py
python -B experiments/v4160-b0b0-pure-c-candidate/test_verify.py
python -B -O experiments/v4160-b0b0-pure-c-candidate/test_verify.py
```

原始指令正常返回時保持完整 `a0`、覆寫 `a5`；此候選的 `void` 介面不能保證 `a0` 保持，亦不能保證相同 `a5` 或機器碼，尤其尾跳的上層 caller 可能觀察到差異。既有 guard 的 relocation 集合及原址重編碼對 store 型 PC-relative relocation 的支援亦須另行審核，不能因語意相似而繞過。

本次未編譯、未連結、未執行 C harness、未驗證 codegen、ABI 或 runtime；未模擬或執行韌體，未接觸硬體。通過資料檢查不等於候選可用或與韌體等價。
