# 時鐘、亂數與 idle 的條件式路徑

[English](readme.en.md) · [前輪 SNV／Flash](../tsl9-original-SNV-Flash-binding/README.md) · [候選時鐘 C/C++](../tsl9-resident-clock-services/README.md) · [亂數 C/C++](../tsl9-resident-range-random/README.md)

核對 **11 個完整 SDK 函式／3,840 bytes** 與原 APP 初始化函式 **308 bytes**，共 **4,148 bytes／1,433 指令**。本輪新增 14 處條件式串接；[逐點清單](ledger-v1.json) 累計 **35／51 點**：27 個條件式目標、8 個零值略過或上層 gate；其餘 16 點尚未串接，不是缺失函式數或功能完成率。[驗證收據](verification-v1.json)

| 本輪路徑 | 點數 | 條件式結果 |
| --- | ---: | --- |
| Raw clock | 10 | 原時鐘設定已接受且槽值穩定時，呼叫 `0x191C6` |
| 原設定的 srandCB | 1 | `0x433D2` 呼叫 `0x43520`，不要求先完成時鐘設定 |
| Status | 2 | 複製後 staCB 維持零值時，原 guard 略過 `0x6537C`／`0x655F6` |
| Idle 的上層 gate | 1 | 指定排程器入口的零值 guard 阻止進入 idle service；不是 service 內部的 null 保護 |

## 亂數來源與狀態更新

原 APP 在 `0x19A74` 讀候選槽 `0x4007C`，於 `0x19A90` 寫入 BLE 設定的 srandCB 欄位（offset36）。候選槽的實際值是 `0x43520`；複製至 `0x200031EC` 後，`0x433C4` 從 `0x20003210` 載入它，非零路徑於 `0x433D2` 呼叫。這項綁定不等同於已完成時鐘初始化。

`0x43520` 另讀 provider 槽 `0x20003230`：零值時略過巢狀呼叫，回傳既有 word `0x200031B0`；非零且符合前輪註冊／時鐘條件時，路徑才是 `0x43520 → 0x43D62 → 0x191C6`。沒有證明這些註冊一定早於每一次亂數呼叫。

亂數狀態 word 位於 `0x20002EC8`。有 callback 時，程式先重新讀取 callback 返回後的狀態，加上 callback 的 A0，再計算：

```text
updated = fresh_state_after_callback + callback_A0
result  = updated * 214013 + 2531011
```

以上均為 RV32 unsigned modulo `2^32`。若主要 callback 為零，原程式另有 raw-clock fallback；兩者均為零時略過該次加值。**未證明初始種子、熵來源、亂數品質或實機輸出。** 原 MMIO `0x4002420C` 存取與 FENCE.I 也不能單獨證明實體 IRQ 原子性。

## Idle 的 gate 在哪裡

原 BLE 設定的 idleCB（offset40／自身 SP56..60）在已知清零與複製條件下維持零值，對應槽 `0x20003214`。`TMOS_SystemProcess` 候選入口 `0x200007D0` 在 `0x2000087C` 檢查它；零值路徑返回，不到尾跳 `0x200008BE → 0x2000061A`。

但 idle service 的 `0x2000071E` **沒有本地 null guard**。本輪只證明上述已知 caller 情境會阻止進入，沒有將其他 caller、非零 idleCB 或任意直接呼叫宣稱為安全。重建時不能刪掉上層 gate，也不能自行替原 service 加上不同語義。

驗證涵蓋完整原始 bytes、CFG、最後定義到使用點的暫存器路徑、既有 native C11／C++17 物件與兩個 ELF 讀取器。跨 callee 的 saved register 仍要求原 private ABI；IRQ、重入、記憶體別名與實體 ROM 身分仍有前提。前輪所有綁定及限制保留。

沒有新增目標 C/C++、編譯或 BIN。候選組合仍為 **35,324 CODE + 256 DATA bytes／12,195 指令／0 具名 UND**；APP 靜態覆蓋率仍為 **95.54%**。既有 4-byte 啟動來源缺口與原機 ROM／RAM／ISA／IRQ／Flash／OTA 相容性未解決，**尚不可宣稱可燒錄**。

可考慮加入離線 callback／clock 來源與 idle 上層 gate 診斷；目前未實作，也不會發送硬體控制。

```sh
python experiments/tsl9-original-clock-random-idle-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```
