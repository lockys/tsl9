# OTA 頁面回覆實作與驗證

[English](readme.en.md)

本範圍提供可讀 C11/C++17 `9B8E..9C0A`、具名合成 HOST 提供者、實際原生編譯與嚴格連結驗證。原始來源證據為 `../source-review/` 的 124 bytes / 50 條指令；`../ABI-review/` 與 `../code-review/` 分別獨立評閱原生區段及 HOST 效果。

兩種語言的編譯器輸出都是124 bytes /50條指令，但兩段 ABI 順序不同。實際管線保留 `page_reply.o` 與 IR，再執行專案內 `reply-abi-order/order.py`，產生 `source-ordered.o` 與 `ABI-order.json`。排序只重排本次編譯出的指令，改動28 bytes，保留完整 ELF metadata、符號與唯一 TX 重定位；沒有用原始 BIN 產生程式碼。排序後固定連結在9B8E的124 bytes與原版完全一致。

缺少 TX 提供者的嚴格連結必須失敗；成功的 `ADDRESS-WITNESS-ONLY.elf` 僅把 TX 符號設成數值8A56，不提供該函式的280-byte內容。因此沒有新的完整映像、BIN、ROM實作或可燒錄承諾。

## 使用

```sh
python -B experiments/tsl9-v4160-ota-page-reply/verify_host.py --project-root . --language both
python -B experiments/tsl9-v4160-ota-page-reply/verify_native.py --project-root . --tool-dir "$LLVM" --language both
```

可用 `.sh` 包裝器，或指定專案內尚不存在的 `--build-root`。兩個 CLI 的 `--replay RECEIPT` 都只讀取實際產物。`verify_native.py` 匯出 `context(root)`、`static_checks(ctx,folder)`、`replay(root,receipt)`；HOST 匯出 `replay(root,receipt)`。原生結果包含 `checks`、6個真實管線命令、11個原始位元組／IR控制、3個實際編譯錯誤版本，以及每個產物雜湊。HOST包含精確3/87/3634結果、6個實際編譯錯誤版本與每次執行前後的主機格式檢查。

`results.json` 索引四份選定收據；`receipts/` 保留位元組相同的中繼資料。產物／日誌只保留本機忽略的模型 `build/`。預設 `check.py --project-root ROOT` 僅核對封存成員與目前來源，不宣稱重新編譯、執行或讀取未發布的本機封存。`--archives` 才重讀四份實際本機封存；`--host-receipt`／`--native-receipt` 可指定新根目錄內產生的收據。

HOST回呼在READ/WRITE正常返回時不得改動暫存器；具名外部呼叫才允許任意GPR/SP/frame變更。未知結果與不返回會停止模型並保留已提交效果，不發明清理或統一成功碼。原始與JALR遮罩後目標／連結分開記錄。廣泛HOST變動覆蓋不證明原生C的未知callee-saved/SP慣例。主機格式檢查支援PE/ELF/thin Mach-O，實測Windows；macOS fat/universal Python不支援。

排序後區段的位元組一致性、原生C條件性ABI與合成HOST證據分開陳述。計算出的內部入口、未知駐留ABI、非同步／fault、實體硬體與OTA仍未驗證。未執行RV32、ISA模擬、網路或裝置I/O。
