# 離線官方來源重現 sparse segments

來源固定為 [openwch/ch32v20x commit ec059e0b18046b111ee850e44f105fcd095e775c 的 EVT/EXAM/BLE/LIB/wchble_rom.hex](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.hex)。請自行以有權限的方式取得 **Git 原始檔 bytes** 或使用既有本機副本；程式不存取網路、不修改輸入。校驗 SHA-256 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5` 和 Git blob SHA-1 `13202d1678c9766117d787d98b4de55ed61fc571`；雜湊確認內容一致，不是對取得管道的獨立身分驗證。倉庫不新增官方大檔。

```sh
python -B scripts/extract_v131_sparse.py --hex <EXISTING_RAW_HEX> --out <NEW_EXTERNAL_REFERENCE_DIR>
python -B scripts/verify-sparse-resident-link.py --project-root . --hex <EXISTING_RAW_HEX> --reference-dir <NEW_EXTERNAL_REFERENCE_DIR> --conditional-dir <BUILD_DIR>/conditional-link --tool-dir <LLVM_BIN> --out <NEW_EXTERNAL_LINK_DIR>
```

輸出目錄必須不存在、位於專案外且不在輸入所在目錄內；原始 HEX 必須保留以供後續獨立驗證。先前 README 的 conditional build 和工具鏈要求仍適用。產生器嚴格解析 HEX、依實際連續位址生成 17 段及 deterministic map，不填空洞；驗證器從固定 HEX 重新推導並逐 byte 比較 map 和每段。舊版固定 map 路徑仍支援。不同於舊 map，新的 map 不包含取得環境或 record 行號。`[0x6eb2c,0x6eb30)` 仍缺失；輸出不是可燒錄映像。

## 隔離實測紀錄

工作樹 `C:/Users/locky/Documents/projects/tsl9-v131-rf-sparse-checkpoint`，HEAD `44049b083af8015db56c83396e4605014a579cdc`，branch `cindy/v131-rf-sparse-checkpoint-20261111`。原有未提交變更包含 `scripts/sparse_resident_evidence.py`、`scripts/verify-sparse-resident-link.py`，以及本工具、測試、文件和本機 HEX 等未追蹤檔；本次另修改 `analysis/v131-startup-source/check.py`、測試及本文件。主工作樹 `tsl9-reversed` 為不同 cwd，HEAD `0dcc6986b7510080d0b18a1a9e1d6d8a1f9c0681`，亦有大量既有未提交檔案；未在該處操作。

以本機 pinned HEX、系統暫存目錄執行兩次抽取，原始輸出（暫存目錄於測試後刪除）：

```text
HEX sha256: 11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5
mode: ['normal'] exit: 0
Generated 17 sparse segments in C:\Users\locky\AppData\Local\Temp\tmp6bkqajn6\normal; not flashable
stderr: ''
mode: ['-O'] exit: 0
Generated 17 sparse segments in C:\Users\locky\AppData\Local\Temp\tmp6bkqajn6\optimized; not flashable
stderr: ''
byte-identical: True
map sha256: 7e5492a19d8de3ef3620599ddcecbe6832eebd21dd1dae1c4a4508f37a39c12c
segments: 17
segment bytes: 191244
```

`python -B tests/test_extract_v131_sparse.py -v` 與 `python -O -B tests/test_extract_v131_sparse.py -v` 均 exit 0，分別輸出：

```text
test_offline_roundtrip_and_negative_controls (__main__.ExtractionTests.test_offline_roundtrip_and_negative_controls) ... ok
test_adversarial_records (__main__.ParserTests.test_adversarial_records) ... ok

----------------------------------------------------------------------
Ran 2 tests in 1.109s

OK
```

`-O` 的相同輸出僅時間為 `1.130s`。對抗案例包括內嵌空白、垂直定位字元、EOF 缺失或後有記錄、重疊、錯誤 checksum/長度/型別/EOF、跨 64K 和 32-bit 位址溢位；合法 CRLF 也有測試。修正 parser 原本 `bytes.fromhex` 接受內嵌空白、`splitlines` 接受非換行分隔符，及未拒絕跨位址邊界的問題。測試在 `-O` 時也以 `-O` 啟動抽取子程序。

測試：設定環境變數 `V131_HEX` 指向本機固定 HEX（或使用既有 `analysis/v131-startup-source/wchble_rom.hex`），執行 `python -B tests/test_extract_v131_sparse.py`；無副本時測試會 skip。測試包括重複產生、來源與 segment 污染、map 變更、既有輸出及專案內輸出拒絕。沒有設備；不證明設備 resident、ABI、啟動或硬體相容性。
