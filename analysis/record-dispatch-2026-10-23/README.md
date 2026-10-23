# Record dispatcher 離線重建
[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本輪重建並選入 `src/`：`12A08` record dispatcher（102B／35i）與 `821E` predicate（42B／15i）。後者由 C 算術及空暫存器埠編譯，全部42B與官方 V4.1.60 相同；前者保留私有架構 frame／控制轉移埠、74B完整非控制指令與689原始位元。

實際將三份既有正式物件部分連結成950B／330i／42 genuine FUNC，並真實綁定 `12A08`、`81AA`、`821E`。C／C++物件相同；50 pending RELA與六個外部provider仍未閉合。不是執行映像或可燒錄BIN。詳見 [summary.json](summary.json) 與 [獨立原始 ELF 檢查](final-root-review.json)。

驗證包含 dispatcher每語言212負例、predicate65負例、實際join25負例與完整上游收據重播。整理後59個C/H、33個native TU通過66組／132個物件比對；原62組結果與373個產物保持相同。C/C++ strict firmware gate 均在 bounded PASS 後 exit1，沒有執行 target／ISA／MMIO／硬體或呼叫網路API。

[公開收據](publication-provenance.json) 有四份可攜原件與三份明示的路徑衍生版；後者保留原件SHA／大小／本機相對位置，可反向還原相同JSON，不宣稱原件bytes或原件重播。原收據留本機及 `build/record-original-receipts-20261023.zip`。驗證方式：
```sh
python scripts/check-record-publication.py
python scripts/anonymize_public_evidence.py --check
```

predicate最初失敗的驗證器未封存，已明載於來源歷史；已知修正前版本與失敗輸出有保留。本輪只修正 interpreter路徑正規化；不同Python執行檔雜湊會正確拒絕重播，不放寬證據相等條件。

下一個邊界為 [18CA4的212B／72i周邊寫入流程](next-peripheral.md)。三個bank與寄存器配置可能屬傳送介面，仍是推論；目前不能確認CAN型號、座椅／免打擾語意、完整ABI或OTA相容性。[新功能候選](feature-candidates.md) 先保留為診斷需求，不加入未證實的車輛控制。
