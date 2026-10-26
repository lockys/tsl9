# 時鐘服務候選 C/C++

[English](readme.en.md) · [Timer 服務](../tsl9-resident-timer-service/README.md) · [RAM 配置](../tsl9-resident-task-layout-contract/README.md)

本輪重建五個完整函式，共 **474 bytes／168 條指令**。這是公開 SDK V1.31 的條件式候選；實機 ROM 身分尚未確認。[來源](resident_clock_services.c)使用原始暫存器與 C/assembly，不能當作一般 HOST C API 呼叫。

| 函式 | 原始位址範圍（end exclusive） | Bytes |
| --- | --- | ---: |
| TMOS_TimerInit | Flash 0x43F46..0x44022 | 220 |
| Provider 註冊 | Flash 0x43B0A..0x43B28 | 30 |
| Delta provider | Flash 0x43D62..0x43DE4 | 130 |
| 預設 counter getter | 條件式 RAM 0x20000986..0x200009BA | 52 |
| TMOS_GetSystemClock | Flash 0x43520..0x4354A | 42 |

**實際驗證：** C11／C++17 物件相同，33 個正尺寸 FUNC、19 筆重定位；還原原位址編碼後每個 byte 吻合。7 個條件式 Xwchc byte／halfword 指令已依官方定義與 28 個向量核對。編譯確認 `bleClockConfig_t` 大小 16、alignment 4、欄位 offset 0/4/8/10/12；ABI assertion 物件沒有 runtime bytes。

## 已確認的流程

- 非空 config 要求 callback、MaxCount、Frequency、Accuracy 都非零。irqEnable 非零時另要求 BLE connection sum ≤2。驗證前可能先呼叫 rcCB；正常返回 0 不等於硬體初始化成功。
- 接受後複製 16 bytes 至 `0x20003234`，raw callback 另寫入 `0x200031E0`。WaitWindow 原值為零時，用 **ClockFrequency（offset 8）** ×1400 與 1,000,000 建立算術 helper 引數，取返回 A0 的低 8 bits。helper `0x6DF1A` 尚未重建，除法語意仍是推論。
- 註冊 helper 把 `0x43D62` 寫入 `0x20003230`，立即呼叫，然後把返回值寫入 baseline `0x200031B4`。Delta provider 本身也會更新此 word；重複初始化的 baseline 語意尚未閉合。
- Delta provider 以 raw counter×1600 的完整 64-bit 乘積與 Frequency 建立 helper 引數，再依新舊值相等／遞增／wrap 分支計算差值。保留實際 unsigned 運算，沒有把未確認 helper 換成假實作。
- 公開 getter 把非空 provider 返回值累加到 `0x200031B0`。官方標頭記載單位 **0.625 ms**；這是文件單位，不是已量測的硬體頻率。
- 預設 getter 暫時清除 `0x4002420C` 的 bit 14，讀取 `0x200031B8`／`0x40024268`，恢復原 MMIO，再返回 u32 `(software_word<<26) | ((~counter_word)>>6)`。實體 MMIO／IRQ 語意未確認。

各函式自身 frame 為 32/16/32/0/16 bytes，正常返回均平衡；這不包含 callback／callee／IRQ 或全程 stack 上限。數值 CODE 指標 `0x43D62` 與 `0x20000986` 有真實本體，但不是 linker relocation，尚未做原位址執行連結。

## 原 APP 如何呼叫

既有三個 APP 本體共 280 bytes，**本輪不新增 APP CODE**。`0x19B56` 先清零 16-byte config，再填入 callback `0x191C6`、MaxCount `0xFFFFFFFF`、標稱 Frequency **16000 Hz**／Accuracy **1000 ppm**；irqEnable 初值為零。仍需被呼叫 helper／IRQ／alias 不覆寫 caller config。

`0x19BCC` 經官方 slot 16 呼叫 TimerInit；外層 `0x19B3A` 覆寫其 status，未使用返回值。90-byte callback `0x191C6..0x19220` 對 `0x40002818`／`0x4000281C` 的 high／low halfword 做重複相等讀取與 high 重查，組成 32-bit 值。重試終止、coherent snapshot 及實際頻率尚未證明。

## 組合與限制

真實 copy provider 解析本輪匯入後，C／C++ 非載入式 ET_REL 均為 **3512 bytes／1242 條指令**、312 個正尺寸 FUNC、224 筆重定位；每個輸入 byte、符號、重定位皆保留。仍缺 RAM `0x2000061A`／`0x20002610` 與 Flash `0x63DD0`／`0x6DF1A`，以及 raw RAM／callback 契約。

保留先前 **4-byte 啟動來源缺口**。未連入 APP、沒有新增 BIN，實機 RAM／ROM／ISA／IRQ／stack／Flash／OTA 相容性尚未確認。APP byte 覆蓋維持 **95.54%**，不代表功能完成率。Clock range／baseline／重新初始化診斷只是候選功能，尚未實作。

證據：[完整稽核](audit-result-v1.json)、[摘要](summary.json)、[原始指令](evidence-v1.json)、[規格與雜湊](spec-v1.json)。

## 重跑

需先備齊 spec、evidence、audit 所列原 APP、SDK／標頭／指令參考與先前 native 產物；此提交未附原 SDK 與 native 產物，也不會自動下載。從專案根目錄使用固定雜湊的 Windows NDK LLVM：

```sh
python experiments/tsl9-resident-clock-services/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-clock-services/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在。有既存產物時，第一個改用 `--replay experiments/tsl9-resident-clock-services/build/native-v1`，第二個省略 `--link-trial`。未執行目標／HOST 模型／ISA 模擬，未存取硬體或廠商 API。
