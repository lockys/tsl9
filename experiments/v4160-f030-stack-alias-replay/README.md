# F030 保存槽位址交集：離線重播

此實驗重播 `analysis/v4160-f030-stack-alias-bounded.zh-TW.md` 的有界算術，使用同一參考 BIN；不執行或模擬韌體。從 repo 根目錄執行：

```text
python -I -B experiments/v4160-f030-stack-alias-replay/verify.py --test
python -I -B -O experiments/v4160-f030-stack-alias-replay/verify.py --test
python -I -B experiments/v4160-f030-stack-alias-replay/verify.py --inspect
```

固定完整 BIN 的長度、SHA-256 與十處原始 bytes。檢驗三個假設寫入位址對三種原始保存槽的九組 entry SP 集合、交集及 alignment 篩選。測試以 8-bit 環完整窮舉，以及實際 32-bit 指定位址附近和 wrap 邊界的正向枚舉，與反解公式比對；每個 anchor byte、長度、非 anchor byte 和錯置槽名稱有負例。以測試專用變更後 digest 隔離 anchor guard，並不更改 inspect 所用 pin。這不是窮舉全部 32-bit 位址，也不檢查完整指令語義或所有寫入者。

所有 SP 均指 `0xf016` 配置 16-byte frame 前的入口 SP；呼叫後 SP 是否維持未知。F030 位址依賴 EE9A 返回時保留 `s0`，F03A 依賴 BD46 正常返回；alignment 只是額外假設。原始指令邊界及 BIN base `0x8000` 為假設，不證可達、成功存取、保存槽內容不變、ABI、RAM owner 或完整 BIN。
