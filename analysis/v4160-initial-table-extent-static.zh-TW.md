# v4.1.60：首次配置至table發布的條件性範圍

本輪把bootstrap、allocator core、fill與post-config的已驗證原指令接起來，收斂到一條具體的首次配置路徑：若heap-init當下fresh設定為APP名義值`H=0x2000418c、L=0x7000`，且符合有效存取、frame／heap／globals分離及無外部干擾等條件，所有post-config request都會命中第一個large block並split，返回固定`P=0x200045b4`。

在這些條件下，進入後續late-init呼叫之前，`P′=P`、`N1=N2=N0`可以由本機寫入範圍推出；callback table與event table都落在新配置payload內。這比前一輪把snapshot等值及extent另列為前提更具體，但仍不是實機目前allocation或provider綁定證明。

全程只做原bytes／CFG及封閉整數、位址區間推導。未建立mutable heap／linked list，未執行或模擬目標ISA、allocator、fill、MMIO或裝置。重用原本體而新增的是串接證明，C重建覆蓋率未增加。

## 證據與截止點

承接 [registration的範圍條件](v4160-task-registration-static.zh-TW.md) 與 [heap bootstrap](v4160-heap-bootstrap-static.zh-TW.md)。程式：[check_v4160_initial_table_extent_static.py](check_v4160_initial_table_extent_static.py)。證據：[v4160-initial-table-extent-static.json](v4160-initial-table-extent-static.json)。所有原APP／candidate／sparse HEX／SDK／Xwchc身分與完整原本體驗證鏈重新核對。

| 候選 | post-config本體入口 | bootstrap返回後的prefix起點 | 證明截止點（不含） |
|---|---|---|---|
| V1.31 | `43b3e` | `43b8c` | `43c00`，即post+194 |
| V1.40 | `43bca` | `43c18` | `43c8c`，即post+194 |

截止點本身是下一個late-init call。此處之後的reset／config-I/O、builtin table stores、APP wrapper或後續registration，都沒有由本輪自動取得保存保證。

重用原bootstrap／walker、完整208-byte allocator core、46-byte fill及完整post-config／registration。core中依名義header與request域選出的56條指令形成閉合有限鏈，不經search backedge或fallback；這是靜態CFG的case proof，不是逐指令執行。

## fresh H/L與APP operand要分開

APP原指令形成的heap base／length是`H=2000418c、L=7000`。初始化copy、field44 callback、其他writers與實際installed provider仍可能影響之後的fresh設定值，因此本輪明列：**在heap-bootstrap入口讀到這組H/L**，而不只憑更早的APP stores就認定成立。

還需相符code、有效且分離的frame／header／global、正常存取與無不利physical alias／外部writer。下文所有名義範圍與返回推導均使用這些前提。

## bootstrap給出的第一個large block

固定原指令的位址公式產生：

| 項目 | 名義值 |
|---|---|
| small header A | `200043ac` |
| small payload size | 504 |
| large header B | `200045ac` |
| large payload size | 27600 |
| sentinel E | `2000b184` |
| large payload起點P=B+8 | `200045b4` |

bootstrap寫入`A.next=B`、`B.next=E`與兩個free flags=0。固定globals與headers保持一致、無干擾時，walker只需兩個nonsentinel nodes，size sum為28104；sentinel相等時不再讀其next。這是由寫入與讀取關係導出的條件性兩節點合約，並未建立或遍歷模擬heap，也不是任意list的終止證明。

bootstrap返回後至request形成前沒有另一個opaque call。post-config從fresh來源byte形成：

```text
N0 = 14 + 3*((byte>>2) + (byte&3))
q  = 576 + 6*N0
R  = roundup4(q)
```

256種byte產生67種capacity `{14,17,…,212}`；q及R的最小／最大值都是660／1848，且R不發生原core的U16 rounding回繞。所有R都大於52，因此選large head B。

## 首次命中必走split

在上述初始headers保持時，B不是E、free flag=0，27600也大於所有R。差額`27600−R`介於25752..26940，必大於8，所以core直接split：

```text
返回 P = B+8 = 200045b4
配置payload = [P,P+R)
新remainder header = P+R
新remainder size = 27600−R−8
```

remainder size介於25744..26932，且`P+R+8+remainder_size=E`。新header範圍為`20004848..20004cec`；它不是配置payload的一部分。返回payload至少能容納q，沒有將early request直接冒充任意時刻的有效allocation。

選定路徑只走第一個large block，不讀下一個free-list節點，也不呼叫fallback。core的accounting寫入是`U16[context+6]`，與capacity `context+2`及P slot `state+64=context+144`分離；其heap header stores則在名義heap內。

## P′與N1／N2在prefix內為何可相等

post-config先存capacity=N0，再呼叫core；返回P後立刻把它寫入allocation-reply word，之後要求fill：

```text
fill(P,0,576+6*fresh_capacity_N1)
```

完整fill原本體的直接寫入只含目的byte區間與encoded控制word`4002420c`，不定義S0／S1／SP／RA。當heap／frame／globals及MMIO effects無不利alias、無外部改寫時：

- core的account／headers／child frame不改capacity或P slot，因此N1=N0。
- fill範圍`[P,P+q)`與capacity／P slot／hook等fixed globals分離，因此P′=P、N2=N0。
- 此prefix沒有其他未知callee；最後才在post+194遇到下一個call。

這些等值只在明列的局部條件與截止點前成立。valid frame、physical alias及外部干擾並非單憑本輪已驗證。

## table與event table的配置內分區

發布前計算：

```text
T = P+576 = 200047f4
callback table = [T,T+4*N0)
event table    = [T+4*N0,T+6*N0)
T+6*N0 = P+q <= P+R
```

因此兩者都在本次payload內。capacity 14..212存成byte不損失bits；callback table的end介於`2000482c..20004b44`，整個分區的end不超過`20004cec`。

名義heap／table位址高於兩版hook words `2000321c`／`2000326c`與context count byte。這次core／fill／pointer發布，在正常存取、無不利physical alias等條件下不會直接寫hook。

若此後T、capacity與有效allocation仍保存，registration的`n<c`就能把4-byte word footprint限制在callback table內，排除hook／count等alias。但本輪沒有跨過post+194/+198及後續writers，所以尚不能將這個條件性配置範圍當作實際registration當下的狀態。

## 重播與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_initial_table_extent_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_initial_table_extent_static.py
```

檢查包含256個來源byte／67個capacity、28,928個條件性admitted word footprints、原core的56指令case chain、rounding／split／分區等式、所有原本體接點與30個core operand變異拒絕；JSON須逐bytes重播一致。

後續仍需追查post+194/+198 callees及後續table writers、heap H/L進入bootstrap前的保存、allocation生命週期與table／capacity延續至registration的條件，以及實際provider綁定與MMIO／非同步副作用。
