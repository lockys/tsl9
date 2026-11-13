# BD46／BD50 拆分時的 `.llvm_addrsig` 差異

## 範圍

以 `queue-consumer-a0-a5` profile 離線編譯原本的 `src/native/receive/record_continuations.c`，並將兩個完整函式定義從經雜湊核對的記憶體副本各精確移除一次，再編譯該副本。C11 與 C++17 都各自編譯原本與拆分後的單元；不修改正式來源、不執行或模擬目標韌體。原單元仍包含其他 inline assembly，這不是純 C 重建。

實驗從固定版本的 Clang 18.0.2 與既有的 ELF32 reader 解析新產生的 ET_REL。此次對 `.llvm_addrsig` payload 採用 32-bit ULEB 索引解讀；這是本實驗的明示假設，並非此處對 LLVM 格式規範的獨立證明。四個實測 payload 每一項均只有一 byte。

## 實測觀察

| | 原單元 | 移除兩函式的單元 |
|---|---:|---:|
| 解讀的索引數 | 33 | 31 |
| `.llvm_addrsig` section type | `0x6fff4c03` | `0x6fff4c03` |
| flags | `0x80000000` | `0x80000000` |
| `sh_link`（各自物件的 `.symtab`） | 60 | 58 |
| payload bytes | `292a2b2c2e3031323435363338393a3c3e3f3b404243454446484a494b47414c4d` | `27282a2c2d2e3032332f353637393b3c383d3f4042414345474648443e4a4b` |
| 當次 C11／C++17 object SHA-256 | `93b44375739aea2e64f42ff6c9cd87e9bcb2633ac92e098eab8c09d1952ebd3f` | `3fe3a5f25c7738bd5a10958244f54e160c8565378aecdb44a07b78c7c0921f7f` |

原 payload 所解出的前兩項分別指向 `tsl9_record_helpers_provider_bd46`、`tsl9_record_helpers_provider_bd50`；原單元中的兩者是各自 section 內的 GLOBAL FUNC、大小 10，對應 bytes 依次是 `170500201305b51c8280`、`170500201305051c8280`。拆分單元中，同名符號是 GLOBAL UND NOTYPE，不是已定義 FUNC。

原 payload 解讀後剩餘 31 項，與拆分單元 31 項的受限 canonical symbol／section attributes 及順序一致；但兩側數字索引及原始 payload **不相同**。觀察沒有比較所有其他 symbol、relocation 或 section bytes，也不證 LLVM linker 對此差異的語義等價，更不證明函式 ABI、caller 可達性、實際 RAM owner 或完整映像。

先前以 `ld.lld -r --no-relax` 將拆分單元和兩個純 C leaf 候選重新部分連結的另一項本機探索，產生 32 筆 RELA；原單元經部分連結產生 28 筆。兩種輸出 `.llvm_addrsig` 的 `sh_link` 都是 0，不能直接把輸出 symtab 的索引解讀當成已證實的跨單元重映射。這只是探索紀錄，並未驗收重連等價。

## 輸入及本輪驗證

- 正式原 source SHA-256：`8f3e6bf141c89a8236e9eb075aa7d6af604c58e7ff8aec5b382462dd5a52d85e`。
- source manifest：`30e7076ed9fa896f5745024ab6fa0a9f016124a2dd11ae12fe566e2107f06479`；build manifest：`466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739`；`experiments/tsl9-record-continuations/spec-v1.json`：`9207967d0689aca3c11a779ac1459bf0e00cc5de8487aca8fb3c18ae2c25180e`。
- `experiments/tsl9-feature-dispatch-tree/elf_reader-v4.py`：`2f7a5dc2d4eeb823e0e4c63f81b3c4fdcffe7cbb39262dc7f6731be675016b15`；本機 Clang：`047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`。
- 提交前以 GitHub `main` 的 `94e7bb4a988f214a16f897a46526fd0a6754e2ff` 非截斷遞迴 tree 核對上述 **五個 repository 檔案**的本機 Git blob：source `0491079233b534e221e57ca8f084b7b0e68f36cd`、source manifest `66de11cd6310fb3e08cd1710a5a0f2aac84dc6e6`、build manifest `a4f5b767f84bcbc3a77297d18276b806c0085285`、spec `8a73238047ab6724b10e53b25fc38eae1fe32f0c`、reader `a8212de0ee0cf3a593c6ecd7947738a0863647d1`；這項核對不包含本機 Clang。
- 實際編譯採 manifest profile 並額外加 `--no-default-config`、`-H`；前者避免 Clang 載入預設設定，後者核對實際 include trace。固定的 `stdint.h` SHA-256 為 `7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34`。執行檔及 header pin 不等於固定所有 DLL、OS、Python 或供應鏈，並假設工具不被並行替換。
- 觀察器與 mutation 測試目前只在本機 `experiments/v4160-bd46-bd50-addrsig-evidence/`，**不包含於本提交**；當次 `probe.py` SHA-256 `6f95c734d0630199fb093425334c3516437a64007b7120589e33e5a6a413eb17`，`test_probe.py` `c19bb8aada6cdb7e4b4b3352ab87d46d746018cc721bb481490cbbea9e8efa31`。本輪實際重播 normal／Python `-O` 各 18 項測試通過，兩種模式的觀察器均返回 `PASS: bounded direct addrsig observation, not ABI or linker equivalence`；本次 18 項完整 log 未包含於本提交。測試包含錯誤符號、section、截斷 ULEB、編譯失敗、污染 include 和 Clang 設定檔負例；不是硬體驗證或 CI 通過證明。
- 初次獨立重播因臨時複製的 Clang 缺少執行期 DLL 而失敗，回傳 `0xC0000135`；調整僅供測試子程序使用的 PATH 後上述重播通過。DLL 未逐一 pin，此結果不能消除環境限制。

下一步需以明確的符號與 relocation 身分、含 `.llvm_addrsig` 的部分連結證據，以及真正資料 provider 分別驗證整合；不能把上述受限投影或人工 ABS witness 當成正式整合成功。
