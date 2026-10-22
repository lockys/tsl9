# 事件 callback 的可讀重建

[English](readme.en.md)

這個實驗重建 ID2966 V4.1.60 `0x8614..0x888C` 的 632-byte、217-instruction callback 邏輯。`src/callback.c` 是共享 C11/C++17 演算法；`io.h` 分開實體 volatile 操作與合成 HOST provider。沒有把原始指令 bytes 當作程式模板，沒有執行 RISC-V、模擬 ISA、連線裝置或產生新 BIN。

事件優先序是 mask `0x8000`（只檢查輸入 LOW16 符號位）、`0x8`、完整 32-bit context 與 fresh task byte 比對，再依 mask `1`、`2`、`4`。回傳值使用 live 完整事件字 XOR 所處理 mask，不是共用成功碼。mask1 的 ROM gate 僅接受回傳 1；mask2 的 gate 只測最低位。容量先減 3 再截 16-bit；pending 差值先 modulo16 再作 signed16 正值判斷。寬度、fresh reads、null 分配後的寫入、count wrap、copy/send/release 的順序均保留在共享來源。

```sh
python -B experiments/tsl9-v4160-event-callback/verify.py --language both
python -B experiments/tsl9-v4160-event-callback/verify.py --kind native \
  --tool-dir /path/to/pinned/LLVM --language both
```

也可用 POSIX `verify.sh`；`PYTHON=/path/to/python` 可指定直譯器。HOST 預設不需要 RISC-V LLVM。`--build-root` 必須在本 model/build 下且尚不存在；省略時建立 UUID 新目錄。native 使用已驗證的 Windows NDK LLVM，沒有宣稱實測 Linux/macOS 工具鏈。

```sh
python -B experiments/tsl9-v4160-event-callback/verify.py \
  --replay /path/to/HOST/verification.json
python -B experiments/tsl9-v4160-event-callback/verify.py --kind native \
  --replay /path/to/native/verification.json
```

HOST 每語言有 12 個定向案例、34 個檢查及 5 個實際編譯語意反例；所有正例/反例 executable 均經既有 immutable machine guard 後才可啟動。provider 只允許 opaque-call 邊界修改 named carried values/argument residues；memory callback 的這類修改會成為 UNKNOWN。合成 frame 在每次 restore 都 fresh read，包括 provider 改變 live SP 後的情境。HALT/TRANSFER/UNKNOWN 停止後不補做 cleanup。HOST 診斷 budget 不是原始 native timeout。

`defined_argument_mask` 表達明確演算法呼叫參數投影，並非所有中間物理 GPR prefix 證明。`return_address` 是 saved-frame bookkeeping，不表示每次 opaque call 的 architectural RA；HOST 不跳到還原的地址執行。named state 不是 CPU/ISA interpreter。

唯一 bounded native 改進是將 typed opaque-call primitive 設為 `always_inline`。修正後 baseline 944+90=1,034 bytes，採用後為單一真實 FUNC658、241 instructions、48-byte frame、15 次 opaque JALR，沒有 UND/libcall stubs。它仍比原始 632 bytes 多 26 bytes：原位 fit、完整原始 ABI、物理 S-register 對應、call RA offsets、fault/interrupt 行為均未承認。原始 SP+0 未寫入，新 native 會保存 S10 到該位置；save order 也不同。這些是實際未解差異，不以 HOST passed 掩蓋。

元件 ELF 位於獨立 scratch VA `0x1000`，名稱為 `COMPONENT-ONLY-NOT-FIRMWARE.elf`。僅有 conventional callee-preservation 條件下的 native 來源重建；未知 ROM 可以改變原始 live S/SP/GP 的行為不因此獲得證明。沒有整合到既有完整映像，沒有燒錄、硬體相容或 OTA 驗證。
