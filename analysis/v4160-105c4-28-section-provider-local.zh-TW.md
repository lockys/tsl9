# V4.1.60：105c4 的 28 選段 provider 連結（本機觀察）

## 範圍與結果

這是離線靜態實驗，不是完整韌體重建。沿用六段實驗的純 C `105c4` 候選與記憶體來源拆分，擴至先前列出的 21 段，再保留七個正式來源中的 provider／支援區段。以 C11、C++17 各比較原始 owner 與 split + 純 C leaf，共四次 strict selected link：每次所選的 **28 個 section、400 bytes**，皆與參考 BIN 對應窗口相符；原 21 段為 302 bytes，七個新增段為 98 bytes。這些 byte 數不代表新增了等量的純 C 正式成果：多個來源仍含 inline assembly。

參考檔 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 長 76,800 bytes、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。使用 **假設** 的線性基址 `0x8000`；依此將 section 地址減 `0x8000` 取 BIN 窗口。

## 原有 21 段

以下是離散選段，格式為「原址／長度（bytes）」；不表示其間未選地址也被比較。來源與更多靜態脈絡見 `analysis/v4160-105c4-six-section-local-link.zh-TW.md` 及 `analysis/v4160-105c4-return-continuations-candidates.zh-TW.md`。

`0x105c4/12`、`0x107c6/18`、`0x107d8/2`、`0x107da/16`、`0x107ea/4`、`0x107ee/10`、`0x107f8/10`、`0x10802/14`、`0x10810/6`、`0x1083c/12`、`0x10848/4`、`0x1084c/6`、`0x10852/20`、`0x10866/10`、`0x10944/22`、`0x1095a/2`、`0x1095c/10`、`0x10966/86`、`0x109bc/8`、`0x10bbe/4`、`0x10bde/26`。

## 加入的七段

| 原址 | bytes | 來源 symbol | linked bytes |
|---:|---:|---|---|
| `0x81aa` | 6 | `tsl9_queue_status_81aa` | `03c5710a8280` |
| `0x820c` | 18 | `tsl9_queue_clear_820c` | `894763e7a7009387010caa97a38007008280` |
| `0x9124` | 22 | `tsl9_callback_external_9124` | `01114ac806ce22cc26ca4ec652c417390020130969cd` |
| `0xd272` | 22 | `tsl9_callback_provider_entry_d272` | `b707040003a387044d46814517f5ff1f1305a5cc0283` |
| `0x1074c` | 12 | `tsl9_feature_external_1074c` | `411106c622c42a84efc0ffb1` |
| `0x107c0` | 6 | `tsl9_callback_deferred_107c0` | `01456ff0bff8` |
| `0x12a08` | 12 | `tsl9_queue_external_12a08` | `797122d406d62a84ef50aff9` |

實驗使用 `src/native/receive/feature_state_records.c`、`src/native/receive/feature_callback.c`、`src/native/receive/queue_small_providers.c`、`src/native/receive/record_dispatch.c`、`src/native/receive/scheduler.c`、`src/native/receive/callback_providers.c`，以及 `experiments/v4160-new-leaf-turn/leaf.c`。編譯依 `src/source-build-manifest.json` 的對應 profile；拆分由 `experiments/v4160-105c4-source-split-replay/verify.py` 驗證。用 `KEEP` 保留實際 object 的七個輸入 section，並以 `src/compact-layout.json` 的 **candidate aliases** 建立下列 section-relative 別名，而非手填 ABS provider：

- `tsl9_queue_external_820c = tsl9_queue_clear_820c`
- `tsl9_queue_external_81aa = tsl9_queue_status_81aa`
- `tsl9_callback_external_d272 = tsl9_callback_provider_entry_d272`

新增選段中觀察到 `0x12a08` 的 JAL 引用 `tsl9_queue_external_81aa`、`0x1074c` 的 JAL 引用 `tsl9_callback_external_d272`，以及 `0x107c0` 跳轉 `tsl9_feature_external_1074c`。保留全部七段及三個別名後，四個輸出的已命名 undefined symbol 清單均為空。

## 實驗輸入身分

下表為本機實驗使用的 SHA-256；這些 hash 本身不證明 Git membership 或足以重播整個實驗。

| 路徑或記憶體產物 | SHA-256 |
|---|---|
| `src/source-build-manifest.json` | `466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739` |
| `src/compact-layout.json` | `af2aec2d6b88b40c72c4f7ddc1c696630ac65f25462d3173c18d53d140896b4b` |
| `src/native/receive/feature_state_records.c` | `19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3` |
| `src/native/receive/feature_callback.c` | `6de8a0bd3b39b9f9d5fd420fd924ed742b30658c015b1d2644260bca14a695f5` |
| `src/native/receive/queue_small_providers.c` | `40fe794b59002d80057b0e4f70d3b0e51f528378bd5de6ca5cf81600411b7a13` |
| `src/native/receive/record_dispatch.c` | `6d90475b039233f5bea21aa3f7a3af3938f06e4c9ac4a293c1c5f43f6bc3cd1b` |
| `src/native/receive/scheduler.c` | `95d54f0277f717f7b79dc49a1b55f7e4988e05ffdb6dd53e9195153159b94457` |
| `src/native/receive/callback_providers.c` | `daaf2f45bed63cb62eea82a981f03a79f8c5b25ea5e3b79941b223818f3c4e3f` |
| `experiments/v4160-new-leaf-turn/leaf.c` | `e358a04a1c0d57589107315751ac0daf33cad9c53e104da80a7598da983396ff` |
| `experiments/v4160-105c4-source-split-replay/verify.py` | `f00f3d5fd4719b802315b9e3002caca9f76dc6ffdc4981ec8a78c219311f81f6` |
| `analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py` | `00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141` |
| 拆分後 owner | `d7f29f5420dc209f206eb424a527b6c9ed8000eb392ee25a35e2be2b1b90aada` |

## 對照與身分

- 僅保留 21 段時，四次 link 非零：診斷包含 `tsl9_queue_clear_820c`、`tsl9_queue_external_820c`、`tsl9_queue_external_12a08`、`tsl9_callback_external_9124` 未定義，以及指向已丟棄 `1074c`／`107c0` 區段的引用。
- 加入部分支援段及前兩別名、但未綁定 `d272` 時，四次 link 仍非零，出現 `tsl9_callback_external_d272` 未定義。
- 在 C 原 owner 的 28 段實驗，分別移除三個別名，每次 link 均 exit 1，並分別出現被移除的名稱未定義。這是三個分開的負例，不是全部 ABI 或 provider 的測試。
- 原 owner 輸出 ELF SHA-256：`3066300cfcdea3157c88f0dca6950ce2d3c435e928067554a25def1d32b72c5b`；split + leaf：`466423573cacfc6b66ff67d9df97548017bc943790b149368d5df197f7db6ab7`。此次 C/C++ 各自得到相同的相應 hash，不推廣到其他工具或旗標。
- 離線使用 NDK Clang／LLD 18.0.2，二者 SHA-256 分別為 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`、`fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`；使用的 `stdint.h` SHA-256 為 `7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34`。Python、OS、其他工具依賴和並發替換不在完整信任封裝內。

## 不能推論的事項

這次 `--no-undefined --no-relax --gc-sections --fatal-warnings` 只針對保留區段的可見符號 relocation；實驗刻意丟棄其他 sections 和 `.llvm_addrsig`，ELF 的選段使用 `:NONE` 而非可載入映像。`0x1074c`、`0x9124`、`0x12a08` 仍有未保留的後繼；`0xd272` 有間接跳轉。成功連結不能證明控制流程閉合、真實可達性、private ABI、原始資料 owner、所有呼叫者或完整 BIN 等價。candidate alias 與所選位址是研究假設，不是正式整合批准。

本記錄是本機觀察；實驗腳本及完整逐條 receipt 未隨本文發布，不能把它當作 clean-main 自足重播或 CI 通過。沒有執行、模擬或燒錄目標韌體，也未修改正式來源或放寬正式 guard。
