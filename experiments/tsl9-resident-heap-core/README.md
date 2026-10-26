# Resident heap 候選 C/C++

[English](readme.en.md) · [訊息 API 候選](../tsl9-resident-message-api/README.md)

本輪僅重建公開 WCH SDK V1.31 的兩個私有 helper，**未確認 TSL9 實機 ROM 身分，也不是可刷韌體**。

| 入口（條件式 RAM 位址） | 範圍 | bytes |
| --- | --- | ---: |
| 配置 | `0x20000040..0x20000110` | 208 |
| 釋放／合併 | `0x20000110..0x200001E4` | 212 |

[來源](resident_heap_core.c)共 145 條指令、37 個實際 FUNC 區域、26 筆直接控制重定位；C11／C++17 物件相同，420 bytes 皆在還原原始位址編碼後吻合。22 條條件式 Xwchc LHU／SH 保留明確原始指令埠，官方 14 個相關向量亦已核對。

與上一輪訊息 API 部分連結後為 **584 bytes／207 條指令**，兩個具名 heap 匯入由真實函式解析，51 個 FUNC 與 37 筆重定位完整保留。這只是非載入式 ET_REL 證據；具名 UND 為零仍不代表執行環境閉合。

## 已確認的候選邏輯

- 大小經 16-bit 截斷及 4-byte 對齊；52 bytes 為串列選擇門檻。區塊 header 為 8 bytes，`+4` 為大小、`+6` 為旗標，配置回傳區塊 `+8`。
- 可用空間減需求大於 8 時切割；釋放會巡訪、清除旗標並條件式合併。未證明實際串列無環或操作必定終止。
- `0x200000A0` 透過 RAM `0x20003220` 呼叫不透明 callback。其正常返回後走配置失敗路徑，本 helper 不重試。
- V1.31／V1.40 的全部差異限於 **13 條 RAM 立即數指令相差 `+0x50`**，其餘 helper bytes 相同；兩版 RAM 全域配置不可直接混用。

證據與限制：[audit-result-v2.json](audit-result-v2.json)、[summary.json](summary.json)、[原始映射與指令證據](evidence-v1.json)。尚缺 heap 初始化、RAM 界限／所有權、callback、實機 ISA／ROM、IRQ 與 OTA 相容性證據。存取 `0x4002420C` 的物理意義與恢復效果亦未確認。

## 重跑本機驗證

需固定版本的 Windows NDK LLVM 工具（雜湊見 [spec-v1.json](spec-v1.json)）。由專案根目錄執行，將 `LLVM_BIN` 設為工具目錄；下列建立名稱必須尚不存在：

```sh
python experiments/tsl9-resident-heap-core/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-heap-core/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

既有產物以不含 `--link-trial` 的第二個指令唯讀重驗。沒有執行目標／HOST 模型／ISA 模擬，也未存取硬體或產生 BIN。APP 正式 byte 覆蓋仍為 **95.54%**，不代表功能完成度。
