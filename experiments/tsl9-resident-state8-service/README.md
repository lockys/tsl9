# State8 與 provider 候選 C/C++

[English](readme.en.md) · [呼叫端狀態服務](../tsl9-resident-scheduler-state-services/README.md) · [Timer 服務](../tsl9-resident-timer-service/README.md)

五個完整本體共 **1432 bytes／492 條指令**：

| 本體 | 原始範圍（end exclusive） | Bytes／自身 frame |
| --- | --- | ---: |
| State8 服務 | Flash 0x64F04..0x65164 | 608／64 |
| Callback setter | 條件式 RAM 0x2000078A..0x200007A0 | 22／0 |
| Register helper | Flash 0x6434A..0x6440A | 192／0 |
| Register helper | Flash 0x63C54..0x63D6A | 278／0 |
| 官方 slot9 timer start | Flash 0x43728..0x43874 | 332／48 |

這是公開 SDK V1.31 候選，實機 ROM 相同性未確認。[來源](resident_state8_service.c)保留原始暫存器與 C/assembly，不能當成一般 HOST C API。C11／C++17 物件相同，原位址編碼後每個 byte 吻合；94 個正尺寸 FUNC、70 筆重定位。11 條條件式 Xwchc 指令依官方定義與 28 個向量核對。

## 已確認的流程

- State8 的先前 608-byte 參考資料現在已有真實 native 本體。依本地條件返回 0／1／2／3；這些值**不是硬體成功證明**。所有本地正常返回前都按原路徑恢復 `0x4002420C` 保存值，其實體 IRQ 語意仍未確認。
- Buffer pointer 在 `0x20003564`。配置引數 size=`parameter byte29+2`（2..257）、第二引數=73；已有 buffer 時沿用。複製至 buffer+2，count 來自 entry A1，byte1 保存低 8 bits 或零。**實際容量、輸入範圍與 alias 尚未證明**，沒有自行加 clamp 或改寫原流程。
- Callback setter 把 A0 寫入 `0x20002EF8`；非零時設 `0x20002EFC=1`，零輸入不會清 flag，setter 本身不呼叫 callback。真實 CODE 數值 `0x65164`／`0x653A0` 仍是**未提供的 callback 本體**，不是 linker relocation；named UND 少不代表它們已閉合。
- State8 會在條件成立時呼叫真實 timer start：task byte=`0x20003570`、event=16、interval literal=1600。**返回值未檢查**，不宣稱 timer 已成功建立，也未換算為實體時間。
- Timer start 檢查 task count 與 cached raw-clock pointer。它在 raw callback 前後兩次讀取 Frequency（`0x4377C`／`0x437CC`），保留 64-bit 乘積+800、denominator=1600 的原始算術 helper 引數；先前除法語意仍未完成證明。
- 找到既有 timer 時，只更新 deadline offset8，**不重設 interval offset4**。新節點配置 16 bytes，欄位 task0／flag1=1／event2／interval4=0／deadline8／next12；沿 next 串列追加。串列終止、所有權與 callback 副作用仍未閉合。
- 兩個 register helper 有完整本體，保留間接指標讀寫與常數運算。`0x6434A` 會在使用 incoming A0 前覆寫它；未假定呼叫端傳入的該值一定影響硬體。

各自 frame 在正常返回平衡；state8+timer 自身 frame 合計 112 bytes，**不含其他 callee、父層、重入或 IRQ 的完整 stack 預算**。保留既有 BLE／clock 編譯期 ABI assertions，不據此推定實機 RAM 布局。

## 真實部分連結與限制

既有 allocator、copy、算術與 timer lookup 都使用真實先前本體；setter／register／timer provider 也有本輪實際 CODE。C／C++ 非載入式 ET_REL 均為 **6554 bytes CODE＋256 bytes DATA／2274 條指令**，549 個正尺寸 FUNC、1 個 OBJECT、402 筆重定位；每個輸入 byte、符號與重定位皆保留。

仍有兩個 genuine UND：`0x57DAE`／`0x6020A`，另有上述兩個數值 CODE callback 及 raw RAM／opaque callback 契約。保留 **4-byte 啟動來源缺口**與未完成算術語意。APP byte 覆蓋維持 **95.54%**，不代表功能完成率；未做原位址執行連結或 APP 整合，沒有新增 BIN。實機 RAM／ROM／ISA／IRQ／stack／Flash／OTA 相容性未確認。

證據：[完整稽核](audit-result-v1.json)、[摘要](summary.json)、[原始指令／官方 binding](evidence-v1.json)、[規格與雜湊](spec-v1.json)。Timer failure／buffer capacity／callback lifecycle 診斷是未實作的候選功能。

## 重跑

先備齊 spec／evidence／audit 指定的原 APP、SDK／標頭／指令參考與既存 native 產物；此提交未附原 SDK 與 native 產物，不會自動下載。從專案根目錄，以固定雜湊的 Windows NDK LLVM 執行：

```sh
python experiments/tsl9-resident-state8-service/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-state8-service/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；有既存產物時，第一個改用 `--replay experiments/tsl9-resident-state8-service/build/native-v1`，第二個省略 `--link-trial`。未執行目標／HOST 模型／ISA 模擬，未存取硬體或廠商 API。
