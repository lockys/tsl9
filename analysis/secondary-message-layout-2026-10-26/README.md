# 次要訊息候選：原位址與靜態流程

本頁為候選階段快照；兩個單元已正式收錄 SRC，完整來源與新原位址證據見[整合報告](../secondary-message-integration-2026-10-26/README.md)。

[English](readme.en.md) · [驗證摘要](summary.json) · [CODE C/C++](../../experiments/tsl9-secondary-message-dispatch/secondary_message_dispatch.c) · [DATA C/C++](../../experiments/tsl9-secondary-message-data/src/secondary_message_data.v1.c)

已將合併候選放回原始位址，**72,610／76,800 bytes＝94.54%** 與官方 ID2966 V4.1.60 對應位置完全相同。這是尚未收錄 `src/` 的候選位址 bytes 覆蓋率；正式數字維持 **70,522 bytes／91.83%**，不是功能完成率或硬體相容性證明。

| 已確認項目 | 實測結果 |
|---|---|
| 原位址 CODE／DATA | 68,648／3,962 bytes，6,174 個正長度 owner、48 個僅相鄰合併的 span |
| C11／C++17 診斷 ELF | 內容雜湊相同，全部 5,215 個重定位角色保留 |
| 指令與直接轉移 | 23,314 條指令；4,576 個直接轉移 |
| 順序／呼叫返回位置 | 一般順序缺口 0；1406 個返回位置皆有實際 CODE |
| 受限跳表 | 13 個；新增七格事件表對應六個實際 CODE 入口 |
| 來源位址 | 新增兩組 DATA HI/LO 與五組 callable 位址均指向實際正長度物件 |
| 獨立解析 | 逐欄比較 ELF header、節區、全部 file-backed bytes、symbol 與 relocation，均相同 |

原合併來源有 828 個 ELF 節區，超過舊 v3 讀取器的 512 上限，因此新版本明確使用已核對的 v5（上限 2,048）；沒有改寫舊驗證版本。只排除八個精確列出的、未被引用且位於非 ALLOC `.comment` 的編譯器標記，不排除執行內容。

通用末端掃描仍列出 `0x8034` 的原始 EBREAK → `0x8038` vector DATA；專用流程檢查將它辨識為 trap，不當成一般順序跳轉。trap handler／resume target 尚未證明。905 個 register-indirect 轉移包含 RET；它們的實際執行目標與全域可達性並未因此全部證明。

六個編譯器 UND 與四個 literal-only 相依維持明示。既有 `0x1AAE8` 查表仍無全域索引界限證明，不能以 UND 數量代表全部執行缺口。鄰近 padding、`0x14056` 私有 body 與受保護 default payload 均未補入或以假 stub 代替。

## 本機重現

先按 [DATA／部分連結階段](../../experiments/tsl9-secondary-message-data/README.md) 建立輸入。設定 `LLVM_BIN` 指向 spec 所列 LLVM `bin`，再從 repo 根目錄首次建立：

```sh
python experiments/tsl9-original-layout/build-v63.py --tool-dir "$LLVM_BIN" --trial secondary-message-v1
python experiments/tsl9-original-layout/verify-flow-v63.py --trial secondary-message-flow-v1
```

既有目錄不可覆寫；核對保留物件時，改用相應的 `--replay experiments/tsl9-original-layout/build/<trial>`。本輪公開文字來源、檢查器與收據摘要，不新增上傳 ELF／`.o`／BIN。

診斷 ELF 的 entry=0、PT_LOAD=0，六個未實作目標僅是隱藏的 NOTYPE reference constants，沒有 ABS FUNC provider。**未產出可刷寫 BIN**，未執行目標、HOST model 或 ISA 模擬，也未接觸硬體或廠商 API。原機啟動、ROM ABI、RAM／IRQ、藍牙與 OTA 相容性仍待證明。

下一步是收錄兩個候選單元到 `src/` 並獨立驗證整體來源閉包，再調整正式覆蓋率。離線事件／相依瀏覽器可作為新增工具的方向，目前並未增加硬體功能。
