# V4.1.60 clock 的可讀 C/C++ 契約

對應原1874A..18834的234B／93條指令，包括18830的cold tail。原native工程的clock.c仍保留原指令；本模組是另存的可讀語義移植，沒有替換既有native整合或關閉原31UND。

所有32-bit MMIO與SP+8／12存取透過顯式provider，數字地址不轉成host指標。entry_sp由caller提供，frame為其減16的32-bit數值，非實體stack/RAM有效性證明。每次讀取皆live，不把未知讀值或provider改寫的stack變數當成快照。

第一次poll讀0x40021000的bit17，普通無alias堆疊下counter達4096停止；0x20000是ready mask，不是迴圈上限。離開loop後另讀狀態，故先前sample ready也不能代替fresh bit17判斷。cold tail會清SP+12再回共用分支。兩個看bit25／status[3:2]的後段poll沒有原逾時條件；觀察預算只限制主機分析，不改造成韌體timeout。

保留原先兩次read後same-value write，以及之後各次AND／OR和fresh read的順序。值與known-mask一起傳遞，無法判斷的branch保留unknown邊界；HALT／TRANSFER及預算停止不還原已發生的provider效果。

以 `./verify.ps1` 與 `./verify.ps1 -Cpp` 執行主機合成測試。先核對原BIN和234B範圍hash，再以MSVC C11／C++17編譯，並用既有NDK clang將同一production source編成freestanding RV32IMAC物件；物件不執行。測試包括4096樣本、fresh狀態反轉、live stack改寫、32-bit counter wrap、部分未知資料、延後ready、無限poll預算以及正常路徑每個provider位置的HALT／TRANSFER。

`VC_RETURNED`是本分析介面的控制結果，不是原函式回傳成功碼；原body沒有設定a0。RV32物件提供的是本模組自己的vc_* API，尚非原clock ABI的替代品，未整合入原startup、IRQ或resident。自己state的clear有真C實作，沒有以libc memset或假ROM provider隱藏依賴；這不會減少整個原生工程的31UND。

候選WCH register名稱只作關聯，不能由此證晶片、實體晶振頻率、時鐘穩定時間、IRQABI、ROM接受或OTA相容。沒有CPU／韌體執行或模擬、沒有MMIO／硬體／網路I/O；沒有native BIN，`OTA_ready=false`。
