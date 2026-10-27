# 原 APP 在 library 綁定前的中斷啟用

[English](readme.en.md) · [SDK 啟動／slot2](../tsl9-resident-slot2-startup/README.md) · [APP callback 綁定](../tsl9-original-APP-library-binding/README.md) · [trap 合約](../tsl9-trap-profile-contract/README.md)

本輪核對既有 C/C++，**沒有新增或重編譯 target code**。6 個完整函式共 328 CODE bytes／113 指令，另有 5 個 vector words（20 DATA bytes）；原 BIN、兩份 C/C++ 原位址診斷 ELF 與兩個獨立 ELF reader 全部一致。

## 已確認的編碼順序

原 APP `0x9250` 在 `0x9258` 呼叫 IRQ initializer `0x9A42`，之後才於 `0x9268` 進入 `0x8E88` → `0x199E2` 的 library 初始化路徑；slot2 → GP+384 的 binding store 位於 `0x199EC`。

IRQ initializer 使用自身 16-byte frame，在 `0x9A4C` 設 S2=`0x88`，於 `0x9A50` 執行 `csrc 0x800,s2`。6 次 RCC calls 都有完整既有本體，僅對 `0x40021000` 的 +0x18／+0x1C／+0x0C／+0x10 做 word RMW，沒有修改 S2、GP 或 CSR。最後在 `0x9AC2` 執行 `csrs 0x800,s2`，之後才載回 incoming S2、釋放 frame 並返回。這是無條件設定 mask bits，**沒有先讀取並還原進入函式前的全域 mask 狀態**。

已保存的 WCH 官方 core header 使用相同 CSR／mask 作為全域停用／啟用中斷。這是候選 profile 的來源證據，仍不證明實機相同。官方 disable helper 另有 `fence.i`，原 `0x9A42` 函式沒有；本輪保留差異，沒有修改原程式或宣稱兩者整段相同。

## 三個 enable requests

三次 word store 的目的都是候選 PFIC `IENR[1] = 0xE000E104`，各次都另寫相應 priority byte：

| Store PC | Mask | 候選 IRQ／priority | 原始 vector target |
| --- | --- | --- | --- |
| `0x9AA0` | `0x2000` | 45，TIM3／`0x00` | `0x979E` |
| `0x9AAE` | `0x10` | 36，USB_LP_CAN1_RX0／`0x20` | `0x12C24` |
| `0x9ABE` | `0x80` | 39，EXTI9_5／`0x30` | `0x16FB6` |

官方 header 的 controller layout、IRQ enum 與 enable 位址／mask 算術均已核對。這三個數值**不要求啟用 BB63 或 LLE64，也不能據此認定其他 lines 被停用**。BB63／LLE64 的原始 vector targets 仍是 `0x1873E`／`0x8498`；尚未觀測實機 enable／pending 或 peripheral source 狀態。

在正常返回、有效記憶體、callee 暫存器與無非同步干擾等條件下，clear、6 次 RCC calls、全部 priority／enable stores 與最後 global-set 在完整 CFG 中支配 normal return；IRQ setup call 也支配進入 library 的 call。因此，**原程式存在 library binding 前的全域啟用請求，不能假設所有中斷一直保持關閉到 binding 完成**。

這不是實際 delivery、早期 LLE dispatch、競態或硬體故障的證明，也沒有封閉三個 handler／其他先前 callees 的非同步記憶體效應。下一步需要確認 BB/LLE 初始 controller 與來源狀態、pending 條件、handler effects 和實機 trap profile。

## 使用與狀態

[既有 IRQ C/C++](../../src/native/irq/irq_initializer.c) · [主流程 C/C++](../../src/native/startup/main_family.c) · [證據](evidence-v1.json) · [收據](verification-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-original-APP-early-IRQ/verify-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需固定的本機 BIN、官方 header 與前輪 native artifacts；不自動下載。Windows NDK LLVM 的既有 C11／C++17 artifacts 已核對；跨平台驗證未確認。

APP 維持 159 C/H、95.54% 位元組覆蓋率（不是功能完成率）；SDK 候選組合維持 20,346 CODE＋256 DATA、11 個具名依賴。4-byte 啟動來源缺口及 ROM／RAM／ISA／IRQ／stack／alias／callback／Flash／OTA 相容性仍開放。沒有新增 BIN、APP 整合、硬體／目標／HOST-model／ISA 執行；**尚未成功重建可用替代韌體**。唯讀啟動 IRQ 相容性報告列為後續功能候選，尚未實作 UI。
