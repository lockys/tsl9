# Callback 流程與狀態組裝整合

[English](readme.en.md)

本輪完成七個入口及兩個被函式位址參照的輔助函式，共 **1082B／368 條指令＋96B 唯讀資料**，來源已置於 [src/](../../src/native/receive/callback_flow.c)。完整保留 13346 的 672B 狀態組裝流程及第一個 ret 後的分支；未用固定回傳值代替未知功能。

C11／C++17 原生物件一致。整合後為 **13864B code＋674B data、4832 條原始指令、930 RELA、95 UND**。既有 12782B code 與 578B data 均未改變；新增七個別名都指向真實入口，沒有 stub 或 ABS 提供者。

[原始指令證據](evidence.json) · [結果與雜湊](summary.json) · [未解析入口](next-providers.json) · [整合檢查器](../../experiments/tsl9-callback-flow/integrate-v1.py)

| 原始範圍 | 已確認內容 |
| --- | --- |
| 1070A–1074C、1061C–10630 | 保留清除／取消呼叫與函式位址參照；1061C 位址傳入 90B0，不能據此宣稱已成功註冊 |
| 1299E–12A08、12AA0–12ABE | 保留 96B 來源位址、14 次迴圈、原堆疊及原分支；19BF0 的實作仍未知 |
| 13346–135E6 | 完整 672B 多來源取值與資料組裝，含回傳後的其他路徑 |
| 135E6–13660、1333C–13346 | 傳入回呼位址 1333C 與常數 300；設定與清除指向相同原始 RAM 位址 2000C794。時間單位／欄位意義未證 |
| 16DD4–16E0C | 保留兩種參數分支與堆疊 payload，實體命令效果未證 |

先前中間收據的 registered callback 標籤只代表函式位址參照，沒有觀察到執行或註冊事件。本輪依原始位址重用既有符號名稱；未知實作仍是 UND。接通七個舊入口後又展開 21 個新入口，所以 **81→95**，未以符號計數代替完成度。

來源集為 98 個 C/H、71 個 code units；含獨立指標資料共 144 組比較／288 個物件。舊 140 組結果及 841 筆產物記錄保持一致，清單僅作精確的 97→98 檔延伸；凍結的舊檢查器未修改，不宣稱其舊整份 manifest 重播適用新清單。

```sh
python3 experiments/tsl9-callback-flow/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-flow/build/component-v1
```

下一步先證明選定區塊的原始位址配置與 fall-through，再擴展新提供者。現有物件仍是 VMA=0 的 ET_REL，尚未證明完整原址配置、RAM 擁有權、私有 ABI、實體 MCU／installed ROM／中斷或 OTA 相容性，**不能燒錄**。未執行目標、模型或 ISA 模擬，未連線、接觸硬體、產生 BIN 或 commit／push；歷史個資問題尚存。

新功能候選：只讀的遞延旗標與狀態來源診斷。上述同位址寫入／清除提供了線索，但尚未實作介面，也未以未知時間單位修改控制策略。
