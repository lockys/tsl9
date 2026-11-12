# v4.1.60 `0x12e86` 有界事件候選

僅離線靜態分析；這不是可部署韌體，也不宣稱執行過 C 或與硬體等價。原始映像 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，映射基址 `0x8000`，函式範圍 `[0x12e86,0x12ee6)`。

以工具索引所列 `C:\Users\locky\Tools\radare2\bin\r2.exe` 唯讀執行 `-q -n -a riscv -b 32 -m 0x8000 -c "e scr.color=false; pd 42 @ 0x12e86" <映像>`；完整函式末端在 `0x12ee2` 的跳轉，之後是另一函式。`auipc s0` 以其自身 PC `0x12e90` 計算得到基址 `0x2000c494`。

函式先讀取 word `[0x40048]`，接著以 `jalr` 呼叫 `(slot & 0xfffffffe)`，參數為 `(0x2000c494, 0, 256)`。slot 值與被呼叫者任何讀寫、副作用、返回值均未知，不能假設它清零了記憶體，也不能假設 target 有效。call hook 須在正常返回且保留供後續使用的 s0、s1、gp、sp 時回傳非零；否則候選立即停止，不發出後續直接 store 或 tail。這是有界假設，不是對任意破壞 ABI 的執行之模擬。

成功返回後，直接資料寫入按指令順序如下（不是按地址順序）：

| PC | 相對 s0 | 寬度 | 數值 | little-endian 記憶體 bytes |
|---|---:|---:|---:|---|
| 12ea8 | ff | 1 | 5a | 5a |
| 12eb4 | 00 | 4 | 0b431402 | 02 14 43 0b |
| 12ebe | 04 | 4 | 0d450c44 | 44 0c 45 0d |
| 12ec8 | 08 | 4 | 2b0c2c0a | 0a 2c 0c 2b |
| 12ed0 | 0c | 4 | 5f1f501e | 1e 50 1f 5f |
| 12eda | 10 | 4 | 2a211e20 | 20 1e 21 2a |

這些事件以數值和寬度表示，不依賴執行候選的主機 endianness。除 slot 讀取外，函式本身還在 stack 儲存並讀回 s0、ra；候選刻意不模擬 stack 指令、故障、非正常跳轉或 hook 自身副作用。此處假設 stack 有效，保存槽不與觀察資料或 callee 可寫記憶體別名、且未被破壞；在此條件下原函式恢復 s0、ra、sp 後以無連結跳轉 tail 到 `0x12e54`；候選只發出 tail 事件，沒有執行該函式，亦不聲稱知道其入口的 volatile 暫存器值或後續副作用。

`candidate.c` 的 hooks 都必須非空；它不直接解參考目標地址。`test_candidate.py` 比對固定映像雜湊、完整函式原始 bytes、C 中可解析的直接 store 與獨立期望值，並以 Python 事件模型測試正常、失敗、低位遮罩和反例。這些是靜態與模型測試，不是 C 的編譯或執行證據；即使 C 檔案雜湊一致也不能證明 C 行為。執行：

```
python -B test_candidate.py
python -B -O test_candidate.py
```
