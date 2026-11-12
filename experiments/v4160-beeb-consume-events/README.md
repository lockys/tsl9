# V4.1.60 `0x2000beeb` 局部 byte 事件模型

以 `experiments/v4160-beeb-consume-evidence/` 的靜態證據為起點，重新只讀核對 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`：76800 bytes、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，raw image VA base `0x8000`。本機唯讀靜態反組譯：

```text
C:\Users\locky\Tools\radare2\bin\r2.exe -n -a riscv -b 32 -m 0x8000 -q -c "e scr.color=0; pd 22 @ 0xae9e" <BIN>
```

固定 window `[0xae9e,0xaecc)` 包含 `0xaec8` 完整指令；測試中是獨立的 bytes literal，不從被測 image 或先前 verifier 生成。全檔 hash/長度與 window 均有負例，window 每個 byte 翻轉及每個截斷點分別直接驗證。

## 靜態推導與模型邊界

`0xae9e` AUIPC 和 `0xaea2` LBU 算出 `0x2000beeb`；`0xaeb4` AUIPC 和 `0xaeb8` SB 也算出同一地址。事件有序、每項為 `(指令位址, read/write, u32位址, byte值)`：

1. `0xaea2` 讀 x。x=0 直接到 `0xaebc`；x≠0 才依序 `0xaeac` 寫 6 到 gp+188、`0xaeb0` 寫 `(x+3)&255` 到 gp+189、`0xaeb8` 寫 0 到來源。
2. `0xaebc` 再讀 gp+188，不能沿用先前的 6。若為零，出口 `0xaf48`；非零則 `0xaec4` 寫該次讀值減一，再於 `0xaec8` 讀 gp+189，出口 `0xaecc`。後續操作不在模型中。

地址加法以 u32 wrap；所有位置共用同一 byte dict，因此 `gp+188` 或 `gp+189` 均可與來源 alias。前者 alias 時來源清零使第二次讀值為零；後者 alias 時最後一次讀取看到清零。模型只讀被實際存取的位置，缺值報錯；寫入在 dict 中建立位置。輸入 gp 必須為 u32，讀入值必須為 byte。

假設各 byte 存取正常完成、一般記憶體且執行期間沒有中斷、DMA、其他執行緒或其他非同步介入；這不是原子 read-and-clear，不能推出真實系統恰好一次消費或後續 byte 值。沒有 MMIO、副作用讀寫、故障、指令取得、時間、memory model 或外部呼叫模型；本切片不證明入口可達、gp 的 ABI 已達成、記憶體有效或指令實際執行。這是手工導出的 Python 事件關係，**不執行或模擬 target**，亦不執行 C、編譯或使用硬體。

## 測試

```text
python -B experiments/v4160-beeb-consume-events/test_model.py
python -B -O experiments/v4160-beeb-consume-events/test_model.py
```

測試 x=0、1、253、254、255，初始 gp+188=0、1、255，兩種來源別名、gp=`0xffffffff`、完整 read/write trace、錯誤輸入，以及固定 image 的正反例；unittest 檢查不依賴會被 `-O` 移除的 assert。
