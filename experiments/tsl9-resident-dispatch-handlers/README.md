# 兩個原缺失 handler 與 register provider

[English](readme.en.md) · [既有 LLE／ECALL](../tsl9-resident-lle-callback-gateway/README.md) · [啟動／trap 契約](../tsl9-trap-profile-contract/README.md)

新增 **1118 bytes／384 條指令、4 個完整候選本體**。0x57DAE／0x6020A 直接供應先前真實 UND 的同名函式，沒有 stub 或 ABS 假提供者。

| 本體 | 原始範圍（end exclusive） | Bytes／自身 frame |
| --- | --- | ---: |
| 原缺失 handler | Flash 0x57DAE..0x57EEA | 316／32 |
| 原缺失 handler | Flash 0x6020A..0x60350 | 326／32 |
| Register provider | Flash 0x63C54..0x63D6A | 278／0 |
| Register provider | Flash 0x63EDA..0x63FA0 | 198／16 |

每個 entry 的 CFG 覆蓋本體內全部指令，所有 local normal return 的自身 frame 平衡。不能以首次 RET 截斷：兩個 handler 在後續分支完成後，分別以0x57EE8／0x6034E跳回先前的共用返回；緊接的獨立16-byte frame函式不屬於本體。Register provider 同樣保留 RET 後仍可達的分支。

## 已確認與仍未知

兩個 handler 都檢查共享 state+7／+9；特定分支向 state+8 寫入 halfword0x0107／0x0106。這支持延後狀態處理的推論，尚未確認實際封包或產品功能語意。

兩組 AUIPC／JALR 實際呼叫已有本體的 setter0x2000078A。旗標0x20003240為零時，0x57DAE路徑仍呼叫 setter，A0=0；0x6020A路徑則跳過 setter。非零時分別載入RAM word0x200034F0／0x200034F8作為A0；這些 raw callback targets尚未提供，不能因 linker 沒有 UND 就視為已解決。

0x63C54先檢查 descriptor word0x2000350C，非零時透過其內部指標做兩次 pointed-word更新；容量、指標有效性與目標周邊未證明。0x63EDA會讀取、清零並在各 local normal return前寫回候選硬體 word0x4002420C，中間包含 FENCE.I。寫回所用S2的有效性仍依賴 callee 保留暫存器與無 alias，未證明 IRQ atomicity 或硬體 mask 語意。

0x63F26仍可能透過共享RAM指標0x20003550呼叫未知函式，A0=17、A1=A2=0。此路徑有 state 條件，沒有 pointer null guard；效果未封閉。

## 實際驗證

C11／C++17 實際物件相同，1118 bytes 在原始VA語境下逐byte吻合，52個官方 Xwchc正例與29個實際條件操作核對通過。65個正大小 FUNC是編譯分割區段，不是65個邏輯函式。

不供載入的部分連結物件累計 **10726 CODE＋256 DATA bytes／3751指令**，865個FUNC區段、1個OBJECT、629個relocations。兩個獨立ELF reader與逐輸入 bytes／symbols／relocations檢查通過，**此組部分連結的具名UND為0**；這不等於完整ROM、callback、私有ABI或執行依賴已封閉。所有既有真實本體與 trap 契約保留。

APP位元組覆蓋率仍95.54%，新增APP CODE=0。實機ROM／RAM／ISA、GP／frame／IRQ／alias、4-byte啟動來源缺口、Flash與OTA仍未確認；沒有硬體、HOST model或ISA執行、vendor API、APP整合或新BIN。**尚未成功逆向出可用替代韌體。** 可考慮未來加入 deferred-state／callback來源診斷，此功能尚未實作。

[完整收據](audit-result-v1.json) · [摘要](summary.json) · [原始指令](evidence-v1.json) · [C/C++](resident_dispatch_handlers.c)

## 重現

需要規格固定的原始APP、SDK、指令文件、先前native artifacts，以及 trap 契約的本機官方標頭；不會自動下載缺少的輸入。

```sh
python experiments/tsl9-resident-dispatch-handlers/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-dispatch-handlers/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1
```

Trial名稱必須未存在；保留既有產物時，第一行改用 `--replay experiments/tsl9-resident-dispatch-handlers/build/native-v1`，第二行省略 `--link-trial`。工具pins為Windows NDK LLVM，尚未驗證跨平台編譯。
