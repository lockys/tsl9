# 計時函式的原機暫存器契約

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

以可讀 C 重建官方 ID2966 V4.1.60 的 `[0x19764,0x1979A)`。C11 與 C++17 的完整函式均為 **54 bytes／22 指令**，object 與獨立連結後的函式皆逐位元組等於原 BIN。已將相同來源放入 [src/native/timer/delay.c](../../src/native/timer/delay.c)。

## 實作與契約

volatile 讀寫、乘法、位元運算及輪詢均為 C；inline asm 僅作固定暫存器／live GP 介面，以及在第一次 fresh read 後將 A3 設零的常數輸出。沒有複製原指令串、裸函式或外部常數 provider。

令 B=0xE000F000，順序為：

1. fresh R32(B+4)，然後 A3=0，清 bit0 並寫回。
2. fresh R8(live GP+382)，乘上完整入口 A0，取低32位寫 B+16；零寫 B+20。
3. 對 B 各做一次 fresh R32／OR 0x10／W32 與 fresh R32／OR 0x21／W32。
4. 反覆 fresh R32(B+4)，直到 bit0=1；最後 fresh R32(B)，清 bit0 並寫回。

正常出口 A0／A1 不變、A2=乘積、A3=0、A4=最後 CTRL 清 bit0、A5=B。唯一被寫入的 GPR 是 A2／A3／A4／A5；沒有 frame、call、CSR 或 fence。首次讀取 fault 時 A3 尚未清零；GP byte read fault 時 A2 尚未改寫。完整機器碼相同支持這個函式內的指令順序，不證明整機 fault／IRQ 環境相同。

原始碼回傳型別僅描述 C 的 A0 return。其他暫存器契約依賴本配方與實際產物，未自動傳遞到任意 C 呼叫端。此葉函式是獨立 translation unit；尚未替換 NV callback 內的舊 timer，亦未整合到 OTA BIN。

## 離線驗證

在專案根目錄執行，明確指定已安裝的 LLVM 與原始 BIN：

```sh
python3 experiments/tsl9-delay-register-contract/verify.py --project-root . --tool-dir "/absolute/path/to/llvm/bin" --firmware "/absolute/path/to/ID-2966-V4.1.60-decoded.bin"
```

Windows 可改用 `py -3`／`python`。目前實測為 Windows 的 Android NDK27.1.12297006／LLVM18；工具與 stdint hash 必須符合配方，其他平台未實測。Shell wrapper 只轉交同一 Python 入口，未在此 Windows 會話執行。

```sh
python3 experiments/tsl9-delay-register-contract/verify.py --project-root . --replay "/absolute/path/to/build/native-v3/c/verification.json"
```

最新本機收據為 `build/native-v3/{c,cpp}/verification.json`。檢查完整 FUNC、精確 allocated sections／flags／types、UND／global ABS、relocations、實際 compiler dependency closure、工具／來源 hash、命令與日誌，再唯讀重播。IR 留存供複核，checker 不將它當成另一次語意證明。GPR／存取結論來自原始列與完整機器碼相同。

| 產物 | 函式 bytes | 總配置 bytes | 備註 |
| --- | --- | --- | --- |
| C object／linked | 54 | 54 | 無 relocation，函式 VMA=0 |
| C++ object | 54 | 94 | .eh_frame=40，3個 unwind relocation |
| C++ linked | 54 | 98 | .eh_frame=44，函式 VMA=0x2C，無 relocation |

VMA=0／0x2C 僅為離線比較配置。第一版 `native-v1` 曾將 A2 提早用作 scratch，58B／24指令，因此失敗；其輸出保留。修正 A4 的 read/write register barrier 後 `native-v2` 已 code-exact，後續強化 verifier 得到 `native-v3`。舊版本收據屬歷史快照，不以新版 verifier 宣稱可重播。

## 仍未證明

實體晶片、GP 初始化先後與 scale 時間單位、完整中斷／記憶體配置、原機 ROM／BOOT、NV callback 的 frame／source slot，以及整機啟動仍未完成驗證。原函式無 timeout，此重建保留原輪詢條件。工具只編譯、連結和讀取檔案，不執行 RV32／MMIO，不產生韌體 BIN，也不操作硬體或網路。
