> 此頁保留先前實驗快照。最新正式來源與原位址證明見[整合結果](../../analysis/central-callback-integration-2026-10-26/README.md)。

# 中央角色事件與輔助函式：C/C++ 實驗

本輪重建 **1,938 bytes／645 條指令**：五個輔助函式與一個事件回呼。C 與 C++ 產生相同的 RV32 物件；147 個實際 FUNC、97 筆直接控制重定位及兩組位址參考均與原 BIN 相符。這是綁定原始暫存器的 C，保留明確組語介面，需要原位址與私有呼叫慣例。

| 原始範圍 | bytes／指令 | 已確認的靜態結構 |
|---|---:|---|
| `0x10CE0..0x10D2E` | 78／26 | 依長度與型別搜尋欄位，輸出資料指標與長度 |
| `0x110F8..0x11252` | 346／121 | 記錄迴圈、狀態與 ROM 呼叫 |
| `0x11252..0x11266` | 20／6 | 共用的 ROM 暫存器尾呼叫 |
| `0x11266..0x11356` | 240／88 | 記錄比對／狀態更新，尾跳至 `0x11252` |
| `0x114E2..0x11544` | 98／30 | 狀態設定與回呼轉送 |
| `0x11544..0x119C8` | 1,156／374 | 事件值 0..16 的守衛與七個跳轉入口 |

保守靜態控制圖涵蓋全部 645 條指令，保留兩處不透明 ROM 尾呼叫。相鄰、已正式重建的 `0x11356..0x11442` 沒有重複納入。

與上一輪三個回呼及正式元件部分連結後，實驗物件含 **66,600 CODE bytes、3,830 DATA bytes、4,967 筆重定位**。11 個外部 CODE 相依已接上；原有配置、71 個 CODE 別名與六個 DATA 標籤全部保留。尚缺 `0x1A548` 的事件跳轉表 DATA；舊有八個未提供符號也仍保留。未解析符號數不代表完整執行期缺口清單。

**尚未正式整合至 `src/`，正式覆蓋率仍為 89.03%。** 這次未做原位址診斷連結、未產生 BIN、未執行目標或存取硬體。實機 MCU／ROM／RAM／IRQ／BLE OTA 與全域狀態邊界尚未證明，不宣稱完整還原原廠原始碼或可燒錄。

## 本機重跑

在專案根目錄執行；`LLVM_BIN` 指向與 spec 雜湊相符的 NDK LLVM 目錄。

```sh
python experiments/tsl9-central-event-callbacks/audit-v1.py
python experiments/tsl9-central-event-callbacks/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-central-event-callbacks/integrate-v1.py --tool-dir "$LLVM_BIN" --trial component-v1
```

編譯前先完成[三個回呼](../tsl9-central-callback-leaves/README.md)的 build，並保留既有正式元件。試驗目錄採只建立模式；已存在 `native-v1` 時用 build 的 `--replay experiments/tsl9-central-event-callbacks/build/native-v1` 取代 `--trial native-v1`。所有檢查都只讀取指令／物件與交叉編譯，不執行韌體。

下一步：提供並驗證事件跳轉表與兩個回呼表的 DATA／CODE 關係，再整理正式來源及原位址整合。可研究的新功能是 RSSI 連線診斷、事件追蹤與欄位解析診斷；尚未實作，也未加入硬體控制行為。

[English](readme.en.md) · [C 來源](src/central_event_callbacks.v1.c) · [證據摘要](summary.json)
