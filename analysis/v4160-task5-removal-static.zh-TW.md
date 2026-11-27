# task5 物件移除、backing reset 與 ID 清理：完整原指令合約

接續 [table0／物件 cleanup](v4160-task5-object-static.zh-TW.md)，本輪展開 cleanup 的 object-key 與 ID helpers。原始目標仍為 ID-2966 V4.1.60 APP、76,800B；V1.31／V1.40 resident 為參考候選，尚未證明是原機 installed provider。

| 完整本體 | V1.31 | V1.40 | 各版本 bytes／指令 |
| --- | --- | --- | --- |
| key remove | `0x57A4A..0x57AC4` | `0x57B8A..0x57C04` | 122B／43i |
| backing reset | `0x57A1E..0x57A4A` | `0x57B5E..0x57B8A` | 44B／15i |
| ID clear | `0x43A14..0x43A8C` | `0x43AA0..0x43B18` | 120B／43i |

合計 **572B／202 指令**，全部由原始 sparse HEX 完整提供，與 candidate bytes 相同。新合約固定每條 operand／hash／CFG，沒有為缺失 source 指派補值；不是新增 C 重建覆蓋。

以下 B=`0x200033B8`／`0x20003408`、C=`0x2000319C`／`0x200031EC`。remove 使用 registry head B156、tail 欄位 B160、U16 count B180；reset 使用 backing pointer B172。這些是原指令使用的欄位角色，沒有由名稱推定完整 ownership 或實體功能。

## key remove：第一個符合 key 的物件

入口 requested ID 保持為完整 RV32 值。函式先取樣 B156，沿 cur+0 next 掃描，逐一比較 fresh U16[cur+8] 與完整 ID，選第一個 match。每輪先以 cur==0 判斷是否結束，才讀 key；沒有本機 extent 或 cycle 檢查。重複 key、實際物件身分與鏈表有限仍需來源證據。

匹配後的本機 unlink 分支：

| 分支 | private release 前的 stores |
| --- | --- |
| prev=0，匹配 head | B156=captured head 的 next；**不更新 B160** |
| prev!=0，fresh B160==cur | B160=prev；此分支沒有立即改 prev.next |
| prev!=0，fresh B160!=cur | prev.next=cur.next |

接著把 **cur 原值**傳給 private release `0x20000110`。這與前輪 cleanup 呼叫 private release(node+4 的 payload pointer) 不同；此處確實提出匹配物件指標的 cleanup attempt，但是否成功釋放對應區塊，仍需要 cur 的配置來源、containing header、heap globals／account、nonalias 等證據。

### release 呼叫之後還有 tail 存取

remove 在 private release 正常返回後，重新讀 fresh U32[B160]，直接 `SW0[tail+0]`，**沒有 null guard**。只有這個 store 之後才處理 count。

若只有一個物件，且 head=cur、cur.next=0、tail 欄位保持 cur，head 分支會將 B156 寫成 0，但沒有把 B160 改掉。於是後續 fresh tail 仍可能是 cur，並在 cleanup attempt 後寫 cur+0。

這條原始路徑已固定在 checker。它不證明 private release 已成功，也不證明後續 store 仍具有有效 ownership／保存期；更不能自行補上一個 tail reset、交換 free/store 順序或把單節點分支當作已安全完成。缺少的是配置與 lifetime／writers 證據，並非本輪執行了任何 free 或裝置程式。

## count、未命中與 reset 的關係

匹配路徑在 tail store 之後讀 fresh U16[B180]：非零時減一並以 SH 寫回，再重新讀 count；零時不做減法。需要 reset 的兩種入口為：

- 剛才取樣的 count 已為 0。
- 減法後重新讀到 count=0。

reset 正常返回後，remove 再寫零到 B156。若沒有 key match，也會在掃描結束時讀 fresh count：count=0 仍會呼叫 reset 並清 head；非零則直接返回。**沒有證明 count 與實際 list 長度一致**，不可由這個 count 分支推回掃描身分或物件數。

remove 沒有固定成功返回碼。未命中且 fresh count 非零時，這條路徑沒有 callee 或本機 A0 定義，因此返回原 requested ID；其他路徑可能轉送 private release／reset 的 then-live A0。不能把 requested ID 恰好為 0、2 或其他數字時的回覆，解讀成統一 status API。

## backing reset：清 pointer 不等於釋放已成功

reset 先讀 fresh B172 到 A0；非零時以原 pointer 呼叫 private release，正常返回後才 SW0 到 B172。初始 pointer=0 時略過 callee，但同樣 SW0 B172。

這個函式沒有本機 B160／B180 store，也沒有直接清 registry head；remove 才在 reset 後清 B156。pointer=0 路徑可由本機 load 得到返回 0，nonnull 路徑則轉送 private release 的 A0；沒有額外成功判斷。B172 原指向何種配置、是否與其他 owner 共用、release 是否有作用，仍未封閉。

## ID clear：0～47、三組 record 與停止事件

ID clear 保存 control word `0x4002420C`、寫零並執行原始 `FENCE.I`，再以 unsigned 比較檢查完整 ID<=47。超界時還原 control／frame，返回 **2**，不讀 arena。

對有效 ID：

```text
offset = 12 * ID
group  = ID >> 4         // 0～2
mask   = low16(1 << (ID & 15))
```

先從 slot C144（`0x2000322C`／`0x2000327C`）取得 arena pointer，讀取 arena+offset 的 word0；它為 0 時返回 **2**。arena pointer 本身沒有 null guard，需有效且範圍足夠。

word0 非零時，呼叫既有 stop-task `0x439A8`／`0x43A34`(group,mask)，之後不檢查其 scalar 回覆。原指令重新從 C144 讀取 fresh arena，清除 fresh arena+offset 的 words0／4，再返回 **0**。本機沒有清 metadata+8，也沒有呼叫 record 的 callback、free arena 或 free callback argument。

兩次 arena sample 之間有 stop-task 呼叫。只有 pointer／offset／frame 及必要欄位保持有效，才能把「先前確認 active」與「稍後被清」視為同一個 record。stop-task 返回 0 或其他正常狀態都不會改變這兩個本機 clear；實際取消、原子性與事件送達仍未證。

48 個 ID 覆蓋三組各 16 records。576B 有效 arena 足夠涵蓋這個靜態 footprint；此算式不證明 arena 實際配置、所有 ID 可達，或 metadata 的真實用途。

## 接回 cleanup 與 parser

前輪 cleanup 會取樣 O39、O38、O40、O41；只要 byte 不等於 255，就呼叫本輪 ID helper。因此值 48～254 也會進入 helper，只是返回 2。cleanup 不測試該回覆：**O41 即使被 helper 拒絕，也會在正常返回後被本機寫成 255**；O38／O39／O40 沒有對應的本機 invalidation。

cleanup 接著以 fresh U16[O8] 呼叫 remove。key-only lookup／remove 選到的物件未必就是原 O，需要 first-match identity／唯一性與保存證據；即使提出 private release(cur)，也不能直接宣稱原 O 已經釋放。

cleanup 在這個呼叫之後不再解參考原 O，後段使用固定 B／C 全域。reason5 parser 在 cleanup 返回後同樣不再解參考 O，自行將 scalar status 設為 0。這個局部順序有原指令證據，但不能取代 nested release、tail post-access、message／object 分離與完整 lifetime 證明。

## 驗證與剩餘界線

[checker](check_v4160_task5_removal_static.py) · [精確 ledger](v4160-task5-removal-static.json)

```powershell
python -B analysis/check_v4160_task5_removal_static.py
python -O -B analysis/check_v4160_task5_removal_static.py
```

202 條新指令各有單點變異拒絕，另有 4 個 count LHU→LH 變異。兩版共 192 條不可變 match-position／count CFG 見證，涵蓋 remove 每條本機邊；reset 與 ID helper 另有 10 條完整 DAG 路徑。全部 48 組 ID／group／mask／record footprint、256 個 caller byte 值及全部 U16 count 寬度均以 scalar 算式核對。

普通／`-O` 須與同一 ledger 逐 byte 相符，核對固定 APP、兩 candidate、SDK raw header 與 Xwchc 來源向量。前提仍包括 conditional ISA、有效對齊的 objects／tailword／arena／frames／heap／globals、normal callee 保存，以及無不利 alias、IRQ／DMA／重入／其他 writers。fresh snapshots 不能無條件當成同值。

未執行原韌體、target ISA、registry／heap／event 模型、provider、callback、MMIO 或硬體。GitHub 僅新增本輪三份分析檔；原 BIN、既有工作與 C 重建覆蓋率不變。後續需追查 object／B172 的配置來源與 post-release tail 保存期，並展開 V34 的 payload 處理與實際 provider／task binding。
