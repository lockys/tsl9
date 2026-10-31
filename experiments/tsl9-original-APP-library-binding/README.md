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

### 候選 BLE 記憶體池與其他 RAM 區間

在上一項初始幾何、兩個 free 節點和 sentinel 均正確且沒有其他配置的前提下，`0x20000040` 候選配置器檢查的是**單一節點**是否足夠，不是將兩個 payload 大小相加。對原始請求 `1..65532` 且第二參數非零，最大初始連續 payload 為 **27,600 bytes**；27,601 經 4-byte 對齊變成 27,604，超過兩個初始節點各自的大小。若走到串列末端、候選失敗 callback 未設定或正常返回，該 helper 走返回 0 的路徑，沒有在 callback 後重新搜尋。

這只是以[候選配置器](../tsl9-resident-heap-core/README.md)和前述 V1.31 初始化推算的條件式邊界；實機 resident、記憶體、串列、callback、並行修改與實際最大配置量均未驗證。大於 65,532 的輸入另涉及 16-bit 回繞，不能套用此上限。檢查器固定兩份候選來源並驗算對齊與幾何，沒有執行 allocator 或設備。


以原 APP 傳入的 `MEMAddr=0x2000418C`、`MEMLen=0x7000` 代入[既有 V1.31 heap 初始化公式](../tsl9-resident-heap-initialization/README.md)，第一節點為 `0x200043AC`、第二節點為 `0x200045AC`、sentinel 為 `0x2000B184`。依該候選初始化的 8-byte header 與長度欄位，兩筆初始 payload 數值分別為 **504** 與 **27,600 bytes**，合計 28,104 bytes；池開頭另有 544 bytes，兩筆 header 加 sentinel 共 24 bytes。

這是原 APP 設定和**V1.31 候選**初始化程式的條件式交叉推算：需實機 resident 與候選相符、設定正確複製、位址／記憶體有效、初始化正常完成且無重入或覆寫。它不證明實際可配置容量、池子所有權、V1.40 使用相同全域位址或實機已啟動。[檢查器](check-ble-pool-bounds.py)固定 APP 指令窗口與候選來源，檢查數值範圍；沒有執行目標。


`0x19A3A..0x19A46` 將數值 `0x2000418C` 寫至 config offset 0，將 `0x7000`（28,672）寫至 offset 4。依固定版本 [WCH BLE config 定義](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h)，這兩個欄位分別為 `MEMAddr` 與 `MEMLen`；若原機 ABI 相符且設定未被後續呼叫或 alias 改寫，傳入的候選記憶體池為 `[0x2000418C,0x2000B18C)`。後續 `0x19AD2..0x19ADC` 檢查 pointer 非零與長度至少 `0x1000`，不檢查整段實際 RAM 可用性。

此數值區間完整位於原 APP reset 的 `[0x20004080,0x2000C958)` 清零範圍。它位於 GP+384 的 slot2 指標 `0x20004180..0x20004184` 之後，也在已識別的接收 payload 窗口 `[0x2000B9D8,0x2000BDE8)` 之前，相距 `0x84C` bytes；這只排除**這兩個已識別區間**的數值重疊，不證明整個池子沒有其他 APP、DMA、stack 或 resident 使用者。

依既有 WCH 連續 RAM 範例，池子超出 32 KiB 範圍，但位於 48／64 KiB 的數值範圍；完整 reset 與其他已知存取仍有更高要求。這不是實機記憶體配置、pool 初始化成功或完整所有權的證明。[靜態檢查器](check-ble-pool-bounds.py)核對固定原始指令及區間算術，不執行目標或讀取排除區。

候選 slot `0x400A4` 指向 BLE_LibInit `0x43C7E`。其 zero／copy64 至 `0x200031EC` 後，`0x43D38` 讀 config+44 呼叫 tsCB，並將低 halfword 寫入 baseline `0x200031A4`。前輪 monitor `0x43EDC` 讀相同 tsCB／rcCB words。因此，在**實機 ROM 相符、copy64 完成、有效不重疊記憶體、callee／IRQ／alias 條件成立**時，可把這些間接呼叫對應到既有 APP C/C++。尚未觀測實機 RAM 中的指標，原 opaque calls 的作用並未全部封閉。

rcCB `0x197B8` 以 A0=3、無自身 frame 尾跳既有 `0x1929A..0x196C4` 校準 worker；worker 自身 frame 為 80 bytes，保留原始 signed DIV／輪詢／RMW，沒有宣稱校準收斂或全程 stack 上限。

## tsCB 回傳資料寬度

既有 `0x197F0..0x1995C` callback 在 `0x198DC` 呼叫 ADC 候選 helper `0x18A66`。該 helper 用原始 **C.SLLI16／C.SRLI16** 取低 16 bits；結果在 `0x198E0` 保存至自身 SP+28，於 `0x1991E` 載回、`0x19948` 移至 A0。

上述 call／save／load／move 支配正常 return，且此 frame 的 SP+28 只有該明確 word store。14 函式 CPU-store 合約重新核對通過。因此在該合約的有效記憶體、callee 正常返回、nonalias 與無非同步覆寫條件下，原始 callback 的返回值位於 0..65535。這收斂前輪 uint16_t ABI 的來源條件，**不證明攝氏單位、ADC 實體身分或校準成功**。

## 版本與 IRQ：證明的邊界

原 APP 只比較 21-byte `CH32V20x_BLE_LIB_V1.3` 前綴；候選 table 的版本 pointer 為 `0x6E6A0`，比較 provider 是已有本體的 RAM `0x20000442`。候選前綴吻合，但這個比較不區分完整 library 版本或晶片料號，也不證明實機 ROM 身分；仍要求指標有效與 comparator 契約。

### 版本 gate 與候選 comparator 的特殊契約

`0x199F4..0x19A08` 從 `0x4003C` 載入比較目標，從 `0x40034` 載入版本指標，傳入 APP 字串與長度 21；返回值非零才往 `0x19A0A` 繼續，零則停在 `0x19A08` 自迴圈。候選 `0x20000442` 對有效、非空的相等資料返回 1，遇不相等返回 0，因此與標準 C `memcmp` 的「相等返回 0」慣例相反。直接換用標準 `memcmp` 會改變此處的分支行為。

候選比較函式在任一輸入指標為 0 或長度為 0 時也返回 1，而且仍先讀取、暫存及清零 `0x4002420C`、執行 `FENCE.I`，返回前恢復該 word。因而若假設 `0x4003C` 是此候選、但 `0x40034` 恰為 0，且 MMIO 操作正常完成，這個 APP gate 會繼續，不能當成已驗證有效版本字串；這是條件式反例，不是已觀測到的實機狀態。原候選 table 本身記錄的版本 pointer 非零。之後 `0x19AD2..0x19AE0` 另檢查設定 pointer 非零及大小至少 `0x1000`，`0x19AEE..0x19AF0` 在 library initializer 非零返回時自迴圈；通過版本 gate 不等於完成初始化。

這些結論仍依候選 ROM／slot 身分、記憶體、原始指令與無干擾條件成立；不證明實際可達、實機版本或異常。[檢查器](check-version-gate.py)只核對 APP 與公開候選的有限指令／table 窗口，沒有讀取排除區或執行目標。

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
