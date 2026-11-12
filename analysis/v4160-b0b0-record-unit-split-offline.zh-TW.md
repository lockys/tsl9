# V4.1.60 `0xb0b0`：隔離拆分 unit 的離線物件觀察

## 範圍與方法

在暫存目錄對同一份 `src/native/receive/record_helpers.c` 做兩個副本，一份完整，另一份只刪除唯一的 `tsl9_record_dispatch_provider_b0b0` 定義。以 `scripts/verify-curated-source.py` 的 `queue-consumer-a0-a5` profile 分別編譯 C11 與 C++17，各比較完整與刪除後的 RV32 ET_REL；沒有加入純 C 候選、連結或執行 target。實驗不是正式 build 或正式來源變更。

四次編譯使用 NDK Clang SHA-256 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`；每次前後核對可執行檔 hash。來源和 origin 的 SHA-256 均為 `deebd11bf4d9f852eade96fb581004ae2edbbbc14e3fbd11c5811bcd64e9e2f6`。本地來源與 manifest 有未追蹤或未提交狀態，但 GitHub commit `a17bbe64cd81345f04ce6183069be2aa88535dfc` 對應來源、origin、manifest、profile 腳本及 ELF reader 的 Git blobs 與本地相同；這不證完整 publication 可信。

## 實測

```text
c: retained facts match; removed-section RELA: []
cpp: retained facts match; removed-section RELA: []
ET_REL facts only; no link, execution, loader simulation, ABI or integration equivalence
```

比較範圍包括保留的 region 函式 bytes 與 symbols、allocated sections、剩餘 RELA 及其 target symbol 資訊。刪除區段自身沒有 RELA。保留的、未被 relocation 引用且符合特定形狀的 `$x.N`／`$d.N` assembler mapping symbol 只正規化數字後綴，仍比較類別、section、offset 和重數；其他命名 local symbol 不正規化。原先嚴格比較失敗：C 組診斷顯示保留函式、allocated sections、RELA、relocation target 資訊與 globals 相同，但 mapping symbol 流水號變動。

本機比較器的 synthetic tests 一般及 Python `-O` 模式各 14 項通過，包含匿名 section、符號身分碰撞、額外 global／weak alias、mapping symbol 越界及被 relocation 引用等負例。刪除區段的 local `STT_NOTYPE` 符號被忽略，無法區分 label 和 local alias。比較器位於本機 `experiments/v4160-b0b0-record-unit-split/`，**不包含在本次提交**；本紀錄是實測摘要，不是可獨立重播的完整驗證套件。暫存 object 已清除，未保留可獨立查驗的 ELF。

## 限制

只證固定環境下兩種語言模式的選定 ET_REL facts；不證新增候選後的連結、placement、跨單元引用、private ABI、動態行為或完整 BIN 一致。編譯器資源、系統函式庫及 headers 未逐一 pin；hash 前後檢查不排除並發替換，隔離暫存目錄不是安全 sandbox。
