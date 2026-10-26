# 原始 APP callback 設定與局部 IRQ 順序

[English](readme.en.md) · [RF task／取樣](../tsl9-original-RF-task-path/README.md) · [CPU store 合約](../tsl9-tscb-store-contract/README.md) · [trap 契約](../tsl9-trap-profile-contract/README.md)

本輪新增跨 APP／SDK 的設定與流程證據，**沒有新增或重編譯 target code**。6 個完整 APP 參考函式共 **2,136 bytes／697 指令**，與原始 BIN、既有 C／C++ 原位址診斷 ELF 逐 byte 一致；兩個獨立 ELF reader 核對通過。

## callback 不再只是未知名稱

原始 initializer `0x199E2` 配置 96-byte frame，在 SP+16 建立 64-byte library config，與保存的 S0／RA（SP+88／+92）分離：

| 欄位 | 原始 literal | Store PC／caller stack |
| --- | --- | --- |
| tsCB，config+44 | `0x197F0` | `0x19A9E`／SP+60 |
| rcCB，config+48 | `0x197B8` | `0x19AB2`／SP+64 |

兩個 store 在完整正常返回 CFG 中支配 `0x19AEC` 的 library call。原始設定明確使用非零 callback；MAC helper 的 6-byte 寫入與複製避開這兩個欄位，沒有讀取實機 MAC／UID 值。

候選 slot `0x400A4` 指向 BLE_LibInit `0x43C7E`。其 zero／copy64 至 `0x200031EC` 後，`0x43D38` 讀 config+44 呼叫 tsCB，並將低 halfword 寫入 baseline `0x200031A4`。前輪 monitor `0x43EDC` 讀相同 tsCB／rcCB words。因此，在**實機 ROM 相符、copy64 完成、有效不重疊記憶體、callee／IRQ／alias 條件成立**時，可把這些間接呼叫對應到既有 APP C/C++。尚未觀測實機 RAM 中的指標，原 opaque calls 的作用並未全部封閉。

rcCB `0x197B8` 以 A0=3、無自身 frame 尾跳既有 `0x1929A..0x196C4` 校準 worker；worker 自身 frame 為 80 bytes，保留原始 signed DIV／輪詢／RMW，沒有宣稱校準收斂或全程 stack 上限。

## tsCB 回傳資料寬度

既有 `0x197F0..0x1995C` callback 在 `0x198DC` 呼叫 ADC 候選 helper `0x18A66`。該 helper 用原始 **C.SLLI16／C.SRLI16** 取低 16 bits；結果在 `0x198E0` 保存至自身 SP+28，於 `0x1991E` 載回、`0x19948` 移至 A0。

上述 call／save／load／move 支配正常 return，且此 frame 的 SP+28 只有該明確 word store。14 函式 CPU-store 合約重新核對通過。因此在該合約的有效記憶體、callee 正常返回、nonalias 與無非同步覆寫條件下，原始 callback 的返回值位於 0..65535。這收斂前輪 uint16_t ABI 的來源條件，**不證明攝氏單位、ADC 實體身分或校準成功**。

## 版本與 IRQ：證明的邊界

原 APP 只比較 21-byte `CH32V20x_BLE_LIB_V1.3` 前綴；候選 table 的版本 pointer 為 `0x6E6A0`，比較 provider 是已有本體的 RAM `0x20000442`。候選前綴吻合，但這個比較不區分完整 library 版本或晶片料號，也不證明實機 ROM 身分；仍要求指標有效與 comparator 契約。

在 `0x199EC`，原碼把 word `0x20000008` 寫到 incoming GP+384。若 GP 維持 reset 的 `0x20004000`，目的為 LLE wrapper 使用的 `0x20004180`。該 assignment 支配此函式的全部對外 call 及兩處直接 enable stores：

- `0x19B08`：`0xE000E104 ← 0x80000000`，數值對應候選 IRQ63。
- `0x19B0E`：`0xE000E108 ← 1`，數值對應候選 IRQ64。

原主流程在 RF_RoleInit／RF constructor 之前呼叫此 initializer。但**沒有證明 slot2 非零且正確、GP／callback word 不被改寫，或這些 stores 早於全域任何可能的 dispatch**；更早的 IRQ 狀態、callee／DMA／alias 與實體向量模式仍未知。這補上局部編碼順序，不取代實機啟動證據。

## 使用與狀態

[既有 startup C/C++](../../src/native/startup/resident_startup.c) · [周邊 C/C++](../../src/native/startup/peripheral_primitives.c) · [完整證據](evidence-v1.json) · [驗證收據](verification-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-original-APP-library-binding/verify-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定的本機原 BIN、既有 native artifacts、Windows NDK LLVM 及官方 header；不自動下載。跨平台驗證未確認。

APP 仍為 159 個正式 C/H、95.54% 位元組覆蓋率；SDK 組合仍為 20,112 CODE＋256 DATA，11 個未提供具名依賴。沒有新增 BIN、APP 整合、目標／HOST model／ISA 執行或硬體操作。4-byte 啟動來源缺口、ROM／RAM／ISA／IRQ、stack／alias、callback、Flash／OTA 仍開放；**尚未成功重建可用替代韌體**。啟動設定來源與相容性證據顯示列為後續唯讀功能，尚未實作 UI。
