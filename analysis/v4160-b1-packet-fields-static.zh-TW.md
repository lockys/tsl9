# v4.1.60：資料欄位解析、部分輸出與 B+120 發布來源

這次封閉一個從物件 N+80 指標讀取資料的完整 parser，以及相鄰但獨立的 B+120 publisher。Parser 有具體 type／length／flags 欄位規則；這些規則仍未證明來源的實際 ingress 長度。Publisher 寫入的是另一個函式地址，不是 parser。

[驗證程式](check_v4160_b1_packet_fields_static.py)與 [JSON ledger](v4160-b1-packet-fields-static.json)只核對原始 bytes、operands、strict sparse HEX、不可變 CFG 與 host 欄位算術。未執行或模擬目標 ISA、RAM、packet、provider、callback、MMIO 或裝置。

| 完整本體 | V131 半開區間 | V140 半開區間 | 每份 bytes／指令 |
|---|---|---|---:|
| parser | `[0x5d9ac,0x5da52)` | `[0x5daf4,0x5db9a)` | 166／68 |
| publisher | `[0x5da52,0x5da64)` | `[0x5db9a,0x5dbac)` | 18／5 |

新增原指令驗證 **368 bytes、146 條指令**。另重驗完整 RAM service 共256 bytes、node creator共388 bytes、dispatch callback共2,218 bytes與table共104 bytes，均不重複計為新增。本次沒有增加既有 C 重建覆蓋率，也沒有證明參考 resident 候選等於實際 installed provider。

## 先請求服務，再重新讀取資料指標

Parser 擷取入口 N=A0、輸出 O=A1，使用16-byte frame保存 RA、S0、S1。先讀 fresh U32[N+80]，請求：

```text
RAM 0x2000263a / 0x20002686(fresh N80, 0, low32(O+1), 0)
```

完整 matching service 的合約已重驗：A1=0會跳過 entry A0 的 packet 解參考，A3=0跳過 signed halfword輸出；若 A2非零且初始 bit5 gate通過，可以先寫 byte[O+1]，再寫全域狀態 byte並返回0。初始 gate未通過返回1，不作這些 data stores。O+1的有效範圍、不回繞與不利別名排除仍是前提。

Parser 對任何非零 service回覆固定返回1；自身後續 data stores全部略過。這不代表未知provider沒有副作用。服務回覆為零時，parser **重新讀取 N+80到P**，沒有把它與呼叫前傳入的指標視為同一 snapshot。

## 寫入 type／length 後才做欄位 gates

讀取皆為byte，且不是不可變 packet快照：

1. 讀 P+0，將低4位寫入 N+19；讀 P+1，將整個byte L寫入 N+18。
2. 低4位不等於7，返回7。N+18／N+19已被寫入。
3. 讀 P+2。令 d=低6位、h=高2位；先要求 d<L，否則返回3。
4. 再要求 h=0，否則返回5。
5. 寫 byte[O+5]=L−1−d，接著讀 P+3 flags。

完整byte域中，h=0且d<L共有14,304組，算術結果位於0..254，不會在這個 gate下發生減法下溢。這只是欄位關係：沒有證明 L等於實際buffer extent、來源曾完整初始化或後續所讀bytes在真實接收長度內。

## Flags、可選欄位與固定回覆

| 檢查順序 | 原始條件／動作 | 本機回覆 |
|---|---|---:|
| 第一個flags gate | bit1設置，直接退出；O+5已寫 | 17 |
| 選擇欄位 | bit2設置：讀P+4低2位寫O+2，cursor=P+5；否則O+2=255，cursor=P+4 | 繼續 |
| 下一個gate | bit3設置 | 20 |
| 再下一個gate | bit4設置 | 21 |
| 最後拒絕gate | bit5設置 | 22 |
| 正常路徑 | bit6設置時讀byte[cursor]，否則用literal127；寫O+0 | 0 |

所有拒絕均按原指令優先順序處理。bit3／4／5的失敗路徑已寫O+5與O+2；matching service也可能較早寫O+1。因此錯誤回傳不提供 transactional no-write保證。

本機回覆集合為 **0、1、3、5、7、17、20、21、22**。這些數值不自行命名為協定錯誤或實機狀態；0也不代表已形成完整輸出record。

直接來源讀取最多到P+5，需要最多6個可讀bytes；N明示存取需要至少84 bytes。輸出O明示欄位是+0、+2、+5，matching service可能寫+1；O+3／O+4沒有本機初始化，因此不能聲稱完整6-byte輸出已形成。所有存取皆無本機null guard，動態別名、code／frame／N／O／P保存與物理干擾仍需另證。

## N+80 的條件性來源

完整既有node creator `0x5397c..0x53a3e`／`0x53a2a..0x53aec`重新核對：它從固定 S+36 fresh讀取word，存到新node N+80；S分別為`0x20003514／0x20003564`。這連回先前的來源鏈，但尚未證明 parser入口的N就是該次建立的node，也未證明N+80、S+36或P在中途保持原值。

即使條件性指標來源相同，也沒有找到實際填入P所指bytes的producer。硬體面向的 pointer publication、另一條APP ingress或同名欄位，均不能取代資料內容／長度／物件身分的證據。

## B+120：具體函式位址，仍不是 parser 綁定

相鄰publisher是獨立18-byte leaf，沒有frame或child call，也不改A0。它寫出：

| 候選 | 固定B | 寫入位置 | 寫入函式位址 |
|---|---|---|---|
| V131 | `0x200033b8` | B+120=`0x20003430` | `0x5d5c4` |
| V140 | `0x20003408` | B+120=`0x20003480` | `0x5d70c` |

重驗完整dispatch callback與table，並以encoded reaching definitions核對相關讀取的S1確實來自形成B的+0x28定義。Dispatch會fresh讀B+120，沒有null guard，以其先前擷取的N作A0間接呼叫。

只有publisher先執行、槽位／code／frame／callee context保存等條件成立，才能把這個數值publication帶到實際call。寫入值**不是**`0x5d9ac／0x5daf4`；目標`0x5d5c4／0x5d70c`的完整本體仍未封閉，不宣稱它已呼叫本次parser。

## B+125：先分清楚消費的bit

既有dispatch的兩個固定B+125讀取位置，V131為+0x2d8／+0x342，V140為+0x2da／+0x344；它們檢查的是 **bit0**。上一階段IRQ零分支的OR2／OR8則分別設定bit1／bit3，不能當成直接對應的完成條件。

另外已定位到上述未封閉B+120目標內的bit1 waits；目前僅列為後續完整函式驗證入口。沒有將局部視窗算成新完整函式，也沒有宣稱所有B+125 readers／writers、派送順序或polling進展已被覆蓋。

## 重播與後續

兩版parser各15條局部CFG語法路徑都恢復同一frame後到唯一RET；兩版publisher各1條路徑。驗證器核對所有新增指令、11個QingKe byte存取、所有stores、唯一linked-call與source／publisher／consumer串接；拒絕 **146個逐指令變異**。

host欄位檢查包含65,536組P+2／L的scalar cases及256個flags的優先分割，不建立或回放packet。一般與`-O`模式需逐byte重放同一JSON，完整上游證據鏈也重新驗證。

```powershell
python analysis/check_v4160_b1_packet_fields_static.py
python -O analysis/check_v4160_b1_packet_fields_static.py
```

後續優先封閉`0x5d5c4／0x5d70c`，接通B+125 bit1的等待與清除。實際資料內容producer、ingress長度、parser入口物件身分、installed provider、callback順序與完整指標ownership／保存期仍未證明。
