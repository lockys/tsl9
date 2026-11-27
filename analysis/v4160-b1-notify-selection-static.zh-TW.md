# B1 通知輸入切片與私有 selector：離線靜態驗證

本階段接續[完整 record callback](v4160-b1-record-callback-static.zh-TW.md)，展開兩個參考 carrier 的通知函式、RAM selector 與 register-pair shift。新增完整範圍共 **1,512 bytes／548 條指令**；這是原指令與條件性合約的驗證，沒有增加既有 C 重建覆蓋率，也不是可用韌體或實機功能驗證。

重播工具：[Python checker](check_v4160_b1_notify_selection_static.py)；固定帳本：[JSON](v4160-b1-notify-selection-static.json)。所有 byte 範圍同時對照 carrier 與嚴格 sparse HEX，不以零補齊缺口。

## 完整範圍與來源

| 函式 | V131 | V140 | 每版本 bytes／指令 |
|---|---|---|---|
| notifier | FLASH `[0x52d80,0x52dde)` | FLASH `[0x52e28,0x52e86)` | 94／37 |
| selector | RAM `[0x200017d6,0x20001a40)`，FLASH `[0x41a46,0x41cb0)` | 同一 RAM 範圍，FLASH `[0x41a86,0x41cf0)` | 618／222 |
| pair shift | FLASH `[0x6dec2,0x6deee)` | FLASH `[0x6e0b2,0x6e0de)` | 44／15 |

selector 的完整 FLASH→RAM 第一段複製來源已核對。兩個 shift 本體 byte 相同。帳本包含各完整本體 SHA256、逐指令 operands、所有 store、CFG、每條 CFG 邊的語法路徑證書與 SCC。selector 的 `+0x266` 命中塊、shift 的 `+0x1e` 高半字路徑都在首次 RET 之後，仍屬可達本體，不能提前截斷。

## SP+12 的缺口如何縮小

notifier 先讀固定 task byte：V131 `0x200033b3`、V140 `0x20003403`。若初次讀值是 255，直接正常返回，A0 保留入口 Q。否則保存 Q、呼叫 RAM `0x20000236(6)`；配置返回零時正常返回零。

配置成功取得 M 時，依原指令順序組成六個可見 bytes：

```text
M[0..5] = F0 00 27 Q[1] Q[2] Q[3]
```

三次 Q 讀取與相應 M store 交錯，沒有聲稱它們是原子快照。**本體不讀 Q[0]**；也沒有 Q 的 null／extent 檢查。

上層 record callback 的 Q 是 SP+12，所以實際明示讀取為 SP+13、SP+14、SP+15。完整上層本體已有這三個 byte 的本機寫入來源：N+8、零、fresh child+4。SP+12 本身仍沒有本機寫入，但這個相符 notifier 不需要讀它。此結論仍依賴來源／frame 有效、別名與 callee 保存、實際綁定等前提，不能延伸為任意未知 provider 都不讀 SP+12。

notifier 本機 store 不發布 Q 指標，後續子呼叫也沒有以明示參數傳 Q；這不排除未知程式從 ambient registers、別名或外部狀態觀察／保存它。上層在任何正常通知返回後都清 child+10，沒有檢查通知是否成功。

## 配置、送出與釋放界線

重用[message wrapper](v4160-message-marker-static.zh-TW.md) 與[入佇列合約](v4160-threshold-message-static.zh-TW.md)的完整原指令驗證：六 byte 可見訊息對 core 的請求為 size 14、tag `0xF006`，失敗提示值為 `0x000EF006`。若 core 私有 header 是 H，core payload P=H+8，wrapper 返回 M=P+8=H+16。

wrapper 寫入 P+0 的 next=0、P+4 的 U16 length=6、P+6 的 marker=255。P+7 未因此初始化；不可把 header 與六個可見 bytes 的寫入說成整塊配置完全初始化。

組裝完成後，notifier 再讀一次 task byte，將 fresh task 與 M 交給 sender。它先恢復自己的 16-byte frame，再以無新 link 的 tail jump 送出；上層 64-byte frame 尚未因這個 tail 消失。兩次 task 觀察不能當成同值，fresh task 也沒有重新檢查 255。

sender 的 task 必須同時大於 2、且小於 fresh U8 task count；256×256 個 scalar 組合中有 31,878 個滿足此式。非空 M 也須符合 next=0 與 marker=255。無效 task／header 的分支請求 deallocation；這不能證明真實釋放，因公開 release 仍以 M=H+16 轉送，不能套用只對另一個 exact-payload 指標成立的 free 證明。

符合條件時才寫 task marker、append 到全域鏈表並呼叫 event(task,0x8000)，sender 忽略 event reply 後返回零。實際 provider、鏈表有限性、task 消費、delivery、釋放與完整 ownership 均未證明。

## 私有 selector 的完整輸入與輸出

令 N 為入口物件。明示非 frame 輸入只有：U32 N+140、U16 N+136、U32 N+160、U32 N+164，以及初次 bit 為零後才 fresh 讀取的 U8 N+129。唯一非 frame store 是 U8 N+126。沒有物件 null／extent guard；兩個完整 mask word 的讀取要求至少 168-byte 可讀範圍。

令 `R16` 為各 byte 內 bit 反轉、保留兩個 byte 的原 lane，所有 low16 均取低 16 bits：

```text
K = low16(U32[N+140] XOR (U32[N+140] >> 16))
x = U16[N+136] XOR K
重複三次：x = low16(17 * R16(x) + K)
s = low16(x XOR K)
initial = s % 37
```

初次對 held mask `U32[N+164]:U32[N+160]` 測試 initial bit。若它為 1，寫 initial 到 N+126。否則計算 `rank=floor(freshU8[N+129]*s/65536)`（0..254），從索引 0 至 36 掃描 set bits；ordinal 從零開始，匹配 rank 時寫當前索引。掃描耗盡則仍寫 initial，**不保證該 bit 已被設置**。

迴圈 counter 從零每次加一，到 37 結束；ordinal 最多 37，不會 byte wrap。在相符 child 正常返回與無干擾等前提下，至多 37 次 scan call，加上初次測試共 38 次。這是固定 CFG 與整數界線推導，沒有重播可變 selector 狀態。

44-byte child 只變動 A0/A1/A2/A5，沒有 frame、資料記憶體讀寫或子呼叫。僅在上層可達的 count 0..36 證明它等於 logical 64-bit pair right shift；不推廣到任意 count ABI。父函式 AND 1，故只觀察 held mask 的低 37 bits。B+120 optional copy 五 bytes 到 N+160..164 涵蓋這些有效 bit，但不能單獨證明其餘完整 word 可讀且來源全部初始化。

**A0 是最後一次測試得到的 bit，不是 N+126 索引或成功旗標。** 掃描耗盡時也可能返回 0 或 1。B+120 呼叫端在其後明示設 A0=2 再呼叫下一服務，未直接採用 selector 回傳值；較後 record callback 會讀 N+126 並 AND 127。兩處是否實際為同一物件、欄位是否保存、全域執行順序與 installed provider，仍沒有完整證明。

## 可重播驗證與剩餘工作

```powershell
python analysis/check_v4160_b1_notify_selection_static.py
python -O analysis/check_v4160_b1_notify_selection_static.py
```

兩種模式都核對完整祖先證據、嚴格 HEX、固定帳本；548 個逐指令變異與 10 個 typed-load 變異必須被拒絕。另核對 256 個 byte permutation、65,536 個 word permutation、262,144 個 modular-round identities、2,368 個 shift bit-basis 與 65,536 個 sender task/count scalar 組合。這些是 host 上的封閉代數／範圍檢查，不是目標韌體執行或硬體模擬。

後續仍需展開私有 `0x43414`／`0x5c830`／`0x5d006` 等服務、實際綁定與來源 writers，以及通知訊息的消費／釋放、實際 RX 長度、TX delivery、callback 順序和完整指標保存期。原始 APP／carrier／HEX 不修改；沒有硬體連線、目標流量或動態 target 執行。
