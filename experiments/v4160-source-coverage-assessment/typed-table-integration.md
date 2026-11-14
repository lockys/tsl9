# 型別化相對表整合與歷史證據邊界

`src/native/receive/opaque_allowed_gaps.c` 將原 `[0x1a6a0,0x1a6b8)` 分成 4-byte opaque prefix 和五個 `int32_t` 相對值；基址為 `0x1a6a4`。五個目標是 `0x1452e, 0x1453e, 0x1454a, 0x1473e, 0x14748`。這是固定座標，沒有連結至目標符號的 relocation；移動目標時不會自動更新。20 bytes 原先已由 opaque carrier 擁有，不增加覆蓋率。

舊 24-byte `tsl9_opaque_gap_0001a6a0` alias 綁定 prefix section，在此 LLD 診斷布局跨越兩個相鄰 section；不宣稱對其他 linker 或所有消費者相容。`scripts/relative_table_owner.py` 檢查 section、值及符號（包含 section index）。用下列命令對完整候選建置所產生的兩個診斷 ELF 執行變造負向測試：

```text
python -I -B scripts/test_relative_table_owner.py --build <candidate-build-output>
python -I -OB scripts/test_relative_table_owner.py --build <candidate-build-output>
```

這次整合不改寫歷史封存。以下驗證器固定舊版來源或 layout hash，在新樹拒絕是預期的版本邊界，不可直接更新 hash 後聲稱歷史結果重新驗證：

- `experiments/v4160-d472-event-alias-bounded/audit.py`
- `experiments/v4160-105c4-release-link/replay.py`
- `experiments/v4160-105c4-callers-bounded-next/scan.py`
- `experiments/v4160-105c4-six-section-published-split/probe.py`
- `experiments/v4160-beeb-bounded-compact/verify.py`

這些工具應以原紀錄的輸入快照重播；例如 Git commit `efb57145a2c9c0f73fa53dbf40a9fb2ca2fcf563` 的來源快照可重播第一個 audit。這只是對該舊快照的驗證，不能作為整合後驗證器的通過結果。

`scripts/verify-source-layout.py` 是另一條以歷史物件推導 section 座標的舊驗證路徑。後續在本機忽略追蹤的建置目錄找到其固定 SHA-256 的歷史物件與 linker script，複製至隔離來源快照後重播：C/C++ 均通過，分別比對 6,235 sections、73,551 bytes，嚴格連結各有 7 個未定符號、診斷 ELF 無 PT_LOAD。該歷史選取未包含新表及其他後加的 opaque 區域；此通過結果不能代替檢查含表的 73,672-byte compact layout，也不等於可刷韌體。這些被忽略的歷史物件不包含於來源提交；缺少時仍不能重播。

候選映像與整合前基準一致，不等於完整原廠映像或硬體功能等價。未驗證 resident ROM、RAM 佔有、實機或刷寫安全。
