# State8 callbacks／runner 候選 C/C++

[English](readme.en.md) · [State8 呼叫端](../tsl9-resident-state8-service/README.md) · [主排程](../tsl9-resident-scheduler/README.md)

重建八個完整本體，共 **2118 bytes／755 條指令**：

| 本體 | 原始範圍（end exclusive） | Bytes／自身 frame |
| --- | --- | ---: |
| 已註冊 callback | Flash 0x65164..0x653A0 | 572／48 |
| 已註冊 callback | Flash 0x653A0..0x65620 | 640／48 |
| Shared-pointer runner | 條件式 RAM 0x200007A0..0x200007D0 | 48／16 |
| Receive-status helper | 條件式 RAM 0x2000263A..0x200026BA | 128／0 |
| Register reset wrapper | Flash 0x6440A..0x64422 | 24／16 |
| Register helper | Flash 0x63B0E..0x63C54 | 326／0 |
| Register reset helper | Flash 0x63E58..0x63EDA | 130／0 |
| Register-work helper | 條件式 RAM 0x200026BA..0x200027B4 | 250／16 |

這是公開 SDK V1.31 候選，實機 ROM 相同性尚未確認。[來源](resident_state8_callbacks.c)保留原始暫存器與 C/assembly，不能當成一般 HOST C API。C11／C++17 物件相同，原位址編碼後全部 bytes 吻合；154 個正尺寸 FUNC、114 筆重定位。

## 已確認的流程與解碼

- 先前由 state8 註冊的數值 CODE `0x65164`／`0x653A0` 現在都有真實本體；數值地址仍不是 linker relocation，也未做原位址執行連結。
- 以官方定義驗證 **八類 Xwchc、52 個正向向量**（含 24 個 stack 向量）。兩處原被 radare2 拆成兩個 `invalid` byte 的 `0x879C`，已按正式 bit fields 解為 `qk.c.lbusp a5,15(sp)`；沒有跳過或猜補指令。45 條實際自訂指令保持條件式 profile，未證明實體 ISA。
- 兩個 callback 都用 48-byte frame，先把 SP+15 清零，再把該 byte 位址傳給真實 receive-status helper。兩個已知呼叫均傳 A1=0／A3=0；SP+15 的 load 在該呼叫之後。這不等於證明整體 stack／alias 安全。
- Runner 從 `0x20002EF8` 載入非空指標並呼叫，返回後重新讀 `0x20002EFC`；fresh flag=0 時清除 pointer word。**沒有先比對 pointer 是否仍是呼叫前的值**，atomicity 與 lifetime 尚未閉合。
- callback 會呼叫真實 event setter，event literal=2；不宣稱事件已成功排入。部分分支經 `0x20003550` 呼叫 opaque callback，沒有本地 null guard；保留實際 A0=3／status low8／descriptor 引數。
- Receive-status helper 保留本地返回碼 0／1／6／14、optional byte／halfword 輸出與原始 signed DIV。這些不是硬體成功碼。Register-work helper 的 polling back edges 也保留，終止未證明。
- 第二個 callback 經真實 setter 再註冊 **`0x65620`**；該下一階段本體仍未提供。

各自 frame 在所有本地正常返回平衡；callee 正常返回與保存 SP 仍是前提，整體 IRQ／重入／stack 上限未閉合。既有 BLE／clock ABI assertion 不證明實機 RAM 布局。

## 入口證據的限制

原始 RAM 對應 `0x20002E28` 有 `JAL runner` 後接 `ECALL` 的確切 bytes。**該序列的入口、可達性、所屬函式與 IRQ 角色尚未證明**，不把它宣稱為已驗證 IRQ 呼叫鏈，也未把周邊線性視窗當成單一函式。

## 實際部分連結

C／C++ 非載入式 ET_REL 均為 **8672 bytes CODE＋256 bytes DATA／3029 條指令**，703 個正尺寸 FUNC、1 個 OBJECT、516 筆重定位；每個輸入 byte、符號與重定位皆保留。Event setter、state8 與 callback setter 匯入由真實先前本體提供，本輪八個 provider 也都有實際 CODE。

仍有 genuine UND `0x57DAE`／`0x6020A`、數值 CODE `0x65620`，以及 runner invoker、opaque callback、descriptor／RAM 契約。保留 **4-byte 啟動來源缺口**與未完成算術語意。APP byte 覆蓋仍為 **95.54%**，不代表功能完成率；未連入 APP、沒有新增 BIN，實機 RAM／ROM／ISA／IRQ／stack／Flash／OTA 相容性未確認。

證據：[完整稽核](audit-result-v1.json)、[摘要](summary.json)、[原始指令／正式向量](evidence-v1.json)、[規格與雜湊](spec-v1.json)。Callback lifetime／receive-status 診斷是未實作的候選功能。

## 重跑

先備齊 spec／evidence／audit 指定的原 APP、SDK／標頭／指令參考與既存 native 產物；此提交未附原 SDK 與 native 產物，不會自動下載。從專案根目錄，以固定雜湊的 Windows NDK LLVM 執行：

```sh
python experiments/tsl9-resident-state8-callbacks/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-state8-callbacks/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；有既存產物時，第一個改用 `--replay experiments/tsl9-resident-state8-callbacks/build/native-v1`，第二個省略 `--link-trial`。未執行目標／HOST 模型／ISA 模擬，未存取硬體或廠商 API。
