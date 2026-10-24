# 原始 ROM 表與回呼流程重建

[English](readme.en.md)

已接入 [C/C++](../../src/native/receive/rom_driver_family.c) 的六個完整函式，合計 **564B／208條指令、57個原始區塊、37個直接控制轉移與兩組函式位址參照**。包括171BA換算入口、主初始化173A2與四個必要依賴；所有RET後的相關分支均保留。

| 完整原始範圍 | 大小 |
| --- | --- |
| `171BA–171DE` | 36B / 14i |
| `171DE–172B6` | 216B / 76i |
| `172B6–17320` | 106B / 38i |
| `17320–17344` | 36B / 14i |
| `17344–173A2` | 94B / 37i |
| `173A2–173EE` | 76B / 29i |

原生C11／C++17元件一致：**15232B code＋674B data、5304條指令、1004 RELA、80 UND**。先前14668B code與674B data保留。接通兩個舊入口後，實際展開9792、9FC2、A2EE、ABF2四個新依賴，因此78→80；未用stub代替它們。原生連結器配置的 **15906B** 全部與官方BIN原址相同。產物是entry=0、無PT_LOAD的診斷ELF，**不能燒錄**。

171BA從40060讀取函式位址，以A0=byte[GP+365]、A1=1間接呼叫，再執行低32位乘10、邏輯右移4、加50。其餘路徑保留40038／40048／40050／40058／4005C／40080表項、原始16B frame、S0／S1及DIVU／REMU操作。173A2將172B6位址傳入40080表項指向的函式，再把回傳值的低byte存GP+365；這沒有證明執行過回呼註冊。數值單位與ROM函式語意仍未知。

對19B資料的追查：已編譯的D272將A0=2000BF48、A1=0、A2=19交給40048表項的函式；新173A2使用相同表項，參數為GP+364、0、1。這是清零形狀的參數證據，尚未證明實際ROM實作或寫入事件。原reset在186AA的兩條指令可靜態算出GP=20004000，但執行時GP保存、RAM所有權及欄位用途仍未證，不能據此命名VIN。

[原始指令與範圍限制](evidence.json) · [結果、ROM位置及雜湊](summary.json) · [80個待完成提供者](next-providers.json) · [整合器](../../experiments/tsl9-rom-driver-family/integrate-v1.py)

來源集104個C/H、77個code units及1個獨立資料單位，共156組比對／312物件。舊152組結果及913筆產物記錄保留。875條直接轉移中795條指向實際指令，80條仍為未實作參照；4873個普通順序位置與311個可能call-return位置皆有指令。254個暫存器間接轉移、10個MRET及8034 EBREAK後續仍待證，未宣稱完整CFG。

第一次C編譯要求額外S-register保存並拒絕三處c.j語法；接受的v2以明確原始暫存器操作保留框架，未改編譯旗標。整合v1因檢查器的ELF型別常數錯誤而拒絕；修正為正確FUNC info18後的component-v2才是本輪正式證據。失敗記錄保留，不當成通過結果。

下一步追四個新依賴與installed-ROM契約。可新增功能候選為**離線ROM表呼叫參數與換算診斷**，目前僅提案，顯示原值與未知單位而不改硬體控制。

實體MCU、RAM／ROM、完整啟動／私有ABI／非同步IRQ與OTA仍未證。未執行目標、HOST模型或ISA模擬，未連網或接觸硬體，未產生BIN或commit／push；歷史個資問題尚存。

```sh
python3 experiments/tsl9-rom-driver-family/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rom-driver-family/build/component-v2
python3 experiments/tsl9-original-layout/build-v10.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/rom-driver-family-v1
python3 experiments/tsl9-original-layout/verify-flow-v9.py --replay experiments/tsl9-original-layout/build/rom-driver-family-flow-v1
```
