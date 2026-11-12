# V4.1.60 `0xb0b0` 回傳值隔離候選

`leaf.c` 是純 C 候選：對 volatile byte lvalue 寫入參數低 8 bit，然後回傳原始完整 `uint32_t`。預設 lvalue 為 `0x2000beeb`，只有在該位址確實可供 byte 寫入時才有意義；不宣稱位址可寫或有任何硬體效果。這是獨立的新函式，不修改既有 void 候選或正式 `src`。既有 `void v4160_b0b0(uint32_t)` 與此 `uint32_t v4160_b0b0_return_value(uint32_t)` 的函式型別不相容，不可透過轉型、相同符號或函式指標互換。

`host_harness.c` 是未執行的測試設計，在同一 translation unit 注入三個 volatile byte 的主機 stub，檢查中央 byte、前後 sentinel 與完整返回值；測試所有低 byte，搭配零、`0x123456`、`0xffffff` 高位。不可另外連結第二份 `leaf.c`。stub 不映射目標記憶體，亦不能驗證目標硬體。

唯讀固定 BIN：`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，offset 0 對應 `0x8000`。窗口 `[0xb0b0,0xb0ba)` 固定為 `97 17 00 20 a3 8d a7 e2 82 80`；既有局部靜態解讀為 AUIPC、SB、ret，見 `experiments/v4160-b0b0-direct-edge-evidence/README.md`。窗口比對不是指令解碼或 C 語意證明。

## 離線檢查

```
python -B experiments/v4160-b0b0-return-value-candidate/verify.py
python -B experiments/v4160-b0b0-return-value-candidate/test_verify.py
python -B -O experiments/v4160-b0b0-return-value-candidate/test_verify.py
```

`verify.py` 也固定檢查此目錄三個檔案的原始位元組 SHA-256：

- `leaf.c`: `125459d53d0c9a111b2f28d7b5949b9945b64de777fc13403b5fb2849dadee56`
- `leaf.h`: `4c16e55b67d349cd1fbc04aaeeb01d299239cf934eb4f53ecdd1cdd90daf4e77`
- `host_harness.c`: `30fc6866a3ba570413a88d2f3b011c60c009f2397f2ba709f3472693d2a5a9c3`

這些 pin 只確認檔案身分，並非語意、正確性或 C 與 BIN 等價證明。測試身份長度、雜湊、每個窗口 bit 翻轉、截斷及窗外變動；另對每個 C 檔測試位元翻轉、截斷、附加與缺檔，不依賴 `assert`。此 Python 驗證不檢查 C 與 BIN 等價。本次沒有編譯或執行 C；沒有 ABI、codegen 或完整 caller 證明，也沒有網路、硬體、目標執行或模擬、設定變更。靜態窗口本身不能證明實際呼叫、返回或寫入。
