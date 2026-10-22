# callback 保存指令的有限重排

[English](readme.en.md)

本步驟只處理真實 C/C++ 編譯得到的單一 `FUNC624` ET_REL 物件：將開頭 offset+2 的 `SW RA,44(SP)` 與 offset+4 的 `SW S0,40(SP)` 兩個既有 2-byte word 交換，使十一個 stack store 的相對順序與原碼一致。它不製造指令，不讀取原始 BIN 作為產生程式碼的模板，也不補上剩餘 8 bytes。

套用前必須核對 48-byte frame、全部十一個 register／slot、唯一真實 GLOBAL FUNC624、獨立 code section、零 REL／RELA、沒有區域內符號，以及 header／section／檔案儲存範圍沒有重疊。交換後，指定四個檔案 bytes 以外的所有 ELF bytes 都必須完全一致；symbol、section 與 relocation metadata 不改寫。

## 明確的證據範圍

原始 callback 在第一次 S0 store 之前，還有一條 SLLI A5 的 4-byte 指令；新元件的其他暫存器操作與呼叫位置也不同。**本檢查只證明保存指令的相對順序，不證明完整入口 prefix、ROM 呼叫／返回 ABI 或 placement。** 624 小於 632 只是數值條件，不能把剩餘 8 bytes 自行當成安全 padding，也不產生可刷寫 BIN。

```sh
python3 -B experiments/tsl9-v4160-callback-registers/postpass/frame.py --project-root /absolute/re-tsl9 --input /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new/raw.o --output /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new/ordered.o --receipt /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new/frame.json
python3 -B experiments/tsl9-v4160-callback-registers/postpass/frame.py --project-root /absolute/re-tsl9 --replay /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new/frame.json
```

三個路徑必須互異並位於本 model 的 build 內；輸出只能新建。重播直接重讀兩份實際物件，依相同規則重新計算交換，逐 byte 比對；不執行或模擬 RISC-V，也不使用既有 IRQ／Flash／TX 排序器的擴充例外。
