# OTA handler C/C++ compact 實驗

[English](readme.en.md)

在封存 handler 的完整八暫存器輸入輸出 bridge 上，以兩個來源調整縮小 native：將 S reply 的 volatile 兩個 bytes 拆成獨立 C object，及共用原始 small／packet／page 末端 reply labels。沒有縮小 caller residue 契約或移除 memory clobber。

| 實際編譯 | bytes | 指令 | frame | direct JAL / RELA |
|---|---:|---:|---:|---:|
| 已封存 baseline | 776 | 285 | 112 | 15 / 23 |
| W loop 禁止展開 | 776 | 285 | 112 | 15 / 23 |
| 分離 response object | 592 | 196 | 48 | 15 / 23 |
| 共用 reply labels（選定） | 568 | 193 | 48 | 12 / 20 |

所有值皆來自實際 C11/C++17 兩語言編譯。禁止展開 pragma 沒有改善：baseline 本來只有一個 static quarter JAL 加 backedge，並非四份展開。該無效 pragma 已從最終來源移除。最終比 baseline 減少 208B，仍比原始 530B 多 38B。

`oh_port` 原內嵌 response 地址會逃逸到 opaque packet provider。分離為 wrapper 自有 `volatile uint8_t response[2]`，讓其餘 state/args 不必同物件逃逸。這保留私有 C reply 語義，**不證明原始 SP、pointer alias 或 physical frame 等價**。native 仍以普通 callee S/SP 保存為條件；HOST 可變 named state 不是該條件的證明。

共用末端 labels 保留原本 setter 次序；small/page 的 defined mask 仍是 W=63、U/R=7，packet=15。完整八個 read/write asm operands、所有 opaque clobbers、volatile memory 次序、W A3/A4/A5 投影均保留。12 個 direct JAL 和一個 slot4C indirect JALR 的數量不單獨構成完整 call ABI 證明。

```sh
python3 -B experiments/tsl9-v4160-ota-handler-compact/verify_host.py --project-root . --language both
sh experiments/tsl9-v4160-ota-handler-compact/verify.sh --project-root . --language both
python3 -B apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
```

兩種 CLI 均支援 `--replay PATH/verification.json`。fresh 以 UUID 新目錄為預設，`--build-root NEW` 必須在本 model/build 且不存在；replay 唯讀、不啟動 compiler。發布版 case 位於 `analysis/v4160-ota-handler-compact-2026-10-22`。shell wrapper 預設 python3，也接受 `PYTHON`。

HOST 沿用不變 smoke tests，每語言 10 cases／8292 checks＋3 個實際編譯反例；不是 target 執行。每個 HOST executable 使用封存 machine guard，已實測 Windows；thin Mach-O Python 可解析，universal/fat Python 不支援。可攜 CLI 不表示已在 macOS/Linux 實跑。

native 僅產生 ET_REL／IR／完整反組譯及 -MD resource-header closure，9 個真 UND 保留。沒有 link／stub／numeric provider／BIN／RV32執行或硬體 OTA。原始 530B 的 fit、完整 raw8/frame/RA/alias/async/callee ABI 與 placement 均未通過。不得把 frame48 與原始相同解釋為完整 frame 等價。U/S/W/R/E 的上一輪效果限制繼續有效，BOOT write alias 不改為 Runtime 自刷。

`implementation/hypotheses.json` 記錄 W 的真實 probe metadata；舊 archives 留本機、不隨發布，預設 archive replay=false。原始 BIN 僅供證據，不作產碼輸入。最終仍是未整合 component，既有完整 image 不變。
