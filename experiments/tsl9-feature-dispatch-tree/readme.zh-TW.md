# 模式 1 分派樹：離線 C/C++ 實驗

[English](readme.en.md)

重建原廠候選 `[0x14D5E,0x1505C)` 的 766 bytes／229 指令。選用來源為 `src/tree.v1.c`，含 96 個真實架構區域；這些區域須依原始順序配置，並非可獨立呼叫的普通 C ABI 函式。

C/C++ 的實際 `build/trial-v2` 原生編譯均通過：非重定位位元完全相等，95 個重定位的型別及原廠目標相符；尚有 63 個真實外部符號。控制立即數仍未解析，沒有可燒錄 BIN 或硬體成功宣稱。此為窄範圍試驗，尚非完整正式證明。

C 負責常數與遮罩；實體 S0 載入、寄存器搬移、堆疊還原及控制轉移由架構埠表示。呼叫後使用當下 SP／S0，不假設被呼叫者遵守普通 ABI。共同返回的 RA→S0→SP→RET 次序與外部尾呼叫的 S0→RA→SP 次序分別保留。

`spec.json` 記錄區域、控制邊與證據雜湊。使用固定 LLVM／profile 在新名稱目錄進行試驗：

```sh
python -B experiments/tsl9-feature-dispatch-tree/probe-v3.py --trial trial-new
```

`trial-v1` 的編譯成功但舊 ELF reader 限制少於 64 sections，故讀取失敗；完整保留。樹的實際物件有 199 sections，本目錄 reader 僅將上限擴為少於 512，未變更舊 reader。未執行目標、ISA、HOST 模型、MMIO、硬體或網路操作。
