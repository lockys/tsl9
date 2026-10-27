# 原 APP callback 來源與初始化條件

[English](readme.en.md) · [前輪完整 parser／C/C++](../tsl9-resident-task-parser/README.md) · [既有 clock services](../tsl9-resident-clock-services/README.md)

本輪以 [C/C++ ABI assertions](callback_abi.c) 與跨單元驗證，串起四個原間接 call sites 的設定來源。**沒有新增韌體 CODE、provider 或 BIN，也沒有把原始間接 call 改成 direct call。**

核對原 APP 五個完整函式，共 **972 bytes／325 指令**：`0x8E88`、`0x199E2`、`0x19B16`、`0x19B56`、`0x191C6`。每個 CFG／自身 frame 均核對，所有 bytes 與既有 C／C++ 原位址診斷產物及原 BIN 相同，兩個獨立 ELF readers 一致。

## 三個 clock sites 的條件式來源

原 APP `0x19B56` 先清零16-byte caller config，再寫入 getClockValue=`0x191C6`、ClockMaxCount=`0xFFFFFFFF`、frequency數值16000、accuracy數值1000，irqEnable保持0。實際 `0x19BCC` 呼叫候選表 slot16／`0x40074`→`0x43F46` TimerInit。

非 null config 的成功值路徑會通過四個非零欄位檢查；irqEnable=0 跳過額外 connection-count guard。原 copy16 將設定寫至 `0x20003234`，再把首 word 寫至 `0x200031E0`。在成功路徑、正確 copy／callee 契約與欄位穩定條件成立時：

| 原間接 call PC | Fresh pointer slot | 條件成立時的原 APP 本體 |
| --- | --- | --- |
| `0x5F6D6` | `0x20003234` | `0x191C6..0x19220` |
| `0x5F708` | `0x200031E0` | `0x191C6..0x19220` |
| `0x4346C` | `0x200031E0` | `0x191C6..0x19220` |

`0x191C6` 是既有 **90-byte／28指令、frame0 leaf**。已以原 bytes 及兩份 native C/C++ 診斷核對：沒有編碼上的 store、callee、CSR 請求，也不改寫 RA／SP／GP／saved registers。它重讀 numeric MMIO halfwords `0x40002818`／`0x4000281C`，返回 `u32(high_last<<16 | low_last)`。**迴圈終止、coherent snapshot、MMIO實體意義、讀取副作用與實際時脈頻率仍未證明。**

16000／1000 是原 APP 設定值，單位依候選 header 為Hz／ppm，不是量測結果。TimerInit 也有 default／invalid paths；本輪沒有把 default path 與非 null copy path 合併。APP 在 `0x19B3A` 覆寫其返回狀態，**呼叫已發生不代表初始化成功**。

## Optional status callback 的 post-copy 條件

原 `0x199E2` 在 `0x19A38` 請求清零 `[SP+16,SP+80)` 的64-byte BLE config。primary `staCB` offset=52，對應 caller `[SP+68,SP+72)`；後續明確 local stores 與六位元組 MAC copy `[SP+40,SP+46)` 都未覆寫此 word。未讀取或公開實際 MAC values。

候選 BLE Init 的成功值路徑先 copy64 至 `0x200031EC`，故 offset52對應 `0x20003220`。若 memset／copy契約成立且沒有 callee、alias、IRQ或其他覆寫，該 slot 條件式為0；`0x434A4` null guard 會跳過 optional call `0x434AA`。

**此結論僅限 BLE copy64 完成後的穩定狀態，不證明 copy 前或初始化期間 heap-call 的 staCB 值。** 既有「早期 heap callback 值未證明」收據保持不變；沒有用後來的零值請求取代早期未知狀態。

## C/C++ 與未封閉條件

[requirements-v1.h](requirements-v1.h) 只列條件式位址需求；[callback_abi.c](callback_abi.c) 核對 primary clock/status 函式指標型別、RV32 widths、clock16／BLE64 layout與offset52。實際 C11／C++17 物件相同，**allocated bytes／providers／imports／relocations均為0**。include closure只允許本輪兩份source、確切hash的官方header與compiler resources。

原 APP main 的 local正常控制流在後續RF calls前依序呼叫 BLE與clock初始化；**尚未證明任何全域dispatch都在初始化後，也未觀測實機callback值**。仍需相符installed ROM、成功路徑、有效且穩定的記憶體、正確copy／memset與private-callee契約，以及無非同步alias覆寫。不能據此宣稱四個live callback或全程副作用都已封閉。

既有SDK組合保持 **25,102 CODE＋256 DATA／8,580指令／11具名缺口**；四個原間接call ports不變。APP仍159 C/H、95.54%位元組覆蓋率，**不是功能完成率**。4-byte啟動來源缺口及ROM／RAM／ISA／IRQ／Flash／OTA相容性仍開放。

[證據](evidence-v1.json) · [完整驗證](verification-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-original-callback-provenance/verify-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機APP／SDK、既有native artifacts與Windows NDK LLVM；無下載，其他平台未驗證。沒有target／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。後續唯讀 callback來源／初始化條件顯示仍是未實作UI候選，不修改live callback或硬體。
