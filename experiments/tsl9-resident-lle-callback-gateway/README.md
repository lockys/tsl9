# LLE／callback／ECALL 候選 C/C++

[English](readme.en.md) · [前一輪 callback](../tsl9-resident-state8-callbacks/README.md)

新增 **936 bytes／338 條指令、5 個完整候選本體**；原始 APP 另有 226 bytes 作為比對證據，未新增 APP CODE。

| 本體 | 原始範圍（end exclusive） | Bytes |
| --- | --- | ---: |
| Callback | Flash 0x65620..0x656C6 | 166 |
| LLE IRQ entry | 條件式 RAM 0x20002E34..0x20002E6C | 56 |
| Runner／ECALL gateway | 條件式 RAM 0x20002E28..0x20002E30 | 8 |
| Register helpers | 條件式 RAM 0x2000298E..0x20002B4C、0x20002B4C..0x20002C50 | 706 |

原始位址語境下的 register-bound C／組語，不能直接當作一般 C API。`MRET`、`ECALL`、opaque tail 分別處理；`ECALL` 結束此處的分析範圍，不表示已證明它不會返回。

## 新確認的靜態關係

候選 SDK 初始化把 0x20002E34 寫到 RAM slot2；原始 APP 初始化（0x199E2..0x199F0）把 slot2 複製到 live GP+384。APP 的 LLE wrapper（0x8498..0x851E）配置 128-byte frame，從 GP+384 載入並呼叫該指標。

LLE entry 的 AUIPC／ADDI 實際形成 gateway 0x20002E28，保存舊 `mepc` 到 SP+0，再將 gateway 寫入 `mepc`（0x20002E48..0x20002E56）。另一分支以 SP+120 暫存 RA。這兩個 word 均在 128-byte frame 內，避開 29 個已保存暫存器的 SP+4..SP+116。

Gateway 呼叫已重建 runner 0x200007A0，接著 ECALL。原始 APP restore（0x8448..0x8496）從 SP+0 載入 `mepc`、恢復相同 29 個暫存器、釋放 128 bytes 並 MRET。向量 carrier 0x804C／0x8058 有數值 0x8448，但尚未證明實際 cause／mode dispatch。

兩組 PC-relative 地址形成保留原編碼，**不是 linker relocation**；本輪未進行原始位址連結。Callback 0x65620 的共享指標 0x20003550 仍是 opaque tail；數值 callback 本體已補齊，不代表效果已封閉。

## 驗證與限制

C11／C++17 的實際物件相同；936 bytes 與原始候選逐位元組一致，97 個正大小 FUNC 區段是編譯分割區段，並非 97 個邏輯函式。52 個官方 Xwchc 正例與本輪 24 個原始操作保留核對。

累計不供載入的部分連結物件含 **9608 bytes CODE＋256 bytes DATA／3367 條指令**，800 個 FUNC 區段、582 個 relocations；逐項保留輸入的 bytes、symbols、relocations。仍有真實未提供函式 0x57DAE／0x6020A。

**這是條件式結構吻合，尚未成功逆向出可用替代韌體。** 尚須證明實機 ROM／RAM／ISA、初始化完成與既有 4-byte copy 缺口、GP 穩定、frame／MMIO 無 alias、callee 保留 SP、IRQ nesting、ECALL trap frame／vector mode 與 CSR 0x804 語意。沒有硬體、HOST model 或 ISA 執行，沒有 vendor API 請求、APP 整合或新 BIN；95.54% 仍只是既有 APP 位元組覆蓋率。

證據：[完整檢查](audit-result-v1.json) · [摘要](summary.json) · [原始指令與來源](evidence-v1.json) · [規格](spec-v1.json)

## 重現

需要規格列出的原始 APP、SDK、官方指令文件及先前 native artifacts；不會自動下載缺少的輸入。從專案根目錄指定雜湊相符的 Windows NDK LLVM：

```sh
python experiments/tsl9-resident-lle-callback-gateway/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-lle-callback-gateway/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial 名稱必須尚未存在；若保留既有產物，第一行改用 `--replay experiments/tsl9-resident-lle-callback-gateway/build/native-v1`，第二行省略 `--link-trial`。工具雜湊目前固定 Windows 版本，尚未驗證跨平台編譯器。
