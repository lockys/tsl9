# v4.1.60：ID10 配置、fill 與首次 status／NV 邊界

接續 [ID9 至 ID10 返回](v4160-b1-fallback-id9-static.zh-TW.md)，本輪驗證第五個 initializer 的配置核心、records、兩段共用 fill、saved ID10 發布與 loader 前段。零計數路徑停在第一個 status call 前，正計數路徑停在第一個 NV read 前；尚未接到 ID11／count12。

檢查器：[check_v4160_b1_fallback_id10_static.py](check_v4160_b1_fallback_id10_static.py)；證據：[JSON ledger](v4160-b1-fallback-id10-static.json)。全程核對原始 bytes、不可變 CFG、閉合幾何／區間與 frame 關係，沒有執行或模擬目標、NV、status 或硬體操作，也沒有建立可變 target RAM／heap／provider／MMIO 模型。本輪新增 C 重建 bytes 為0，原始 bin 不變。

## 所選來源域與請求零的含意

令 G=`0x20003000`，V1.31 的 δ=0、V1.40 的 δ=80，F=`G+492+δ`。配置來源是 fresh `U8[F+14]`，本輪額外選 m=0..3 作為條件，不把它當作實際 boot 設定。先前共用來源 b／q／r 的1024組家族各自乘上這四個 NV count，得到1024組 m=0、3072組 m=1..3。

| 項目 | V1.31 候選 | V1.40 候選 |
|---|---|---|
| ID10 wrapper | `0x6c300` | `0x6c4ec` |
| Allocate | `0x6b928` | `0x6bb0c` |
| Loader | `0x6b286` | `0x6b46a` |
| Fresh NV count 來源 F+14 | `0x200031fa` | `0x2000324a` |
| NV pool word | `0x20002fbc` | `0x2000300c` |
| NV count byte | `0x20002fc1` | `0x20003011` |
| NV limit byte | `0x20002fba` | `0x2000300a` |
| ID10 byte | `0x20002fc2` | `0x20003012` |

Allocator 一律被呼叫，請求為 `(16*m,66)`。m=0 走匹配核心的 request-zero 早退、回覆0、發布零 pool pointer；這不是配置成功，也不是 sentinel／fallback 失敗。Count 在所選保存條件下保持0，略過 records 與 F+8 判斷，但仍執行兩段共用 fill16。

## m=1..3 的60組 small-list 幾何

正請求為16、32、48 bytes，tag=`66`，都選 small list。下表 n 是先前 first count 家族；q 仍由先前共用來源 byte 推導，不與 r 任意配對。

| 承接條件 | 所選 free header | 跳過 allocated headers |
|---|---|---:|
| n=0，q=0 或 q>=5 | S=`A+24`，free480 | 1 |
| n=0，q=1..3 | Third small remainder | 3 |
| n=0，q=4 | Third small remainder | 2 |
| n=1..3，q=0 或 q>=5 | First small remainder | 2 |
| n=1..3，q=1..4 | Third small remainder | 3 |

所有正請求另需 fresh small head A 已配置16、tag=`0xff03`、next=S，以及匹配的 allocated header chain／free remainder。即使先前只使用 large arena，也不能因此推得 small head 狀態；這是本輪明列的額外前提。

以 n、特殊 q 分組與 m 合併，共60組幾何形狀，逐一映射至3072組來源家族。各組都滿足 gap>8，P=H+8、N=P+16*m，新 free size=`old_size-16*m-8`，remainder 精確接回 large-list 起點 B；account 減少 `16*m+8` 後按16 bits 截取。Core 有限 CFG 證書跳過1／2／3個 allocated headers，再 fit／split，不讀 fallback slot 或呼叫 failure hook。

所選舊 free header 會刻意變成新 allocated header；其他既有配置 owners 與未選中 headers 都保留。m=4..255、任意不同 headers／配置失敗／非零 fallback 不在本輪已閉合域內。

## Records、共用 fill 與保存範圍

成功配置後，第二次 fresh F+14 被存為 count；迴圈每次又重讀 count 與 pool pointer。它們並非指令保證相等。本輪只在來源／count／pool 保留為 m／P、匹配 core／fill、合法 owned payload／frame、沒有不利介入寫入等條件下接通。

每筆 stride16 record 依序 fill `ff` 六 bytes 於 +0、六 bytes 於 +6，再寫零半字於 +12、零 byte 於 +14。**Byte15 沒有被這條路徑初始化**，不能把整筆 record 宣稱為全零、全 ff 或完全已知。有限 CFG 證書核對 m=1..3 次 record body、byte counter 與所有 write extents，沒有重播目標指令。

兩段共用 fill 都是16 bytes 零值：

| 範圍起點 | V1.31 | V1.40 |
|---|---|---|
| G+380+δ | `0x2000317c` | `0x200031cc` |
| G+364+δ | `0x2000316c` | `0x200031bc` |

所有固定 stores、共用 fills、core accounting／control、配置 headers 與 record stores，都逐家族排除對先前 resource／first 或 second／third／ID8 owners、未選中的 headers、完整第一張 table payload、fallback、F96 的既有保存／預期更新、CB48、ID9 vector36、records0..2、ID／task metadata、timer、ID8 pointers／hooks 的覆蓋。

正配置完成 records 後讀完整 U32[F+8]：零值使 `G+1443+δ` 寫 `0x80`，非零使該 byte 寫0。m=0 路徑完全略過這個更新，不能推定其舊值。其餘 setup stores 與各前提、60組幾何及七條配置 CFG 路徑都列於 ledger。

## Saved ID、frame 與兩個截止點

Allocate 前段先把 ID byte 設 `0xff`；正常返回後，wrapper 從自己 SP+12 重載入口 ID10，覆寫該 byte 為10，並非拿 callee 的 A0 當 ID。Wrapper 釋放32-byte frame 後尾跳 loader；loader 的32-byte frame 重用已釋放範圍。

此階段最高同時存活 outer16＋wrapper32＋allocate32＋core16=96 bytes。到兩個截止點時，只剩 outer16＋loader32=48 bytes。Saved words、S／GP／SP／RA、matching software fill 與實體不別名仍是前提。

| 所選路徑 | V1.31 截止點 | V1.40 截止點 |
|---|---|---|
| m=0，第一個 status call 前 | `0x6b2aa → 0x6af88` | `0x6b48e → 0x6b16c` |
| m=1..3，第一個 NV read 前 | `0x6b2f6 → 0x440c2` | `0x6b4da → 0x44156` |

正計數的第一筆 NV read 參數為 `(512,16,P)`；實際單位、輸出、保留 pointer 與返回合約尚未接通。兩路皆保持 task count11、fallback0、gate5、local ID10=10。m=0 之後仍會執行 status／可能的 optional services 與 save 尾段，所以不能把零記錄當作完整 provider-free 返回，更不能在這兩個 cutoff 宣稱 ID11／count12 已發布。

## 驗證與剩餘合約

兩個候選各有8個 strict sparse HEX 範圍核對。重核1464 bytes／454個本輪原指令護欄、合計2003組變異拒絕、65536組 index／count 關係、4096組本輪來源家族與60組幾何。Save wrapper 的 SBSP decoding 也用快取 LLVM 的6個原向量／128個 field combinations 核對；其單 byte stack source 與 NV write 並未在本輪串接或執行。

```powershell
python analysis/check_v4160_b1_fallback_id10_static.py
python -O analysis/check_v4160_b1_fallback_id10_static.py
```

正常與 `-O` 模式均須重算並逐 byte 比對 ledger。實際 installed 綁定、其他 m／header／失敗域、status／NV read／optional／save-write 的副作用與 borrowed buffer 保存期、完整返回後的 ID11 登記、第六個 initializer／outer tail、跨事件消費／釋放期與實機功能仍未完成驗證。
