# v4.1.60：heap bootstrap、sum walker 與後段 reset 的完整靜態合約

日期：2026-11-26。承接 [post-config callee](v4160-post-config-static.zh-TW.md)，展開其中 heap-init／late-init 兩個呼叫邊，以及 heap-init 內唯一的 walker。新 [檢查器](check_v4160_heap_bootstrap_static.py)／[JSON ledger](v4160-heap-bootstrap-static.json) 固定兩版本全部本體、operands、寫入順序與 CFG，另外核對原 APP 設定指令窗。沒有執行或模擬 ISA、heap／linked-list state、provider 或 MMIO，C 還原覆蓋率未增加。

## 六個完整本體

各版本 walker 36B／13 instructions、bootstrap 112B／36 instructions、reset 10B／3 instructions；合計 **316 bytes／104 instructions**。區間終點均不含。

| 候選／角色 | flash range | SHA-256 |
| --- | --- | --- |
| V1.31 walker | `430e0..43104` | `8f1f4e0425a68707da3ab94395611ae4190c0c42917bd52688d01d893d8bb035` |
| V1.40 walker | `4316c..43190` | `cd3672ac77f49ab93fd3ef6fb79b745701f4a95973976e65b9f8a03d91760f6b` |
| V1.31 bootstrap | `43104..43174` | `08fabd9e35085e531dc922755f25e9bbc0b59436321f0e379a98382cafc8bc9f` |
| V1.40 bootstrap | `43190..43200` | `284aeff7f1aeda778c7d5d781d881b2e61dd1b5bc3cde69448e3e93906d98154` |
| V1.31 reset | `4329a..432a4` | `20b6e8c0db1202a821074e9d59f332d7f232de9d0f830fc7a28a5a310b3ddec6` |
| V1.40 reset | `43326..43330` | `17fbeb7a0e85fa837644f95ad788d07d604ce2004353b56869dec4e771ee6e55` |

bootstrap／reset 的數值 entry 分別與前輪兩個 call targets 相符，bootstrap 的 compressed JAL 也接至同版本完整 walker。解碼仍以固定 LLVM 來源／vectors 支持的條件性 Xwchc 與標準 RV32I/C 語義為前提，不證實體 ISA 或 installed 身分。

## 從設定欄位計算幾何

| 候選 | config base | small-head slot | large-head slot | sentinel slot | accounting U16 | reset U32 |
| --- | --- | --- | --- | --- | --- | --- |
| V1.31 | `200031ec` | `20003194` | `20003190` | `2000318c` | `200031a2` | `20003198` |
| V1.40 | `2000323c` | `200031e4` | `200031e0` | `200031dc` | `200031f2` | `200031e8` |

bootstrap 分別 fresh 讀 H=U32[config]、L=U16[config+4]；不是原子設定快照。本體 operands 支持：

```text
A = (H + 544) & 0xffffffff             # small head
E = (H + L - 8) & 0xffffffff           # sentinel
S = L>>3 if L<=0x1007 else 512
B = (A + S) & 0xffffffff               # large head
small_size = (S - 8) & 0xffff
large_size = (E - B - 8) & 0xffff
```

在 U16 L 的算術域，S 等價於 `min(L>>3,512)`。這個函式沒有本機檢查 H／L 是否構成有效 heap、對齊、足夠長度或不回繞。小長度可以造成 halfword size 截斷／下溢或 header alias；算式成立不代表存取合法。

## 十一筆 bootstrap store 的順序

完整 census 依序為：

1. small-head slot=A。
2. sentinel slot=E。
3. 建立 16-byte frame 後，保存 RA 至當時 SP+12。
4. large-head slot=B。
5. U32[A]=B。
6. U16[A+4]=small_size。
7. U16[A+6]=0。
8. U32[B]=E。
9. U16[B+4]=large_size。
10. U16[B+6]=0。
11. walker 正常返回後，U16[accounting]=low16(A0)。

第 3 項的 frame 減法實際發生在第 2 項 store 之前；列出的順序是 stores 的順序。caller RA 在 walker 返回後、accounting store 之前從 frame 重載。本體沒有寫 sentinel 所指的 header。

若動態 H／A／B、固定 globals、stack、code 或外部 writer 相互影響，就不能把這些公式當作最後記憶體狀態。ledger 保留實際指令順序與地址公式，未建立合成 heap。

## walker：入口快照、逐節點 fresh reads

walker 在入口只讀一次 small-head 與 sentinel，存於 A5／A4，A0=0。每輪先比較 current 與保存的 sentinel：

- 相等便返回，不讀 sentinel 的 flag、size 或 next。
- 不等時 fresh 讀 U16[current+6]；只有 flag=0 才 fresh 讀 U16[current+4] 並加至 A0。
- fresh 讀 U32[current] 作 next，繼續比較。A0 累加採 RV32 模數加法。

沒有 pointer-bit 正規化、null／範圍／對齊 guard、cycle detection 或 iteration bound。每份 walker 有一個七節點 SCC，offsets 為 `18,24,26,28,30,32,34`；穩定且未抵達 sentinel 的循環可不返回。head／end 不會每輪重新載入，節點欄位則逐次讀取。

walker 無 store、stack 操作或 nested call，encoded GPR writes 僅 A0／A3／A4／A5。bootstrap writes 為 RA／SP／A0..A5，reset 只寫 A5；這些是本體指令集合，仍以正確 profile、code 穩定及有效存取為前提。沒有固定 MMIO operand 不等於任意 H／next pointer 的存取都不會落入 MMIO。

## 原 APP 的名義幾何證據

`0x19a3a..0x19a4a` 的 16-byte 指令窗以 AUIPC／ADDI 得 H=`0x2000418c`，存至 SP+16；另把 L=`0x7000` 存至 SP+20。新檢查器核對這五條指令及目的寬度，不把它們自動提升為後來 resident config 的 live 值。

若這份設定經必要呼叫／copy 保持適用，且 headers、globals、frame、code 不受不利 alias／干擾，名義算式為：

| 項目 | 值 |
| --- | --- |
| A | `0x200043ac` |
| S | 512 |
| B | `0x200045ac` |
| E | `0x2000b184` |
| small payload size | 504 |
| large payload size | 27600 |
| 兩個 size 的算術和 | **28104（`0x6dc8`）** |

兩個互不重疊、欄位保持所需值的節點若形成 A→B→E，才可把這個和接到 walker 的正常回覆與 accounting store。檢查器只做位址／數值代數，沒有建立或走訪這條鏈，也不證明啟動完成、物件 ownership 或物理 RAM 可用性。

對不回繞的數學幾何且 L≥639，兩個未截斷 size 皆非負，和為 L−568；這不是所有這類 L 都具合法對齊／mapping 的證明。generic walker 對任意鏈仍可能累加超過 U16；caller 只把回覆的 low16 存到 accounting，A0 本身未被該 store 截斷。

## 後段 reset 的範圍

`4329a/43326` 的完整本體都是 LUI／SW zero／RET，只清上表 reset word，encoded instructions 不改 A0。這是前輪 late-init 邊界的本機效果；緊接其後的 `44022/440b6` 及其中巢狀 provider 仍沒有由本輪解除未知。

bootstrap 的四個固定 cursor／accounting 目的及 reset word 均與 fallback `20003220/20003270` 不重疊。但 heap headers、SP-relative 保存字及 walker 讀址仍需個別的有效性／不重疊條件，不能據固定 globals 的分離宣稱整條鏈不碰 fallback 或 saved frame。

## 實際重播與反例

```text
python analysis/check_v4160_heap_bootstrap_static.py
python -O analysis/check_v4160_heap_bootstrap_static.py
```

兩模式均實際輸出：

```text
PASS: 65536 split distances; 64897 nonnegative size identities; 32 wrapped geometry cases; APP witness; 10 specified raw mutations
PASS: 6 complete candidate bodies, 316 bytes/104 instructions; 24 local stores; linked walker call; APP16 operand pin
PASS: ledger exact replay; installed/geometry validity/termination UNPROVED; NO ISA/provider/heap/MMIO execution
```

24 stores 指兩版本各 11 個 bootstrap stores 加 1 個 reset store；APP 指令窗另有兩筆設定 stores，不混入候選 body census。65536／64897 cases 是 U16 算術域與非負 size 恆等式，32 cases 是四個 H × 八個 L 的模數地址例證，均非 heap 或 CPU 狀態執行。

十種 raw mutations 改 walker sentinel 比較、flag offset、next offset、bootstrap threshold、split cap、第一個 size store offset、第二個 flag store offset、accounting offset、reset word offset、APP H 的 ADDI。每種直接進入推導並要求指定 guard 拒絕，不以全檔 hash 不符或任意 decoder exception 充作通過。

重跑需八個已發布 Python dependency 模組，以及既有本機 APP、兩份 carrier、SDK header 與 LLVM 欄位／vector 來源。候選輸入目錄未隨本次發布，僅 clone repo 不足以重現。預設只讀重算並精確比對 JSON；`--write` 僅建立不存在的 ledger。

剩餘範圍：`44022/440b6`、其實際 callback／輸出 buffer 合約、其他可達 writer、後續 pointer／capacity 穩定性與 installed resident 綁定。先前完整 sparse HEX 最後缺失的 4-byte 啟動來源也未由本輪補值或執行。
