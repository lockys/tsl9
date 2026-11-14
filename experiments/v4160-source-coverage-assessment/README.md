# v4.1.60 原始資料表與覆蓋口徑：本機重新驗證

這是 2026-11-15 的本機檢查紀錄，不是完整韌體驗收或新的正式來源覆蓋率。原始 decoded APP 為 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。歷史正式收據的 73,538／76,800 是當時的原位址靜態統計，不可直接視為所有後續候選的最新功能完成率。

## 表格候選

`[0x1a6a4,0x1a6b8)` 是五個相對於表格起點 `0x1a6a4` 的有號 32-bit 值，指向 `0x1452e`、`0x1453e`、`0x1454a`、`0x1473e`、`0x14748`。它目前已在 `[0x1a6a0,0x1a6b8)` 的 opaque owner 內，故將其改成具型別資料即使整合成功，**也不能再算成新增的已選原址 bytes**。前四 bytes 仍未知。

本機工作樹另有尚未加入 main 的 `experiments/v4160-typed-relative-table/`。這次以 Android NDK 27.1.12297006 LLVM 對該本地實驗重新執行：

- `verify.py`：C11 與 C++17 各比對原始 20 bytes 和五個目標，五種單項突變均被拒絕。
- `verify-overlay.py`：兩種語言的暫存診斷 ELF 各 6,267 sections，73,672 個已選 bytes 與各自既有基準一致；strict link 仍有七個未定義符號，沒有 `PT_LOAD`。符號與一個合成 consumer relocation 解析檢查通過；目標突變和重疊被拒絕。
- 該 73,672 bytes 與原始 BIN 尚有 93 bytes 不同，第一個位址是 `0x8a7f`。因此不是完整逐 byte 原廠影像，也不是可刷韌體。

以固定 SHA 的原 BIN 獨立解包五個 little-endian signed 值並加 `0x1a6a4`，確認上述五個目標；以 `0x1a6a0` 當基址則每個結果都少 4 bytes，不可混用。此前本紀錄曾誤寫為 `0x1a6a0`，現已更正。

正式整合還須共同更新來源清單與 provenance hash、`src/compact-layout.json` 的 section mapping、相關封存及下游 section-count 檢查，並重新驗證實際正式 build，而不是只重連暫存 ELF。原本 6,266 sections 拆為兩個 owner 時預期 6,267，但必須由實際產物確認；不能單純改固定值使檢查通過。

這些命令依賴**本機未提交的實驗及其工作樹依賴**；本紀錄不假裝它們已包含在 main，也不保證其他 checkout 能重播。該實驗以固定座標常數建表，沒有隨目標搬移更新的 relocation。跨 section 的舊 24-byte 符號、正式 manifest、來源封存與 carrier 稽核仍需整合及驗證；其他 linker 或所有 consumer 的相容性未知。

## 尚未解決的依賴

歷史六個 APP provider 包含 resident `0x40000`、dispatcher `0x14056` 與資料參考 `0x1ab48`、`0x1a078`、`0x1a638`、`0x1a69c`。不同實驗的條件式 alias、數值定位見證、或本機未提交 dispatcher 片段，不等於在相同正式基線中證明六者均已實作。各條件式連結的未定義符號數也不能直接與歷史六個相加或替換。實機 ROM、ABI、RAM、IRQ 與硬體行為未驗證。
