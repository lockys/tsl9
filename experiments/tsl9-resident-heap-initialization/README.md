# Heap 初始化候選 C/C++

[English](readme.en.md) · [配置／釋放候選](../tsl9-resident-heap-core/README.md)

本輪重建公開 WCH SDK V1.31 的 **148 bytes／49 條指令**，不是可刷韌體，也未確認實機 ROM。

| 候選 Flash 本體 | bytes | 用途 |
| --- | ---: | --- |
| `0x430E0..0x43104` | 36 | 遍歷候選 heap 串列並累計可用區塊大小 |
| `0x43104..0x43174` | 112 | 建立小／大區段、sentinel，呼叫前者計算可用量 |

[C/C++ 來源](resident_heap_initialization.c)有 10 個正尺寸 FUNC、5 筆重定位、5 條條件式 Xwchc 指令埠。C11／C++17 物件相同，還原原始位址編碼後全部 bytes 吻合；兩個獨立 ELF reader 亦一致。[原始指令](evidence-v1.json)與[實際編譯收據](native-proof-v1.json)供核對。

## 設定與界限

候選讀取 `0x200031EC` 設定中的 `MEMAddr`／`MEMLen`，第一個節點為 `MEMAddr+544`，大小區段分界為該節點加 `min(MEMLen>>3,512)`，sentinel 為 `MEMAddr+MEMLen-8`。大小以 halfword 儲存；本 helper 本身不驗證輸入範圍、實體 RAM、串列終止或所有權。

[官方標頭 ABI 編譯斷言](config_abi.c)在 RV32 C11／C++17 均通過：結構 64 bytes、對齊 4、`MEMAddr`／`MEMLen` 位移 0／4、`staCB` 位移 52。候選基址加 52 對應先前配置器的 callback 儲存位置 `0x20003220`；**尚未證明 callback 的值或實際呼叫**。ABI 斷言物件沒有配置任何 runtime bytes。

[既有 APP 重建來源](../../src/native/startup/resident_startup.c)把設定記憶體長度設為 `0x7000`（28 KiB），並經 `0x400A4` 指標呼叫；實機的 ROM、設定複製完整呼叫鏈、記憶體配置及 IRQ 契約仍待核對。此模組尚未與上一輪物件或 APP 連結。APP 正式 byte 覆蓋維持 **95.54%**，不是功能完成度。

## 本機驗證

使用 [spec-v1.json](spec-v1.json)固定雜湊的 Windows NDK LLVM，從專案根目錄執行；`LLVM_BIN` 為工具目錄，trial 名稱必須不存在：

```sh
python experiments/tsl9-resident-heap-initialization/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
```

已有產物時以 `--replay experiments/tsl9-resident-heap-initialization/build/native-v1` 取代 `--trial native-v1`。只交叉編譯與讀檔，沒有執行目標／HOST 模型／ISA 模擬、連接硬體或產生 BIN。

可考慮新增 heap 用量與配置失敗診斷；目前僅列為候選，須先驗證實機 RAM、callback 與 IRQ 所有權。
