# Idle 服務與 register helper 候選 C/C++

[English](readme.en.md) · [主排程](../tsl9-resident-scheduler/README.md) · [時鐘服務](../tsl9-resident-clock-services/README.md)

重建三個完整本體，共 **518 bytes／178 條指令**：條件式 RAM `0x2000061A..0x2000078A`（368 bytes）、Flash `0x6430E..0x6434A`（60 bytes）與 `0x638EA..0x63944`（90 bytes）。相鄰的 `0x2000078A`／`0x200007A0` 是別的函式，未納入。

這是公開 SDK V1.31 候選，實機 ROM 相同性尚未確認。[C/C++ 來源](resident_idle_service.c)使用原始暫存器與 C/assembly，不能當成一般 HOST C API。

## 已驗證的流程

- C11／C++17 物件相同，原位址編碼後全部 bytes 吻合；41 個正尺寸 FUNC、28 筆重定位。唯一條件式 Xwchc byte 指令依官方定義與 28 個向量核對。
- 真正主排程在 `0x200008BE` 尾端轉入此服務，**先釋放自己的 32-byte frame**。此服務自身另用 32 bytes；兩者自身 frame 不同時疊加，但 callback／callee／IRQ 與全程 stack 上限仍未閉合。
- 主排程的 raw clock／idleCB 非空檢查都支配這條 tail 路徑，仍需指標保持穩定。編譯確認官方 `bleConfig_t.idleCB` offset=40，對應 `0x20003214`；標頭型別是 `uint32_t (*)(uint32_t)`。callee 內沒有另加 null guard。
- 服務保存 `0x4002420C`、寫零、執行 FENCE.I，之後恢復保存值；恢復點支配 idleCB 呼叫。這是指令順序，尚未證明該 word 的實體 IRQ 語意。
- deadline 路徑保留四個 raw clock 呼叫點與 fresh reads，不把不同次 clock 讀取合併。fallback 常數是 **−30000000**，只按原分支做最多一次 MaxCount 減法，不改成一般 `%`，也未換算為實際時間。
- idleCB 前設 `0x20003520=1`，引數若為零則改用 live MaxCount。返回非零時跳過本地 timer 呼叫；返回零時走向真實 timer 服務。只有 fresh gate 與 flag 皆非零的分支，才依序呼叫兩個真實 helper，再清 flag。
- callback 前後重新讀取 `0x20003538` 與 `0x20003590`。指標+8 的 AND mask=`0xFFCCFFFF`、OR mask=`0x00330000`；gate 或指標可能改變，**未證明這是成對的硬體還原**。

兩個 Flash helper 分別透過 `0x2000353C`／`0x20003508` 的指標存取區塊，最少需 120／56 bytes 有效範圍；硬體 register 身分、alias、副作用與所有權仍未確認。

## 實際部分連結與限制

真實 idle 本體解析既有 `0x2000061A` 匯入，本輪 timer 匯入也由既有真實本體解析。C／C++ 非載入式 ET_REL 都是 **4944 bytes CODE＋256 bytes DATA／1716 條指令**，434 個正尺寸 FUNC、1 個 OBJECT、317 筆重定位；每個輸入 byte、符號及重定位皆保留。

仍缺 RAM `0x20002610` 與 Flash `0x63DD0`，以及整體 callback／RAM 契約。先前 **4-byte 啟動來源缺口**與算術 helper 的未完成語意證明保留。APP byte 覆蓋仍為 **95.54%**，不代表功能完成率；沒有新增 BIN，實機 RAM／ROM／ISA／IRQ／stack／Flash／OTA 相容性仍未確認。

證據：[完整稽核](audit-result-v1.json)、[摘要](summary.json)、[原始指令](evidence-v1.json)、[規格與雜湊](spec-v1.json)。Idle phase／callback 返回值／deadline 診斷是候選新功能，尚未實作。

## 重跑

先備齊 spec／evidence／audit 指定的原 APP、SDK／標頭／指令參考與既存 native 產物；此提交未附原 SDK 與 native 產物，也不會自動下載。從專案根目錄，以固定雜湊的 Windows NDK LLVM 執行：

```sh
python experiments/tsl9-resident-idle-service/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-idle-service/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；有既存產物時，第一個改用 `--replay experiments/tsl9-resident-idle-service/build/native-v1`，第二個省略 `--link-trial`。未執行目標／HOST 模型／ISA 模擬，未存取硬體或廠商 API。
