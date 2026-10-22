# R77 最新進度

本輪補入432B查表資料與兩個provider；所有618個函式本體、707個FUNC名字、4591重定位及原3023B RO保持。資料只按首次load之前的算術界限選取，沒有將19D10的重疊前16B當作完整provider。memory剩11個真實UND，最終連結仍嚴格失敗。[分析](analysis/round77/README.md)／[原機條件](analysis/round77/native-target-status.md)。

沒有新增已驗證的原機功能或擴大130-row host fixture覆蓋；兩語2540項host檢查維持。四份BLE descriptor雖在兩個候選header均為三callback欄位，真實ROM provider的讀取extent仍未知，因此未供應48B猜測物件。尚無可藍牙燒錄BIN。

---

# R76 最新進度

新增37個有真實consumer證據的callback/helper及546B有限資料視窗；原581個函式本體、2477B RO及174份C/H完整前綴保持。整合618個本體／707個FUNC符號／4591個重定位，memory剩13個真實未解析項目。[完整證據](analysis/round76/README.md)／[限制與原機條件](analysis/round76/native-target-status.md)。

這一輪是靜態實作與ABI/位元組證據；130-row host fixture的2540項檢查保持，未新增原機功能驗證。546B是已明示選取的compare/copy/lookup operands，545B有讀取／請求範圍，另1B只維持數值位址起點；原始物件邊界及ROM服務語意仍有條件。尚無可藍牙燒錄BIN。

---

# R75 最新進度

新增199個必要helper／分派與回呼區塊的C/C++重建（24,500B／8,011指令）及10張有界跳躍表（1,036B）。指令位元、573個直接轉移、510組PC位址配對與259組表格語意重定位均通過；原382個本體與1,441B RO保存。整合581個實體本體，memory仍有70個真實未解析符號。

這是離線編譯與靜態核對，未增加130-row凍結host fixture所涵蓋的硬體行為，也不代表免打擾或其他整機功能已在原硬體驗證。尚無可藍牙燒錄BIN。[完整證據](analysis/round75/README.md)／[尚缺條件](analysis/round75/native-target-status.md)。下方保留歷輪記錄，以R75判斷目前狀態。

---

# R74 最新進度

新增66個必要程式區塊的C/C++原生重建（3400B／1124指令），既有C/H保持不變。整合後382個physical bodies、137個未解析memory符號，尚無可燒錄BIN。完整範圍、收據統計更正與限制見 [R74分析](analysis/round74/README.md)。

入口：`pwsh -NoProfile -File ./verify.ps1 -Suite target-settings-accessors-native`（可加`-Cpp`）。下方保留歷輪說明，以R74實際收據判斷目前狀態。

---

# R73 最新進度

已加入 30 個必要 callback/helper 的 C/C++ 原生重建（2,064B／708 指令），並重用七個既有私有函式；兩語編譯及靜態指令／重定位比對通過。整合後有 316 個 physical bodies、164 個未解析 memory 符號，仍無可燒錄 BIN。完整範圍、限制與目的地收據見 [R73 分析](analysis/round73/README.md)。

新入口：`pwsh -NoProfile -File ./verify.ps1 -Suite target-startup-callbacks-native`（可加 `-Cpp`）。原有歷輪說明保留在下方；以 R73 的收據判斷目前進度。

---

# R72 當前覆蓋與缺口

新增87C4 BLE callback632B／217ops、5組HI/ownLO、15個間接呼叫；保留原事件優先、完整回值、跨call的fresh讀寫、null判斷先後與兩種不同status條件。沒有恢復或假設ROM原型／事件語意。原27660B BLE前綴及6778B記憶體來源前綴保持；原37個RAM標籤、136B opaque initializer與35152B NOBITS均保持。

平台286physical／330FUNCnames／72public／44hidden／218UND／1840relocs／1441B RO；原33個其他component SHA保持。新BDF8僅zero-size NOTYPE位址標籤，不推定物件extent；38bindings後仍180UND，新19A78資料來源未解。init直接圖120body／159sites不變，原地址缺口降至6symbols／6sites，但新callback另外需要19A78來源。

每語unit6＋platform286（含entry-JAL）=292，共584原生cohort核對；layout286physical各語保存共572。Host仍每語2540/0、89native／98總guard，130row fixture不變；53 frozen仍45whole＋8prefix，六個alias容器與兩個code append容器，BLE完整前輪prefix核對更新到27660B。[R72證據](analysis/round72/README.md)。總UND沒有下降；新增原callback本體與位址證據不等於可燒錄。以下保留歷史紀錄。

# R71 當前覆蓋與缺口

新增 AEEC 原 callback44B／14ops：bit0 clear 回0且不碰記憶體；odd 路徑依序LBU GP+193／194／195，僅當值≤2時SB值+1，最後保留完整32bit a1 XOR1回值。GP+192不被callback讀寫。這只證明原指令行為，不推定事件名稱、時間單位或ROM實際invocation。

既有 feature-init 完整27069B前綴保留，unit27→28 bodies、16UND／59relocs；平台285physical／329FUNCnames／71public／44hidden／217UND／1830relocs。原33個其他component SHA保持，原全部284physical保留；37記憶體綁定不變，記憶體層剩180UND。已知init圖120body／159sites／0directUND，地址剩7symbols／9sites。

兩語primary cohort各unit28＋platform285（含entry-JAL）=313，共626核對；相對layout各285個physical保存共570核對。Host每語2540／0，130row fixture不變；89native／98總guard，53 frozen來源為45whole＋8prefix，六個alias容器及兩個code append容器。[R71證據](analysis/round71/README.md)。MCU／ROM／provider／BOOT／IRQ／stack／最終VMA/LMA及OTA仍未證明，沒有可燒錄BIN。以下保留歷史紀錄。

# R70 當前覆蓋與缺口

本輪新增 reset data／BSS 的原生 storage 表示，沒有新增或猜測業務功能：136B 原初始化來源＋136B copy destination＋35016B BSS，後兩者共用單一 35152B SHT_NOBITS RAM 容器。34 個 BSS 地址別名皆為 zero-size NOTYPE；另 data_start／data_load 各為 136B OBJECT，bss_end 為 one-past point；stack_top 保留 UND。

36 個 RAM 位址＋1 個來源位址有實際 section backing。C／C++ ET_REL 同為 136508B、同 SHA；全部舊 284 physical／328 FUNC names／1830 relocs／1441B RO 保留。218→181 UND，922E 已知直接圖仍 120 body／159 sites／0 direct UND，地址缺口降至 8 symbols／10 sites。opaque source 裡可能有尚未分類、沒有 ELF relocations 的指標，故不能任意重定位或宣稱最終 image ready。

Host 每語仍為 2540／0；130-row fixture 未增加語意覆蓋，native guards 88、總 input guards 97；53 frozen來源仍 46 whole＋7 exact prefix。兩語全部舊函式各 284 個機器碼比較是保存證據，不是功能完成率。參見 [R70 證據與限制](analysis/round70/README.md) 與 [硬體條件](analysis/round70/native-target-status.md)。尚無可燒錄 BIN。以下保留歷史紀錄。

# R69 當前覆蓋與缺口

新增85E2原生callback406B／140ops：只在既有target_ble_platform.c完整16524B前綴後追加，舊四個單元函式與13B唯讀資料保持。保留48B frame、六個事件位元的原先後判斷、完整回值、GP讀寫與十一個ROM間接呼叫；不推定ROM單位、實際事件語意或呼叫成功。

34components／284physical／328FUNC names／70public／44hidden／218UND／1830relocs／1441B RO。舊283physical／327名稱不變，33個舊component raw SHA不變；原8FCA的HI23 callback地址現在有已定義本體。

主cohort為兩語unit5（四舊一新）＋platform284，共578 body checks；另568 layout保存核對。host fixture不變，各2540/0、83 native／92總guard；53 frozen來源為46whole＋7prefix，其中六個alias容器與一個原生本體append容器。這些數量不是完成率。

[當前frontier與證據](analysis/round69/README.md)：922E直接圖120body／159sites、無直接UND，仍有41symbols／80sites地址義務；全平台218UND仍致命阻止最終link。[硬體與BOOT gates](analysis/round69/independent-hardware-gates/README.md)仍待證；沒有可燒錄BIN。以下為歷史紀錄。

# R68 當前覆蓋與缺口

新增啟動檢查935C／9312／9298／926E四個原生函式，216B／87ops；6calls保留1個4B JAL及5個2B C.JAL。935C的儲存欄位與完整32bit結果比較、GP+175寫入、9298的兩次fresh ROM pointer load及JR tail均保留，沒有成功stub、實際UID運算或啟用生成器。

34components／283physical／327FUNCnames／69public／44hidden／219UND／1824relocs／1441B RO。舊279個實體函式及322個名稱的機器碼均保留；32個既有component raw SHA不變，config container僅追加273B hidden alias，完整R67來源前綴17664B保留。

每語unit4＋platform283，共574 body checks；另566 layout保存檢查。host各2540/0、82 native／91總guard，53 frozen來源仍47whole＋6prefix，新增一個完整前輪container前綴guard。fixture語意覆蓋未增加，數量不能換算完成率。

[本輪證據與限制](analysis/round68/README.md)。219個真實未解符號仍阻止最終連結；尚無可燒錄BIN。ROM參數8／6的長度單位、MCU／PCB／記憶體provider／IRQ／OTA仍未知。以下為歷史紀錄。

# R67 當前覆蓋與缺口

補上18CAA啟動讀取程式50B／14ops：只讀取原可執行code，未讀取實際UID或改動caller檢查。33components／279physical／322FUNCnames／68public／43hidden／220UND／1818relocs／1441B RO；舊278physical與32component SHA保留。原19808 JAL17現在有已編入目標。

unit及platform每語cohort1＋279＝560bodychecks，另558 layout保存檢查；host fixture不變，各2540/0，79native／88總守衛，53 frozen來源47whole＋6prefix。這些數字不能換算韌體完成率。

[本輪證據與限制](analysis/round67/README.md)。最終Flash配置、MCU／ROM／資料providers／IRQ／OTA仍缺，嚴格link因220UND拒絕，尚無可燒錄BIN。以下為歷史覆蓋紀錄。

# R66 當前覆蓋與缺口

新增dispatch section分離與已知Runtime linker契約：278 physical／321 FUNC names／67 exports／43 hidden／221 UND／1818 relocations／1441B RO均保留。148B reset已在單一ET_REL section內按0/138/142/146排列，沒有填充；原始holes仍未知。

LLD -r即使通過ADDR assertions也序列化sh_addr=0，因此仍不證明最終VMA/LMA。嚴格最終link因全部221UND正確拒絕，未產生executable或BIN。host fixture不變，各2540/0，76 native／85總來源守衛，53 frozen來源仍47whole＋6prefix。

[當輪證據](analysis/round66/README.md)。MCU／ROM／資料providers／IRQ／最終映像／OTA相容性仍缺。以下為歷史覆蓋紀錄。

# R65 當前覆蓋與缺口

新增 `target_reset_fidelity.c/.h` 與原生 verifier，保留舊 reset/clock 來源。原始 reset 148B 四段各有唯一 owner；新增主體與 private MRET 共142B／38ops，既有6B defaults未變。六組 AUIPC/ADDI＋兩個4B JAL已逐欄驗證，兩個 GP+136 端點仍由指令計算。

32 components／278 physical／321 FUNC names／67 public／43 hidden／221 UND／1818 relocations／1441B readonly。560 body checks只衡量編入片段，不能換算韌體完成率。53 frozen來源保留47全檔＋6 prefix；來源守衛72／總輸入81。host fixture未變，各2540/0。

[當輪證據及限制](analysis/round65/README.md)。完整 MCU／ROM／資料／最終 linker／IRQ／OTA 相容性仍缺，沒有可燒錄 BIN。以下為歷史覆蓋紀錄。

# R64 當前覆蓋與缺口

| 項目 | 已確認證據 | 限制 |
|---|---|---|
| 原生SystemInit | 234B／93ops，完整16B leaf frame、33個MMIO存取站點、SP8/12及RET後fail tail均保留 | 無實際時脈／IRQ timing／原機啟動證明 |
| 平台替換 | 舊10模型helper／1286B code與12B backend不再編入平台；新1個原入口仍為sc_native_init | 舊C/H與host測試保留，未將模型測試宣稱硬體驗證 |
| 舊成果保留 | 276非clock本體／319名稱、31raw components、82vectors保持 | 載入／provider／最終配置仍未閉合 |
| 依賴分類 | 222UND；150direct、60data/layout、5declared-code address、6opaque address、1ROMhandoff；495站點全有owner | 所有15個922E有序callee已定義，但呼叫可能阻塞／失敗，indirect未知 |
| 初始化 | runtime copy136B／BSS35016B；BOOT copy104B／BSS22840B | GP84/88/92有copy不代表pointer有效；RAM0/4/8在copy/zero之外 |
| 當前驗證 | 兩語554所選body/entry；host各2540/0；69來源guard／78總輸入 | 無新增R56 fixture語意覆蓋，非完成率 |
| 原機與OTA | V4.1.00固定輸入保存 | MCU/PCB、ROM/ABI、RAM/IRQ/stack/layout及原OTA仍待證，尚無BIN |

[本輪證據](analysis/round64/README.md)／[原機條件](analysis/round64/native-target-status.md)／[交付憑據](analysis/round64-delivery.json)。以下為保留歷史。

# R63 當前覆蓋與缺口

| 項目 | 已確認證據 | 未確認部分 |
|---|---|---|
| 優先相依分類 | 舊 136 UND：60 data/layout、1 ROM handoff、4 opaque address、66 direct callee、5 declared address；313 次重定位皆有原站點 | 232 個來源標記 indirect sites 是有界清單，非完整呼叫圖；不能稱 15378 為開機必要路徑 |
| 15378 服務分派 | 完整 3494B／1419 ops；37 calls＋170 tails；3 I-type PC pairs；253 ordinal／171 目標跳表 | 未證語意路徑可行性、被呼叫者 ABI、回值或硬體效果 |
| 共用與未知 | 9 個既有本體、4 hidden aliases；舊 15378 已定義；85 新直接目標＋2 opaque 地址 | 下游內容未讀，保留真 UND；總量 136→222 |
| 平台保留 | 32 components、286 physical／329 FUNC；舊 285 bodies／324 names、441B RO、82 vectors 保持 | ET_REL；無 ET_EXEC／BIN／原機啟動證據 |
| 本機驗證 | 所選兩語 552 body/entry checks；host 各2540/0；66 native／75 total guards | R56 的130列 fixture 不增加新函式語意覆蓋；非完成百分比 |
| 原機與更新 | 固定 V4.1.00 輸入身分及既有證據保存 | MCU/PCB、ROM/ABI、RAM8、IRQ、stack/layout、原 OTA 和 V4.1.60 差異均待證 |

[詳細證據](analysis/round63/README.md)、[原機條件](analysis/round63/native-target-status.md)及[交付憑據](analysis/round63-delivery.json)記錄目前結果。以下保留歷史，不能用舊數字代替當前狀態。

# R62 當前覆蓋與缺口

| 項目 | 確認證據 | 未確認部分 |
|---|---|---|
| 17A22訊息準備 | 98B／29ops；C91C+8 snapshot；SP4..10與SP15寫入，17A7A呼叫已有12864 | partial record、舊SP9/10留在a3/a4；不推定成功或硬體欄位語意 |
| 95EC timer callback | 74B／24ops；95F2 C.JAL→93EE、95F4 S-pair→BECC、962E C.J→9388 | 指標ownership／大小、未寫欄位、scheduler與回呼執行未知 |
| 相依閉合 | 3direct＋2pairs＝7真reloc；沿用1public＋2hidden bodies與2data symbols | 無新增alias或資料配置，仍136UND |
| 平台保留 | 31components／285physical／324FUNC；舊283本體及30raw components保持bytes | ET_REL；尚無ET_EXEC或BIN |
| 本機覆蓋 | 當前unit＋platform兩語552checks；host各2540/0；64native/73total guards | 130列fixture仍R56來源，新函式沒有host語意覆蓋 |
| 硬體與OTA | 固定輸入身分及先前未知條件保留 | MCU/PCB／ROM／RAM8／IRQ／stack／final placement／原OTA均未證 |

[詳細分析](analysis/round62/README.md)及[交付憑據](analysis/round62-delivery.json)記錄當前結果。以下保留歷史覆蓋，不能以舊輪次數字代替當前狀態。

# R61 當前覆蓋與缺口

| 項目 | 已確認證據 | 限制 |
|---|---|---|
| 事件相依8函式 | 原始code／canonical／fresh r2 一致；C、C++各1252B、15直接轉移、28PC pairs | 被呼叫者返回是語法CFG抽象，不證可達路徑實際可行 |
| 94E6 timer callback | 94EC C.JAL→93EE；9524 C.J→9388；952A RET完整保留 | 地址被引用不等於實際回呼成功 |
| 8386 header／frame preparation | 保留32位 shift／OR直到SH才截16；65536輸入反例已記錄 | 不推定傳送成功，ROM4004C參數單位未證 |
| 10D2E 掃描 | 保留GP+92指標及43B步距掃描／比較 | 未讀所指資料，不假定有效陣列界限或ROM回值語意 |
| 17D52 遞迴 | 17DF6 C.JAL與兩組self HI/LO真重定位 | 終止／最大深度／完整stack預算未知 |
| 平台整合 | 30 components；283 physical／322 FUNC；1099 reloc；138 UND | ET_REL；無ET_EXEC、BIN或硬體執行 |
| 舊來源保存 | 47整檔＋6完整prefix＝53凍結C/H；62當前native guards | 原130列fixture沒有新函式的host語意測試 |
| 硬體／OTA | 保留先前靜態限制與原始輸入身分 | MCU/PCB、ROM/ABI、RAM8、IRQ、位置與原OTA仍未證 |

[詳細分析](analysis/round61/README.md)與[交付憑據](analysis/round61-delivery.json)提供當前結果。以下為保留的歷史覆蓋記錄。

# 目前已重建功能：第六十輪

新增[11844事件handler C/C++](experiments/tsl9-contract-model/src/target_ble_event_handler.c)，2884B／915指令，完整syntactic CFG915nodes／282blocks。優先序8000→2→4→8→16→1，只選單一分支並保留raw32 XOR回值；無最終u16截位。32個indirectcalls均保留fresh load；實際ROM內容／ABI未知。

15條4B JAL、46組PC pairs（36I/10S）逐證，14RAM地址重用BFC4/BFD0/BFE8三既有symbol+addend。111D2及10C48新增兩strong hidden aliases共用236／182B；9102沿用既有300B alias。17Flash data、5callee及94E6 address-only callback維持真UND，未讀內容或猜配置。

29物件platform109680／109800B，275實體／310名稱、60public／35hidden、142UND／1028reloc。舊274實體／307名稱、27raw components、441B RO與82vector保持。unit兩語各8108B；主530body checks是當前unit/platform兩語cohort，非BIN完成率。兩語host各2540checks，60native guards、50frozen全檔＋3完整prefix，fixture仍為R56的130row。

UND120→142係消除11844、揭露5callee＋18address依賴；不把增加的未知當已完成，也不以dummy壓低數字。[證據](analysis/round60/README.md)／[原機缺口](analysis/round60/native-target-status.md)。仍缺原機V4.1.60、MCU/PCB/ROM/ABI、完整依賴、final image與OTA，尚無可燒錄BIN。

## 以下歷史輪次當時狀態

舊統計與opaque邊界屬各輪當時狀態；以R60為目前結果，不相加為完成率。

# 目前已重建功能：第五十九輪

新增[HAL callback原生C/C++](experiments/tsl9-contract-model/src/target_ble_hal_callbacks.c)：194EE read wrapper、19512 write wrapper、19544 ADC保存／取樣／還原與11個ADC／delay helper，合14函式／978B／366指令。21個4B JAL為20rd1＋1rd0 tail，沒有新data引用。三個HAL callback地址已接真定義，UND123→120。

四Flash與兩APB2 helper新增六strong hidden alias；memset8518共用既有alias。舊260實體／287名稱、25raw components、441B RO、82vector紀錄保持。兩個alias容器保留完整原source prefix。

28物件platform102584／102704B，274實體／307名稱、59public／33hidden、120UND／921reloc；兩語unit各4816B。主554body checks是當前unit／platform兩語cohort，非BIN完成率。host各2540checks，58native guards、51frozen全檔＋2完整prefix；fixture仍為R56的130row，未覆蓋新硬體效果。

原194EE／19512均回傳0並忽略底層狀態；19512忽略incoming a1，program helper固定讀256B。ADC選定16word save/restore、status/data未整體保存、poll無timeout，raw shift／fresh順序保持。回傳0不代表Flash成功。

[證據](analysis/round59/README.md)／[原機缺口](analysis/round59/native-target-status.md)。966unique公開ROM bytes包含code/data，reset→未保存6DD04，未閉合RAM0/4/8 population。仍缺原機V4.1.60、MCU/PCB/ROM/ABI、final image及OTA，尚無可燒錄BIN。

## 以下歷史輪次當時狀態

下列舊統計及opaque邊界為各輪當時狀態；以R59為目前結果，不相加為完成率。

# 目前已重建功能：第五十八輪

新增 [HAL原生C/C++模組](experiments/tsl9-contract-model/src/target_ble_hal_init.c)：19736完整308B／106指令與18E5A helper30B／12指令，合計338B／118指令、2條JAL、6組HI/LO。確認19736／1973A／19740從RAM8讀32-bit值、在無中間外部呼叫下寫入GP+384；WCH公開WCHBLE_Init reference提供相同cache流程，實際ROM值／硬體ABI仍未證。

保留原三個failure self-loop、96B frame、raw ROM結果判斷、6-byte外部結果複製與CRC/AHB→IRQ順序。1950C沿用既有6B strong hidden alias；版本資料1A7A0、heap numeric418C、identity reader18CAA、194EE／19512／19544 callback均明列外部依賴，不讀內容、繞過檢查或填dummy。

27物件C/C++98720／98840B，260實體／287FUNC names、56public／27hidden／123UND／900reloc／441B RO。舊258實體／285名稱、26raw components、RO、82vector紀錄保持。主502個body核對是本輪cohort，不是整機比例；新unit兩語各2256B，338B逐證。兩語host各2540檢查保持，56個當前native guards與53個frozen C/H來源保持。

R57的『RAM8未觀察』只適用當時26個已重建來源的範圍；本輪新讀取原HAL後已有實際RAM8 consumer與GP384 writer，保留舊封存並在此更新結論。RAM0／RAM4／RAM8自身population與pointer callability仍unknown。[完整證據](analysis/round58/README.md)、[原機/BIN條件](analysis/round58/native-target-status.md)。

## R57 歷史功能與當時驗證

延伸既有 [C 記憶體解析器](experiments/tsl9-contract-model/src/runtime_memory_layout.c)，新增 rml_observe_witness；同一來源以 C11／C++17 編譯。檢查 GP signed offset／RV32 wrap、point 與 observed window 的 Runtime／BOOT 分類、copy／zero 範圍，並把 pointer-provider 需求明確保留。address-only 的 bytes=0；不把地址、ROM raw operand 或最小 window 當成 allocation。

兩語 host 各 2,540 checks／0 failure，含 262 舊檢查、68 手寫邊界／反例及 130 個實際 GP 引用的 2,210 檢查；54 個原生來源／介面／整合腳本 hash 受 guard。最初 TDD RED／GREEN 各 325 checks，RED 的 43 failures 來自 stub；其後才加入完整 fixture 與額外邊界，不能把整個最終 fixture 宣稱成原始 RED 覆蓋。

本輪獨立核 36 numeric identities、6 linker contracts、152 own-anchor HI/LO，及 GP384／RAM0／RAM4 的局部 pointer 鏈。兩份既有 R56 ELF 各 20,252 executable bytes／7,050 instructions 的有限靜態解碼只找到 reset 寫 GP；外部 ROM／未重建函式保持 GP 未證。ROM 30 個數值 slot 不能視為已確認內容或可呼叫 ABI。

C91C 的 raw 52 只證明原 ROM 引數；RAM8 沒有已觀察 native 存取，只是 R51 合成負向測試。保留歷史封存並在本輪更正解讀。[完整證據](analysis/round57/README.md)、[原機與 BIN 缺口](analysis/round57/native-target-status.md)。

原生 26 物件保持 R56 的 258 實體／285 FUNC names、55 public／27 hidden／118 UND／886 reloc／441B RO；本輪沒有新增原生函式、配置 RAM、完成連結或輸出可燒錄 BIN。所有 host／static 結果均不是硬體或 OTA 驗證。

## R56 歷史功能與當時驗證

新增[排程回呼原生模組](experiments/tsl9-contract-model/src/target_ble_queue_callbacks.c)：13156/13960/13CAC/13CC8四個完整函式，105指令/258B。接回R55兩個callback位址引用、C790清零、原NULL/長度分流、ROM配置/複製/釋放支援與兩紀錄送出；8CFA共用既有280B私有本體，增加strong hidden alias。

26物件C/C++97336/97456B，55public27hidden118UND886reloc441RO；相較R55少2個UND且沒有新UND。主502body checks，alias preservation另8；這些不是整機或BIN完成比例。[完整證據](analysis/round56/README.md)、[尚缺條件](analysis/round56/native-target-status.md)。ROM角色名稱依使用方式推論，實際ABI/語義未證。未取得原機V4.1.60 dump、ROM/硬體ABI或實體OTA證據，尚無可燒錄BIN。

## R55 歷史功能與當時驗證

新增[服務事件原生模組](experiments/tsl9-contract-model/src/target_ble_service_events.c)：7函式/352指令/992B，涵蓋112BE/196B0註冊入口、原事件mask優先、10C16首個sentinel選擇、10C48/111D2狀態掃描、133FA副作用與13AF0排程/釋放順序。1950C與既有6B本體共用。

25物件C/C++95948/96068B；254實體/280名稱、53public26hidden120UND878reloc441RO。舊247實體/272名稱/25aliases與全部441RO、vector/IRQ保持；23個old raw component雜湊不變，1個僅加alias。主500body checks，alias另60；這些不是整機完成比例。

[完整證據](analysis/round55/README.md)、[尚缺條件](analysis/round55/native-target-status.md)。未實作15378/13156/13CC8下游，未取得原機V4.1.60 dump、ROM/硬體ABI或實體OTA證據；尚無可燒錄BIN。下列保留各歷史輪次的當時範圍與限制。

## R51 歷史功能與當時驗證

R51沒有新增原生函式，補上原機啟動所需的記憶體證據及離線C/C++解析工具。[原生修正](experiments/tsl9-contract-model/src/target_bridge_frame.c)、[解析器](experiments/tsl9-contract-model/src/runtime_memory_layout.c)、[報告](analysis/round51/README.md)。原82C8的C790引用與既有config_records數值同址，改為同一UND；原指令及5reloc語義保持。

Runtime／BOOT reset各40指令148B，資料複製分別136／104B，BSS清除範圍分別[20004088,2000C950)／[20004068,200099A0)。37個歷史資料引用有完整origin來源，其中34個RAM名稱、33個唯一地址都在Runtime BSS起址範圍內；三個Flash引用只記地址、不讀內容。C790兩名稱同址，現已去重。GP384在兩者BSS；RAM4/8則都不在初始化範圍。

21object C／C++75992／76112B，41pub＋15hidden／54UND／615reloc，229physical／244names；20old rawSHA保持，bridge只改引用名稱，舊229body及15alias／RO353／vector82/62保持。兩語unit1968B。原生440bodychecks；離線host各262checks另計，不能合稱BIN覆蓋率。54UND＝42layout/data＋3directcallee＋9callback refs，未把原始bounds自動綁到替代linker配置。

沒有可燒錄BIN、target執行／模擬、網路或硬體動作；原機V4.1.60、ROM／MCU／RAM／stack／IRQ、完整依賴、final link及OTA仍缺證。以下歷史文字保持封存。

# 目前已重建功能：第五十輪

R50新增原82C8紀錄篩選與8CFA BLE佇列封包，共2完整C／C++函式、165指令／470B。[來源](experiments/tsl9-contract-model/src/target_bridge_frame.c)／[報告](analysis/round50/README.md)。1條4B rd1 JAL與2組I HI23／LO24 pair逐證目標、addend及LO own-anchor；原12AC0→82C8接到真實定義。

兩語unit1972B（1public／2UND／5reloc）；21物件platform76032／76152B（41public＋15hidden／55UND／615reloc），229physical／244FUNC names。舊227physical／242names、15hidden aliases、353B RO及82/62vector保存，全部20old raw SHA不變，無新增共用alias。主440checks＝兩語unit各2＋兩語platform各218；不是整個BIN完成率。

82C8兩個stride4紀錄的條件／重疊欄位與raw s4回值保存；s4在長度檢查前寫入，非傳送成功旗標。copy後fresh長度／handle不合併。8CFA保留1039 unsigned guard、兩次fresh ROM4013C的完整a0==1、32位迴圈索引與low16比較、byte checksum、metadata順序與ROM40050 tail。新增C790資料維持UND，B18C重用既有BLE state；不猜配置或宣稱實體傳送。55UND＝43layout/data＋3directcallee＋9callback refs。

原機V4.1.60、MCU／ROM／RAM／IRQ、完整功能、final link及OTA仍缺證，沒有可燒錄BIN。以下歷史文字保持封存，不把數字相加為完成率。

# 目前已重建功能：第四十九輪

R49 新增原 1524E 功能初始化與 26 個直接 helper，共 27 完整 C／C++ 函式、241 指令／746B。[來源](experiments/tsl9-contract-model/src/target_feature_init.c)／[報告](analysis/round49/README.md)。27 條 4B JAL＝26 rd1＋1 rd0 tail，16 I PC pairs 逐證 HI23／LO24、目標、addend 與 LO own-anchor。原 925A→1524E 已接到真實定義。

兩語 unit 8852B（1 public／17 UND／59 reloc）；20 物件 platform 74928／75048B（40 public＋15 hidden／55 UND／610 reloc），227 physical／242 FUNC names。C634 完整 18B 透過一個 strong hidden alias 共用，無重複 code。舊 200 physical／214 names、14 hidden aliases、353B RO 與 82/62 vector 保存，十八個舊 raw SHA 不變，僅 TX alias 容器改 hash。

本輪主 486 checks＝兩語 unit 各27＋兩語 platform 各216，另加 TX alias RED/GREEN 四 runs 共68舊 body checks。這些是物件核對次數，不能相加為整個 BIN 的完成率。55 UND＝42 layout/data＋4 direct callee＋9 callback-address refs。十四個新 RAM 與 AEEC callback 地址不猜配置或實作；BFB0 只用已證數值關係 BFB4−4。AF18 的 SB 只寫低8位，後續 tail 仍用完整 raw a0；C516 兩次 fresh provider 及所有 JR 邊界保存。ROM 參數不證清除成功／時間單位。仍沒有可燒錄 BIN；原機 V4.1.60、MCU／ROM／RAM／IRQ、完整功能、final link 與 OTA 缺證。以下歷史文字保持封存，數字不相加為完成率。

# 目前已重建功能：第四十八輪

R48新增原12FDC啟動設定loader與六組default／writer，共13完整C／C++函式、395指令／1222B。[來源](experiments/tsl9-contract-model/src/target_settings_load.c)／[報告](analysis/round48/README.md)。18條4B JAL＝11rd1＋7rd0 tail；26I PCpairs逐證HI23／LO24、原目標、addend與LO own-anchor。原9242→12FDC接到真實定義。

兩語unit7236B（1public／8UND／70reloc）；19物件platform66936／67056B（39public＋14hidden／41UND／551reloc），200physical／214FUNCnames。9B6C完整64B透過一strong hidden alias共用，無重複code。舊187physical／200names與13hidden alias、353B RO及82/62vector保存，十七oldraw SHA不變，僅config_storage alias容器改hash。

本輪主404checks＝兩語unit各13＋兩語platform各189，另加config alias RED/GREEN四runs共40舊bodychecks，不是BIN覆蓋率。41UND＝28layout/data＋5directcallee＋8callback-address refs；新增六RAM及一opaque常數引用維持明確UND，不猜配置或匯出常數內容。保留四字元loop、magic90 LBU、short-copy後未由本體初始化的尾段、post-clear讀取與GP84 pointer，未推斷ROM實體成功。原機V4.1.60差異、MCU／ROM／RAM／IRQ、完整功能、final link與OTA仍缺證，沒有可燒錄BIN。以下歷史文字保持封存，不把數字相加為完成率。

R47新增原1290A路由設定與12780內建CAN descriptor、188F6 filter MMIO、16A38外接SPI filters、165CC ROM切換helper，共5完整C／C++函式、254指令／730B。[來源](experiments/tsl9-contract-model/src/target_can_filters.c)／[報告](analysis/round47/README.md)。9條4B JAL含7條rd1及2條rd0 tail，無PC pair。原12B3C／12B56兩條1290A呼叫接到真實定義。

兩語unit2824B（1public／3UND／9reloc）；18物件platform60524／60644B（38public＋13hidden／35UND／481reloc），187physical／200FUNCnames。三新alias共用舊SPI16652完整96B、16750完整84B、167A4完整76B。舊182physical／192names、10hidden alias、353B RO與82/62vector保存，十六oldraw SHA不變，僅TX容器因alias改hash。

本輪主362checks＝兩語unit各5＋兩語platform各176，另加TX alias RED/GREEN四runs共68舊bodychecks，不能相加為BIN覆蓋率。35UND＝21layout/data＋6directcallee＋8callback-address refs。channel gate僅低8位，但後續用raw32；165CC zero-mode不設a2；ROM clear/copy不保證成功；HAL保留完整u8 bank位址與低5位shift的差別、fresh reads及原return。原機V4.1.60差異、MCU／ROM／RAM／IRQ、final link與OTA仍缺證，沒有可燒錄BIN。以下歷史文字保持原封存，不把數字相加為完成率。

R46新增9432 Timer排程、9936 Timer init、17176 RF init與完整相依鏈，共12完整C／C++函式、325指令／932B。[來源](experiments/tsl9-contract-model/src/target_rf_timer.c)／[報告](analysis/round46/README.md)。17directedges含10條4B JAL、4條2B C.JAL、3條2B C.J；14PCpairs為6I／8S，1049A自我位址保留真HI／LO reloc，沒有忽略或放寬mask。

兩語unit5584B（3public／9UND／45reloc）；17物件platform58520／58640B（37public＋10hidden／36UND／472reloc），182physical／192FUNCnames。三新alias共用舊93CC34B／821442B／908E116B，沒有複製code。舊170physical／177names、向量與353B RO保留；十三舊raw SHA相同，三個alias容器的舊body／reloc另證不變。

本輪主366body checks另加68alias unit舊body checks，不能相加為整個BIN覆蓋率。36UND＝21layout/data＋7directcallee＋8callback-address refs：三callee閉合但新增一data與兩callback refs。Timer raw32長度與SH截16、allocator不保證zero-fill、RF rawenable與低byte store不同、ROM tail與fresh reread皆保存；未證實體time units或功能效果。ROM／MCU／RAM／IRQ／stack、原機V4.1.60差異、完整依賴、final link與OTA仍缺證，沒有可燒錄BIN。以下歷史封存文字不改，數字不相加為完成率。

R45新增CAN初始化12B9C、SPI周邊初始化16DAC及五個直接helper，共7完整C／C++本體、387指令／1084B。[來源](experiments/tsl9-contract-model/src/target_bus_init.c)／[報告](analysis/round45/README.md)。17條4B JAL及3組HI／LO pair另證，兩個舊initializer caller已defined。9A02完整30B與8518完整168B透過strong hidden alias共用，沒有複製code。

兩語unit3780B（2public／5UND／23reloc），16物件platform53980／54100B（34public＋7hidden／36UND／427reloc），170physical／177FUNCnames。舊163physical／168names與向量／353B RO保存；十三舊raw SHA相同，只有sgpio／tx因alias改容器hash。332主body checks，另有48個共用alias unit舊body checks；不能相加為整個BIN覆蓋率。

36UND＝20layout/data＋10directcallee＋6callback-address refs。aux2000C1B4與status2000C28C差216僅為位址事實，沒有配置alias或宣稱ROM clear成功；16C6C只保留opaque callback位址。CAN init不依helper回值分支，仍設定中斷位元且保留a0回值；未知clock descriptor0可使timingword成FFFFFFFF。SPI DIVU分母固定8M，低clock時保留FFFF／7FFF回繞，不改原條件。實體MCU／ROM／RAM／IRQ／stack、完整功能、final link、V4.1.60差異與OTA未證，仍無可燒錄BIN。以下歷史封存文字不改，數字不相加為完成率。

R44新增CAN gate／發送、RF狀態接收、SPI byte／register／burst／poll／capture與memset相依鏈，共17個完整原生C／C++本體、616指令／1728B。[來源](experiments/tsl9-contract-model/src/target_can_transmit.c)／[報告](analysis/round44/README.md)。關閉8202、C612、12864、1687E四個真callee，35直接邊（含2B C.J）及一組PC pair另證；8518的兩個AUIPC0是local computed-store算術，沒有錯當重定位。

兩語unit6496B（4public／3UND／37reloc），十五物件platform51104／51224B（32public＋5hidden／36UND／404reloc），163physical／168FUNCnames。新增兩個strong hidden alias分別共用舊81B0完整26B與129D8完整92B，沒有複製碼；舊146physical／149FUNCnames與向量／353B RO保存，其餘十三個舊raw SHA相同。36UND=19layout/data＋12directcallee＋5callbackrefs；2000C28C保持獨立未配置符號。

338個本輪主body checks，另有12個共享alias舊body checks；不能相加為整個BIN覆蓋率。12864保留raw8bit copy長度；189F8 DLC只&15並固定讀八個payload bytes；168F0通過初始<=8後仍fresh reread長度，沒有新增clamp。16750的unsigned wrap差值>5不是已證毫秒；時鐘停滯可使外層等待無界。MCU／ROM／RAM／IRQ／stack、實體傳輸、V4.1.60差異、完整依賴、final link與OTA仍未證，沒有可燒錄BIN。以下歷史封存文字保持原樣，數字不可相加為完成率。

R43 新增 RF queue／scheduler 十一個完整原生 C／C++ 本體：908E、1743A、17474、174CC、17650、176CC、1771C、1775E、17966、17998、179CA，共434指令／1222B。[來源](experiments/tsl9-contract-model/src/target_rf_queue.c)／[報告](analysis/round43/README.md)。關閉922E→179CA、接上17498／17514→1730E，21 PC pairs（17I／4S）及16直接邊另證；9102以strong hidden alias共用實際300B舊body。

兩語unit6364B（2public／6UND／58reloc），十四物件platform45560／45680B（28public＋3hidden／39UND／367reloc），146physical／149FUNCnames。原135physical及全部舊alias／vector／353B RO保存；只有sgpio因新alias改容器SHA，其餘十二舊raw SHA相同。39UND=18layout/data＋16directcallee＋5callbackrefs；queue／lookup仍UND，C612opaque。292本輪主body checks另有14個alias body checks；不相加為整個BIN覆蓋率。

更正R42歷史文字的17496：實際upstream起點17474、呼叫17498。17474的a4=2為copy operand，a2=15是flags；不可混成15B讀取。MCU／ROM／RAM／IRQ／stack、V4.1.60差異、完整native依賴、final link與OTA仍缺證，沒有可燒錄BIN。以下歷史封存文字保持原樣，數字不可相加為完成率。

R42 新增 RF init 173BC、task/status callbacks 1724A／172C2、producer 1730E、retry 17216 與 completion 171C2，六完整本體 213 指令／632B。[來源](experiments/tsl9-contract-model/src/target_rf_runtime.c)／[R42報告](analysis/round42/README.md)。173BC 已解析既有 8E82 的呼叫；producer 的上游 17496 尚未移植。24 PC-relative pairs 分別 15 I／9 S-format，四直接邊另證；保留 raw32 copy 長度、原截斷與 fresh ROM/state 讀取次序，沒有猜 payload 上限。

兩語 unit 4336B（2public／1UND／52reloc）；十三物件 platform 40108／40228B（26public＋2hidden／37UND／309reloc），135 physical bodies／137 FUNC names。原十二 raw object hash、129 physical bodies／131 names、向量與353B allocated readonly data保留。新 RF state 僅 UND、無新 RAM／RO配置。37UND=16layout/data＋16directcallee＋5callbackrefs；260 body checks描述本輪cohort，不是完成率。留存 SDK descriptor/slot 宣告尚未綁定實體 ROM。MCU／ROM／RAM／IRQ／stack、完整 callbacks／上游、V4.1.60差異、final link與OTA未證，仍無可燒錄BIN。

以下保留歷史盤點，不相加為整體覆蓋率。

R41 補上12388藍牙服務初始化、1986A RTC啟動與完整相依鏈（含1066B校正），共15函式627指令1930B。[來源](experiments/tsl9-contract-model/src/target_ble_services.c)／[R41報告](analysis/round41/README.md)。17freshROM service calls、25directedges、七PCpairs與原stack／MMIO次序保存；112BE／11844／196B0只保留opaque callback-address依賴。

18E96／18FC6透過兩個strong hidden internal alias共用原body，無重複碼；四missing-alias RED／四GREEN通過。兩語unit6612B（2public／8UND／39reloc），十二物件platform36604／36724B（24public＋2hidden／37UND／257reloc）。原114函式與向量保存，兩舊物件只因alias有意變hash，其餘九個舊rawobject hash保留。沒有新RAM／RO配置，原13B AD保持。37UND=15layout/data＋17directcallee＋5callbackrefs，非全部剩餘工作量；266checks只描述本輪cohort。

RTC signed DIV與無界innerwait維持原指令，不代表物理校正成功。ROM／MCU／RAM／IRQ／stack、完整callback與功能、V4.1.60差異、final link／短跳距離及OTA未證，仍無可燒錄BIN。以下保留歷史盤點，數字不相加為整體覆蓋率。

R40 接上真BLE入口8E82、9058 scheduler init、8FF8 event runner及85C0 wrapper，共4函式186指令540B；另原13B唯讀AD真const重建。[來源](experiments/tsl9-contract-model/src/target_ble_platform.c)／[R40報告](analysis/round40/README.md)。R38 register／本輪runner與init共享slots，19A94 callback-data表維持UND且不猜長度。

兩語unit3468B，1public／9UND／26reloc；十一物件platform30860／30980B，22public／33UND／218reloc；舊110函式與vector保留。33UND展開為12layout/data＋19directcallee＋2候選callbackrefs，非剩餘總工作；214body checks與4const檢查只描述本輪cohort。ROM／MCU／RAM／stack、完整BLE服務與callbacks、final link及OTA未證，仍無可燒錄BIN。

R39 補上9E2C設定初始化、14A54 RAM記錄初始化、9D76／9D9E wrapper、9B6C與五個Flash控制helper，共10函式171指令456B。[來源](experiments/tsl9-contract-model/src/target_config_storage.c)／[R39報告](analysis/round39/README.md)。只靜態編譯／ELF核對，沒有實際擦寫或執行target；935C及身分資料鏈維持未知。

兩語unit3388B，2public／2UND／11reloc；十物件platform28256／28376B，21public／26UND／192reloc，舊100函式與vector另證保留。26UND展開為10layout/data＋16directcallee，非全部剩餘工作。ROM4004C a2=8的單位與writer256B來源契約、08077B00映射、RAM0/1、ROM／IRQ／stack、final link與OTA都待證；仍無可燒錄BIN。

R38 補上9B2C GPIO狀態初始化與9B14 gated toggle，連同完整9102排程、9A02／18CDC設定、9ACE／9AB0，共7函式230指令648B。[來源](experiments/tsl9-contract-model/src/target_scheduler_gpio.c)／[R38報告](analysis/round38/README.md)。排程15槽180B顯式UND；callback address連到實際函式，原C.JAL/C.J保持2B且分辨rd，沒有補dummy。GPIO效果不直接宣稱免打擾或實體LED。

兩語unit各3056B，2公開定義／1UND／10reloc；九物件platform25740／25860B，19公開定義／26UND／181reloc，原93函式與向量另證保存。尚有9layout/data＋17實際callee；192 checks不是整體覆蓋率。ROM、原機GPIO／IRQ／RAM與final link、完整功能及OTA尚未證，仍無可燒錄BIN。

R37 完成9A20周邊clock／IRQ初始化、19490延遲校正、9E66 watchdog及四個完整RCC helper，7函式120條／344B。兩語unit各2476B、3公開定義／0UND／6符號JAL；[原生程式](experiments/tsl9-contract-model/src/target_board_init.c)／[R37報告](analysis/round37/README.md)。C API asm alias維持原caller symbol，三個名稱含unported的歷史符號現在確實defined。

八物件platform為23548／23668B，17公開定義／27UND／171reloc；原86函式與向量另證保存。三個實際缺口已關閉，仍有8layout/data及19功能callee。178 body checks不是整體覆蓋率。clock／CSR與watchdog效果僅靜態，原機MCU、ROM／RAM／IRQ ABI、完整功能、final link與OTA仍未證，尚無可燒錄BIN。

R36新增Runtime真正入口8FE6、主迴圈8180、初始化呼叫順序922E、完整clock update18588、EXTI消費者16D6E及CAN消費者12A68，共6本體226條／668B C/C++。29直接calls／tail（3個C.JAL）與共享CAN slots PC pair另證link target；非relocation bytes與原碼相同。[Runtime程式](experiments/tsl9-contract-model/src/target_runtime_entry.c)、[R36報告](analysis/round36/README.md)。

七物件ET_REL為21,980／22,100B，14公開定義、30UND、165reloc；原80函式與向量保留。30UND是展開原Runtime入口後明列的8個配置及22個真實callee，不是整個Runtime或startup已完成。原data/BSS涵蓋新CAN／Timer區域不等新版初始化、pointer／alias、原機或OTA證明；沒有可刷寫BIN。歷史數字不可加總為原BIN覆蓋率。

R35 新增真正 RV32 CAN／Timer 6 個完整 C/C++ 函式（263 條／810B）：12A34 IRQ、18ACC 完整接收擷取、129D8 32-slot producer、977C 完整 Timer IRQ、81B0 時鐘及93CC停止。19 組原 PC 相對 SRAM 位址改為合法 HI／LO linker relocation，8 個直接呼叫保留原 rd／寬度，兩個 C.JAL 維持2B。[原生週邊程式](experiments/tsl9-contract-model/src/target_peripherals.c)、[R35 報告](analysis/round35/README.md)。

觀察向量的非零目標均有實際原生函式；六物件 ET_REL 為18,616／18,736B，13 公開定義、9 配置 UND、134 reloc。9 個缺口為原7個配置與新增2個共享 SRAM 符號，不能說全部依賴已關閉。ROM／callback／IRQ ABI、原CAN輸入與Timer條件、整機功能及OTA仍未證，尚無可刷寫BIN。歷史盤點不可加總成原BIN覆蓋率。

R34 新增 3 個真正 RV32 中斷／context 入口與完整 RTC 輔助鏈 C/C++：8440 的 CSR804 bit5 OR-set、slot0→MEPC、29 暫存器恢復及 SP+128；16D22 的兩次 fresh EXTI pending／ack／GP-byte OR；19928 與 4 個原生輔助函式的 GP+392 flag、32-bit EXTI ack、16-bit RTC clear/poll。7 個本體 232B，除 4 個已證明目標的 JAL 重定位外均逐 byte 相同。[原生事件程式](experiments/tsl9-contract-model/src/target_events.c)、[R34 報告](analysis/round34/README.md)。

C／C++ 五物件 ET_REL 為 15,340／15,460B，11 個公開定義、9 個未解析符號、88 個重定位。實際 IRQ 缺口從 5 種降為 CAN／計時器 2 種；7 個配置及實體 ABI／frame producer／整機功能／OTA 仍待證。沒有可燒錄 BIN，下方歷史數字不能加總成覆蓋率。

R33 新增原生 RV32 向量資料區與 JAL 映像入口 C/C++，將觀察到的 82-word 區塊接到實際 reset／BB／LLE、52 個相同自迴圈與一個 MRET。5 種未移植的真實 IRQ 保持 undefined，未填空函式。表尾 12 個零值尚無硬體保留槽證據。[向量程式](experiments/tsl9-contract-model/src/target_vectors.c)、[R33 報告](analysis/round33/README.md)。

C／C++ 四物件 ET_REL 為 13,916／14,036B，8 個公開定義、12 個未解析符號及 84 個重定位；53 個預設本體、既有 13 個函式均有靜態核對。尚無最終 linked image 或可刷寫 BIN；原機 IRQ／ROM／配置與 OTA 待證。下方為保留的歷史盤點，不能加總成原 BIN 覆蓋率。

R32新增原生BLE BB／LLE IRQ入口C/C++，完整12B／134B與固定Runtime逐byte相同；29個保存／恢復槽、128B frame、RAM dispatch及mret有直接指令證據。[IRQ C](experiments/tsl9-contract-model/src/target_irq.c)、[R32報告](analysis/round32/README.md)。未執行任何IRQ；canonical首條LLE邊界偏差有明示fresh resync，未修改共用輸入。

單IRQ ET_REL兩語言均1256B、2exports／0UND／reloc；三物件platform4288／4408B、6defined exports／8個同前layout UND／21relocs。RAM指標有效性、physical IRQ／ROM、完整vector／memory／stack／功能與OTA仍待證，沒有可燒錄BIN。下方保留R31及先前歷史盤點，不能加總為原BIN覆蓋率。

R31新增真正RV32 reset及完整93條時鐘初始化C/C++：先gp/sp、資料搬移與清零、CSR、volatile MMIO C後端、原暫存器效果的48B裸函式shim及ROM handoff。reset+clock ET_REL仍有8個明確layout symbols未定義，沒有補dummy連成假韌體。[時鐘C](experiments/tsl9-contract-model/src/startup_clock.c)、[reset C](experiments/tsl9-contract-model/src/target_reset.c)、[本輪報告](analysis/round31/README.md)。

本輪staging時鐘+GATT整合C／C++各8組458 checks全過；目的目錄另有實測收據。無linked image或可燒錄BIN，physical ROM、IRQ／stack、整體原板啟動與OTA仍未驗證。下方保留R30與R29歷史盤點，不能把歷史數字加總成原BIN覆蓋率。

R30 新增完整 0x8B2E GATT 接收回呼 C/C++ 與 portable GATT 註冊 binding。已接入口 gates、CCCD 原參數轉交、共用 DA81B0 時鐘、逾時、分段封包、0／1040 長度邊界、校驗及中止前效果。命令分派 0x13E6A 仍需 provider；未重建或繞過其驗證。[接收程式](experiments/tsl9-contract-model/src/gatt_parser.c)、[整合程式](experiments/tsl9-contract-model/src/gatt_runtime.c)、[R30 報告](analysis/round30/README.md)。

本輪 staging C／C++ 各 32 組、2,031 checks 全過；九物件 RV32 ET_REL 為 34,000／36,856 bytes、38 exports、102 defined relocations。portable table/context、來源 alias 與部分效果有合成測試；原 ROM ABI、啟動、IRQ、最終連結、原機及藍牙 OTA 均未通過，尚無可燒錄 BIN。下方為保留的 R29 功能盤點及其歷史測試數字。

核對日期：2026-10-18。程式目錄：目前專案根目錄（由腳本位置解析）。

**目前交付是可在電腦編譯／測試的 C11／C++17 離線行為模型，尚非可燒錄韌體，也沒有任何功能經實體車輛驗證。**「已建模」表示指定程式範圍及其外部合約已重建，不能直接視為整項產品功能完成。

## 已有程式的範圍

| 功能 | 已重建內容 | 尚缺／限制 | 程式證據 |
| --- | --- | --- | --- |
| 藍牙韌體更新流程（OTA） | BOOT／Runtime 的握手、更新狀態、分頁資料處理、讀回比對、重試、metadata及完成後的重啟／跳轉請求 | 以本機資料與provider驗證，沒有實際BLE更新或刷寫；不是完整晶片啟動鏈 | [model.c](experiments/tsl9-contract-model/src/model.c)、[tsl9_contract.h](experiments/tsl9-contract-model/src/tsl9_contract.h) |
| BLE／UART通訊解析、Runtime queue與consumer（R28） | 封包邊界、長度、checksum、逾時重置；BOOT UART模型；R28新增Runtime8CFA／87C4完整原生本體及RTB分塊提交 | ROM／radio／IRQ仍需provider，未實際無線／串列埠傳送；Runtime不能直接套BOOT UART流程 | [model.c](experiments/tsl9-contract-model/src/model.c)、[boot_ram.c](experiments/tsl9-contract-model/src/boot_ram.c)、[ble_transport.c](experiments/tsl9-contract-model/src/ble_transport.c) |
| App命令、狀態回報與BLE生命週期（R29） | 28種一般BLE命令的入口／gate／分派；選定報告；R29原生state／parameter callback、App註冊表與portable role binding | 原ROM callback ABI／完整init／GATT binding未證；部分命令helper未移植，有入口不等於完整功能 | [general_ble.c](experiments/tsl9-contract-model/src/general_ble.c)、[general_deep.c](experiments/tsl9-contract-model/src/general_deep.c)、[general_reports.c](experiments/tsl9-contract-model/src/general_reports.c) |
| 免打擾、提示與mode0回報控制（R28） | 原五個核心、模式producer、查詢、15槽取消，加9432／13B5C等8入口為共用freestanding C；共32個辨識入口 | R28已加入原生13160／8CFA／87C4與直接C鏈；實體ROM／MMIO／排程／radio仍需backend；必要CAN consumer／設定事件、板級執行層未全部移植，無實體功能驗證 | [dnd_actions.c](experiments/tsl9-contract-model/src/dnd_actions.c)、[adapter](experiments/tsl9-contract-model/src/general_helpers.c)、[R26報告](analysis/round26/README.md) |
| 車門相關邏輯（部分） | 請求狀態、部分速度gate、長按／延遲的底層計時邏輯、24種門控制frame欄位處理 | 尚未完成所有按鍵／App入口到車門動作的整條鏈；沒有門馬達或開關成功證據 | [feature.c](experiments/tsl9-contract-model/src/feature.c)、[feature.h](experiments/tsl9-contract-model/src/feature.h) |
| 霧燈相關邏輯（部分） | 指定持續／閃爍狀態、one-shot優先順序、callback重新排程／取消、CAN欄位改寫 | 非完整車燈功能；部分setter回饋／通知及外部依賴未閉合 | [feature.c](experiments/tsl9-contract-model/src/feature.c) |
| 檔位請求相關邏輯（部分） | 指定請求狀態、0x229／0x678 frame改寫、counter、checksum、次數預算及部分gate | 不是完整換檔功能，沒有實際檔位變化或車端ACK驗證 | [feature.c](experiments/tsl9-contract-model/src/feature.c) |
| CAN接收／快取／選定observer | queue、debug、19個cache索引；332／3B3／679處理，以及3E9的checksum／counter清零／排程前綴 | Mode1共57個selector leaf：13個移植至既定primitive邊界、5個只有前綴、39個只有選擇器。多數已移植leaf是快取處理，不能算成13項車輛功能 | [can_receive.c](experiments/tsl9-contract-model/src/can_receive.c)、[round19-summary.json](evidence/round19-summary.json) |
| SPI／內建CAN傳送路徑（選定範圍） | 指定route、queue、filter清理、SPI／MMIO欄位與控制流 | 缺少必要硬體provider時停止；不能宣稱實體已發送或收到ACK | [spi_can.c](experiments/tsl9-contract-model/src/spi_can.c) |
| Flash操作邏輯 | 選定BOOT／Runtime頁寫入wrapper與解鎖、erase、program、busy／lock、CSR順序 | 硬體I/O仍是合約／provider；未實際寫Flash，未證明掉電或持久性行為 | [flash_page.c](experiments/tsl9-contract-model/src/flash_page.c) |
| 共用RAM、排程與部分回呼 | 共用SRAM、15槽排程、替換／取消、部分啟動與OTA回呼；候選ROM的配置／訊息／計時器及部分kernel行為 | 候選ROM不等於實體resident ROM；未移植callback仍停止，完整任務系統尚未完成 | [ram_bridge.c](experiments/tsl9-contract-model/src/ram_bridge.c)、[feature.c](experiments/tsl9-contract-model/src/feature.c)、[rom_candidate.c](experiments/tsl9-contract-model/src/rom_candidate.c)、[rom_kernel.c](experiments/tsl9-contract-model/src/rom_kernel.c) |

## 仍不能算已完成的功能

- **完整免打擾：** R28已加入A0／queue／完整事件本體與直接C鏈，五物件RV32部分連結通過；仍缺實體ROM、callback binding、必要設定事件及板級執行層，不能視為完整原機功能。
- **完整AP輔助／自動恢復、所有BB按鍵動作及其他車身功能：** 部分已有靜態分析或零散底層邏輯，尚不能當作整項功能可用；須逐項確認入口、核心、CAN輸出及依賴。
- **完整3E9處理：** checksum通過後的AD16／FA58，以及1063C排程callback尚未閉合。
- **完整可燒錄韌體與硬體適配：** rootloader、所有ROM／外設、實際MCU／BOM／PCB仍有缺口。

## 驗證到哪一層

第十九輪收據記錄在此目錄執行30次新host程式：每種語言14個parent／integration suite、108組12,476項檢查；另有CAN接收unit各25組2,674項，均0失敗。獨立reviewer各8組2,512項通過。這些數字不是原始BIN覆蓋率，也不是原韌體或硬體測試。

R29主代理執行5項host suite，C11／C++17各23組／1,633 checks通過；BL與七物件部分連結通過ELF解析。[R29](analysis/round29/README.md)區分portable C callback與原ROM未知ABI。其他歷史suite未全部重跑；目的目錄的實測範圍見[verification-local.json](verification-local.json)。

全程維持離線，不呼叫第三方API、不執行或模擬原始BIN、不連接BLE／CAN硬體、不刷寫。




## R52 主分派器與跳表

- 新原生來源：[`target_dispatch.c`](experiments/tsl9-contract-model/src/target_dispatch.c)／[`target_dispatch.h`](experiments/tsl9-contract-model/src/target_dispatch.h)。固定 Runtime `8294..829E` 與 `14AF8..1524E` 共 657 指令／1888B；兩個跳表 `1A33C..1A378` 共 60B／15 ordinal。raw、完整 canonical 與新鮮局部反組譯三方吻合。
- 模式為 BFB4−3 的 unsigned byte。mode>6 將 a0=0 後尾呼叫 105C8，不能宣稱本函式回傳 0。部分有效模式的 common RET 保留 table entry 地址；15070→1835A 保留 live a0，不自行補入其他參數。
- C544 共用既有 206B 私有本體，新增 strong hidden alias；67 個其他新接出下游未重建。三個 1051C 引用僅為 opaque 地址，角色未明。
- C11／C++17：分派器兩本體與 15 ordinal 的實際 ADD32/SUB32、JAL、HI/LO 均驗證；整合 22 物件，42 public＋16 hidden／121 UND／736 relocation／413B RO。主建置 444 body checks 與另列 alias RED/GREEN 68 個舊本體檢查；皆為靜態或交叉編譯證據。
- 原 229 實體／244 名稱全部保持；新增兩個實體函式，合計 231／247。舊 21 個 component 有 20 個 raw SHA 不變，TX 容器僅新增共體 alias；舊函式內容及 metadata 逐一核對。
- 不能由此推論免打擾、車輛效果或全部 feature 已完整可用。仍無可啟動／可 OTA BIN；[本輪報告](analysis/round52/README.md)、[待證條件](analysis/round52/native-target-status.md)。


## R53 共用控制與排程支援

- [新增 C/C++ 原生來源](experiments/tsl9-contract-model/src/target_dispatch_control.c)／[介面](experiments/tsl9-contract-model/src/target_dispatch_control.h)：8282、829E、10564、1063C、10642、10692、106B8、107B2 共 104 指令／284B。8 組 PC pairs（6 I／2 S）與 8 條 4B JAL 逐項對原始指令與實際 ELF。
- 829E 先 fresh LW4004C，再低32位 index×12；依入口 a0 選擇兩個指標的方向，長度參數為12，再 JR t1。這證明引數準備與地址流，不能證明 resident ROM 實際複製、重疊語義或成功。
- 10564 先讀 BFB0 判斷 >=4，條件允許時再次讀取後加1低8位；兩次讀取可能不同，第二次255會繞回0。回傳第一次 predicate，沒有改成更新後的計數或成功旗標。
- 10642 保留 indirect callback 的 raw return 與 unsigned threshold；106B8 保存原 raw return，非零時才呼叫8202與排程，之後回傳原值。10692 只將0改1、低32位乘1000、寫BFB4=1，再排程；不新增正數限制或溢位防護。
- 10692 的 1049A 引用改接既有20B private `tsl9_rf_cancel_1049a` 的 strong hidden alias，未複製程式。1041A 仍為 opaque 地址；未讀其內容／本體。
- 整合後 23 物件，48 public＋17 hidden／118 UND／760 relocation／413B RO；239 實體函式／256 名稱。舊231實體／247名稱、16aliases、所有舊RO／向量保持；舊22 component 有21個 raw SHA不變，RFtimer容器僅新增共體alias。
- 主4次編譯472 body checks，RF alias RED/GREEN另列48舊本體檢查。仍無 final ET_EXEC／BIN、原機啟動或 BLE OTA 實證。[R53 報告](analysis/round53/README.md)、[未完成條件](analysis/round53/native-target-status.md)。


## R54 模式切換與篩選器設定支援

- [新增 C/C++ 原生來源](experiments/tsl9-contract-model/src/target_mode_setup.c)／[介面](experiments/tsl9-contract-model/src/target_mode_setup.h)：10586、105C8、12820、128EC、1291C、16B20、16B48、19944共254指令／738B；完整收錄1291C的RET後cases，19944結束於199FA，未把後方illegal/padding當程式。
- 新表僅讀1A318..1A334恰28B，7個signed32 offsets，ordinal2/3仍各自指向129B8；原始base＋offset與native ADD32/SUB32逐槽核對。未碰鄰接opaque1A334常數。
- 105C8傳給1291C的是mode低8位，但500ms排程及raw==6的20ms路徑比較原32位值。例0x106的篩選器設定用6，但不會走raw==6的尾排程。13B5C原呼叫仍保留，未重建本體或繞過。
- 1291C的range guard在10586／12820／128EC(1)／128EC(2)四個call之後；超界模式仍保留這些前綴效果。12820每輪20B描述資料按原store順序初始化，共14輪；未為其他原stack欄位補零。
- 16B20以((raw−1)&255)<=1判斷，但向下游保留原raw channel；16B48只對raw exact1/2寫921/880，其他仍以原4B零資料呼叫。兩者沒有合併為新的通道正規化規則。
- 19944保留byte peel、word尾段、raw32末址比較及36B／9word bulk的讀寫順序。第9個LW在第一個SW之後，不能替換為一般memmove，亦未宣稱所有重疊／wrap輸入都等同標準memcpy。
- 共用8個既有body的strong hidden aliases，未複製原碼。104AE有scope選擇時的canonical-only初步查看，本輪不重建、不追加fresh body讀取；其lookup內容與199FC110B來源內容未讀。
- 整合24物件，51public＋25hidden／119UND／822reloc／441B RO；247實體／272名稱。舊239實體／256名稱／17alias、413B RO與向量保存；19個舊raw component不變，4個僅增加alias。主488body checks，alias RED/GREEN另列188舊本體檢查。
- 仍未達final ET_EXEC／BIN、原機啟動或BLE OTA實證。[R54報告](analysis/round54/README.md)、[未完成條件](analysis/round54/native-target-status.md)。
