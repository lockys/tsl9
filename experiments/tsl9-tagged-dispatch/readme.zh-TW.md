# 標記記錄傳送候選 0x16B7C

[English](readme.en.md)

本輪以 C11／C++17 重建官方 ID2966 V4.1.60 的候選範圍 `[0x16B7C,0x16C72)`：246 bytes、86 條 RV32 指令。這是 15 個私有架構分區；C 負責常數、算術、遮罩及兩個 volatile word load，架構埠保留實體暫存器、記憶體、frame 與控制順序。分區不是可由一般 C ABI 呼叫的函式，也不是完整高階原始碼還原。

## 已確認

- 新讀 record[11]，僅接受 tag 1／2；新讀 [GP+84] 指標的 byte4，bit3 設定則無 frame 回傳 4。
- 64-byte frame 依序保存 RA、S0、S1、S2、S3；初始長度大於 8 時走完整還原。opaque call 後的長度重新讀取，不能假設初始界限仍成立。
- stack 表格為 0x30／0x40／0x50。識別碼的兩個 byte、長度、payload 引數及寫入次序依原指令保留。
- 五次直接 JAL 指向四個外部提供者；一次 C.JALR 從新讀 [0x4004C] 取目標，RA=0x16BFA。未知呼叫後重新觀察 then-live SP／S0–S3，不假設普通 callee ABI。
- busy 路徑先遞增 S1，再判斷 S1!=S3；狀態 &0x70 最後壓成 0／4。RET 後的 cold 區塊仍可達。

## 靜態驗證

`build/verified-v2/{c,cpp}/verification.json` 為本機原始收據。每種語言實際執行五個編譯、IR、讀取與部分連結步驟；15 FUNC、11 pending RELA、4 strong UND、0 global ABS。所有非重定位位元及 86 條指令的寬度、實體運算元與順序符合原 BIN。保留 pending branch/call 的機器立即值，沒有假 ABS 提供者，也未宣稱完整246-byte相等。

每種語言 132 項負向檢查：86 個原始指令改動、11 個 relocation addend 改動、30 個 IR 架構埠與5個 C scalar 改動；檢查時關閉完整 ELF／IR 雜湊比較。另有完整 ELF、IR、來源、工具、MD include closure、實際 recipes 與產物雜湊核對。負向檢查並非完整涵蓋所有 metadata／SSA wiring：定義符號的 binding 與 SSA 運算元重新接線目前依完整 ELF／IR 雜湊拒絕；scalar 清單僅核對運算種類與常數。

`probe-v1` 成功；初次 `verified-v1` 編譯成功但 checker 讀取局部 helper 時發生 `KeyError: portable`，尚未產生正式收據。修正 checker 的 helper 取得方式，原版保留在 `history/verify.pre-portable-fix.py`，來源、編譯旗標與工具鏈未改。正式 `verified-v2` 全新編譯後通過，並通過唯讀重播；strict firmware gate 如預期回傳1。

從 repo 根目錄使用既有、雜湊相符的 Windows LLVM：

```sh
python -B experiments/tsl9-tagged-dispatch/verify.py --build --out-dir experiments/tsl9-tagged-dispatch/build/local-v1 --llvm-bin "$LLVM_BIN"
python -B experiments/tsl9-tagged-dispatch/verify.py --out-dir experiments/tsl9-tagged-dispatch/build/local-v1 --llvm-bin "$LLVM_BIN"
```

輸出目錄必須全新。本輪沒有下載工具、執行目標／ISA 模擬／主機模型，或操作 BLE、CAN、UART、Flash。

## 推論與未確認

0x30／0x40／0x50、bit3 與0x70 組合支持「三個傳送緩衝控制暫存器」的研究方向；尚未證實特定外接晶片、板件型號或控制器數量。全域函式邊界與所有外部 incoming reference 亦未證實。

尚缺 0x8520、0x168DE、0x1693E 的可靠實作；0x16994 已有獨立 C 重建，但本輪未將其連入此候選物件。[0x4004C] 的實體 ROM 身分、完整 ABI、原 PC 位置、啟動／IRQ／OTA 與硬體行為仍未知。原先1162-byte整合證據保持原樣，本輪候選尚未加入該整合。

可研究新增診斷，區分 tag、全域禁用、長度、busy 與原始狀態失敗原因；本輪只提出方向，未改變原裝置行為。**未產出可燒錄 BIN，未完成逆向。**
