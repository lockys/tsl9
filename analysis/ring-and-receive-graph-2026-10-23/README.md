# Ring 與接收鏈原位驗證

[English](readme.en.md)

官方 ID2966 V4.1.60 的 ring 寫入已整理至 [src/native/receive/ring_insert.c](../../src/native/receive/ring_insert.c)。這是 C／C++ 搭配明示架構 ports 的重建，並非還原原始碼或一般 C ABI。**尚未完成逆向，不能當成可燒錄韌體。**

| 本輪證據 | 實測結果 | 範圍限制 |
| --- | --- | --- |
| Ring v3 | C11／C++17 原位連結完整 92B／32 指令相同；每語言 40 個負例 | 動態 resident 呼叫與保存契約未知 |
| 接收鏈 partial link | 494B／178 指令、19 FUNC、23 筆待解析 relocation；每語言 48 個 raw-ELF 負例 | 22 筆綁定真實定義，唯一 UND 為 ring；機器立即數仍未解析 |
| 七段原位連結 | 586B／210 指令、24 FUNC、26 處 symbolic control 全部解析；每語言 86 個 raw-ELF 負例 | 僅七段程式相同；載入間隙與完整韌體未證 |
| `src/` 整理驗證 | 51 個 C/H、25 個編譯入口、50 組比對、100 個物件 | 本機 LLVM18；未執行目標程式或舊 HOST 測試 |

Ring 的五個區域位於 `[0x12BC8,0x12C24)`。PC `0x12BD2` 參與計算佇列基址 `0x2000C038`，不能任意重定位。32 格各 12B；先寫 ID16／length8，再新讀 `LW32[0x0004004C]`，以 A5 間接呼叫；A1 與完整 A2 傳入。呼叫後 tag 寫入使用當下 S0／S1。指標、長度邊界、callee 身分及保存契約未證。v1 因保留 SP 編譯失敗；v2 的 provider 位址暫存器錯誤；兩者均保留，未混入 v3 成功結論。

七段為 ring92、SPI72、register-read72、register-write76、packet142、receiver70、flag-consumer62B。各段在原廠位址的所有位元組均相同，串接 SHA256 為 `ea0695de5c5abe95f730285256d89dd5e63f265b7d83f5a70687e08f6e4e828f`。**ELF 的 RX LOAD 共 17,528B，其中 16,942B 間隙未驗證，不能轉成平面 BIN 燒錄。** 無 UND／RELA 只代表這 26 個 symbolic sites 已解析；`0x12C0C` 的動態 resident 呼叫仍未知。

驗證入口（使用本機既有 `LLVM_BIN`；Windows 可用 `python`）：

```sh
python3 -B experiments/tsl9-ring-insert/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-ring-insert/build/verified-v1/c/verification.json
python3 -B experiments/tsl9-packet-receive/verify_pipeline.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-packet-receive/build/pipeline-verified-v2/c/verification.json
python3 -B experiments/tsl9-ring-insert/verify_receive_graph.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-ring-insert/build/receive-graph-verified-v1/c/verification.json
```

本輪 C／C++ replay 均 exit 0。加上 `--require-firmware-ready` 會拒絕（exit 1）。重播需要原始本機 build artifacts，公開 JSON 並不包含編譯物。新建 build 的方式見 [ring 實驗](../../experiments/tsl9-ring-insert/README.md)。

公開收據與隱私：

- [summary.json](summary.json) 記錄各來源、checker 與收據雜湊。
- `receipts/ring-{c,cpp}.json`、`pipeline-{c,cpp}.json`、`graph-{c,cpp}.json` 是本來就採變數路徑的原始 LF 收據，公開副本逐位元組相同。
- [curated-source.json](receipts/curated-source.json) 是匿名衍生 JSON；本機原件保留於 `build/curated-source/ring-20261023-v1/verification.json`。只替換路徑字串與字典鍵為 `${PROJECT_ROOT}`／`${LLVM_BIN}`／`${CLANG_RESOURCE}`，反向替換 JSON 與原件相等。保留原件 SHA256，但不宣稱衍生檔可按原件雜湊直接 replay。歷史原始收據與 BIN／APK 未改寫。

下一段離線研究見 [next-boundary.md](next-boundary.md)：IRQ adapter 52B 與 queue consumer 314B 尚未重建。ID0 同時被當空槽的表示衝突是值得查證的功能線索；未證實實機掉包，也未修改格式。

未執行目標／ISA／MMIO、BLE／CAN／UART／Flash；未下載工具鏈、操作硬體或第三方 API。完整 startup／resident ABI／IRQ／記憶體所有權／晶片／OTA 相容性仍未證明。本輪沒有產生完整韌體 BIN。
