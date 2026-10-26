# Scheduler polling／狀態服務候選 C/C++

[English](readme.en.md) · [主排程](../tsl9-resident-scheduler/README.md) · [Idle 服務](../tsl9-resident-idle-service/README.md)

重建兩個完整本體：條件式 RAM `0x20002610..0x2000263A`（42 bytes）與 Flash `0x63DD0..0x63E58`（136 bytes），共 **178 bytes／66 條指令**。這是公開 SDK V1.31 候選，實機 ROM 相同性尚未確認。[C/C++ 來源](resident_scheduler_state_services.c)保留原暫存器與 C/assembly，不能當成一般 HOST C API。

## 已驗證

- C11／C++17 物件相同，原位址編碼後每個 byte 吻合；21 個正尺寸 FUNC、15 筆重定位。11 條條件式 Xwchc byte 指令依官方定義與 28 個向量核對。
- 主排程 `0x20000812`／`0x200008CC` 呼叫 polling 本體，far call `0x2000096E` 呼叫狀態服務；相鄰獨立函式未混入。
- Polling 逐次讀取 `0x20003514` 的 byte 0／1 bit 0，並讀取 `*(0x2000353C)+100`。若旗標未就緒且 register word 非零，回到 `0x20002620`。**可能持續等待，終止尚未證明**；沒有加入 timeout 或執行負向測試。
- 所有正常 polling 返回前，都清除 state byte 5；其前面原本「讀出但未使用」的 byte 5 load 仍保留。它不替 A0 指派 status，不能把返回值當作固定成功碼。
- 狀態服務在 `0x63DDE`／`0x63E14`／`0x63E2C` 分別重新讀取 state byte 8，比對 8／6／7。**未改成快取一次的 switch**，因前一 handler 可能影響後續狀態。
- state=8 路徑從 parameter block `0x20003560` 取 A2=byte3、A3=byte2。參數 bit0 與 buffer pointer 條件成立時，A0=buffer+2、A1=buffer byte1；否則 A0=A1=0，仍保留 A2/A3。`0x64F04` 返回非零時才設 state byte9=1；其 status 意義仍未確認。
- state=6／7 分別經 `0x20003438`／`0x2000344C` descriptor 的 byte11／byte7 決定是否轉入 handler；**指標本身沒有本地 null guard**。自身 16-byte frame 在正常返回與 `0x57DAE` tail 前均釋放。

原 byte-state 結構、descriptor 範圍、register 身分、所有權與 handler 副作用尚未閉合。保留既有 BLE／clock 編譯期 ABI assertion；它不證明這些 runtime byte-state 的實體布局。

## 真實依賴與組合

本輪以真實本體解析先前 `0x20002610`／`0x63DD0` 兩個匯入，並顯露三個實際 callee：**`0x57DAE`、`0x6020A`、`0x64F04`**。這些保持 genuine UND，沒有 stub；匯入數量不能當成功能完成率。另保存 `0x64F04` 的 608-byte 正向參考資料，**尚未把它算成已重建 CODE**，也未宣稱其語意與依賴已閉合。

C／C++ 非載入式 ET_REL 均為 **5122 bytes CODE＋256 bytes DATA／1782 條指令**，455 個正尺寸 FUNC、1 個 OBJECT、332 筆重定位。每個輸入 byte、符號與重定位皆保留。

先前 **4-byte 啟動來源缺口**、未完成的算術語意與整體 callback／RAM 契約仍保留。APP byte 覆蓋維持 **95.54%**，不代表功能完成率；未連入 APP，沒有新增 BIN。實機 RAM／ROM／ISA／IRQ／stack／Flash／OTA 相容性尚未確認。

證據：[完整稽核](audit-result-v1.json)、[摘要](summary.json)、[原始指令與 callee 參考](evidence-v1.json)、[規格與雜湊](spec-v1.json)。Polling／phase 診斷是候選新功能，尚未實作。

## 重跑

先備齊 spec／evidence／audit 指定的原 APP、SDK／標頭／指令參考與既存 native 產物；此提交未附原 SDK 與 native 產物，不會自動下載。從專案根目錄，以固定雜湊的 Windows NDK LLVM 執行：

```sh
python experiments/tsl9-resident-scheduler-state-services/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-scheduler-state-services/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；有既存產物時，第一個改用 `--replay experiments/tsl9-resident-scheduler-state-services/build/native-v1`，第二個省略 `--link-trial`。未執行目標／HOST 模型／ISA 模擬，未存取硬體或廠商 API。
