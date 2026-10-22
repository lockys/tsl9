# 已驗證里程碑

## NV read callback 已重建，正常出口暫存字已核對

原始 30-byte NV read callback 已重建為真實 C11／C++17，各 32 bytes／14 指令、1 global FUNC、UND／RELA／ABS 為零。獨立檢查核對 fresh slot、word 數乘四、間接呼叫參數及返回零，每語言拒絕八個反例。新增 A3、fault 時序與原範圍大小仍有限制，**沒有新 BIN，尚未整合到既有候選**。

另證明 ADC 新暫存字在 callback 正常退出時被最後呼叫覆寫為同一值 `0x198EA`；不代表無限 poll 一定返回或所有 RAM／IRQ 等價。config+56／+60 已連到原 App read／write 函式；條件式 NV 數值範圍為 `0x08077C00..0x08077F00`，仍未證明原機 Flash ownership 或 OTA。[C/C++、來源與全部限制](../analysis/v4160-callback-frontiers-2026-10-22/README.md)

## ADC caller 已接上真實 C/C++ 實驗映像

由原始 caller 推導暫存器配置後，C11／C++17 產生相同的 110-byte／42 指令函式，保留 A7 與 T／S／GP／TP，新增 16-byte 私有 frame。獨立審查支持明示前提下的正常 caller 投影；私有 frame 殘值不在此投影的觀察範圍，完整原 ABI、fault 與中斷等價仍未證實。

已透過真實 assembler JAL relocation 與 linker 接入另存的 **78,848-byte 離線候選**，原 77,824-byte 映像保留。只有原 caller 的三個 bytes 改變，另附加 110-byte C 函式及 914-byte FF 頁尾資料。獨立讀回 ELF、LOAD、JAL 與整個 BIN；四個未用真實函式經 GC 移除。**候選仍為 NOT-FLASH-VALIDATED，尚不可宣稱可供原硬體 OTA 燒錄。**

另外核對兩份候選 resident 各 8 個完整函式（各 1,056 bytes／359 列）；尚未閉合 config+52、config+56 與 fresh live S0+60 的間接 callback，也未證實實體 ROM、BOOT、Flash／NV／RAM ownership。可新增的離線相容性與配置診斷目前為提案。[本輪 C/C++、實檔與來源證據](../analysis/v4160-adc-caller-2026-10-22/README.md)

## ADC 配置已重建為 C/C++，callback 相依已閉合

原始88B／37指令的配置邏輯已重建為共享C11／C++17，保留14次依序IO、完整高位元、alias與uint32回繞。實作HOST各80案例／6864檢查，獨立HOST各74案例／2904檢查；兩套各有3個實際編譯語意反例。native入口102B／38指令、無call／frame，完整物件254B／93指令、5個真實global FUNC、UND／RELA為零。**額外A2／A6／A7寫入及超出原範圍14B仍未解決，沒有新的重建韌體BIN。**

另核對8個原始函式386B／148列，閉合364-byte callback全部13個呼叫點的受限相依。SP／RA／S／GP／TP正常返回保存需要有效且不重疊的144-byte stack等前提；poll無timeout，不能保證終止。特定caller會覆寫A2／A6，原A7則保持至退出，新A7改寫仍會逃逸。正常讀取結果是raw16，不是已校準攝氏溫度。[C/C++、測試與原始來源](../analysis/v4160-adc-config-2026-10-22/README.md)

## 完整暫存器保留配方仍未符合原始 ABI

以每個原始 leaf 的可寫暫存器與三個輸入推導唯一完整 mask，C11／C++17 六份實際物件都能編譯。選定 compare60／fill68／copy64 bytes（23／24／22指令），但全部新增16-byte frame與RA／SP寫入，fill另暫時寫A2；因此此配方不能直接替換原機leaf。完整物件各保留十一個真實global FUNC，為454／492／418B，UND／RELA皆零。**沒有新BIN，舊元件及實驗映像保持不變。**

另完成原始0x188E2與唯一相依0x19160共106B／37列：對callback傳入的0x40012400，遮罩0x200先OR、再fresh read並AND ~mask；不能宣稱整字恢復原值。此有界鏈在明示前提下保存SP／RA／S／GP／TP，仍未證明整個callback或config52生命期。下一來源缺口為0x19896→0x1892E。[C/C++、獨立ABI與來源證據](../analysis/v4160-register-contract-2026-10-22/README.md)

## 原生記憶體 IO 入口已移除 context 與 frame

沿用封存的共享 C 演算法，新增真實 volatile byte／word IO 與 FENCE.I。兩個實測 profile 後，C11／C++17 三參數、單值回傳入口為 compare52／fill48／copy52 bytes，合計152B／52指令；三入口無 context／sret、call 或 SP／RA／S／A1／A2 明示寫入。整個物件仍包含八個未使用的真實 global functions230B，總382B／138指令，0UND／0RELA。**額外暫存器、scratch與fault時序仍不同，fill也超過原範圍2B；完整ABI與placement未通過，沒有新BIN。**

原App field44的197F0入口已界定364B／130指令，並核對第一段aligned填零路徑與兩個小RCC leaf；13個呼叫點及無明示timeout的輪詢仍有未解依賴，不能宣稱callback後staCB保持零值。 [原生C/C++、實物與限制](../analysis/v4160-resident-native-2026-10-22/README.md)

## 三個候選記憶體 leaf 已重建為 C/C++

新增比較固定 byte、填值與向前複製的 C11／C++17 元件，保留參數判斷前的 MMIO guard、FENCE.I 與正常退出恢復。比較採完整32-bit期望值；fill回傳前移位址，copy回傳原目的位址並保留重疊時的向前回饋。以合成 IO 測試及原生物件檢查驗證，**尚非原機 ROM provider，沒有新 BIN**。

兩候選完整初始化228B／92指令已讀取；在明示映射、有效記憶體、無不利 alias／非同步修改及正常返回條件下，staCB零值推導可延伸至設定copy與第一個後續callback入口。該callback的原App數值來源為197F0；tsCB／temperature名稱仍屬header推論，其效果與後續初始化待證。 [C/C++、證據與限制](../analysis/v4160-resident-memory-2026-10-22/README.md)

## 原回覆位置的獨立4-byte C物件與設定入口界線

兩個有根據的profile先將完整Flash base在copy前具體化，移除額外S7保存，得到552B／8saves／SP14兩byte；再宣告有align4的4-byte backing，實際C11／C++17為550B／186指令／48frame，物件SP12..15與保存槽SP16..47不overlap。只寫前兩byte；S2與E0/0的IR phi邊已逐對核對。原七個保存位置相同，額外S6、保存順序、callRA與完整ABI仍未證。**狹義指標位置相同，沒有新BIN或live替換。**

原18F56..18F88的50B／14指令helper只寫六byte；caller66B／24指令的MAC copy只寫SP40..45，未碰staCB68..71。兩份候選slot48的46B／14指令fill含MMIO save/zero/FENCE.I/restore，正常byte區間及A0進位回傳均實讀。結合全部App本體與局部範圍，可在明示有效nonnull stack／無alias／無async／正常存取條件下推得19AEC入口staCB零值，**不證明callee200004BC後或runtime永久零值**。 [程式與證據](../analysis/v4160-config-lifetime-2026-10-22/README.md)

## 配置 callback 的欄位來源與有界 C frame 實驗

兩份候選的114-byte BLE 初始化 prefix 以64-byte copy將設定+52寫到配置 callback word；加上各30-byte zero helper及8-byte initializer tail的實讀，並不構成 callback live值或永久零值證明。實際 RV32 C 包含兩份官方 header 得到staCB52／readFlash56／writeFlash60／config64；原 App308-byte本體的32選定欄位與23標準store，確認數值SNVAddr08077C00及無明示SP68 store，仍有未知calls與alias界線。

兩個 C profile 從568→560→556 bytes，最後188指令／48frame／RA+S0..S7保存，真實2-byte回覆物件SP10/11，不重疊S7@12。相對入口−38不等於原−36，故**沒有修好原回覆指標 ABI，未替換568元件或現有77,824-byte實驗 BIN**。新 HOST演算法未改、沒有RV32／硬體執行或新連結。 [本輪原碼與證據](../analysis/v4160-allocator-callback-2026-10-22/README.md)

## OTA 原 caller 接上真實 C/C++ 完整實驗映像

保留既有 691 個配置，只在副本弱化原 NOTYPE handler 全域入口，讓同 TU 的真實 FUNC568 強別名接手。C11／C++17 的完整實驗 BIN 相同，為 77,824 bytes，SHA-256 `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`。原 caller `0x14094` 的實際 JAL 指向 `0x1AC00`，RA 為 `0x14098`；繼承 76,800-byte 範圍僅該指令有三個 byte 差異。原 raw530 不變，新 C568 與非執行 FF456 形成新增一頁。

部分物件的唯一 ROM UND 沒有被偽裝為 provider。完整 ELF 使用與原始 `0x18730` JAL 一致的既有數值 `0x40000`，**只證明地址見證**。兩份候選 slot70 wrapper／core prefix 的 A2 會流向 fresh 未知 callback；新增 Flash／NV 所有權、實機 ROM、完整 ABI、BOOT 與 OTA 接受／恢復未證。沒有執行 RV32 或硬體。 [本輪程式與證據](../analysis/v4160-ota-source-wiring-2026-10-22/README.md) | [未驗證可刷寫的 BIN](../artifacts/offline-images/ID2966-V4.1.60-ota-source-wired/README.md)

下列未整合／無新 BIN 敘述保留各輪原始範圍。

## OTA 真實 provider 部分連結與配置義務

以既有實際 C11／C++17 object 與完整映像 provider object 執行 pinned `ld.lld -r`。九個元件 UND 均綁至真實配置，仍有一個原 ROM UND；692個非空配置、8,281筆RELA，所有原配置 bytes／重定位語義保留。原 raw530 與新 FUNC568並存，原 caller 未改向；**不宣稱 final JAL／硬體 ABI 通過，沒有 final ELF／BIN。**

獨立原碼追查確認 S pointer 先進 slot70 的 ambient A2，再進 fresh slot4C 的 A1；不能只靠 copy 候選關閉地址義務。原 BOOT guard 的頁0..95、Runtime實際75頁與後續21頁數值餘量亦已實讀核對，不代表free／NV所有權。單一 C switch 探針與568基線逐byte相同，未採用。 [本輪證據與工具](../analysis/v4160-ota-handler-layout-2026-10-22/README.md)

## OTA 元件：568 bytes，保留完整八暫存器橋接

依 compiler IR 的 escape 現象分離 native 回覆陣列與參數物件，再依原始三個 terminal 回覆共用位置調整 C 控制流。實際 C11／C++17 元件從 776 bytes／285 指令／112-byte frame 降為 **568 bytes／193 指令／48-byte frame**，九個真 UND、20 筆 RELA。所有八暫存器 I/O、memory clobber、HOST 效果與 W A3／A4／A5 投影保留。原始範圍為 530 bytes，還有 38-byte 差距；frame 相等不代表物理 ABI 相等。**沒有連結或新增 BIN，完整 TX 映像不變。** [本輪程式與獨立證據](../analysis/v4160-ota-handler-compact-2026-10-22/README.md)

「停用展開」探針沒有改善，仍為 776 bytes。前輪三份分析 README 把名義四次 quarter 寫成四個 static callsite，已[明示更正](../analysis/v4160-ota-handler-2026-10-22/ERRATA.md)；實際只有一個 quarter JAL 與 backedge，原有獨立物件／metadata 並無該四個呼叫點。UID／builder 及兩份 ROM 候選 copy leaf 的核對只縮小條件性介面義務，不證實已安裝 ROM 或實機 OTA。

## OTA 命令的共享 C/C++ 與實際原生差距

`0x9C4A..0x9E5C` 的 U／S／W／R／E 命令已實作為共享 HOST／native 的可讀 C11／C++17。各語言本組 HOST 通過 10 案例／8,292 檢查與三個編譯語義反例，獨立 HOST 通過 16 案例／18 次 dispatch／898 項行為檢查與四個編譯語義反例。這些是 guarded 合成測試，沒有執行 RV32 或硬體。

實際 ET_REL 每語言為 776 bytes／285 指令／112-byte frame；原始 530 bytes／48-byte frame。九個真 UND、23 筆 RELA、全部指令欄位及原生反例已獨立核對。多出的 246 bytes、callee preservation、live S／SP／RA、配置與 OTA 接受契約尚待證明。**沒有連結或新增 BIN，完整 TX 映像不變。** W 只證明寫 BOOT 數值別名；不得當成 Runtime 自刷證據。 [本輪程式與證據](../analysis/v4160-ota-handler-2026-10-22/README.md)

## callback 原生元件縮減至 624 bytes

新的 C11／C++17 元件均為 624 bytes／223 條指令：明確保留 S10／S11，將六個 GP 使用位置改為讀取當下實體 GP，並以明示步驟交換兩個既有保存指令。48-byte frame、十一組保存／還原、十五個間接呼叫已由獨立審查核對；本輪未重跑 HOST。原始剩餘 8 bytes 含有可執行指令，完整 prefix、呼叫返回 ABI、尾區所有權及原位配置尚未證實。**元件尚未整合，沒有新增 BIN；原有完整 TX 映像維持不變。** [證據與限制](../analysis/v4160-callback-registers-2026-10-22/README.md)

呼叫邊界的後續靜態核對確認：GP+42 的半字在新舊呼叫前均已覆寫，沒有這裡的 A4 漏傳；兩份官方 ROM 候選的 `+0x13C` 小函式對只按一般方式保存／返回 RA，不觀察 caller S4／S7。這縮小了部分限制，但不證明實機 ROM 身分或其餘 callee。候選 slot 對應 CCC 設定讀取與通知送出；讀取可回傳 0..255，仍須區分原始 `==1` 與 `&1` gate。 [呼叫邊界與候選條件](../analysis/v4160-callback-call-frontiers-2026-10-22/README.md)

## 先前事件 callback 的可讀重建與原生差距

`0x8614..0x888C` 的 632-byte callback 已重建為可讀 C/C++，涵蓋事件優先序、兩組 context／connection、分段長度、重試與後續事件。原生明確內聯診斷由 1,034 bytes 降到單函式 658 bytes，取得 48-byte frame／十五個間接呼叫；仍超出 26 bytes，且額外 S10 保存、儲存順序、返回地址及未知 ROM 契約未閉合。**此 callback 尚未納入完整 BIN，沒有新增可刷寫映像。** [分析與限制](../analysis/v4160-event-callback-2026-10-22/README.md)

## TX 已納入完整實驗 BIN

正式 C11／C++17 各新編譯 46 個單元，產出相同的 76,800-byte 實驗 BIN；十三個原始函式範圍共 930 bytes，由十五個真實 FUNC 角色承接，678 個其餘區段仍使用原始承載。與官方 ID2966 的 93 個差異全部位於 TX，其餘 byte 相同。SHA-256：`28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。**新 BIN 尚未驗證可刷寫。** [完整整合](../analysis/v4160-tx-image-integration-2026-10-22/README.md) | [實驗映像](../artifacts/offline-images/ID2966-V4.1.60-tx-integrated/README.md)

以下「尚未整合／沒有新 BIN」描述只適用於其歷史範圍。完整 ABI、實機 ROM／BOOT／Flash、CRC／簽章與硬體 OTA 仍待證。

## OTA 傳送入口與分段還原的實際原生修復

新的 C11／C++17 元件均實際連結為 280 bytes：8-byte 窄組語入口、270-byte 可讀主體及 2-byte 真實返回葉函式。標準 ELF 分支重定位讓超長輸入直接返回、不碰堆疊；兩次 ROM 呼叫的返回位址為原始的 0x8A90／0x8AB6。公開入口的 FUNC 大小如實為 8 bytes，沒有偽造單一 280-byte C 函式。

新排序步驟只移動本次編譯出的五個儲存與五個還原指令，恢復原始儲存順序及 descriptor 寫入前後的 fresh-read 界線。C/C++ 的實際 pre/post 物件與已連結元件均通過獨立檢查，其他 ELF 位元組及 metadata 相同；沒有新 opcode 或原始韌體位元組產碼。實際缺少 RAM provider 的連結及分支超距連結也都遭 linker 拒絕。

這是可重跑的原生元件進展，尚未整合到完整映像，完整 ABI、原硬體／ROM／BOOT 及 BLE OTA 仍未全部證明；沒有新的 BIN。完整映像仍為下方的 12 個可讀函式／650 bytes。詳見[本輪分析](../analysis/v4160-tx-register-abi-2026-10-22/README.md)。

## OTA 封包組裝的原碼核對與原生差異

實際 C11、C++17 主機測試各通過 107 案例／15,605 檢查與八個編譯後的語義反例；獨立測試各通過 31 案例／78,283 檢查與十四個編譯後的語義反例。這些是合成供應者、數值記憶體及明示 ROM 邊界的行為測試，不是執行或模擬 RV32。主機執行檔均經既有不可變的 machine guard 核對。

新增 `0x8A56..0x8B6E` 的可讀 C/C++：原始 280 bytes／96 條指令、40 項運算元反例、9 個外部直接入口及 11 個 owner RELA 均已逐項核對。入口負載上限為 1039 bytes，兩個緩衝區相距 1062 bytes；原始程式使用 16 位元 descriptor 寫入及單一位元組 task 讀取，不能替換成較寬的記憶體操作。

編譯探針符合 280-byte 原區段大小，但獨立審查仍拒絕原機 ABI 適用性：堆疊先於原始 guard 建立、還原操作延後，部分運算元與控制流亦不同，無法只靠排列既有指令關閉差異。這是可讀邏輯重建與有界原生差異證據，**沒有新增完整映像或可燒錄 BIN**。完整映像仍是下節十二函式／650 bytes 版本。

已記錄離線封包預檢與更新等待原因兩項提案，尚未實作為硬體功能。ROM slot 只按原碼的數值與 live register 表達；候選 SDK 名稱不構成安裝版本或 ABI 證明。詳見[本輪分析](../analysis/v4160-ota-tx-2026-10-22/README.md)與[後續路徑](../analysis/v4160-ota-tx-2026-10-22/continuation-plan/README.md)。

## 十二個可讀函式納入完整映像，全部編譯標頭閉合

OTA 頁面回覆已納入完整映像，現在有十二個可讀函式／650 bytes。C11、C++17 各自新編譯 34 個原始承載及 9 個可讀單元，61 個實際命令包括 59 個 LLVM 操作及兩次明確 ABI 排序。兩語言各保存 223 個實際產物雜湊與 41 項整合反例檢查；完整輸出均為 76,800 bytes，與官方 ID2966 V4.1.60 完全相同，SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

43 個單元全部使用 `-MD`，實測 74 份專案輸入、14 份生成輸入與一份 Clang `stdint.h` 資源標頭；其中十四個單元使用該資源標頭。舊 `-MMD` 省略系統標頭，不代表編譯器沒有讀取。來源審查另外檢查完整生成順序、原始／排序物件身分及十三個紀錄反例；它們不是十三次目標執行。

完整檢查保留 691 個配置、679 個原始承載、8,257 筆外部及十二筆 JAL 重定位、53 個相對綁定、21 個入口及十五個 LOAD 的檔案／記憶體範圍和權限。頁面回覆原本 NOTYPE／size 0 公開入口與區域入口仍在，來向 `9DF4` 是 `C.JAL`、連結地址 `9DF6`。編譯器額外地址簽章資料亦依實際來源及精確內容檢查，沒有任意排除中繼資料。

這仍是部分來源重建，其餘內容使用原始承載。**未驗證可燒錄。** ROM 只提供數值地址見證，原硬體、已安裝 ROM／BOOT、BLE OTA 及復原仍待證。未執行或模擬 RV32，未操作硬體；未重跑沒有變更的既有主機行為套件。詳見[完整整合](../analysis/v4160-reply-image-integration-2026-10-22/README.md)與[離線映像](../artifacts/offline-images/ID2966-V4.1.60-reply-integrated/README.md)。

## OTA 頁面回覆的原生 C/C++ 與入口整合邊界

新增 `0x9B8E..0x9C0A` 可讀 C/C++：124 bytes／50 指令。兩語言各自新編譯、明確重排兩段既有編譯指令、固定地址連結並讀回，全部 bytes 與原始函式一致。排序僅改動兩段內的 28 bytes，並保留其他 ELF bytes；不能宣稱編譯器單獨產生最終順序。未提供 TX 實作時嚴格連結失敗，成功者只提供 `0x8A56` 數值地址見證。

每語言主機模型通過 87 案例／3,634 次檢查及六個實際編譯語意反例；獨立來源效果測試另通過 90 案例／6,699 次檢查及十個實際編譯反例。原生證據另含十一項 raw／IR 控制、三個實際編譯反例及三項已連結 ELF 控制。排序獨立檢查每語言拒絕十八個實際 ELF、五種路徑風險及三個收據竄改案例。主機合成測試不證明原生未知服務的暫存器保存契約。

局部兩物件連結保留原始 NOTYPE／size 0 公開入口及 LOCAL／size 0 區域入口，沒有數值 ABS 入口別名或填補；新增 C 函式維持真實 FUNC／size 124。原入口、其他承載區段及外部重定位均已檢查。**完整映像仍是先前十一個可讀函式／526 bytes 的版本；第十二函式尚未整合。** 原硬體、實際 ROM／BOOT 與 BLE OTA 仍未驗證，不可宣稱可燒錄。詳見[元件](../experiments/tsl9-v4160-ota-page-reply/README.md)、[排序](../experiments/tsl9-v4160-reply-abi-order/README.md)及[整合邊界與新功能候選](../analysis/v4160-ota-page-reply-2026-10-22/integration-plan/README.md)。

## 十一個可讀函式的完整映像恢復原始 bytes

五個 Flash 葉函式共 198 bytes／76 指令已恢復原始暫存器、進入前綴、指令邊界與機器碼；IRQ 及 quarter 的自動保存順序另以明確的 ABI 處理恢復。它只重排新編譯物件既有的 C.SWSP 指令，不生成 opcode、不增加長度、不以原始 BIN 回填。保存編譯器處理前後的物件與收據，不能宣稱 Clang 單獨產生最後次序。

C11／C++17 完整鏈各新編譯 42 個單元，包含 34 個原始承載、兩個 IRQ／RCC、六個 Flash 單元；57 個實際命令包括一次明確的 Python ABI 處理。兩語言各匯出 76,800-byte 映像，SHA-256 與官方 ID2966 V4.1.60 完全相同：`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。11 個可讀函式共 526 bytes，其餘映像仍為原始承載資料，**不是完整來源重建**。

核對 691 個配置、680 段保留儲存、8,259 筆範圍外與 11 筆自身 JAL RELA、53 個真實相對綁定、二十個外部入口及十個已明確消去的內部分支。實際區段／15 個 LOAD 支持全部匯出 bytes，沒有補洞、NOBITS 或 ROM 匯出。原機 ROM 缺少實作時嚴格連結仍失敗；成功連結只使用數值位址 witness。

獨立來源與 ABI 審查會讀取實際編譯來源鏈、處理前後物件、ELF 與 BIN。另有 21 個畸形物件及三種路徑別名防護案例；父層唯讀重驗每語言拒絕七個實際收據／輸出篡改案例。封存 metadata 核對、本機實際成品重驗、全新編譯及實體證據分開報告。GitHub 不包含生成的 build 物件；本機 `re-tsl9` 保留完整獨立保存順序封存。

**仍未驗證可刷寫。** 完整目標未完成：確切晶片／板子、原機 ROM、已安裝 BOOT、實體中斷／Flash 行為、BLE OTA 接受性及失敗復原仍缺證據。下一步優先處理 BLE 分頁接收／回覆與版本對應，保持 Runtime 寫 BOOT 與 BOOT 寫 Runtime 的方向分開。新增功能仍限於既有[本機預檢與狀態說明候選](../analysis/v4160-irq-callframe-2026-10-21/feature-candidates/readme.zh-TW.md)，不宣稱已加入硬體。詳見[新版整合](../analysis/v4160-register-image-integration-2026-10-22/README.md)及[保存順序工具](../experiments/tsl9-v4160-frame-schedule/README.md)。Windows Python／LLVM 證據不代表 shell、Linux、macOS 或 CI 已執行。

## 十一個 IRQ／Flash 可讀函式的完整離線映像

已實際以 C11／C++17 編譯 34 個原始載體、兩個 IRQ／RCC 單元及六個 Flash 單元，並匯出相同的 76,800-byte 映像，SHA-256 為 `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`。與官方映像共有 70 個 byte 不同：八個為前輪 IRQ 差異、62 個為新 Flash 差異。十一個可讀函式共 526 bytes；其餘仍是原始載體，屬部分來源重建。

核對全部 691 個配置、680 段保留儲存、53 個真實 section-relative 綁定與二十筆外部入口。實際 RELA 為 8,270 筆：8,259 筆範圍外記錄保留完整角色及次數，另有十一筆可讀函式 JAL。十筆原始內部分支由實際 bytes、條件、PC 及目標明確解除；壓縮呼叫及 tail jump 分別保留其返回位址行為。未連結儲存與重定位後的映像資料分層比較。

全部匯出 bytes 都有實際區段／LOAD 支持，無補洞、原始 BIN 回填、RAM NOBITS 或 ROM bytes。嚴格連結仍拒絕缺失 ROM provider，成功連結只有數字位址見證。獨立來源／配置及 ABI 審查讀取實際連結產物。補充 literal 搜尋在三個完整映像均無命中，但不能排除計算而來或 ROM 引用。完整 fault prefix、原始 program `+8` 邊界、逐指令／非同步 IRQ 狀態、板子／晶片、實際 BOOT 與 BLE OTA 仍未證明。**此 BIN 尚未驗證可刷寫。** 詳見 [繁體中文說明](../analysis/v4160-flash-image-integration-2026-10-22/README.md)。Windows LLVM 證據不代表 shell、Linux、macOS 或 CI 執行結果。

## 原始尺寸的 Flash program 與入口事件順序

新版 C11／C++17 program 函式自然產生 100 bytes／38 指令。補回兩次 fresh 基底暫存器載入，並明確約束 A0／A5 primitive 後，整個區段由新來源持有，沒有 NOP、padding 或借用原始 bytes。六個 Flash 函式合計 262 bytes／99 指令，兩種語言產生相同元件 ELF。入口控制讀取位於 +4，接著在 +6 對齊 A0、+14 首次寫入控制暫存器；五個 program 迴圈目標仍位於原址，最後六個 bytes 是實際清理及返回指令。

主機每語言通過 481 案例／247,191 斷言，並拒絕六個實際編譯變異；新的獨立 expected-effect 測試每語言通過 12 情境／8,964 斷言及十二個編譯變異拒絕，所有主機執行檔均在啟動前後核對架構。獨立靜態審查另外核對實際元件 bytes、IR 及已知分支角色。另以不同韌體參考路徑實際編譯及重播，並確認錯誤參考 context 會被拒絕。

這補上前輪六個 bytes 的來源缺口，但並未保留所有指令邊界：原始 program 的 +8 位於新版四-byte 對齊指令內。scratch 暫存器、fault／非返回 prefix、非同步、ROM、板子及 OTA 相容性仍未證明。此元件里程碑沒有產生完整新映像或 BIN。已封存的下一階段整合規劃涵蓋 691 個配置、十一個可讀函式、680 段保留儲存、8,259 筆範圍外 RELA 及二十筆外部入口引用；預計的 42 個編譯單元尚非完整映像建置成果。詳見 [繁體中文說明](../analysis/v4160-flash-entry-order-2026-10-22/README.md)。主機入口為 `python experiments/tsl9-v4160-flash-entry-order/verify.py --language both`，原生靜態檢查入口為 `python analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --tool-dir <LLVM-bin> --language both`。Windows 證據不代表 shell、Linux、macOS 或 CI 已執行。

## 六個可讀 V4.1.60 Flash 函式

共用 C11／C++17 來源重建 quarter wrapper、status、unlock、lock、erase 與 64-word program。原始證據為 262 bytes／99 指令；六個原址原生元件分別為 64／8／30／14／46／94 bytes，status 與 lock 共 22 bytes 完全一致。正常返回契約保留 32-byte frame、fresh `SP+12` source reload、五個有序呼叫、CSR mask 136 與暫存器殘值。program 剩下的六個 bytes 尚無新的儲存來源；此輪沒有產生完整新映像或 BIN。

主機每語言通過 481 案例／247,191 斷言，並拒絕六個實際編譯變異；獨立 expected-effect 測試每語言另有 12 情境／8,964 斷言與 12 個已編譯變異拒絕。原生靜態檢查讀取實際機器碼及 IR，每語言另拒絕 15 個機器碼與三個 IR 反例。原始六函式、六個高位址 caller slice 與整個物件的已記錄重定位 frontier 分開保存證據。

frontier 在前輪物件的 8,276 筆 RELA 中找出 12 筆外部入口及 11 筆 owned 呼叫／分支，後續整合仍須保留其餘 8,265 筆完整角色。已記錄 RELA 沒有外部 interior target，不等於 ROM、間接數值引用或未知執行期沒有其他入口。frame 保存順序、fault／非返回 GPR prefix、逐指令／非同步狀態、板子／ROM／Flash 與 BLE OTA 仍未證明。詳見 [繁體中文說明](../analysis/v4160-flash-native-2026-10-22/README.md)。預設主機入口為 `python experiments/tsl9-v4160-flash-native/verify.py --language both`；原生入口為 `python analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir <LLVM-bin> --language both`。Windows 證據不代表 POSIX／Linux／macOS／CI 已執行成功。

## IRQ 可讀來源的完整離線映像

已實際重新編譯 34 個原始指令／資料載體與兩個可讀單元，並在 C11／C++17 分別連結、匯出相同的 76,800-byte 映像。新映像 SHA-256 為 `47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`，只在 `0x9A44..0x9A4B` 有八個明確 byte 差異，對應四個 prologue 保存指令的順序。原始 APK、廠商 BIN 與先前來源一致映像未替換。

核對 691 個原始配置、686 段保留儲存、53 個真實區段內符號綁定及八筆外部進入呼叫；8,270 筆範圍外 RELA 保持完整角色與次數。新總數為 8,276，其中六筆為新核心 JAL，四筆原 helper 分支 RELA 由一致 bytes 明確解除。所有匯出 bytes 均由實際區段及 LOAD 支持；無補洞、原始 BIN 回填、RAM NOBITS 或 ROM bytes 匯出。

每語言有 36 個實際編譯單元的依賴閉包、44 個受檢指令及 15 個實際 ELF／重定位／映像負例。完整嚴格連結明確拒絕唯一缺失的 ROM provider；成功產物僅使用 `0x40000` 的數字位址見證。可讀 C/C++ 只取代五個 IRQ／RCC 函式，其餘仍是原始指令／資料載體，不能宣稱完整來源重建。

映像位於 [NOT-FLASH-VALIDATED-irq-callframe.bin](../artifacts/offline-images/ID2966-V4.1.60-readable-IRQ-integration/NOT-FLASH-VALIDATED-irq-callframe.bin)，入口與分開的獨立審查見 [繁體中文說明](../analysis/v4160-irq-image-integration-2026-10-21/readme.zh-TW.md)。原機 ROM、非同步中斷狀態、硬體、實體 Flash 與 BLE OTA 仍未通過；此 BIN **尚未驗證可刷寫**。Windows Python／LLVM 建置不代表 shell、Linux／macOS 或 CI 結果。

## 144-byte IRQ 呼叫框架與 C++ 配置

新版可讀 C/C++ main 改用六個四-byte JAL 呼叫既有 RCC helper，由編譯器建立 16-byte frame。C11／C++17 的實際 main 均為 144 bytes，四個 helper 各 30 bytes，264 bytes／94 指令全部位於原始區段，且無額外配置。C++ 的 `-fno-exceptions` 移除先前 unwind metadata；獨立 predecessor 實驗也確認此單一 flag 不改動其五個函式 bytes。

main 的第一條 SP 調整與 offset 10 以後的 134 bytes 原樣一致，四個 helper 的 120 bytes 完全一致。差異是四個兩-byte prologue store 的排列；frame slot 集合、六個 JAL 的 PC／目標／RA、所有指令邊界及還原載入分別核對。**逐指令 stack 狀態與非同步 IRQ 等價仍未通過。**

主機每語言通過 9184 案例／246384 斷言；獨立測試每語言 3820 案例／138312 斷言，共拒絕 60 個實際編譯變異。原生每語言拒絕六個已編譯／連結反例與 30 個覆蓋反例。完整 source-carrier 的下一階段整合規劃已找出 34 個 C TU、691 個配置、53 個 section-relative alias；四個 helper 的原始 branch RELA 由 byte 一致性解除，不能虛稱新物件仍有 8280 筆 RELA。

此輪尚未整合或生成新 BIN，原 76,800-byte 離線映像與 gate 保持不變；ROM、板子、硬體中斷及 OTA 相容性仍未證明。來源入口為 `sh experiments/tsl9-v4160-irq-callframe/verify.sh --language both`；原生入口為同目錄 `verify-native.sh --tool-dir <LLVM-bin> --language both`。Windows Python／MSVC／LLVM 證據不代表 Linux／macOS 或 shell 已執行成功，既有 CI 帳戶限制未重試或調整。

## 分支式 IRQ 核心與 RCC 原址 bytes

新版 C/C++ 核心讓兩條 RMW 分支各自保留讀取、運算、寫入與返回值，使用逐次基底／立即數與明確的 A0 返回橋接，並停用 machine outliner。四個 RCC helper 各 30 bytes，在原址 0x19124／0x19142／0x19160／0x1917E 連結後與原 BIN 的 120 bytes 完全一致；完整機器碼核對確認只寫 A0/A4/A5，A1 精確保留。IRQ 本體只寫 A0/A1/A4/A5，正常返回輸出符合原始契約；20 個有序效果及六次 fresh RCC 讀取分別由機器碼與 LLVM IR 檢查。

主機 C11／C++17 每語言通過 4 組／9184 案例／246384 斷言，沿用完整 264 bytes／94 指令來源證據。獨立主機測試每語言 3820 案例／138312 斷言，合計拒絕 44 個實際編譯變異。原生每語言另拒絕五個實際編譯變異與 30 個反組譯覆蓋反例。

本體 180 bytes 超過原始 144 bytes，尚未接受任何新位置。C++ 額外配置 `.eh_frame`：object 120 bytes、linked 124 bytes；已配置區段完全由函式持有的 gate 明確為 false，不能以「唯讀」免除整合義務。函式正常返回證據不等於中途狀態／非同步 IRQ 等價。完整映像、ROM、硬體與 OTA 相容性仍未通過，未執行 RV32、未改原始映像、未產生新 BIN。

入口為 `sh experiments/tsl9-v4160-irq-native/verify.sh --language both`，原生入口為同目錄的 `verify-native.sh --tool-dir <LLVM-bin> --language both`。新文件在 `analysis/v4160-irq-native-2026-10-21/`。Windows Python／MSVC／LLVM 證據與未驗證的 POSIX shell、Linux／macOS／CI 結果分開報告。

## 原址審查與中斷暫存器模型

確切配置池為八個分開的原始範圍，共 540 bytes：reset 記憶體 62、時脈查詢 174、衍生欄位 40、IRQ 初始化 **144**，四個 RCC helper **各 30**。綁定 bytes 的審查核對完整固定 linker layout 的 691 個 section 配置與 8,280 筆 RELA。helper 均有其他呼叫端；已納入的程式碼未見外部直接跳進內部，但 939 條間接指令使計算式目標仍未排除，總和算術不能證明可安全連續配置。

實際舊版原生 IRQ 本體否定了看似可用的空間：118-byte 初始化與 22-byte helper 都會寫入原始程式保留的 A2／A3，A1／A4／A5 返回值也不同。既有呼叫鏈上的 A3 會傳到未知 callback，這些舊本體尚不能依原始契約提供替換空間。

新的 `interrupt-registers` C/C++ 模型保留 20 個 MMIO／CSR 效果、helper 完整 A1 bits、分支特定 A4／A5，以及初始化最終 A1=0／A4=128／A5=`0xE000E000`。含完整來源證據的主機測試每語言通過四組／9,184 案例／246,384 項，屬主機正常邊界結果。預定原生配置目前五個函式均出現 `Stack pointer required, but has been reserved.`，未產生 object／ELF，**尚無通過的原生暫存器或原址證據**；三個有限診斷組合也失敗。IR 檢查與預期失敗重現，分開記錄，不當成成功編譯；分支內值生命週期的重整仍待實作。

另有確定的原生大小進展：未改動的 reset C/C++ 改用 `-Oz`，leaf／fragment 從 78／80 降為 66／68 bytes，原始為 62；實體 GP operand 從四處降為三處。時脈查詢／衍生欄位仍為 196／38。合成跳轉證據核對同 section 兩-byte C.J 與外部四-byte JAL x0 的幾何，沒有提供原始入口 adapter 或配置空間。未修改原始映像，也未產生 BIN。

使用 `sh experiments/tsl9-v4160-interrupt-registers/verify.sh --language both`。來源、ABI 反證、獨立測試、成功的有限探針與失敗的新原生配置均位於 `analysis/v4160-placement-2026-10-21/`，英文／繁中指南分開。目的地／checkout 驗證產生新的本機結果，不交付歷史編譯封存。Linux／macOS、原始中斷途中狀態、ROM、板子、Flash 與重建映像 OTA 仍未驗證。

## 啟動記憶體初始化

`0x186BA..0x186F8` 現在有可讀的 C/C++ 實作：分開觀察 GP、交錯向前 word 複製、無號邊界、BSS word 清零，以及正常邊界的 A0／A1／A2。確切 ID2966 來源證據涵蓋 62 bytes／17 條指令，拒絕 17 個 raw 突變；128-byte 初始化資料只當資料讀取。主機測試每語言通過五組／338 案例／133,601 項；獨立審查每語言另通過五組／538 案例／193,964 項，合計拒絕 22 個實際編譯反例。

原始區段直接接到 CSR 設定，沒有函式返回。正常 A0／A1 經原始時脈初始化後仍傳到未知 ROM 入口，不能任由一般 C helper 捨棄。另有 372 bytes／130 條指令的 reset／clock 呼叫端證據記錄此邊界；原機 ROM 身分與中斷相容性仍未證明。

原生 leaf 編譯為 78 bytes／24 條指令，超過原始 62-byte 區段，且新增了 C 編譯器產生的返回。可選的延續 fragment 為 80 bytes；來源雖寫 `c.j`，實際組譯成四 byte JAL，兩者均放不進原始範圍。在不重疊的診斷位址綁定數值延續，只能證明 relocation，並未提供原始入口 adapter。完整指令 bytes、暫存器、記憶體寬度與迴圈 CFG 檢查，也不等於原生全路徑或非同步狀態等價。未替換原始映像，也未產生 BIN。

使用 `sh experiments/tsl9-v4160-reset-memory/verify.sh --language both`。來源、呼叫端、獨立 C/C++ 及編譯器審查位於 `analysis/v4160-reset-memory-2026-10-21/`。交付選定的審查程式、文字與收據 metadata；歷史編譯封存留在工作區，目的地驗證會建立新的本機產物。Windows 結果不代表 Linux／macOS 或 POSIX shell 啟動已通過。

## 時脈正常返回暫存器契約

使用者於 2026-10-21 回報 `tsl9-morphe` 可選取官方 BIN 並成功更新韌體。這是使用者提供的官方映像 OTA 基準，確切 APK／BIN 身分與版本尚未指定；與下述重建映像的啟動、接受與恢復要求分開記錄。

時脈重建新增原始分支特定的 A3、條件式 A2 寫入、查詢 A4／A5 及衍生欄位完整 A5 乘積。新增呼叫端證據覆蓋 298 bytes／98 條指令，另檢視 130 條傳遞指令，顯示 A3 經 fresh `0x4004C` 指標傳入 `0x131E0` 的未知 callback。`1973C` 後的確切呼叫是 `9F4C`，再到 `131C2`。尚不能證明 callback 使用 A3，但也不能任意捨棄。

新 C11／C++17 主機測試每語言通過六組／293,845 項；獨立測試每語言通過四組／5,345 案例／250,316 項，合計拒絕十六個實際編譯的返回值／A2 反例。沿用未修改的 214 bytes／69 條指令及五十個 raw 負例，並另核對原始整數目的暫存器欄位。

原生編譯採用暫存器保留旗標及明確的實體暫存器限制。查詢只寫 A2–A5，A2 不供一般配置使用；本體為 196 bytes，原始為 174 bytes，仍有 22-byte 配置缺口。衍生欄位為 38 bytes，原始為 40 bytes；完整十指令模式確認 unsigned 除法、byte／halfword 寫入及正常返回 A4=1000／A5=完整乘積。這些元件證據不代表非同步中途狀態、中斷、完整映像、ROM 或實體硬體相容。未替換原始本體，也未產生 BIN。

主機驗證使用 `sh experiments/tsl9-v4160-clock-registers/verify.sh --language both`，原生 CLI 與限制記錄於 `analysis/v4160-clock-abi-2026-10-21/compiler-review/`。在先前觀察到的 CI 帳戶限制解除前，Linux／macOS 及 POSIX shell 執行仍未驗證。新文件維持分語言。

## 可讀的原生時脈與衍生欄位

兩個時脈函式新增獨立的可讀 C/C++ 實作，直接使用 volatile MMIO／RAM 與當下 GP，不依賴舊暫存器直譯模型。沿用未修改的 214 bytes／69 條指令及 50 個 raw 負例來源證據。主機測試每語言通過六組／269,618 項；獨立測試每語言通過四組／5,345 案例／214,811 項，合計拒絕十個實際編譯反例。

Freestanding C11／C++17 RV32 編譯結果各為 170-byte 查詢與 44-byte 衍生欄位函式。後者超過原始 40-byte 範圍，不能直接替換原址。獨立連結元件沒有未定義符號、執行期 helper 或可寫資料。完整核對 ELF bytes 的反組譯覆蓋範圍，檢查四／三處 GP 讀取、記憶體寬度與直接分支邊界；LLVM IR 另核對動態 GP 位移與 unsigned 運算。兩語言合計拒絕十個實際編譯的原生突變及 24 個反組譯文字反例。這是結構證據，未證明原生所有路徑語意或原始暫存器／堆疊／中斷 ABI。

來源／主機驗證使用 `sh experiments/tsl9-v4160-native-clock/verify.sh --language both`。獨立 LLVM CLI 記錄於 `analysis/v4160-native-clock-2026-10-21/native-review/readme.zh-TW.md`。未執行或模擬 RV32、未修改原始映像，也未產生新 BIN。新增指南與審查文件分英文與繁中，每個 `README.md` 只連結語言版本。

## 可讀的原生中斷初始化

新增元件以可讀 C/C++ 重建 `0x9A42` 及四個 RCC 輔助函式；原生版本直接使用 volatile MMIO 與 CSR 指令。原始五個函式共 264 bytes／94 條指令，來源核對拒絕 94 個原始指令突變。主機測試每語言通過 4 組／6,680 項；獨立測試每語言通過 4 組／34,267 項，六個實際編譯反例均遭拒絕。

C11 與 C++17 也能編譯及連結成獨立 RV32 元件：四個 helper 各 22 bytes，初始化本體 118 bytes。LLVM IR 與實際機器碼檢查均核對 20 個有序效果，包含六次重新讀取 RCC、確切 word／byte 寬度、CSR 清除／設定遮罩及最後的 RMW 回傳值。八個實際編譯的原生突變均遭拒絕。這些是獨立元件檢查，尚未替換完整韌體，也未證明原始堆疊／暫存器 ABI；沒有 RV32 執行或實體 I/O。既有 691-section／8,280-relocation 映像及唯一缺少實作的 resident 入口保持不變。

本元件來源／主機檢查使用 `sh experiments/tsl9-v4160-interrupt-init/verify.sh --language both`。原生檢查需要 LLVM，明確 CLI 記錄於 `analysis/v4160-interrupt-init-2026-10-21/native-plan/`。上一輪跨平台 CI 因 GitHub 帳戶付款／支出限制，在任何步驟前就停止；沒有重跑，也沒有變更付費設定。

## 跨平台入口與時脈計算

新的 Python 驗證入口涵蓋 runtime-loop、system-clock-query、resident-entry 與 resident-copy 四個模型。每項先核對封存來源證據，再編譯及執行自行重建的 C11／C++17 主機測試。Windows 原生編譯器測試已通過；Linux、macOS 及 shell 啟動須另以 CI 證據確認。此入口不依賴 PowerShell 或 CMake。

新增時脈模型涵蓋 ID2966 V4.1.60 的 `0x18834..0x188E2` 與 `0x1973C..0x19764`，共 214 bytes／69 條指令，來源核對拒絕 50 個 raw operand 突變。每語言通過 7 組／1,414 項。保留分開讀取 RCC、當下暫存器與位址、即時 prescaler 表、無號運算及依寬度寫入。初始化整合只綁定兩個已有證據的呼叫點，中間呼叫仍為未知實作。

## 先前重建模型

| 模型 | 來源證據 | 每語言主機測試 |
| --- | --- | --- |
| Runtime 主程式、初始化、迴圈與派送 | 220 bytes／80 指令；拒絕 45 個 raw 突變 | 6 組／1,431 項 |
| resident 候選入口、初始化與 RAM seed | 230 bytes／66 指令及 4-byte header；拒絕 35 個 raw 突變 | 5 組／121,496 項 |
| 候選 byte-copy | 58 bytes／18 指令；拒絕 23 個 raw 突變 | 5 組／772 項 |

以上是選定範圍的來源與合成主機行為證據。原始韌體只作資料讀取，不執行或模擬。resident 候選在 `0x6EB2C` 缺少原始 bytes，合成延續無法證明缺少的實作。

## 移植進度與證據限制

移植盤點記錄 116 支歷史 PowerShell 腳本與 93 個根目錄 suite。四個跨平台模型不能取代原本 RV32／ELF、整合或下載檢查。新下載器原型僅支援 dry-run 與離線 HTTP 邊界替身；23 個案例不代表已從廠商下載成功。

來源證據位於 `analysis/*/source/`。完整本機獨立審查與整合收據可能綁定未發佈的主機執行檔及日誌。`publication-manifest.json` 核對實際發佈的檔案。歷史封存文件保留原始 bytes；新的使用說明分為英文與繁體中文文件。

WCH CH32V20x 目前是硬體假說，並未確認為 TSL9 料號。原機 ROM、板子、啟動／中斷 ABI、實體 Flash 與 BLE OTA 接受性仍未證實。原有 76,800-byte 來源一致離線映像維持 **NOT-FLASH-VALIDATED**。
