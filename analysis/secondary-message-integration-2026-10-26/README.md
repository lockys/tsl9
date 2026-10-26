# 次要訊息：SRC 正式整合

[English](readme.en.md) · [驗證摘要](summary.json) · [證據](evidence.json) · [未解相依](provider-contracts.json)

九段原始上下文 CODE 與兩個 DATA 物件已收錄至 `src/`。正式位址 bytes 覆蓋率更新為 **72,610／76,800＝94.54%**：68,648B CODE＋3,962B DATA；這不是功能完成率或可刷入比例。

- 158 個 C/H 檔，124 CODE／八 DATA 單元；C11、C++17 合計 264 項比較、528 個實際物件通過。
- 原有 156 個來源檔、246 項 CODE 結果與 1,477 個 artifact 雜湊不變；凍結驗證器未修改。
- `src/` 合併檔與原位址配置保留全部 5,215 個重定位角色、71 個真實 CODE alias、六個真實 DATA label。
- 23,314 條指令、4,576 個直接轉移、1,406 個呼叫返回位置、13 個受限跳表完成靜態核對，一般順序缺口為零。

[次要訊息／分派 C/C++](../../src/native/receive/secondary_message_dispatch.c) 保留原始 register、stack、ROM 與控制轉移 ports。[DATA C/C++](../../src/native/receive/secondary_message_data.c) 只提供七格事件表與明確的 12-byte 複製來源，不補鄰近 padding。七格對應六個實際 CODE 入口；兩組 DATA 與五組 callable HI/LO 位址均有正長度實際內容。

六個編譯器 UND 仍未提供，另有不在 UND 清單內的 `0x1AAE8` 查表尚無全域索引界限證明。905 個 register-indirect 轉移包含 RET，實際目標與全域可達性仍未全部證明。原始 `0x8034` EBREAK／`0x8038` vector 邊界保留；trap handler／resume target 未證。

## 重現

工具版本與雜湊列於各 spec；來源閉包為本機既有 Windows／NDK27.1.12297006／LLVM18 證據。設定 `LLVM_BIN` 後可依順序首次建立：

```sh
python scripts/verify-curated-source.py --tool-dir "$LLVM_BIN" --build-root build/curated-source/secondary-message-20261026-v1
python experiments/tsl9-secondary-message-data/build-v2.py --tool-dir "$LLVM_BIN" --include-curated --trial data-v2
python experiments/tsl9-secondary-message-data/verify-source-v2.py --tool-dir "$LLVM_BIN"
python experiments/tsl9-secondary-message-data/integrate-v2.py --tool-dir "$LLVM_BIN" --trial component-v2
python experiments/tsl9-original-layout/build-v64.py --tool-dir "$LLVM_BIN" --trial secondary-message-v2
python experiments/tsl9-original-layout/verify-flow-v64.py --trial secondary-message-flow-v2
```

需先保留前階段輸入，見[來源索引](../../src/README.md)。trial 不覆寫既有目錄；原生步驟已有輸出時使用各自 `--replay`。本輪只公開文字來源、檢查器與收據摘要，沒有新增上傳 ELF／`.o`／BIN。

**尚無已驗證可刷寫 BIN。** 診斷 ELF 為 entry=0、PT_LOAD=0；六個未實作位址只是隱藏 NOTYPE reference constants，沒有 ABS FUNC。未執行目標、HOST model 或 ISA 模擬，未接觸硬體或廠商 API；完整原機啟動、ROM ABI、RAM／IRQ、藍牙與 OTA 仍待證明。[新功能方向](feature-candidates.json) 目前只是離線診斷工具提案。
