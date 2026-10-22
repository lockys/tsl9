# 原始最後 8 bytes 不是 padding

[English](readme.en.md)

新元件為 624 bytes，原 callback 範圍 `0x8614..0x888C` 為 632 bytes。如果從原入口配置新元件，數值上會留下 `0x8884..0x888C` 的 8 bytes；這不代表它們可以保留、清空或補齊。

`check.py` 核對官方 ID2966 韌體的 SHA-256，使用已固定的原始指令解碼器逐一讀取三條指令：`0x8884` 是透過 A5 的間接呼叫（返回 `0x8886`），`0x8886` 是 `A0 = S0 XOR 8`，`0x888A` 跳至 `0x866C`。它們屬於原本可執行的呼叫／返回路徑，不是已證明未使用的儲存空間。證據摘要保存在 [original-tail.json](original-tail.json)。

```sh
python3 -B analysis/v4160-callback-registers-2026-10-22/tail-plan/check.py --project-root /absolute/re-tsl9 --firmware /absolute/re-tsl9/firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

本檢查只讀取原始檔案，不產生替代指令、填補 bytes 或輸出 BIN；它沒有執行或模擬韌體。原始尾區的完整所有權、控制流與 ROM 返回 ABI 尚待閉合，因此新元件仍不允許 placement。
