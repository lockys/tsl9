# BLE 綁定前的設定讀取、預設值與 Flash 路徑

[English](readme.en.md) · [早期 IRQ 證據](../tsl9-original-APP-early-IRQ/README.md) · [SDK 啟動／slot2](../tsl9-resident-slot2-startup/README.md)

核對既有 C/C++ 的 **9 個完整函式，728 CODE bytes／240 指令**，另有 4-byte 初始 RAM pointer。原 BIN、兩份原位址 C/C++ 診斷 ELF 與兩個獨立 ELF reader 一致。**沒有新增 target code 或編譯、BIN 或實機操作。**

## 條件設定路徑確實早於 library binding

主 initializer 的 `0x9264` 呼叫 `0x131C2`，在完整正常返回 CFG 中支配 `0x9268` → `0x8E88` 的 library call。`0x131C2` 透過 table `0x4004C`，要求將數值位址 `0x08077A00` 的 112 bytes 複製至 RAM `0x2000C29C`。

候選 SDK 的 `0x4004C` 指向已有完整 58-byte 本體的 RAM copy provider `0x20000332`；`0x40048` 指向候選 fill provider `0x2000039C`。它們的實機身分、私有呼叫契約、有效來源／目的與非同步效應仍是必要條件，不能視為普通 libc 或已量測的 Flash API。

原碼檢查 `0x2000C2A8..0x2000C2AC` 的 4 個 bytes：`low8(byte-32) <= 94`，等價於 ASCII 32..126。若遇不符條件的 byte，在 `0x13204` 呼叫預設值函式 `0x1316A`；存在不呼叫該函式的正常 CFG 路徑，不宣稱每次啟動都會寫入設定。

預設值函式要求對 `0x2000C29C` fill 0／112 bytes，再將一個 4-byte literal 複製到 incoming GP+84 word 指向的位址＋12。原 reset 的 128-byte data copy 包含 `0x1ABB4` 的數值 pointer `0x2000C29C`；在 GP／copy／pointer 未被後續改寫的條件下，目的為 `0x2000C2A8`。這不是實機 RAM 觀測。**受排除 literal 的內容與獨立 hash 均未讀入證據或公開。**

`0x131BE` 釋放自身 16-byte frame 後，尾跳 writer `0x13138`；writer 在 `0x1315E` 呼叫既有 Flash transaction `0x9C0A`。其他設定 fallback callees 與其完整副作用仍未封閉。

## 112-byte copy 與 256-byte program 是不同範圍

writer 配置 272-byte frame，將上述設定 buffer 的 **112 bytes 複製到 own SP**，saved RA 位於 SP+268。接著以 destination=`0x08077A00`、source=own SP 呼叫 `0x9C0A`。

Flash program leaf `0x18EF2` 將 A2 改為 **256**，destination 低 8 bits 清零。第二個 fresh status poll 正常退出時 A5=0；loop 依序讀取 source+offset 的 word，寫至 aligned destination+offset，以 offset+=4／offset==256 結束。在一般指令、有效記憶體、無 fault 且 polling 全部正常結束等條件下，數值上是 64 次 CPU word transfer。

因此來源範圍為 **own SP..SP+256**，在 frame 內且不碰 saved RA。writer 明確複製的是前 112 bytes；對額外 **144 bytes** 沒有直接 fill／copy，初始化來源仍未證明。這是證據缺口，**不是已觀測到的未初始化內容、資料洩漏或寫入失敗**。不得擅自補零、縮短搬移，或把它宣稱為完整初始化的 256-byte 設定。

## Flash transaction 的 IRQ 邊界

`0x9C0A` 的自身 frame 為 32 bytes。它在 `0x9C1A` 清除 CSR `0x800` 的 `0x88` bits，呼叫 5 個已有完整本體的 status／unlock／erase／program／lock leaves，再在 `0x9C3C` 設定該 mask，之後才還原 S0。這是無條件 set，不是還原進入前的 mask 狀態。leaves 保留 S0／S1／GP／SP，沒有其他 call／CSR 指令；所有 calls 與最後 set 在正常 CFG 中支配 return。

這補上另一條 **library binding 前可能發生的 Flash／global-enable 路徑**，但不證明 polling 終止、實體 Flash 成功提交、NVM 位址映射／容量、初始 BB/LLE enable／pending、實際 IRQ delivery 或非同步 alias 效應。

## 使用與狀態

[設定 C/C++](../../src/native/startup/main_initializers.c) · [預設值／writer C/C++](../../src/native/startup/settings_defaults.c) · [Flash transaction C/C++](../../src/native/receive/ota_runtime.c) · [證據](evidence-v1.json) · [收據](verification-v2.json) · [摘要](summary.json)

```sh
python experiments/tsl9-original-prebinding-settings/verify-v2.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需固定的本機原 BIN、候選 SDK、官方 header 與既有 Windows NDK LLVM native artifacts；不下載依賴。跨平台驗證未確認。APP 維持 159 C/H、95.54% 位元組覆蓋率（不是功能完成率），SDK 維持 20,346 CODE＋256 DATA、11 個具名依賴。4-byte 啟動來源缺口與 ROM／RAM／ISA／IRQ／Flash／OTA 相容性仍開放；**尚未成功重建可用替代韌體**。

後續功能候選：對使用者合法提供的 NVM backup 做離線相容性預檢，顯示設定驗證與來源範圍缺口；尚未實作，不自動修補或寫入硬體。
