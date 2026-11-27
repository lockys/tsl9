# B0 記錄查找、前綴清理與兩層 callback pointer

接續 [B0 case18／case22](v4160-typeb0-cases-static.zh-TW.md)，本次完整核對記錄陣列lookup、記錄清理，以及獨立callback鏈表的getter與wrapper。兩份參考候選合計 **352 bytes／134條指令**，全部由原始sparse HEX覆蓋，且與候選bytes一致。這是條件性靜態合約，沒有提高既有C重建覆蓋率；實際installed provider、queue進展及完整pointer保存期仍未證明。

| 完整範圍（右端不含） | V1.31 | V1.40 | 每版 |
| --- | --- | --- | --- |
| record clear | `4B5D2..4B61E` | `4B66A..4B6B6` | 76B／30i |
| array lookup | `4B61E..4B650` | `4B6B6..4B6E8` | 50B／16i |
| callback list getter | `4B650..4B66C` | `4B6E8..4B704` | 28B／11i |
| callback pointer wrapper | `4B66C..4B682` | `4B704..4B71A` | 22B／10i |

前三個函式各有一條構成cycle的edge；wrapper為DAG。每個byte、operand、call target與完整CFG固定在[checker](check_v4160_typeb0_record_static.py)及[ledger](v4160-typeb0-record-static.json)。沒有把不同函式的相鄰bytes誤算成同一個body。

## 記錄陣列：一次讀count，一次讀base

array lookup進入後，分別捕捉：

| 用途 | V131 | V140 |
| --- | --- | --- |
| unsigned count byte N | `200033B5` | `20003405` |
| record array pointer P | `20002F8C` | `20002FDC` |
| 另一路callback list head | `20002F94` | `20002FE4` |

count與P是兩個不同時間點的讀取，不是原子配對。callback list head則是另一個儲存格、另一個資料結構，不能和陣列base混用。

lookup以index0開始；只要index不等於捕捉的N，就讀取 `U16[P+184*i]`，與**完整入口A0**比較。第一個相符的record返回該record地址；不相符時index加1並AND255，再繼續。沒有本機store、service call或SP改動。

- N=0時仍讀取P所在的global word，但不解參考P，返回0。
- N>0時沒有P非空檢查，需另證有效extent。
- 因N來自U8，最多255次record key probe；index到N時退出，不需先回繞到0。
- key讀值為U16，但入口A0未截成U16；大於65535的full-register key不可能相等。
- first match不是key唯一性證明，也沒有檢查record其餘欄位。

## 接回較早的184-byte記錄來源

重用 [ID8 resources](v4160-id8-initialization-static.zh-TW.md) 的完整原指令：它從相同count byte取得數量，把allocator回覆寫到上述P word，並以184-byte stride建立外層記錄、每筆含15個12-byte內部槽位。

這接通了array lookup與case22的object形狀，但不是對執行時P、N或配置大小的無條件證明。較早的request、fill與layout使用分開的fresh count；相同配置、來源保存、count一致及有效extent等條件仍須保留。若既有low2來源也持續保存，count可另收緊為0..3；本getter的一般U8域仍為0..255。

case22以message ID呼叫array lookup，失敗再查65535。前一階段已驗證：只有fallback查到record時才SH原ID到record+0，第一次直接查到時不寫該key。清理函式最後的key=`0xFFFF`與這條fallback來源因此有條件地接上；未證明record沒有其他writer或多筆相同key。

## Clear只處理第一個空槽之前的連續前綴

clear以原record O建立16-byte frame，從slot=`O+4`走到endpoint=`O+184`，步長12。每次先讀slot的U16 head：

```text
head == 0 -> 立刻離開迴圈
head != 0:
    Pslot = fresh U32[slot+8]
    Pslot != 0 -> private_release(Pslot)       // 20000110，原值
    fill(slot,0,12)                           // 2000039C 的明確實參
    slot += 12
    U16[slot-12] = 0                          // 直接清前一槽head
    slot != O+184 -> 下一次probe
```

每個已處理槽位都會嘗試fill12，並在返回後直接清head；是否嘗試private release另取決於fresh slot+8是否非零。release傳入的是**slot+8讀出的word**，不是slot地址或record O。

最多處理15槽。若途中先讀到0，該槽與所有後續槽位都不再由這個本機迴圈探查。所有普通返回路徑最後仍會SH `0xFFFF`到原O+0；沒有直接清除O+2..3，也沒有直接釋放整筆record。

因此「key已改為FFFF」不能單獨證明全部15槽都已清理。例如只作純bitstring分析，若slot0 occupied、slot1空、slot2 occupied，迴圈會在slot1結束，後面的slot2沒有被本機走訪。要推導全部active slots都已處理，還需要證明occupied slots始終是從slot0開始的連續前綴。

checker核對全部32,768種15-bit占用形狀；只有16種是純連續前綴。這是有限純量域與原CFG的條件證書，不是對真實RAM、資料可達性或已發生故障的重現。未知provider、alias或其他writer的間接影響仍不能排除。

即使實際fill符合byte-zero合約，完整清理仍另需valid pointer、配置身分、普通callee返回及S/SP/RA／saved-frame保存。沒有執行release/fill，也沒有證明每一次嘗試成功。

## 返回值與模式1 caller

first slot head=0時，clear不呼叫任何服務，A0保持原O。若處理了非空前綴，A0是最後一次fill的then-live回覆；函式沒有強制返回0，也沒有採用private release的scalar作成功判斷。

重用 [已發布的record callback](v4160-special-event-callback-static.zh-TW.md)：其mode1呼叫此array lookup，回覆非零才以該record呼叫clear，之後無條件進入後續enumeration。這裡不把clear的普通返回當成清理全部完成，也不由後續enumeration呼叫推導有限鏈表或物理進展。

## 接回case22保存的pointer

case22對選中槽位準備 `copy(slot,M+8,12)`；在byte-copy語義、欄位保存與無alias等前提下，原M+16的word值會落在slot+8。這與本次clear的private release實參來源吻合。

但case22是在後續request／report之前呼叫slot copy；它們失敗時沒有本機rollback。槽位可能保存原pointer值，而當時父handler又可能走selected-word cleanup。這些只是已核對的來源與呼叫順序，尚未證明兩個時間點必定是同一配置、pointer仍有效、只有一個owner，或unknowncallee未更改它們。

要封閉保存期，仍需追查其他槽位consumer／writer、occupied prefix不變條件、實際copy／fill／release/provider綁定及各分支的配置身分。

## Callback pointer有兩個不同的+8讀取

獨立callback list getter從自己的global head開始，沿 `U32[node+0]`走鏈表，將 `U16[node+4]`與完整入口key比較。第一個key相等時，**返回U32[node+8]的值**；不是返回node地址。若一路未命中而走到null，則返回0。

它沒有count、cycle detection或本機call/store；只有有限、有效、無干擾的鏈表前提才能保證搜尋結束。命中節點但node+8的值為0，也返回0，不能僅由回覆0區分未命中與命中空value。

22-byte wrapper再處理getter回覆：

```text
V = callback_list_getter(key)
V == 0 -> return 0
V != 0 -> return U32[V+8]
```

這是node+8與V+8兩層不同解參考，不能壓成「鏈表節點+8就是callback function」。wrapper只讀出word，不執行它；case18／22之後才對非零回覆作indirect call。真正的node／V來源、extent、function pointer有效性與ABI仍未閉合，回覆非零不等於可安全呼叫。

## Frame與離線重播

clear的16B frame保存RA/S0/S1/S2；wrapper另有16B frame只保存RA。兩個readonly getter不改SP。這些原指令保存證據仍以callee普通返回與saved frame未被破壞為前提，不是no-escape證明。

```powershell
python -B analysis/check_v4160_typeb0_record_static.py
python -O -B analysis/check_v4160_typeb0_record_static.py
```

檢查涵蓋完整operands／hash、每條CFG edge到RET的見證、空前綴／一槽／15槽清理、255筆array lookup、有限鏈表搜尋見證、兩層callback解參考、134條指令與8個typed-load變異，以及32,768個占用bitstring與256個count域。

GitHub僅新增本階段三份分析與驗證檔案，原BIN與既有工作保持不變。全程只讀本機bytes、原始HEX、不可變CFG與host純量；沒有執行或模擬目標ISA、callback、provider、RAM／heap／list、MMIO或硬體。下一段繼續追查callback list writers、槽位consumer與其他下游合約。
