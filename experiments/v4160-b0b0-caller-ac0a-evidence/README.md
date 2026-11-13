# V4.1.60：`0x102e6` caller 經 `0xac0a` 的有界證據

唯一參考輸入是 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長 76,800 (`0x12c00`) bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；raw offset 0 對應 PC `0x8000`。雜湊用於身分固定，不是控制流證明。以下指令是實際從該 BIN 所列地址取得的 little-endian bytes；半開窗口為 `[0x102bc,0x102ee)`、`[0xac0a,0xac18)`、`[0xac6a,0xac70)`、`[0xd05c,0xd07c)`、`[0xb0b0,0xb0ba)`。

## 先更正前提

**`0xac0a` 檢查的是 `lbu a5,354(gp)`，不是 `*(gp+358)`。** 即使 `*(gp+358)==0`，也不能推出此路徑；必須另有 `*(gp+354)==0`。另一分支（`gp+354 != 0` 跳 `0xac18`）在本研究中是 **unknown**。`a0 != 0` 時跳 `0xac58`，此處也不推其結果。沒有根據 `0x8202` 外呼的返回推斷 a1–a4 或其他暫存器不變。

## 原始指令與條件

表中的跳轉目標均由指令自身 PC 加有號位移得到；`bleu s0,a5` 是 `bgeu a5,s0` 的別名（無號比較）。

| PC | raw bytes | 解讀 |
|---|---|---|
| 102bc | `83 c7 77 00` | `lbu a5,7(a5)` |
| 102c0 | `91 8b` | `andi a5,a5,4` |
| 102c2 | `a1 c7` | `beqz a5,0x1030a` |
| 102c4 | `93 07 90 08` | `addi a5,zero,137` |
| 102c8 | `63 ff 87 02` | `bgeu a5,s0,0x10306` |
| 102cc | `83 c7 71 13` | `lbu a5,311(gp)` |
| 102d0 | `89 ef` | `bnez a5,0x102ea` |
| 102d2 | `85 47` | `li a5,1` |
| 102d4 | `a3 8b f1 12` | `sb a5,311(gp)` |
| 102d8 | `ef 70 bf f2` | `jal ra,0x8202` |
| 102dc | `19 c5` | `beqz a0,0x102ea` |
| 102de | `01 45` | `li a0,0` |
| 102e0 | `ef a0 bf 92` | `jal ra,0xac0a`；連結位址 `0x102e4` |
| 102e4 | `11 45` | `li a0,4` |
| 102e6 | `ef a0 bf dc` | `jal ra,0xb0b0`；連結位址 `0x102ea` |
| 102ea | `83 c7 51 13` | `lbu a5,309(gp)` |
| ac0a | `83 c7 21 16` | `lbu a5,354(gp)` |
| ac0e | `89 e7` | `bnez a5,0xac18` |
| ac10 | `21 e5` | `bnez a0,0xac58` |
| ac12 | `05 45` | `li a0,1` |
| ac14 | `85 45` | `li a1,1` |
| ac16 | `91 a8` | `j 0xac6a`，不更改 ra |
| ac6a | `01 46` | `li a2,0` |
| ac6c | `6f 20 00 3f` | `jal zero,0xd05c`，不更改 ra |
| d05c | `97 f7 ff 1f` | `auipc a5,0x1ffff` |
| d060 | `93 87 c7 ed` | `addi a5,a5,-292` |
| d064 | `05 47` | `li a4,1` |
| d066 | `33 06 c0 40` | `sub a2,zero,a2` |
| d06a | `23 80 e7 00` | `sb a4,0(a5)` |
| d06e | `a3 80 a7 00` | `sb a0,1(a5)` |
| d072 | `23 81 c7 00` | `sb a2,2(a5)` |
| d076 | `a3 81 b7 00` | `sb a1,3(a5)` |
| d07a | `82 80` | `ret` (`jalr zero,ra,0`) |
| b0b0 | `97 17 00 20` | `auipc a5,0x20001` |
| b0b4 | `a3 8d a7 e2` | `sb a0,-453(a5)` |
| b0b8 | `82 80` | `ret` (`jalr zero,ra,0`) |

## 有條件的資料流，不是可達性結論

假設從 `0x102bc` 順序進入、相關讀寫成功、無異常或外部干擾，且所有相關寫入及外呼均未改變後續指令與必要狀態（包括不存在會造成此影響的別名）：`lbu` 結果 bit 2 為 1；`s0` **無號大於** 137；`*(gp+311)==0`。則先將 byte 1 寫到 `gp+311`，呼叫 `0x8202`。再假設它正常返回且返回 a0 非零，才順序到 `0x102de`，設 a0=0 後呼叫 `0xac0a`。在 `0xac0a` 的讀取時再假設 `*(gp+354)==0`，兩個 bnez 均不跳：a0=1、a1=1，經 `0xac6a` a2=0，尾跳到 `0xd05c`。

`0xd05c` 以其自身 PC 算出 a5=`0x2000bf38`；a4=1，`neg a2` 把已是 0 的 a2 保持為 0；四個 SB 的來源依序為 a4、a0、a2、a1，因此按指令的位址運算，依次存低 byte `1,1,0,1`。`0xac0a` 此分支、`0xd05c` 到 ret 均不寫 a3，所以 a3 是**進入 `0xac0a` 時**的值；這不是 `0x8202` 外呼之前的值保證。此時 a1=1、a2=0、a4=1，a0=1。假設 store 成功且未改變後續指令或其他必要狀態，ret 使用未被兩個尾跳改寫的 ra，回到 `0x102e4`；其 `li` 改 a0 為 4，然後呼叫 `0xb0b0`。

`0xb0b0` 算出的 store 位址為 `0x2000beeb`，寫入 a0 低 byte（本條件路徑為 4），只改 a5、記憶體及控制流程，**不寫 a0–a4**。若該 store 和 ret 成功，返回 `0x102ea` 時 a0=4、a1=1、a2=0、a4=1，a3 仍是進入 `0xac0a` 的值；`0x102ea` 自身只載入 a5。此說法不保證外部呼叫或其他路徑保留任何參數暫存器，也不證明記憶體位址可寫、無別名、硬體 store 實際發生或返回真的發生。

## 重播與限制

離線反組譯使用 tool-index 的 `C:\Users\locky\Tools\radare2\bin\rasm2.exe` 6.2.4，不需打開或執行目標。下列輸入是上表從固定 BIN 讀到的連續 raw bytes，`-s` 設起始 PC，`-D` 顯示位址和 bytes：

```text
rasm2.exe -a riscv -b 32 -s 0x102bc -D 83c77700918ba1c79307900863ff870283c7711389ef8547a38bf112ef70bff219c50145efa0bf921145efa0bfdc83c75113
rasm2.exe -a riscv -b 32 -s 0xac0a -D 83c7211689e721e50545854591a8
rasm2.exe -a riscv -b 32 -s 0xac6a -D 01466f20003f
rasm2.exe -a riscv -b 32 -s 0xd05c -D 97f7ff1f9387c7ed05473306c0402380e700a380a7002381c700a381b7008280
rasm2.exe -a riscv -b 32 -s 0xb0b0 -D 97170020a38da7e28280
```

標準庫獨立 `verify.py` 檢查長度、整檔 SHA、逐窗口原 bytes，以及每條指令的 opcode、暫存器、立即數、branch/JAL 目標與邊界；只支援本題所需 RV32I/C 子集，不是一般反組譯器，也不執行或模擬韌體。它直接從固定路徑讀取，不依賴其他實驗。測試對合成窗口直接呼叫語意檢查，繞開整檔 hash 和 raw pin，涵蓋 opcode、register、funct、立即數、分支與跳轉位移、逐長度截斷和額外 bytes；另分別測身分、raw guard 與 decoder。所有 guard 使用明確例外而非 `assert`，正常與 `-O` 均可運作：

```text
python -B experiments/v4160-b0b0-caller-ac0a-evidence/verify.py
python -B experiments/v4160-b0b0-caller-ac0a-evidence/test_verify.py
python -B -O experiments/v4160-b0b0-caller-ac0a-evidence/verify.py
python -B -O experiments/v4160-b0b0-caller-ac0a-evidence/test_verify.py
```

本研究沒有執行或模擬目標、使用 compiler/linker、網路或修改原 BIN；沒有推斷任何其他入口、分支、外呼結果或全程可達性。
