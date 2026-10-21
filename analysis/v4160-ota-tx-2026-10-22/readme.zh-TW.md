# OTA 封包組裝：可讀 C/C++ 與尚未通過的原生邊界

[English](readme.en.md)

本輪沿已重建頁面回覆的直接 callee，追查官方 ID2966 V4.1.60 的 `0x8A56..0x8B6E`。原始 280 bytes／96 條指令已逐條解析，40 項運算元變異被拒絕；現有物件的 9 個外部入口均指向函式起點，其中一個不建立返回連結。不能只看 RELA 類型就把所有引用當成一般 C 呼叫。

## 已確認的原始邏輯

入口以完整無號 A3 檢查長度，超過 1039 就在建立堆疊前返回。兩組連線值分別從 live GP 的 `+0x96`、`+0x9A` 讀取，並以新讀取的 `0x4013C` pointer 呼叫服務；只有完整返回值恰好為 1 才選定 lane。第二次呼叫的 A2／A3 可能是第一次呼叫留下的值，不能由候選 SDK 型別擅自歸零或刪除。

選定後，以 `0x2000B18C + lane × 1062` 為 descriptor 基址。封包從 `+6` 開始，包含 `0x7F55` 的 16 位元值、命令、長度欄位、逐 byte 複製的負載，以及命令／長度／負載的低 8 位累加值。descriptor 的長度與清零欄位各是 16 位元寫入；最後從 live GP `+0x94 + 4 × lane` 讀取一個 byte，再以 A1=1 尾端交給新讀取的 `0x40050` pointer。

這份函式內沒有可見的配置／釋放或 memcpy 呼叫。它直接寫入數值緩衝區並交接服務，不能因此宣稱已觀察到藍牙傳送、接收或更新成功。初始長度檢查也不能證明未知 ROM 呼叫之後的 live S0 仍受同一上限約束。

## 證據層級

| 項目 | 本輪狀態 |
| --- | --- |
| 原始指令、位元欄位與來源角色 | 已核對；見 `source-review` 與修正後的 `source-review-v2` 公開入口 |
| 可讀 C/C++ 邏輯 | 新增於 `experiments/tsl9-v4160-ota-tx`，主機合成測試與原生編譯分開報告 |
| 主機合成行為 | C、C++ 各 107 案例／15,605 檢查，8 個實際編譯的語義錯誤版本被拒絕 |
| 獨立來源效果測試 | C、C++ 各 31 案例／78,283 檢查，14 個實際編譯的語義錯誤版本被拒絕 |
| 原生區段大小 | C/C++ 編譯探針均為 280 bytes／96 條指令 |
| 原始機器碼、入口與恢復 ABI | **未通過**；堆疊早於原 guard 建立、恢復較晚，部分運算元／控制流不同 |
| 完整映像 | 維持前一輪十二函式／650 bytes；本輪 TX 未取代原始承載 |
| 原板、ROM／BOOT、BLE OTA、復原 | 尚未驗證；不宣稱可燒錄 |

獨立 ABI 審查確認，當前差異不能只靠排列已產生的指令關閉。沒有借用原始 opcode 補齊新函式，也沒有改寫舊排序器或放寬替換條件。來源效果測試的成功不能取代這項原生拒絕。

後續整合還需分別證明原始八個 private 邊界的用途、PCREL 配對及呼叫延續位置：原 RAM 配對錨點在 `+0x80`，當前編譯結果在 `+0x74`；第二次 gate 的返回位置也從原 `0x8AB6` 移到 `0x8ABA`。即使總長度相同，也不能直接沿用舊偏移或把全部 private 符號當成一般分支標籤刪除。

## 檢查入口與後續

原始來源檢查：

```sh
python experiments/tsl9-v4160-ota-tx/verify_host.py --project-root . --language both
python analysis/v4160-ota-tx-2026-10-22/source-review-v2/check-review.py \
  --project-root . --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin
python analysis/v4160-ota-tx-2026-10-22/continuation-plan/check.py \
  --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin
```

W 工作區的分析路徑前綴為 `apk-analysis/tsl9-`；交付與儲存庫前綴為 `analysis/`。預設來源檢查重新讀取原始 BIN 與來源記錄；只有明確指定實際物件才宣稱重播該物件。`source-review-v2` 僅修正舊公開檢查器在 JSON tuple／list 比較的序列化問題，原解碼器、契約與舊封存 bytes 保持不變。

[靜態輸入核對](inspection/README.md)另記錄 REA 實際 provider 狀態與獨立 LLVM 範圍。[後續計畫](continuation-plan/README.md)追蹤 `0x8614` 共用緩衝區引用、候選 SDK 解釋，以及離線封包預檢／更新等待原因提案。整體目標仍包含必要功能與原機執行層重建、硬體及 OTA 相容性證明，尚未完成。
