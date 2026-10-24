# 常駐程式啟動與 ROM 設定

[繁體中文](README.md) · [English](readme.en.md)

新增八個完整函式，共 **1,082B／385指令**，另有21B公開版本前綴資料。兩個舊啟動入口已有真實程式碼，同時暴露22個 ADC／時鐘／MAC／延遲依賴，剩餘165個。本輪沒有產生韌體 BIN，也沒有存取硬體。

| 靜態證據 | 結果 |
| --- | --- |
| 獨立 C11／C++17 | 物件相同；74個程式區域、21B唯讀物件、66 RELA、52個直接控制重定位、七組型別化位址引用 |
| 整理後來源 | 129個 C/H；204組函式／程式單元比較＋2組獨立資料比較＝206組／412個物件 |
| 主元件 | 38,454B code＋1,771B data；13,408指令；3,193 FUNC、71個零大小別名、14個唯讀物件、2,534 RELA |
| 原始位址 | 40,225個已選 bytes 全部與官方 BIN 相同；3,207個擁有者，112段僅合併相鄰區域的配置 |
| 跳轉 | 2,250個直接跳轉；817個呼叫返回位置；一般接續位置缺口為零 |
| 語意見證 | 201項明列指令、8項位址計算 |
| 獨立 SDK 候選 | 另編譯兩個240B描述資料物件；無 FUNC／重定位／匯入，未連進主元件 |

映像會拿1AB1C處的21 bytes **CH32V20x_BLE_LIB_V1.3** 比較版本。這確認了程式預期的函式庫前綴，也支持 CH32V20x 系列候選；實體 MCU／封裝型號與安裝中的 ROM 版本仍未確認。

已確認的指令行為：

- 199E2 保留版本結果停留迴圈19A08、重新讀取 heap 指標／長度後的檢查迴圈19AE0，以及初始化結果迴圈19AF0，沒有略過檢查。
- 它在SP+16建立64B設定，包含 heap 位址2000418C／長度0x7000、SNV位址0x08077C00、打包值0x0803與0x0E3F、長度251、事件數3，以及頻率／精度欄位16000／1000。另將六個動態暫存 bytes 複製到位移24；沒有讀取裝置 MAC。
- 回呼指向1979A（讀取）、197BE（寫入）、197F0（取樣）、197B8（校正）。這些是保存 header 的候選名稱，安裝中的實作與私有 ABI 尚未證明。
- 1979A 將 word 數量左移兩位後交給 ROM 槽位76複製。197BE 保留18EF2呼叫中，將入口A2保存值同時放入A1與A2的原始行為，沒有宣稱或修補 SDK 回呼 ABI 相容性。
- 197F0 保留編碼中的 RCC／周邊暫存器備份與還原欄位，以及原始輪詢迴圈。1995C 保留15／0／13／14事件優先序、完整寬度事件 XOR 結果、訊息處理與排程參數。
- 19B16 註冊1995C、保存回傳的工作 byte，再呼叫19B56；後者建立16B候選時鐘設定並保留設定呼叫順序，最後呼叫槽位116。既有 RTC 中斷19BD4未重建或改動。

獨立的原生唯讀資料編譯確認：保存 SDK 的 `bleConfig_t` 大小64、`bleClockConfig_t` 大小16、對齊4，所有欄位位移／寬度符合；18處原始堆疊寫入（含壓縮式 C.SWSP）與六 byte 複製迴圈也吻合。兩個描述物件與主來源206組／412物件分開計算，沒有執行 SDK 函式。

程式使用暫存器綁定 C 與明確架構操作。實體晶片、ROM內容、heap保留區、RAM／Flash容量、非同步 ABI／中斷綁定、時鐘單位與藍牙 OTA 相容性仍未證明。原有 opaque 預設資料與20個靜態內容引用尚未提供；完整驗證函式保持私有且未解決。診斷 ELF 的 entry 為0，沒有 PT_LOAD。

[指令／資料證據](evidence.json) · [合約](provider-contracts.json) · [量測摘要](summary.json) · [剩餘依賴](next-providers.json) · [功能候選](feature-candidates.json)

[整理後來源](../../src/native/startup/resident_startup.c) · [原生配方](../../experiments/tsl9-resident-startup/spec-v1.json) · [來源驗證](../../experiments/tsl9-resident-startup/verify-source-v1.py) · [整合配方](../../experiments/tsl9-resident-startup/integration-v1.json) · [位址配置](../../experiments/tsl9-original-layout/spec-v32.json) · [流程驗證](../../experiments/tsl9-original-layout/verify-flow-v35.py) · [SDK配置配方](../../experiments/tsl9-resident-startup/sdk-boot-layout-v1.json)

在 repo 根目錄，使用既有且符合雜湊的本機工具與保留收據：

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v35.py --replay experiments/tsl9-original-layout/build/resident-startup-flow-v1
python3 -B experiments/tsl9-resident-startup/verify-sdk-boot-layout-v1.py --tool-dir "$LLVM_BIN" --sdk-header "$SDK_HEADER" --replay experiments/tsl9-resident-startup/build/sdk-boot-v1
```

`LLVM_BIN`、`SDK_HEADER` 由使用者指定本機路徑。原始收據、保存的 SDK header 與已取代試驗留在本機；未執行目標、host model、ISA模擬或燒錄。
