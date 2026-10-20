# TSL9 R81 C/C++ 原始初始SP位址常數

新增 `src/target_stack_address_r81.c/h`，以原始指令推導的`0x20010000`定義`__tsl9_stack_top`。它是GLOBAL/default/NOTYPE/ABS、size0的純位址常數，沒有OBJECT／FUNC，也沒有配置code／RO／RAM／stack bytes。原有函式、指令、資料及配置區間保持。這不建立實體RAM容量、stack範圍、IRQ或有效性證明，**目前仍無可藍牙燒錄BIN**。

原18406的AUIPC與1840A的ADDI得到 `(0x18406 + 0x1FFF8000 - 1030) mod 2^32 = 0x20010000`。唯一相依轉換是18406的HI23由U(stack_top,0)轉成A(20010000)，own LO24仍指向18406。這是原位址expectation；`C950..10000`的14000B只屬地址算術差距，沒有任何stack保留或容量證據。

C與C++離線結果一致：platform SHA256 `b03e558f5779283a68030cb9ee9a98935f71355f478e309aa7701caf0af67ef4`，memory SHA256 `e60e2df377b398c564e18203de2669da62cb8745309eeb29061aa1c17ff04eab`。保持771個FUNC、5654條重定位、4685B RO、668個memory區塊與唯一136B initializer；新單元0個配置區塊／0個重定位／0個FUNC。新工具產生的非配置attributes marker會另記，不當作程式或資料provider。

目前只剩`__tsl9_opaque_address_19d10`與`__tsl9_rom_entry`兩項嚴格連結錯誤。原18484為`JAL x0 → 0x40000`；已知PC數值不構成resident code provider，ROM仍維持UND。完整原始回應及ZIP對應載體確認Runtime只有76800B，在目前base8000分析模型下覆蓋`8000..1AC00`，不足原raw-U8索引域所需的`1AC00..1AD10`共272B。沒有填值或借用其他模型的資料。

來源BOOT僅`1000..4000`，也未提供root`0000..0FFF`或ROM40000。實體MCU／PCB／晶振、ROM身分／ABI、RAM0/4/8、stack／IRQ、最終VMA/LMA與OTA相容仍未證。來源V4.1.00與截圖V4.1.60不同。原下載完整75頁，未發現extractor漏掉尾端；原APK只查成員metadata，巢狀內容與updater未讀部分尚未排除。

有效驗證仍為 `pwsh -NoProfile -File ./verify-native.ps1`，可加 `-Cpp`；Python只驗證靜態證據。全程沒有網路、識別資料外傳、硬體操作、目標執行或模擬。下方各輪內容保留為原來源快照，其舊source guards不當成本輪現行來源驗證。

---

# TSL9 R80 C/C++ BLE 比較資料視窗

本輪有效流程仍是 `verify-native.ps1`（可加 `-Cpp`）。新增 `src/target_ble_compare_view_r80.c/h`，只發射原始資料差集48B＋4B；與既有2152B合成 `[1A2D0,1AB6C)` 的2204B單一配置。提供 `[1A2D0,1A8F4)` 的1572B byte view；沒有重複配置舊資料或136B initializer，也未改動原程式指令。

1572B是**有條件的捕獲視窗**，不是原始物件大小或實體ROM讀域的證明。來源迴圈在正常返回／callee-save前提下k=0..3，LBU任意0..255，最大起始位移1566；再假定比較長度6表示byte-count且不超讀，才得到該範圍。公開候選header只定義`uint32_t len`，未明說byte單位或不超讀；實體ROM身分、ABI與stack條件仍未證。資料型別與身分用途亦未知。

兩語編譯結果相同：platform SHA256 `7471787af802e76ae5aa9e92fcfc80a275e599fafc30539ee7fb40a40d17aab0`；memory SHA256 `32f5a12ed33ecae7068b816d3363dd3ff92e26f908df13b0ab326ccd40e4e96e`。保留771個FUNC與5654條重定位，RO4633→4685B，memory配置區塊675→668。只將11EB8對A2D0的資料相依綁到真實共體view；原48條R79表格重定位、8個回呼指標與原空值保持。

目前剩3項嚴格連結錯誤：`__tsl9_opaque_address_19d10`、`__tsl9_rom_entry`、`__tsl9_stack_top`。19D10完整4096B raw讀域仍缺272B；不得以正常索引猜測、補零或忽略UND產生韌體。原機根啟動、MCU／PCB／晶振、ROM、RAM0/4/8、IRQ／stack、最終VMA/LMA與OTA相容均未確認，**尚無可藍牙燒錄BIN**。

重建使用C/C++與RV32 inline assembly；Python只做靜態證據核對。來源V4.1.00與截圖V4.1.60不同，全程未連網、操作硬體、執行或模擬原始／重建目標。下方R79及以前內容是歷史來源快照，其舊source guards不當成本輪現行來源驗證。

ELF的8個舊匿名LOCAL／STT_SECTION容器隨共體配置被一個A2D0容器取代，並非其symbol multiset保持不變。保持的是所有原具名／mapping／FUNC／OBJECT資訊與RELA原位址／target語意；唯一資料相依轉換是A2D0 UND→有支撐的1572B OBJECT。

---

# TSL9 R79 C/C++ BLE 回呼相依與原機靜態重建

目前有效流程為本輪 `verify-native.ps1`。C、C++離線編譯與ELF核對均通過，未解析相依由8降為4；**尚無可燒錄BIN**。下方R78內容保留為歷史紀錄，其舊收據對應舊來源雜湊。

- `target_callback_native_r79.c/h`：以原始RV32/RVC指令及語意重定位表達41個入口視窗，23段實體程式共9868B／3323條指令。共享尾段只配置一次；`void(void)`宣告僅作發射錨點，沒有聲稱恢復原始C函式原型或ABI。
- `target_callback_tables_r79.c/h`：四份12B描述資料，以重定位連到8個真實回呼入口，保留4個原始空值；另有12B有條件的原始資料視窗，其型別、身分用途與完整物件邊界未知。12B複製長度依賴有效且不回繞的stack與目的位址條件，尚未證明原機條件。
- 兩張既有跳轉表共96B，保留24項相對位移的48條ADD32/SUB32重定位。16個名稱只指向已存在的LOCAL函式所在section，不將原符號globalize，也不用絕對PC假裝缺少的程式。
- 原618段程式、707個FUNC及4591條重定位原意保留；加入後有771個FUNC錨點、5654條重定位、4633B RO與675個配置區塊。新增64個FUNC錨點包含23段發射區域及41個入口視窗，不能據此認定恢復了64個獨立原始函式。
- C與C++產物相同：platform SHA256 `b606f15097b90f0d17c56a8a42f48c47da4028d1d2561ff21504b8ec672f8241`；memory SHA256 `1a4da597a1314e35b185e807729a19a4960269e07b4386fdee64db0115cce1cc`。136B initializer只配置一次，37個RAM aliases保持。

嚴格最終連結仍必須拒絕以下4項：`__tsl9_ble_event_ro_1a2d0`、`__tsl9_opaque_address_19d10`、`__tsl9_rom_entry`、`__tsl9_stack_top`。沒有補零、忽略相依或改掉原分支。19D10雖能在額外條件下推得索引0..5，但ROM與pointer alias寫入範圍未閉合，不能縮小完整4096B域；現有映像仍缺272B。

證據固定來自V4.1.00，與截圖V4.1.60不同。原機MCU／PCB／晶振、根啟動、ROM身分與ABI、RAM0/4/8、IRQ／stack、最終VMA/LMA及OTA容器相容性尚未確認。全程沒有網路、硬體操作、目標執行或模擬。Python只做靜態證據驗證；重建內容仍是C/C++與RV32 inline assembly。

---

# TSL9 R78 C/C++ 有限查表與原機記憶體靜態重建

此實驗以 C/C++ 加 RV32 inline assembly，補入三個已證明直接讀取範圍的查表視窗，並將既有初始化映像移入同一份實體資料。工作目標仍是原硬體的藍牙 OTA BIN；**目前沒有可燒錄 BIN**。

本目錄是新增的原機執行層實驗。`../tsl9-contract-model` 的既有 R77 程式、來源檢查與驗證流程保持原樣；舊流程仍報11個 memory UND。本輪新流程報8個，兩者不得混為同一份收據。Python 僅解析 ELF 與驗證證據，重建目標仍是 C/C++。

已完成的靜態改變：

- `src/target_lookup_domain_closure.c`：15個差集 fragment，共1118B；與原有15個 RO 區塊按原位址合成兩個連續視窗，共1298B。三個 lookup views 分別為274B、512B、1024B，後兩者有包含關係。
- 1298B中已有180B的 RO 與136B的初始化映像。相對前一輪 memory 物件，實際新增982B。保留六筆跳躍表的12條 ADD32/SUB32 重定位，並計算後比對原始切片；不能只以 raw placeholder bytes 判斷相同。
- `src/target_runtime_ram_only.c`：從既有 memory C 明示移除 initializer definition，保留其餘原敘述；完整原檔在 `provenance/target_runtime_memory-r77.c`。`data_load` 仍是原址136B RO OBJECT；`data_start` 仍是 RAM 的136B OBJECT，另有35016B BSS。平台先綁1個 initializer，memory 再綁37個 RAM aliases。
- C 與 C++ 的靜態物件相同：平台 SHA256 `71370adb8d9a5c377d9bf75913b1c994450b13d28a43a906559a08794c174103`；memory SHA256 `f5c67b279c0f81cd23e0427d32d43c50c86841d8b9edcea54ffcd04c3bd3c1c8`。618個函式本體、707個 FUNC 名稱、4591條重定位的原意均保留，RO為4573B，647個非重疊配置區塊。

在本目錄執行 `pwsh -NoProfile -File ./verify-native.ps1`，或加入 `-Cpp`。未提供 baseline 時會編譯既有平台；可用 `-BaselineReceiptPath <已存在的通過收據>` 重用平台，但會重新核對物件、全部來源與工具雜湊。實際本輪驗證重用 R77 已驗證平台，重新編譯／連結本輪 C、C++ 單元，沒有重新執行 RV32 指令。工具位置沿用這台 Windows 的 NDK 與 Python。

嚴格最終連結必須失敗，而且診斷須逐一包含仍未解析的8項：BLE constant、三個 BLE event 資料、BLE service callbacks、19D10查表、ROM entry、stack top。19D10的完整 byte 索引範圍會超出現有檔案272B；1A2D0會傳指標給 ROM，但讀取長度單位與持有規則未明。均未補零、猜測資料、忽略符號或改掉原比較／錯誤分支。

原始資料固定為 API V4.1.00，與截圖的 V4.1.60 不同。尚未確認實體 MCU／PCB／晶振、0000..0FFF根啟動、resident ROM／函式 ABI、RAM0/4/8角色、IRQ／stack、最終 VMA／LMA及原廠 OTA 容器相容性。ET_REL 的位址映射與 linker ASSERT 不代表已確定可執行配置，更不能據此燒錄。

本輪全程離線：沒有呼叫伺服器、傳送識別資料、操作 BLE／CAN／UART／SPI／Flash、執行或模擬原始／重建目標。數值視窗不代表恢復原始型別、物件邊界或完整原始碼。
