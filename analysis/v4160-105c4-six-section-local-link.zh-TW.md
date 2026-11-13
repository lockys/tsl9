# V4.1.60：105c4 六區段本機選擇性連結

這是離線、非載入式 ELF 的局部結果，**不是完整純 C 映像**。本機 `experiments/v4160-105c4-six-section-local-next/probe.py` 與其 splitter 當時尚未發布；本報告不聲稱能從 GitHub main 單獨重播。

## 方法與結果

以 `src/source-build-manifest.json` 的 `queue-consumer-a0-a5` C11、C++17 profile 分別編譯既有 `src/native/receive/feature_state_records.c` 和 `src/native/receive/feature_callback.c`。各語言比較兩組輸入：原 owner + callback，以及本機 splitter 將 owner 內 105c4 定義換成 extern 後的 split owner + callback + `experiments/v4160-new-leaf-turn/leaf.c`。候選以預處理器將 `leaf` 換成正式符號；C++17 case 是以 C++17 編譯該來源，不是跨語言呼叫測試。原 owner 仍含 inline assembly，替換不代表正式整合。

使用 direct LLD、`--no-undefined --no-relax --gc-sections --fatal-warnings`、指定 section 的 linker script，分別把以下區段固定在列示地址。假設 BIN 線性 base `0x8000`，每 case 各 94 bytes 與該 BIN 窗口相符：

| 選段 | 地址 | bytes |
|---|---:|---:|
| 105c4 候選 | `0x105c4` | 12 |
| trampoline B | `0x107c6` | 18 |
| trampoline A | `0x1083c` | 12 |
| caller A 區段 | `0x10944` | 22 |
| tail 區段 | `0x10bbe` | 4 |
| caller B 區段 | `0x10bde` | 26 |

一般與 Python `-O` 模式各自重播，本機觀察 C11 original、C11 split、C++17 original、C++17 split 四 case 均為 **94/94**。各語言的缺 leaf 連結產生具名 undefined 錯誤；錯誤 target 位址由 section layout 檢查拒絕；將 leaf 判斷常數改為 5 則由該區 BIN bytes 比對拒絕。這只是三種指定負例；本報告未保存完整輸出 receipt，讀者不能單憑本文獨立驗證觀察結果。

原 owner 與 split owner 分別連同 callback 的選段輸入 relocation，依序核對七筆的 owner section、offset、type、symbol name、addend；候選 `.leaf` 無 relocation。這不是完整符號 binding、visibility、definition 或所有非選段 relocation 的核對。連結輸出的 alloc section 清單只含六段，並拒絕 `PT_LOAD`；linker script 丟棄指定 pattern 的輸入 sections，包括 `.llvm_addrsig`，但未盤點所有 non-alloc sections。腳本無論局部成功與否均回報 `INCOMPLETE_FAIL_CLOSED`、`passed: false` 且 exit 1；`selected_checks_passed: true` 僅指所列局部檢查。

## 身分與限制

參考 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本機 probe SHA-256 `1ea891085389389279677cf47eca148e8cc5bf7308a134ea5954239cb9be9d3b`；splitter `experiments/v4160-105c4-real-split-callers-turn6/observe.py` SHA-256 `f4035e612aadf2a8c147775448b48ea3961b43ee7eaf1fb6c566765adbc4cb3e`。owner、callback、候選和 manifest 的 SHA-256 分別為 `19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3`、`6de8a0bd3b39b9f9d5fd420fd924ed742b30658c015b1d2644260bca14a695f5`、`e358a04a1c0d57589107315751ac0daf33cad9c53e104da80a7598da983396ff`、`466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739`。工具與部分輸入固定 hash，未固定 Python、OS、DLL 和全部環境；呼叫前後檢查無法排除並行替換。暫存目錄並非安全 sandbox。

所選 relocation 欄位核對並非完整 CFG：部分順序 fallthrough 進入未選區段。結果不證可達性、指令邊界、實際呼叫者／provider 完整性、private ABI、原始 owner、`.llvm_addrsig` remap、其他區段或完整 BIN 一致，也未執行、模擬或燒錄目標。
