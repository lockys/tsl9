# `0xd000` 的跨版本地址碰撞：離線比較

本紀錄比較兩份固定輸入，兩者均以線性映射假設 BIN base 為 `0x8000`；不是硬體上的載入或版本證明。

- V4.1.00：`apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin`，SHA-256 `32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc`。`experiments/tsl9-contract-model/src/target_feature_init.c:6-8` 說明其版本，`experiments/tsl9-contract-model/verify-target-feature-init-native.ps1:79-82` 固定此輸入。
- V4.1.60：`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

在共同假設下，兩者 `0xd000` 均為檔案 offset `0x5000`：前者四 bytes `1385810e` 對應 `addi a0, gp, 232`，後者 `97f7ff1f` 對應 `auipc a5, 0x1ffff`。`experiments/tsl9-contract-model/src/target_feature_init.c:321-337` 的註解描述前者，不應套用到後者，也沒有依據因此修改舊版程式。

V4.1.00 `0xcff4..0xd006` 的 18 bytes 為 `b707040003a38704114681451385810e0283`。在整份 V4.1.60 檔案以逐 byte 精確搜尋，此序列只有一處命中，位於 offset `0x5196`、名義地址 `0xd196`；其對應 `addi` 在 `0xd1a2`。`src/native/receive/runtime_memory_services.c:78-91` 的重建也將此處描述為使用 `0x40048` provider slot 的尾跳 wrapper。

這是兩份固定檔案的 byte 比較及靜態對應，不證明相同 caller、provider 實作、可達性或實際記憶體效果；逐 byte 命中也不自行證明指令邊界。跨版本不可直接沿用地址或固定 layout。
