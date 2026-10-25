# 目前選用的逆向 C/C++ 原始碼

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

[最新原始位址驗證](../analysis/notification-support-2026-10-25/README.md)：49,074B 已重建 code／data 經原生連結器配置後逐 byte 與官方 BIN 相同；仍缺 131 個提供者。產物是無 PT_LOAD 的診斷 ELF，未通過實機／OTA。

這裡集中目前證據較完整的可讀原始碼，作為後續重建的工作入口。共 137 個 C/H 檔；同一份 C 原始碼可依既定配方分別編譯為 C11 與 C++17。原始實驗與封存證據仍保留於 `experiments/`、`analysis/`，以便追溯。

| [state events](native/receive/state_events.c) | 137C0–13CDC資料組裝、記錄處理與立即／延後通知 | 1308B／461指令原位址碼吻合；真實7346B＋60B圖；接通2個入口、新增27個getter依賴，共93個UND；硬體／OTA未證 |
| [state access](native/receive/state_access.c) | 82A8 記錄搬移、10032 清除與四組狀態更新／讀取 | 336B／108指令，C/C++原位址碼吻合；實際6038B＋60B圖有68個UND；ROM、13C4E用途、索引界限與硬體／OTA未證 |
## 原始碼位置與證據範圍

| 目錄 | 內容 | 目前限制 |
| --- | --- | --- |
| [通知支援函式](native/receive/notification_support.c) | 六函式216B／71i | 狀態判斷、紀錄寫入、條件旗標切換與回呼結果轉接；仍缺131個提供者。[證據](../analysis/notification-support-2026-10-25/README.md) |
| [通知分派](native/receive/selector_notifications.c) | E220..EBAC2444B／789i＋五張表756B | 189個受限索引表項均落於實際指令；仍缺137個提供者。[證據](../analysis/selector-notifications-2026-10-25/README.md) |
| [Selector狀態與查表資料](native/receive/selector_storage.c) | 一個完整狀態流程252B／81i＋四張唯讀表61B | 接上1函式＋4資料入口，新增E220；保留phase、回繞計數、無號時間差與實際查表bytes。主元件43826B code＋1832B data／2849RELA／122UND；45658B原址吻合。[證據](../analysis/selector-storage-2026-10-25/README.md) |
| [功能狀態與記錄](native/receive/feature_state_records.c) | 十九個選定本體1260B／424i | 判定、計數、selector、記錄改寫與私有分派；接上11入口，新增1函式＋4資料缺口。主元件43574B code＋1771B data／2823RELA／126UND；45345B原址吻合。[證據](../analysis/feature-state-records-2026-10-25/README.md) |
| [回呼缺口與輸入組裝](native/receive/callback_completion.c) | 五個完整函式444B／162i | 二位置組裝、模式／門檻、回繞重試與有號16位幅值；接上兩入口，無新依賴。主元件42314B code＋1771B data／2708RELA／132UND；44085B原址吻合。[證據](../analysis/callback-completion-2026-10-25/README.md) |
| [定時記錄與旗標](native/receive/record_continuations.c) | 八個完整函式418B／138i | 旗標指標、記錄位元、序列與回繞重複回呼；接上七入口，無新依賴。主元件41870B code＋1771B data／2675RELA／134UND；43641B原址吻合。[證據](../analysis/record-continuations-2026-10-25/README.md) |
| [記錄參數與模式](native/receive/record_profiles.c) | 四個完整函式978B／310i | 索引、欄位、範圍限制與模式3／4門控；接上兩入口，無新依賴。主元件41452B code＋1771B data／2647RELA／141UND；43223B原址吻合。[證據](../analysis/record-profiles-2026-10-25/README.md) |
| [周邊原語與校正](native/startup/peripheral_primitives.c) | 二十四個完整函式2020B／677i | ADC遮罩、時鐘／計數器路徑、校正與延遲；接上22入口，無新依賴。主元件40474B code＋1771B data／2598RELA／143UND；42245B原址吻合。[證據](../analysis/peripheral-primitives-2026-10-25/README.md) |
| [常駐程式啟動與 ROM 設定](native/startup/resident_startup.c) | 八個完整函式1082B／385i＋21B版本資料 | 預期 CH32V20x ROM 版本、設定／工作註冊與回呼；接上兩入口，新增22依賴。主元件38454B code＋1771B data／2534RELA／165UND；40225B原址吻合。[證據](../analysis/resident-startup-2026-10-25/README.md) |
| [記錄 helper 與週期回呼](native/receive/record_helpers.c) | 十二個完整函式910B／306i | 共用 wrapper、週期回呼、表格選擇與排程；接上十二入口，新增十依賴。主元件37372B code＋1750B data／2468RELA／145UND；39122B原址吻合。[證據](../analysis/record-helpers-2026-10-25/README.md) |
| [記錄動作與共用修改器](native/receive/record_actions.c) | 十九個完整函式1506B／479i | 記錄建立、共用修改及條件通知；接上十九入口，新增五依賴。主元件36462B code＋1750B data／2395RELA／147UND；38212B原址吻合。[證據](../analysis/record-actions-2026-10-25/README.md) |
| [狀態控制與記錄傳輸](native/receive/state_controls.c) | 十個完整函式1266B／452i | 條件控制、記錄傳輸及清理順序；接上七入口，無新依賴。主元件34956B code＋1750B data／2316RELA／161UND；36706B原址吻合。[證據](../analysis/state-controls-2026-10-25/README.md) |
| [控制門控與回呼](native/receive/control_gates.c) | 十二個完整函式892B／308i | 位元圖分派、記錄模式、切換及成對回呼；接上五入口，無新依賴。主元件33690B code＋1750B data／2257RELA／168UND；35440B原址吻合。[證據](../analysis/control-gates-2026-10-25/README.md) |
| [輸出依賴與延後旗標](native/receive/output_dependencies.c) | 十個完整函式374B／130i | 延後旗標、狀態分派、記錄提交及ROM/RAM包裝；接上六入口，無新依賴。主元件32798B code＋1750B data／2142RELA／173UND；34548B原址吻合。[證據](../analysis/output-dependencies-2026-10-25/README.md) |
| [輸出組裝與比較](native/receive/output_builder.c) | 六個完整函式956B／298i | 記錄0x04F3、八組比較、倒數及完整寬度控制；接上四入口、新增兩依賴。主元件32424B code＋1750B data／2117RELA／179UND；34174B原址吻合。[證據](../analysis/output-builder-2026-10-25/README.md) |
| [動作底層與週期輸出](native/receive/action_primitives.c) | 九個完整函式684B／231i＋24B階段表 | 接上六入口、新增兩依賴；主元件31468B code＋1750B data／2069RELA／181UND；33218B原址吻合。時間／產品名稱與實機／OTA未證。[證據](../analysis/action-primitives-2026-10-24/README.md) |
| [動作分派器](native/receive/action_dispatch.c) | 四個完整函式3904B／1571i＋1012B表 | 核對253相對表項／174目標；接上四入口、展開74依賴；主元件30784B code＋1726B data／2007RELA／185UND；32510B原址吻合。[證據](../analysis/action-dispatch-2026-10-24/README.md) |
| [回呼依賴](native/receive/callback_dependencies.c) | 三個完整函式464B／170i | 記錄掃描、資料佇列包裝與狀態條件通道設定；主元件26880B code＋714B data／1755RELA／115UND；27594B原址吻合。[證據](../analysis/callback-dependencies-2026-10-24/README.md) |
| [已註冊回呼](native/receive/registered_callbacks.c) | 三個完整原始函式3220B／1032i | 接上三個入口、展開28個依賴；主元件26416B code＋714B data／1726RELA／115UND；27130B原址吻合。靜態資料與實機／OTA仍未證。[證據](../analysis/registered-callbacks-2026-10-24/README.md) |
| [CRC與周邊底層支援](native/startup/platform_primitives.c) | 六個完整原始函式356B／134i | 接上CRC16、路由、遮罩、描述子與啟用等六個入口，無新增依賴；主元件23196B code＋714B data／1426RELA／90UND；23910B原址吻合。[證據](../analysis/platform-primitives-2026-10-24/README.md) |
| [主程式服務與周邊設定](native/startup/main_services.c) | 五個完整原始函式974B／328i | 接上五個入口、展開31個依賴；主元件22840B code＋714B data／1419RELA／96UND；23554B原址吻合，三個回呼與不透明預設資料仍未提供。[證據](../analysis/main-services-2026-10-24/README.md) |
| [設定預設與持久化](native/startup/settings_defaults.c) | 十二個完整原始函式878B／297i | 接上六個入口，四byte預設資料仍未提供；主元件21866B code＋714B data／1368RELA／70UND；選定22580B原址吻合。[證據](../analysis/settings-defaults-2026-10-24/README.md) |
| [周邊初始化與描述子](native/can/peripheral_initializer.c) | 完整18AB0函式242B／99i與32B描述子型別 | 接上一個入口且無新依賴；主元件20988B code＋714B data／1354RELA／75UND；全部21702B原址吻合。[證據](../analysis/peripheral-initializer-2026-10-24/README.md) |
| [主初始化與設定載入](native/startup/main_initializers.c) | 兩個完整原始函式522B／155i | 接上兩個入口、展開七個預設值／周邊依賴；主元件20746B code＋714B data／1337RELA／76UND；全部21460B原址吻合。[證據](../analysis/main-initializers-2026-10-24/README.md) |
| [更新結束依賴](native/receive/ota_finalizers.c) | 兩個完整原始函式182B／69i | 接上兩個入口且無新依賴；主元件20224B code＋714B data／1314RELA／71UND；全部20938B原址吻合。[證據](../analysis/ota-finalizers-2026-10-24/README.md) |
| [更新回覆與重啟路徑](native/receive/ota_replies.c) | 六個完整原始函式334B／127i | 接上六個入口；主元件20042B code＋714B data／1300RELA／73UND；全部20756B原址吻合。ABI／重啟／實機未證。[證據](../analysis/ota-replies-2026-10-24/README.md) |
| [更新狀態與控制器](native/receive/ota_runtime.c) | 十個完整原始函式1052B／363i | 保留更新／識別／狀態／控制器限制；主元件19708B code＋714B data／1282RELA／77UND；全部20422B原址吻合。[證據](../analysis/ota-runtime-2026-10-24/README.md) |
| [輸入解析與函式指標](native/receive/incoming_protocol.c) | 三個完整處理函式776B／262i與四段40B唯讀前綴 | 三個typed回呼指標；主元件18656B code＋714B data／1201RELA／74UND；全部19370B原址吻合。[證據](../analysis/incoming-protocol-2026-10-24/README.md) |
| [事件回呼與參數載體](native/receive/runtime_callbacks.c) | 三個完整原始函式1072B／369i | 接上兩個位址回呼與8B6E；主元件17880B code＋674B data／1142RELA／72UND；全部18554B原址吻合。[證據](../analysis/runtime-callbacks-2026-10-24/README.md) |
| [主初始化與資料載體](native/receive/main_runtime_family.c) | 六個完整原始函式704B／241i | 接上四個舊入口、展開八個依賴；主元件16808B code＋674B data／1098RELA／75UND；全部17482B原址吻合。[證據](../analysis/main-runtime-family-2026-10-24/README.md) |
| [回呼條件與暫存器設定](native/receive/callback_gate_family.c) | 八個完整原始函式370B／121i | 已接上五個舊入口；主元件16104B code＋674B data／1073RELA／71UND；全部16778B原址吻合。[證據](../analysis/callback-gate-family-2026-10-24/README.md) |
| [狀態寫入與回呼參數](native/receive/state_output_dependencies.c) | 三個完整原始入口80B／24i | 已接上B6EA／D05C／10816；主元件15734B code＋674B data／1052RELA／76UND；全部16408B原址吻合。[證據](../analysis/state-output-dependencies-2026-10-24/README.md) |
| [ROM dependencies](native/receive/rom_dependencies.c) | 七個完整函式422B／153i | 已接上四個舊入口；主元件15654B code＋674B data／1048RELA／79UND；全部16328B原址吻合。[證據](../analysis/rom-dependencies-2026-10-24/README.md) |
| [ROM driver family](native/receive/rom_driver_family.c) | 六個完整原始函式564B／208i | 已接上主初始化173A2與171BA，展開四個新依賴；主元件15232B code＋674B data／1004RELA／80UND；全部15906B原址吻合。[證據](../analysis/rom-driver-family-2026-10-24/README.md) |
| [callback support](native/receive/callback_support.c) | 完整D1A8指標10B與16DAC payload封裝40B | 已接上兩個真實提供者；主元件14668B code＋674B data／963RELA／78UND；全部15342B原生原址配置吻合。[證據](../analysis/callback-support-2026-10-24/README.md) |
| [callback byte getters](native/receive/callback_read_leaves.c) | 11個完整入口94B／29i | 已接上真實提供者；主元件14618B code＋674B data／961RELA／80UND；全部15292B原生原址配置吻合。[證據](../analysis/callback-read-leaves-2026-10-24/README.md) |
| [IRQ initializer](native/irq/irq_initializer.c) | 完整144B9A42 frame／CSR流程與120B RCC helpers | 已接上真實提供者；主元件14524B code＋674B data／961RELA／91UND；全部15198B經原生原址配置吻合。[證據](../analysis/irq-initializer-2026-10-24/README.md) |
| [original clock](native/clock/clock_original.c) | 完整18834查詢174B／58指令與1973C欄位40B／11指令 | 已接上兩個真實提供者；主元件14260B code＋674B data／951RELA／92UND；全部14934B經原生原址配置吻合。[證據](../analysis/clock-original-2026-10-24/README.md) |
| [memory transfer19BF0](native/receive/memory_transfer.c) | 完整182B／54指令，向前byte／word與36B批次搬移 | 已接上真實提供者；主元件14046B code＋674B data／940RELA／94UND；全部14720B經原生原址配置吻合。[證據](../analysis/memory-transfer-2026-10-24/README.md) |
| [callback flow](native/receive/callback_flow.c) | 九個原始入口情境，包含完整672B狀態組裝器；1082B code＋96B data | 主元件13864B code＋674B data／930RELA／95UND；原碼吻合，原機／OTA未證。[證據](../analysis/callback-flow-2026-10-24/README.md) |
| [callback providers](native/receive/callback_providers.c) | 五個入口與 B0D0 回呼，558B code＋62B 唯讀資料 | 原碼／相對表／常數吻合；主元件12782B code＋578B data／860RELA／81UND，原機／OTA未證。[證據](../analysis/callback-providers-2026-10-24/README.md) |
| [state readers](native/receive/state_leaf_reads.c) | 27 個事件讀取入口與 2 個實際輔助函式 | 472B／153i 原碼吻合；已接入主元件12224B code＋516B data／807RELA／79UND。[整合](../analysis/state-callback-integration-2026-10-24/README.md)[證據](../analysis/state-callbacks-2026-10-24/README.md) |
| [dispatch tables](../analysis/dispatch-tables-2026-10-24/README.md) | 重用2736B code＋60B相對表，15項皆接到真實區塊 | 主元件9836B code＋516B data／698RELA／82UND；程式與表格原位址碼吻合，原機／ABI／OTA未證 |
| [main queue](../analysis/main-queue-2026-10-24/README.md) | 佇列、旗標與接收鏈重用1464B／509i | 主元件7100B code＋456B data／424RELA／16UND；接通兩個主入口、展開兩個分派依賴，原機／OTA未證 |
| [record providers](../analysis/record-providers-2026-10-24/README.md) | 重用8個C/C++單位共1000B／349i，包含必要SPI呼叫鏈 | 主元件5636B code＋456B data／356RELA／16UND；原位址碼吻合，原機／ABI／OTA未證 |
| [record decode](native/receive/record_decode.c) | 原212B／77i；C6A8解碼與FAF8狀態寫入 | 184非控制bytes／10原位址參照吻合；主元件4636B code＋456B data／309RELA／20UND。保留fresh fullword與target bits；memory／ABI／OTA未證。[證據](../analysis/record-decode-2026-10-24/README.md) |
| [record consumer](native/receive/record_consumer.c) | 原114B／42i；三個記錄複製／清除／完成入口 | 重用42B82A8與102B12A08；主元件4424B code＋456B data／299RELA／22UND。原位址編碼吻合；原機／ABI／OTA未證。[證據](../analysis/record-consumer-2026-10-24/README.md) |
| [RF completion](native/receive/rf_completion.c) | 原136B／45i、完成回呼／重試提供者 | 126非控制bytes／3原位址參照吻合；主元件4166B code＋456B data／281RELA／17UND。另核對1550B RF相對佈局／6組literal，絕對配置／硬體／OTA未證。[證據](../analysis/rf-completion-2026-10-24/README.md) |
| [RF callbacks](native/receive/rf_callbacks.c) | 更正17476／174EE入口，原196B／65i | 144非控制bytes／16原位址參照吻合；真實4030B code＋456B data／278RELA／19UND。literal連接、buffer界限、installed ABI／硬體／OTA未證。[證據](../analysis/rf-callbacks-2026-10-24/README.md) |
| [resident providers](native/receive/resident_providers.c) | 原300B／103i、八個間接呼叫與RF配置對照 | 298非控制bytes／1原位址參照吻合；真實3834B code＋456B data／262RELA／17UND。SDK32B配置另以資料編譯核對；installed ROM／ABI／硬體／OTA未證。[證據](../analysis/resident-providers-2026-10-24/README.md) |
| [event consumer](native/receive/event_consumer.c) | 原534B／187i、事件／佇列分派與重試回呼 | 472非控制bytes／23原位址參照吻合；真實3534B code＋456B data／261RELA／18UND。保留frame／REM；表格界限、literal配置、ROM／記憶體／IRQ／OTA未證。[證據](../analysis/event-consumer-2026-10-24/README.md) |
| [record queue](native/receive/record_queue.c) | 原270B／94i、佇列／回呼建構／編碼 | 246非控制bytes／7原位址參照吻合；真實3000B code＋456B data／238RELA／17UND。複製前索引界限、記憶體／resident／IRQ／OTA未證。[證據](../analysis/record-queue-2026-10-24/README.md) |
| [record control](native/receive/record_control.c) | 原114B／44i、7B記錄參數與事件啟動 | 98非控制bytes／6原位址參照吻合；真實2730B code＋456B data／231RELA／17UND。保留32B frame與完整word讀取；實體ROM／記憶體／IRQ／OTA未證。[證據](../analysis/record-control-2026-10-24/README.md) |
| [callback table](native/receive/callback_table.c) | 原266B／102i、共用迴圈與取消路徑 | 244非控制bytes／8原位址轉移吻合；真實2616B code＋456B data／225RELA／17UND。實體ROM／記憶體／IRQ／OTA未證。[證據](../analysis/callback-family-2026-10-24/README.md) |
| [init tail](native/startup/init_tail.c) | 原138B／47i與完整300B排程器連結 | 120非控制bytes／5原位址轉移吻合；真實2350B code＋456B data／217RELA／18UND。WCH ROM介面配置有對應證據；installed ROM／IRQ／RAM／硬體／OTA未證。[證據](../analysis/init-tail-2026-10-24/README.md) |
| [main／application／init](native/startup/main_family.c) | 三段原124B／42i與真實main9008連結 | 52非控制bytes／20原位址轉移吻合；接入watchdog40B；真實1912B code＋456B data／201RELA展開17個具體依賴。回呼／entry／ROM／IRQ／硬體／OTA未證。[證據](../analysis/main-family-2026-10-24/README.md) |
| [TIM3 IRQ](native/irq/timer3_irq.c) | 原442B／138i與真實向量45 | 376非控制bytes／24原位址轉移吻合；真實1748B code＋456B data／181RELA／2UND。選定非零向量皆綁定；動態回呼、IRQ／ROM／硬體／OTA仍未證。[證據](../analysis/timer3-irq-2026-10-24/README.md) |
| [RTC alarm IRQ](native/irq/rtc_alarm.c) | 五段原78B／23i與真實向量57連結 | 62個非控制bytes與四個原位址編碼轉移吻合；目前1246B code＋456B data／157RELA／3UND。輪詢、半字寬度、尾跳與MRET保留；IRQ／實體硬體／OTA未證。[證據](../analysis/rtc-alarm-irq-2026-10-24/README.md) |
| [ECALL restore](native/irq/ecall_restore.c) | 原78B／35i恢復與真實向量5／8連結 | C/C++逐byte吻合；目前1168B code＋456B data／153RELA／4UND。保留既有frame、CSRS804遮罩32及MRET；trap／CSR／實體硬體與OTA仍未證。[證據](../analysis/ecall-restore-2026-10-24/README.md) |
| [LLE IRQ](native/irq/lle_irq.c) | 原134B包裝層與真實向量64連結 | 全134B／64i相同；1090B code＋456B data／153RELA／5UND。29組save/load、GP+384 callback與MRET保留；callback／IRQ／實體硬體及OTA未證 |
| [CAN RX0里程碑](../analysis/can-rx0-irq-bind-2026-10-24/README.md) | 原12C24／18D78／12BC8組合 | 先前956B＋456B／153RELA／6UND階段，完整保留於LLE元件。ring原位址配置、resident身分及硬體／OTA仍未證 |
| [向量39里程碑](../analysis/vector-irq-bind-2026-10-24/README.md) | 完整76B16FB6連結 | 先前648B＋456B／144RELA／7UND階段；其原廠provider與資料已完整保留於最新CAN RX0元件 |
| [原廠向量資料](native/startup/boot_vectors.c) | 8038-8180的328B具型別地址資料 | 全部62 R_RISCV_32與20個零值word通過核對；最新真實IRQ連結見上列。硬體IRQ數量、ABI與OTA未證 |
| [原廠啟動](native/startup/boot_original.c) | 原廠header／預設入口／reset／IRQ跳板／完整clock | 572B／212i＋128B真實C初始化資料，原位址碼保持一致；向量資料已於上列獨立元件接入，完整硬體／OTA仍未證 |
| [native/init_mask](native/init_mask/init_mask.c) | V4.1.60 初始化末端的 register-mask leaf | 完整 30-byte 函式與官方 BIN 相同；不證明完整啟動或實體配置 |
| [native/irq/irq_flag.c](native/irq/irq_flag.c) | 真實向量39 handler | 完整76B／21i與原廠16FB6相同；slot39真實連結保留於最新元件。兩次fresh狀態讀取、GP+360 byte更新與MRET保留；實體IRQ上下文未證 |
| [native/irq/flag_consumer.c](native/irq/flag_consumer.c) | 17002 的 GP 旗標消費函式 | 入口8B／主體54B；兩個未解決JAL以外54B與原廠相同，另驗部分連結相鄰關係；接收函式與provider ABI仍未閉合 |
| [native/receive](native/receive/receive_wrapper.c) | 16B0A 接收入口與尾端 register 寫入 | 入口14B／主體56B，非呼叫54B相同、4個JAL未解析；實體S0／S1與frame埠保留當下狀態，未新增C frame；下游ABI仍未閉合 |
| [register read](native/receive/register_read.c)／[write](native/receive/register_write.c) | GPIO選擇、32B frame與三次SPI傳輸 | read72B／write76B，非呼叫60B／64B與原廠相同；保留fresh槽位與清理前讀RA；單體物件保留SPI呼叫，另於352B部分連結綁定真實定義 |
| [SPI transfer](native/receive/spi_transfer_ports.c) | SPI輪詢／資料葉函式 | 8個架構區域與5個RVC埠，獨立原位連結完整72B／25指令相同；非一般C ABI或實機證據 |
| [packet receive](native/receive/packet_receive.c) | 封包接收、DLC／ID與共用出口 | 142B／52指令，3區域14／116／12B；120個非控制位元組相同，4個JAL與2個finish分支仍待解析；private ABI、硬體與燒錄未證 |
| [ring insert](native/receive/ring_insert.c) | 接收佇列與fresh resident間接呼叫 | 5個架構區域，原位連結完整92B／32指令與原廠相同；保留PC衍生table與呼叫後S0／S1；resident身分、caller bounds與硬體未證 |
| [ring IRQ adapter](native/irq/ring_irq_adapter.c) | 條件式frame與兩個MRET出口 | 完整52B／17i已接上真實18D78／12BC8；三單位全部308B／102i於純資料原位址編碼後相同。IRQ／resident上下文未證 |
| [IRQ provider](native/receive/irq_provider.c) | Fresh mailbox讀取與接收記錄欄位 | 全164B／53i與原碼相同，已接入向量36鏈；保存SDK的CAN_Receive配置對應。實體MCU／周邊及IRQ／OTA仍未證 |
| [queue consumer](native/receive/queue_consumer.c) | 佇列釋放與條件分派 | 314B／107指令、10個private regions；230B非控制指令與2163保留位元相同，25筆relocation／八個UND仍待解析；保留實體SP／S-register／CSR及resident殘值，並非完整韌體 |
| [record program](native/receive/record_program.c) | 93AA–94EE記錄配置／控制 | 四個函式324B／109i、19架構區塊，C/C++原位碼全等；opaque40068／40070的身份、記憶體及呼叫後索引界限未證 |
| [通道／濾波設定](../experiments/tsl9-channel-route/README.md) | 分流12ABE、內建128FE／18BA2、外部16CC4及helpers | 六段原位址1242B／445i／94 FUNC全部相同；延伸3166B／1104i／191 FUNC／144 pending RELA，仍缺14D2E。實體晶片、resident ABI、啟動／IRQ及OTA未證明 |
| [完整功能分派](../experiments/tsl9-feature-dispatch/README.md) | 14D2E完整本體、829E及兩張相對表 | 1922B code／60B table於純資料重定位驗算後與原廠相同；5088B＋60B圖仍有70直接provider與1069E callback。ET_REL VMA0，硬體／OTA未證明 |
| [GP word toggle](native/receive/gp_word_toggle.c) | 9B36 byte guard與word XOR2 | 全24B／7i與原廠相同；只改A4／A5，跳過時保留A4。實體用途、GP／記憶體有效性、IRQ／OTA未證 |
| [queue leaves](native/receive/queue_small_providers.c) | V4.1.60旗標與有界清除 | 全部6／18B與原leaf相同；C fresh GP+167 byte、unsigned index<=2清byte；無spill／UND／relocation。僅診斷VMA0，consumer實際整合與硬體尚未證 |
| [queue filter](native/receive/queue_filter.c) | 82D2封裝／轉送條件 | 188B／69指令，166B完整非控制指令相同；7筆待解析轉移含一個C.JAL provider。保留then-live frame／S-register；非零不代表轉送成功 |
| [transport frame](native/receive/transport_frame.c) | 8A56 admission、封裝、複製與checksum | 280B／96指令、246B完整非控制指令相同；9筆local pending RELA／0 UND。fresh4013C admission與40050 tail provider未知；初始guard不保證post-call長度有界 |
| [record dispatch](native/receive/record_dispatch.c) | 12A08 status／ID／tag／copy／peripheral 分派 | 102B／35i、9個私有區塊；4 genuine UND／9 pending RELA；保留 then-live SP／S0／呼叫殘值，provider ABI／硬體仍未證 |
| [record predicate](native/receive/record_predicate.c) | 821E pointer bit／index／byte 條件判斷 | 完整42B／15i C/C++與原BIN相同；無frame／store／call／UND／relocation；GP／記憶體／flag功能與硬體未證 |
| [fill provider](native/receive/fill_provider.c) | 8520 byte／word填值與計算跳轉表格 | 13個架構區域168B／55i，8個pending控制且無UND；保留降序SB、word順序、unsigned指標迴圈與RA／T0。計算目標及退出殘值須依原始PC解讀；非libc替代或硬體證明 |
| [SPI command providers](native/receive/spi_write_providers.c) | 168DE 緩衝路徑與1693E命令路徑 | 20個架構區域182B／68i，13個pending控制與1個真實16896提供者參照；保留32B frame、全寬fresh槽位、零長度前置測試、GPIO word寫入與RA還原順序。實體傳輸與OTA未證 |
| [tagged dispatch](native/receive/tagged_dispatch.c) | 16B7C 標記路徑、64B frame 與記錄處理 | 15個架構區域246B／86i，11個pending控制與4個真實UND；保留early return、then-live SP／S0-S3、opaque residue及不等式迴圈。原廠固定位元與符號目的地由獨立原生實驗核對；提供者ABI、硬體與OTA未證 |
| [peripheral write](native/receive/peripheral_write.c) | 18CA4 bank選擇與ID／長度／payload寫入 | 七個私有區塊、212B／72i原位診斷碼全部相同；保留三次fresh status、22個static load／8個store次序及退出殘值；實體周邊／ABI／OTA未證 |
| [native/irq](native/irq/interrupt_registers.c) | 舊版RCC／IRQ候選 | 保留四個30B helper與180B初始化來源；目前主元件改用上列irq_initializer.c的精確144B＋120B。非同步IRQ／硬體／OTA等價仍未證。 |
| [native/timer](native/timer/delay.c) | V4.1.60 計時器暫存器契約 | 完整54-byte leaf與官方相同；獨立編譯入口，尚未替換 NV callback／OTA BIN |
| [native/nv/nv_write_frame_contract.c](native/nv/nv_write_frame_contract.c) | 新 NV write callback frame／fresh source contract | 已量測原32B frame／source位置及前40B除JAL相同；結尾 LI0 提早，fault／IRQ等價仍未證 |
| [native/nv/nv_read_registers.c](native/nv/nv_read_registers.c) | NV read 暫存器介面 | 30B／14指令；wrapper無新增A3寫入及RA scratch；原版13指令，順序與provider仍有缺口 |
| [native/nv/nv_read_live_count.c](native/nv/nv_read_live_count.c) | NV read 保留原count | 30B／13指令；直接A2移位與原10B call window相同；frame／返回順序及installed provider未證 |
| [native/nv](native/nv/nv_write_callback.c) | NV read/write、timer 與 Flash helpers | 已採用兩處 A1 clobber 修正；write frame、source reload、timer 出口及間接 provider 仍有限制 |
| [native/adc](native/adc/caller_bank.c) | caller 專用 ADC 設定與真實 volatile port | 保留已知 live register bank；新增16-byte frame及 alias／IRQ限制 |
| [native/clock](native/clock/clock_query.c) | 舊版查詢／欄位候選 | 保留歷史來源，未接入目前主元件：query196B／原174B，fields38B／原40B。目前精確原始區塊見上列clock_original.c，實機相容性仍未證。 |
| [native/clock/clock_init.c](native/clock/clock_init.c) | 舊時鐘診斷來源 | 保留舊232B診斷；目前完整234B選用碼見boot_original.c。長度不同本身不證明功能錯誤 |
| [native/startup/init_writes.c](native/startup/init_writes.c) | 9250 初始化鏈的五筆有序寫入 | 完整40B／15指令與官方9F4C函式相同；五筆volatile word寫入，只改A4／A5；周邊身分與完整啟動未證 |
| [native/startup](native/startup/reset_memory.c) | 舊reset診斷來源 | 舊clock與診斷RAM／stack配置保留作歷史；不作原機記憶體容量或啟動證據 |
| [native/resident](native/resident/native.c) | SDK resident candidate 的 compare／fill／copy | 正常記憶體投影；並非已確認原機 ROM，scratch／fault／尺寸差異仍存在 |
| [resident copy 架構](native/resident/copy_arch.c) | WCH V1.31 SDK 候選 copy | 條件式RAM20000332連結後完整58B／18指令吻合；保留T0／A7與故障前綴順序。尚未確認為裝置resident，未連入韌體 |
| [reference/v4100](reference/v4100/dnd_actions.c) | 免打擾、一般設定、GATT framing 行為模型 | 來源是 V4.1.00；外部 provider 仍有未知，不混入 V4.1.60 原機實作 |
| [callback／校驗](native/receive/feature_callback.c) | 七段314B／109指令，含封包校驗、計數與延後回呼 | C/C++原位址碼全等；真實5402B＋60B圖仍有75個未解析符號，排程器／ROM／硬體／OTA未證 |
| [scheduler](native/receive/scheduler.c) | 完整9124–9250，300B／115指令，15槽掃描及計時運算 | C/C++原位址碼全等；真實5702B＋60B圖仍有74個UND，四個resident轉移與硬體相容性未證 |

[source-manifest.json](source-manifest.json) 記錄每個檔案的原始來源、來源／整理後 SHA256、逐項 include 調整、兩處 A1 宣告修正，以及每個編譯入口的證據與限制。較新的 volatile source 實驗尚未解決 frame／slot 差異，仍保留在實驗目錄。

## 使用方式

在專案根目錄執行：

```sh
python3 scripts/verify-curated-source.py
```

預設只核對來源與清單，不需 LLVM。Windows 可將 `python3` 換成 `py -3` 或已安裝的 `python`。

若已安裝支援 RISC-V 的 LLVM，可明確指定工具目錄：

```sh
python3 scripts/verify-curated-source.py --tool-dir "/absolute/path/to/llvm/bin"
```

腳本依 manifest 選擇84個 native translation units，對原始與整理後版本分別編譯 C11／C++17，再讀取物件並比較所有函式、配置區段與 relocation。包含式 C core 由對應入口編入，不能把所有 `.c` 當成互不重複的連結單元。V4.1.00 reference 不納入此原機物件編譯；本次未重跑舊 HOST 矩陣。 另有1個native_data_units純指標資料單位，由experiments/tsl9-original-vectors/build-v1.py獨立驗證，不以假函式納入舊檢查。

本輪以 Android NDK 27.1.12297006 的 LLVM 18 在 Windows 實際通過 190 組比對（380 個物件），收據為 `build/curated-source/action-primitives-20261024-v1/verification.json`。舊整理收據保留為歷史快照。Python 入口使用標準函式庫，未實機驗證其他作業系統；更換工具鏈需重新通過相同檢查，不下載工具或搜尋編譯旗標。 指標資料另外通過2組來源比對／4物件；兩個範圍合計192組／384物件。

既有結果可唯讀重播：

```sh
python3 scripts/verify-curated-source.py --replay "/absolute/path/to/verification.json"
```

**這是原始碼整理與離線證據，不是完整韌體 build。** 尚未證明原機晶片、installed ROM、記憶體 ownership、完整啟動／中斷或 BLE OTA 相容性；重建韌體尚未完成在原硬體成功刷入及正常執行的驗證。腳本不執行 RV32／MMIO，也不產生或燒錄韌體 BIN。

[reset／clock整合檢查](../experiments/tsl9-runtime-reset-clock-fit/README.md)另外核對連結相鄰、原呼叫／RA、IR及負例。舊收據保留為本機歷史快照；其凍結檢查器可能拒絕此新版來源。

[SPI單體與管線檢查](../experiments/tsl9-spi-transfer-leaf/README.md)另外驗證已解析的函式機器碼與352B ET_REL連結；來源副本比對本身不解析這些架構邊界。

[Packet單體檢查](../experiments/tsl9-packet-receive/README.md)使用獨立 verifier；正式收據入口為本機 `experiments/tsl9-packet-receive/build/verified-v2/{c,cpp}/verification.json`。原始碼整理本身不解析六個控制轉移或補足 provider／IRQ ABI。

[ring與接收鏈原位圖](../experiments/tsl9-ring-insert/README.md)另外區分已解析的局部程式圖、未知的動態resident provider，以及完整韌體相容性。

[接收／分派／傳送整合](../analysis/receive-transmit-chain-2026-10-23/README.md)已重新編譯12個既有src單位：九段原位程式共1588B／555指令，沒有直接符號缺口；完整1902B部分連結仍保留四個真實提供者缺口。六個resident間接轉移及66970B RX間隙未證，兩者都不是可刷韌體。

[9B36來源整合](../analysis/gp-word-toggle-2026-10-23/README.md)將診斷部分連結擴為1926B／669指令／108 strong FUNC／97 pending RELA／3 UND，綁定13個當前來源單位；1588B原位圖未改變。v3固定產物證明通過每語言1991個負例；實體用途及完整硬體／OTA相容性仍未證。

[記錄配置／控制整合](../analysis/record-program-2026-10-23/README.md)將真實部分元件擴為2250B／778i／127FUNC／109pending RELA／2UND（12ABE、14D2E）。八個resident轉移仍未知；VMA0的AUIPC不是可執行原位配置。v2每語言通過2600個靜態負例；未宣稱完整韌體或硬體／OTA相容。
