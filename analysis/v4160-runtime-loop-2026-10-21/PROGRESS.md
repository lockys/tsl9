# Runtime loop milestone / Runtime迴圈里程碑

## English

The full goal remains C/C++ reconstruction of necessary TSL9 features and the
original execution layer, ultimately a BIN accepted by original BLE OTA on the
original hardware. This milestone implements fixed source dataflow for main9008,
init9250, permanent loop8180 and dispatcher901A in ID2966 V4.1.60:220B/80
instructions, with45 raw operand mutations rejected by the portable source proof.
Own C11/C++17 suites each pass6 groups/1,431 checks. Independent reuse, review and
actual reset/resident/runtime composition are separate sealed scopes. New code
is delivered to the existing re-tsl9 project; each verified milestone is committed
and pushed to the authorized project repository.

Initialization exposes14 deep callee providers and a tail provider without
inventing prototypes or status checks. Loop budget is a host observation stop,
never a main return. Live shared slots/registers/stack reloads and explicit return
routes are preserved. Dispatcher mode precedes argument; unknown state stops
instead of choosing a later branch. The resident bridge requires explicit exact
candidate MRET with known9008; strictly captured main/main+tail data stops earlier.
Synthetic unknown-memory and provider conditions do not fill artifact holes or
prove installed resident ABI. Numeric symbol storage does not prove implementation.

No original/rebuilt firmware is executed or emulated; no new vendor requests,
device identifiers, BLE/UART/CAN or physical Flash I/O are used. Exact MCU/PCB,
installed ROM, startup/memory/interrupt ABI, physical effects and OTA compatibility
remain unproved. The previous76800-byte source-identical offline image is unchanged
and still NOT-FLASH-VALIDATED. The full goal is not complete.

Final independent review passes7 groups/293 checks per language and rejects six
compiled behavior countercases. Final composition-v2 passes21 groups/725,870
assertions per language and six compiled countercases. The earlier composition
remains an immutable superseded archive. The two corrected findings concern
link-RA prefix observation and incomplete return-route equality; both have
regressions and bind the final source, not the earlier formal receipts.

## 繁體中文

完整目標仍是以C/C++重建TSL9必要功能及原機執行層，最終產出能由原藍牙OTA安裝到
原硬體的BIN。本輪新增ID2966 V4.1.60的main9008、init9250、永久loop8180與
dispatcher901A固定資料流，共220B／80條指令；可攜來源證據拒絕45個原始運算元突變。
自有C11／C++17各通過6組／1,431項；獨立reuse、review及實際reset／resident／runtime
整合分別封存。新程式交付到既有re-tsl9專案；每個驗證里程碑commit／push到已授權
的專案儲存庫。

初始化明示14個深層callee與尾呼叫提供者，不臆造原型或成功檢查。loop次數限制只是
主機觀察停止，不是main返回；保留共用即時槽、暫存器、堆疊重讀與明示返回路徑。
派送先mode後argument，未知狀態即停止，不跳選較後分支。resident橋接須指定候選已
明示MRET且目標完整已知9008；嚴格擷取的main／main+tail都更早停止。合成未知記憶體
與提供者條件不補原檔缺洞，也不證明原機resident ABI。存在數值符號儲存不等於已實作。

不執行或模擬原始／重建韌體，不發新廠商請求、不用真實識別資料，不存取BLE、UART、
CAN或實體Flash。確切MCU／PCB、原機ROM、啟動／記憶體／中斷ABI、實體效果及OTA
相容性仍未知。原有76800-byte來源一致離線映像未改，仍為NOT-FLASH-VALIDATED。
完整目標尚未完成。

最終獨立審查每語言通過7組／293項，拒絕六份已編譯行為反例；最終composition-v2
每語言通過21組／725,870項，六份已編譯反例均遭拒絕。較早整合保留為不可改的舊
archive。兩個已修正問題分別為link-RA前綴觀察及不完整返回位址相等判斷，均有回歸
測試，綁定的是最終來源，並非先前的正式收據。
