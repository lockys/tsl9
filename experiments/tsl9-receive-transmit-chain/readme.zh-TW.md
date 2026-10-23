# 接收、分派與傳送原位整合

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

直接編譯 `src/` 的 12 個 C 單位，每份來源分別以 C11／C++17 建置。未改寫演算法，也未以原廠二進位片段代替 C；兩個既有 6B／18B 函式僅用明列的預處理器名稱對應連接呼叫端，實際本體與強 FUNC 定義都保留。

- 完整部分連結：**1902B／662 指令／107 FUNC**，保留 97 RELA 與 4 個真實 UND：9454、9B36、12ABE、14D2E。五個缺失呼叫點都位於 314B queue consumer。
- 另外驗證可閉合部分：排除該 queue 單位，餘下 **1588B／555 指令／97 FUNC** 分成九段依原位址連結，所有程式位元組與 ID2966 V4.1.60 相同，無 UND／RELA／全域 ABS。沒有宣稱整個程式已閉合。
- 六次 resident 間接轉移、17 RET、兩個已界定的 fill 計算跳轉仍各有契約。零直接符號缺口不代表已知執行期目的地。RX LOAD 為 68558B，其中 66970B 是未證的間隙；ELF 不能當作可刷 BIN。

既有凍結配方與上游實際產物必須已在本機備妥；公開 JSON 不能代替原始物件。此次使用既有 Windows LLVM18／NDK27.1 工具鏈，其他平台未實測，不下載或安裝工具。

```sh
python3 "$TSL9_ROOT/experiments/tsl9-receive-transmit-chain/build-v2.py" --build --out-dir "$TSL9_ROOT/experiments/tsl9-receive-transmit-chain/build/my-run" --llvm-bin "$LLVM_BIN"
python3 "$TSL9_ROOT/experiments/tsl9-receive-transmit-chain/verify-v2.py" --out-dir "$TSL9_ROOT/experiments/tsl9-receive-transmit-chain/build/my-run" --llvm-bin "$LLVM_BIN" --write
```

新建資料夾由 builder 使用；唯讀重播使用 verifier 並省略 `--write`。`--strict-firmware` 在完成檢查後仍回傳 1，因原機／resident／IRQ／OTA 尚未證明。既有失敗 v1、舊檢查器與收據原封保留；v2 verifier 只加嚴相同產物的 metadata 與完整上游來源核對。

正式檢查包含 28 條實際命令／語言、67 個產物、所有 MD include closure、消耗物件、107 個本體、97 筆控制邊、九段完整原始位元組與所有 1217 筆 LLVM 位址列。每種語言 1538 個有限負向控制通過，獨立檢查拒絕 24／24 個來源與 PHDR 變異。

[分析、缺口及公開證據](../../analysis/receive-transmit-chain-2026-10-23/README.md)。沒有執行 HOST 模型、ISA 模擬、硬體或廠商 API，沒有新可刷 BIN。
