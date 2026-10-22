# SPI 傳輸葉函式：離線原機碼重建

[English](readme.en.md)

目前選用 [spi_transfer_ports.c](src/spi_transfer_ports.c)。C11 與 C++17 在固定 LLVM 配方下，經 [component.ld](component.ld) 連結至 `0x16896`，完整 72 bytes／25 指令與官方 ID2966 V4.1.60 的 `[0x16896, 0x168DE)` 相同，SHA-256 為 `654d0f600794c1548c617d0f476ca4f0fa5aaf780f49be7c328b3df69e8878dc`。

這是八個 C 產生的機器區域及明示架構埠，**不是可分別呼叫的一般 C ABI 函式**。C 產生常數、volatile 半字存取、截斷、遮罩與遞減；五個壓縮條件／跳躍指令由組語埠保留。每個埠先產生本地零位移指令，再由標準 ELF RVC relocation 指向真正的 FUNC。沒有複製 opcode、事後改寫物件或 ABS provider。

| 相對位置 | 區域 | 長度 |
| --- | --- | --- |
| 0 | 入口：count=255、base | 8 |
| 8 | TX 狀態讀取／mask 2 | 8 |
| 16 | 取低 16 bits、SH16、重設 count／base | 16 |
| 32 | RX 狀態讀取／mask 1 | 8 |
| 40 | fresh LHU16、取低 8 bits、返回 | 10 |
| 50 | TX 遞減／重試 | 8 |
| 58 | 共用 timeout：A0=0、返回 | 4 |
| 62 | RX 遞減／重試／timeout 跳躍 | 10 |

每階段先讀狀態，未就緒才遞減 `(count-1)&255`，各最多 255 次讀取。成功出口 A0=data&255、A3=`0x40013000`、A4=1、A5=256−RX 讀取次數；兩個 timeout 出口 A0=A4=A5=0。只寫 A0/A3/A4/A5。`__builtin_unreachable` 標示 C 區域結束，區域間的實際控制由明示分支及連結器證明的 fall-through 決定；不能把它當成一般 C 語意證明。

保留的單函式候選 [spi_transfer.c](src/spi_transfer.c) 雖同為 72 bytes／25 指令，分支排列仍不同。普通／極端機率提示都未改變產物。它不是選用版本，也不能用相同長度取代完整位元組 gate。直接跨區域的壓縮助記符會被 LLVM 展開，該候選曾被嚴格長度 gate 拒絕；明示 RVC relocation 解決的是這個組譯問題。

## 驗證

從專案根目錄執行；需要既有的 LLVM 18 工具，腳本不下載依賴。可用 `--llvm-bin` 指定工具目錄，輸出目錄必須尚未存在：

```sh
python3 -B experiments/tsl9-spi-transfer-leaf/verify.py --language c --out-dir experiments/tsl9-spi-transfer-leaf/build/my-check/c
python3 -B experiments/tsl9-spi-transfer-leaf/verify.py --language cpp --out-dir experiments/tsl9-spi-transfer-leaf/build/my-check/cpp
python3 -B experiments/tsl9-spi-transfer-leaf/verify.py --replay experiments/tsl9-spi-transfer-leaf/build/my-check/c/verification.json
```

Windows 可使用 `python` 取代 `python3`。本次正式輸出為 `build/verified-v3/{c,cpp}`：每種語言 2 個實際 ELF、8 個輸入、5 份配方、10 個產物、36 項負例檢查；兩份收據唯讀重播均通過。加上 `--require-firmware-ready` 會以 exit 1 拒絕，這是預期的未就緒 gate。[公開收據](../../analysis/spi-transfer-native-2026-10-23/receipts/)是逐位元組相同的路徑變數化原始收據；本機 ELF／IR／MD／日誌不隨收據一起公開。

[pipeline.ld](pipeline.ld) 用於 352-byte **可重定位部分連結**；其零起點是診斷配置，不是原機 Flash 配置。原有 280-byte 管線的 SPI 呼叫可綁到真實定義，但 packet provider、完整原機執行鏈仍須驗證。

未執行目標、ISA 模擬、MMIO、BLE、CAN 或燒錄，亦未產生韌體 BIN。實體晶片、周邊身分、完整 IRQ／fault 上下文、resident／啟動與 OTA 相容性仍未證實。
