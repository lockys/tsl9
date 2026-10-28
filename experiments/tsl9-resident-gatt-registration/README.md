# GATT 服務註冊與 UUID：候選原機執行層

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_gatt_registration.c) · [UUID 資料](uuid_data.c)

新增4個完整 SDK 候選本體，**536 CODE bytes／219指令＋20 DATA bytes**。C11／C++17機器碼與原始候選指令相符；6組far call、42組直接控制重定位、16個條件式Xwchc port，以及官方GATT結構的零runtime-byte編譯期斷言均已核對。

|已核對位置|行為與範圍|
|---|---|
|`0x445E6..0x44624`|將兩-byte UUID放入16-byte模板的offset12／13；保留null與copy順序|
|`0x44624..0x4468A`|處理2／16-byte UUID比較與必要展開，沿用候選Boolean比較慣例|
|`0x4CE22..0x4CF22`|檢查首筆service type與key size、分配16-byte stride的handle、登記服務節點|
|`0x4CF22..0x4CF96`|包裝服務註冊，再視callback指標與handle登記12-byte callback節點|
|APP `0x8FCC`|完整384B／126指令初始化函式中，唯一資料流為 `A0=GP,A1=4,A2=16,A3=0x19DFC`，呼叫候選slot `0x40130→0x4CF22`|

原reset的128B初始化來源前64B，與官方候選 `gattAttribute_t` 的四筆16B布局相符：UUID長度offset0、UUID指標offset4、permission offset8、handle offset10、value指標offset12。這項條件式解讀要求原reset copy完成、GP穩定、表格至呼叫前未被修改，以及installed候選ABI／ROM／Xwchc相符。

表格指向未選取的 `0x1AB38／0x1AB42／0x1AB44`，但**指標不等於value長度證據**。本輪沒有把那段APP資料補入SRC，也沒有進入刻意排除的命令路由程式／預設資料。key size16落在候選接受的7～16範圍；它不證明連線已加密或已授權。

重要的條件式語義：core註冊成功後，wrapper仍可能因callback節點配置失敗回傳 **19**，且完整wrapper沒有回滾呼叫。因此不能假設所有註冊錯誤都發生在修改狀態之前，也不能任意新增清除／重試行為。這是候選程式的靜態推論，尚非實機觀察。

20B UUID資料來自真實稀疏HEX：重新驗證全部11,973筆record／191,244資料bytes，主連續區段之外的兩個UUID也逐位址查證，沒有補零、補FF或把缺失切片當零值。原有啟動來源的4-byte缺口仍保留。

與真實SDK父元件部分連結後，C/C++完整物件一致：**41,410 CODE＋412 DATA bytes／14,279指令**，2,879正大小FUNC、5個DATA OBJECT、2,295筆重定位、0具名UND。保留全部舊byte／global symbol／typed relocation；四個普通外部入口均綁到實際父CODE。零UND不代表ROM／RAM／callback／IRQ／Flash／OTA執行相依已閉合。

[`verification-v1.json`](verification-v1.json) 與 [`summary.json`](summary.json) 保留完整CFG、唯一reaching definitions、原生與獨立ELF讀取證據。APP正式來源仍162份、靜態覆蓋率 **95.67%**；未接入APP、未做原位址最終配置、未產生BIN或執行target／HOST model／ISA／硬體。**仍未成功重建已驗證可用的替代韌體。**

具備既有本機輸入與固定LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-resident-gatt-registration/verify-v1.py --tool-dir "$LLVM_BIN"
```

此次只提交文字來源與證據；原生產物不包含在提交內。早先停止的composition-v1／v2保留本機，成功試次為composition-v3；不宣稱每次試驗都通過。[新增功能候選](feature-candidates.json)：離線GATT表格一致性及部分註冊狀態診斷，尚未實作。
