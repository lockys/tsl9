# 候選 pseudo-random core 與 callback byte range

[English](readme.en.md) · [前輪設定／Flash](../tsl9-original-prebinding-settings/README.md) · [callback 註冊](../tsl9-resident-callback-registration/README.md) · [clock providers](../tsl9-resident-clock-services/README.md)

新增兩個實際需要的候選 SDK 本體，共 **144 CODE bytes／52 指令**，以原始暫存器上下文的 C11／C++17 編譯。兩者物件相同，7 個正尺寸 FUNC、4 筆 direct-control relocations 全部吻合原 SDK 編碼；沒有新增 custom 指令。這不是原廠 C 原始碼或可直接以一般 C ABI 呼叫的函式。

| 本體 | 完整範圍 | Bytes／指令 |
| --- | --- | --- |
| primary `tmos_rand` 候選 | `0x433A8..0x43414` | 108／37 |
| callback 使用的 byte-range 候選 | `0x43E6A..0x43E8E` | 36／15 |

未選入緊鄰的其他 range／setter 函式。官方 header 的 `BLE_LIB_JT(1)` 與候選 table `0x40038` 都對應 `0x433A8`。

## Core 的確切副作用

core 保存 word `0x4002420C` 至 S1，暫寫 0 並執行 `FENCE.I`，最後還原該 word。其硬體意義、IRQ 原子性與實機相容性仍未證明；沒有把它當作全域中斷鎖。

它優先讀 callback word `0x20003210`；若為零，再讀 `0x200031E0`。非零時於共同的 `0x433D2` 間接呼叫，返回後 fresh-read state `0x20002EC8`，加上 callback result 並寫回。兩者皆零時跳過此加法。之後再次 fresh-read state，執行：

```text
state = low32(state * 214013 + 2531011)
```

完成 state store 與硬體 word 還原後，再讀 state 作為結果。不能把 callback 前的 state 快取後代入，也不能忽略 callback／IRQ／alias 的可能副作用。live state、seed 初始化、entropy、分布、重現性或密碼學品質均未驗證。

## Byte-range 不是 modulo

`0x43E6A` 先保存 lower 與 upper、呼叫 core，再做原始 `MULHSU`：

```text
result = low8(lower + high32(signed32(upper-lower) * unsigned32(rand_result)))
```

獨立解碼已確認 signed A1／unsigned A0 的 operand 順序，保留明確 ISA port，沒有改寫成 modulo 或 `MULHU`。在 0≤lower<upper≤255 的數學條件下，結果位於 `[lower,upper)`；lower==upper 時為 low8(lower)。原函式沒有一般性的 bound guard。

既有完整 callback `0x60516` 的兩處 call `0x605C2`／`0x606A4` 都傳 A0=1、A1=record+19 的 unsigned byte，將結果存入 record+17 的 byte。沒有證明 upper 必定大於 1，也沒有確認這些欄位的應用語意或時間單位。

## 原 APP 的 seed callback 來源

既有 initializer `0x199E2` 在 `0x19A74` 載入 table `0x4007C`，於 `0x19A90` 寫到 SP+52，即 64-byte config 的 srandCB+36；此 store 支配 library config call。官方 header 的 callback 型別 `uint32_t(void)`、config 大小 64 與 offset36 均經 C11／C++17 編譯 assertions 核對，物件沒有 runtime allocation 或 stub。

候選 `0x4007C` 對應 primary `TMOS_GetSystemClock`／`BLE_LIB_JT(18)`，target `0x43520..0x4354A` 的 42-byte 本體已存在。若 ROM 相符、原 config copy64 至 `0x200031EC` 成功，且 pointer／callee／memory／IRQ／alias 條件成立，preferred word `0x20003210` 可對應該 provider。**實際 RAM 指標未觀測，間接 call 的全部效應仍未封閉**。

## 驗證與使用

[C/C++](resident_range_random.c) · [primary ABI assertions](random_abi.c) · [證據](evidence-v1.json) · [收據](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-range-random/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需固定的本機 APP／SDK、官方 header 與既有 Windows NDK LLVM native artifacts；不下載依賴。跨平台驗證未確認。

實際 C／C++ 非載入 ET_REL 組合為 **20,490 CODE＋256 DATA／7,025 指令**；每個輸入 byte／symbol／relocation 保留、原始 CODE 位址不重複、兩個獨立 ELF reader 一致。真實本體解析原 `0x43E6A` 依賴，具名缺口由 11 降為 **10**，沒有 stub；仍有 1 個實際 opaque callback site，不能以 UND 數量代表 runtime 封閉。

APP 維持 159 C/H、95.54% 位元組覆蓋率，不是功能完成率。4-byte 啟動來源缺口、設定 writer 額外 144-byte 來源初始化、ROM／RAM／ISA／IRQ／Flash／OTA 相容性仍開放。未連入 APP、未產生新 BIN，未執行目標／HOST model／ISA 或硬體；**尚未成功重建可用替代韌體**。後續唯讀功能候選為 callback bounds／seed 來源診斷，尚未實作 UI，也不修改任何硬體參數。
