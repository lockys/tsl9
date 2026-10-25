# 次要訊息 DATA 與部分連結

本頁記錄 DATA／部分連結階段。後續原位址與靜態流程驗證見[新階段報告](../../analysis/secondary-message-layout-2026-10-26/README.md)。

[English](readme.en.md) · [DATA C/C++](src/secondary_message_data.v1.c) · [驗證摘要](summary.json) · [九段 CODE 候選](../tsl9-secondary-message-dispatch/README.md)

新增兩個實際唯讀 DATA 物件，共 **40 bytes**。C11、C++17 產生相同物件，全部內容與官方 ID2966 V4.1.60 原始窗口吻合。

| 原始範圍（尾端不含） | bytes | 已確認依據 |
|---|---:|---|
| `0x1A58C..0x1A5A8` | 28 | 原始無號 guard 限制索引到 0..6；七格有號相對位移對應六個實際 CODE 入口 |
| `0x19DD4..0x19DE0` | 12 | `0x155BA` 呼叫既有 `0x19BF0` 複製函式，A1 指向本窗口、A2=12、A0=SP+4 |

12-byte 固定內容在 22 份本機 decoded 韌體中有 18 份各出現一次。沒有據此猜測欄位意義、原始宣告長度或全域記憶體界限；也未選取相鄰 padding。呼叫端配置 32-byte frame，複製目的地 `SP+4..SP+16` 與保存 RA 的 `SP+28` 不重疊；這只是局部配置事實，不是完整 stack 預算證明。

## 合併結果

已將九段 CODE 候選、兩個 DATA 物件與既有正式 component 進行 `ld.lld -r --no-relax` 部分連結。C/C++ 合併物件相同：

- 68,648 CODE bytes、3,962 DATA bytes，總配置 72,610 bytes；這不是新增的正式位址覆蓋率。
- 6,118 個正長度 FUNC、56 個正長度 DATA 物件，保留 71 個真實 CODE alias 與六個真實 DATA label。
- 52 個既有 CODE 參考及兩個 DATA 參考皆由實際內容提供；保留全部 5,215 個來源／類型／addend／目標重定位角色。
- 六個編譯器 UND 維持不變，未以 ABS、stub 或猜測資料替代。這個數量不涵蓋全部執行相依，例如既有 `0x1AAE8` 查表仍無全域索引界限證明。

## 本機重現

設定 `LLVM_BIN` 為 spec 所列 Android NDK 27.1.12297006 LLVM `bin`。先建立既有正式 component，再於 repo 根目錄首次建立本輪輸入：

```sh
python experiments/tsl9-secondary-message-dispatch/build-v1.py --tool-dir "$LLVM_BIN" --trial candidate-v1
python experiments/tsl9-secondary-message-data/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-secondary-message-data/integrate-v1.py --tool-dir "$LLVM_BIN" --trial component-v1
```

部分連結的預設輸入為 CODE `build/candidate-v1`、DATA `build/native-v1` 及既有正式 component；完整路徑與雜湊列於 integration spec。新環境需先按各階段 README 建立既有正式輸入；公開 repo 不包含本輪新增的 `.o`。`--trial` 僅建立新目錄，不能覆寫已有結果；已有輸出時，改用 `--replay <該 trial 路徑>` 核對保留物件。

此階段尚未完成原位址放置與 `src/` 收錄，正式覆蓋率維持 **70,522／76,800 bytes＝91.83%**。未產出 BIN、執行目標／HOST model／ISA 模擬、連接硬體或呼叫廠商 API。原機啟動、ROM ABI、RAM／IRQ、藍牙與 OTA 相容性仍未證明。離線事件／相依瀏覽器可作為後續工具功能，目前只是建議，沒有增加硬體行為。
