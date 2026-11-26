# v4.1.60：特定 RX 來源至 ID1657 快取的條件性欄位限制

本階段承接 [row18 的 length／tag 來源](v4160-cached-record-origin-static.zh-TW.md)，核對一條具體路徑：`0x16a7c → 0x12bc8 → 0x12c58 → 0x14d2e → row18`。在指定的正常返回、實際 copy、來源保存與不干擾前提下，這條 RX 來源的長度為 1–8；tag 則為 RX 入口 A0 的低 byte，函式本身沒有把它限成 1／2。

consumer 的 ID1 特殊長度檢查及 filter 自身的 <=8 比較，都不是 ID1657 的通用長度 guard。另一條 `0x12c24 → 0x18d78` ingress 仍另列邊界，不能套用本 RX 限制。

只解析原 bytes、核對所有 operands／局部 CFG／graph dominators，並驗證主機端 predicates／區間。未執行或模擬 target ISA、CSR、copy、RAM／stack 狀態、provider 或 MMIO，沒有使用先前 CPU fixture。[檢查器](check_v4160_rx_cache_ingress_static.py) 與 [完整指令／CFG ledger](v4160-rx-cache-ingress-static.json)。既有 C 重建 bytes／覆蓋率不變。

## 完整本體

| 角色 | APP 半開區間 | bytes | 指令 | stores |
|---|---|---:|---:|---:|
| consumer | `0x12c58..0x12d92` | 314 | 107 | 14 |
| filter | `0x82d2..0x838e` | 188 | 69 | 13 |
| queue producer | `0x12bc8..0x12c24` | 92 | 32 | 6 |
| RX | `0x16a7c..0x16b0a` | 142 | 52 | 8 |
| 合計 | | **736** | **260** | **41** |

每個本體包括 RET 後的本機 cold block，固定全部指令 operands、完整 bytes SHA-256、可達局部節點、唯一明示 backedge 與所有 stores。子呼叫 fallthrough 僅是正常返回的條件性 CFG，沒有因此證明 callee 一定返回。

APP 為 76,800 bytes、base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。上游 selected mode1／row18 路徑、既有 transfer／probe 本體、SDK／candidate／sparse 覆蓋也重新驗證；candidate 仍不代表 installed provider。

## RX：十三個取樣 bytes 與明示 1–8 guard

RX 建立 48-byte frame，將完整入口 A0 保存至 S1。依序呼叫已固定原 bytes 的 `0x16896(3)`、`0x16896(保存的入口 A1)`，再呼叫 13 次 `0x16896(0)`，將每次回覆的低 byte 放入新 SP+16..28。

既有 transfer 合約只保證 numeric 回覆為 0..255；逾時與正常資料零都可能返回零，所以不能把這 13 bytes 當成已證實的接收 frame。loop 次數、保存狀態與資料 footprint 仍要求有效存取、完整 context 及沒有不利 writer／別名等前提。

取樣後讀 b1=`U8[SP+17]`，要求 `b1&0x18==0`。再取 `L=U8[SP+20]&15`，以 `(L-1)&255<=7` 限制完整 L 為 **1–8**；零及 9–15 均拒絕。接受後提出：

```text
12bc8(
  ID=(U8[SP+16]<<3)|(b1>>5),
  source=SP+21,
  length=L,
  tag=保存的完整入口 A0
)
```

ID 域為 0..2047，ID0 沒有被 RX guard 拒絕。每個 ID 恰有八種通過 flags 條件的兩-byte 標頭編碼；ID1657 為 `cf 20` 至 `cf 27`。這是算術可表示性，沒有證明實際收到、成功入列或已消費。

來源最大為 SP+21..28，落在上述 13-byte capture 範圍。入口 tag 本身沒有有效值 guard；只有另行證明 caller 傳入 1／2 時，才能得到後續 tag1／2。RX 的 I/O 分支不構成此輸入值驗證。

## queue producer：長度寬度與 tag 寫入順序

producer 與 consumer 均形成 base=`0x2000c038`，共 32×12 bytes，結束於 `0x2000c1b8`。producer 找第一個 fresh `U16[row]==0` 的槽：

1. `0x12bf6` 寫 ID 低 16 bits 至 row+0。
2. `0x12bfa` 寫長度低 byte 至 row+2。
3. fresh `[0x4004c]` 接受 `(row+3,入口 source,完整入口 A2)`，未把 copy count 限成 metadata 的低 byte。
4. copy 正常返回後，`0x12c0e` 才將保存的 tag 低 byte 寫到 then-live row+11。

這個一般 producer 沒有 11-bit ID 或長度 <=8 guard。只有本 RX caller 的完整 A2 已被限制為 1–8，才可沿這一條路使用相同的 metadata／copy count。按參考 copy、正常保存及無不利別名等前提，目的 prefix 位於 row+3..10，不碰 row+11 的 tag；未填入的其餘 payload bytes 保留未知舊內容。

滿佇列時不呼叫 copy、不直接寫 queue；A0 沒有共同正規化的 status。在本 RX 的 1–8 長度、參考 copy、context 保存與範圍分離前提下，ID0 即使寫過 payload／tag，首 halfword 仍為零，consumer 會把它當空槽；不將此結論推廣到任意未知 provider 副作用。ID 先寫、payload／tag 隨後寫的順序不等於原子 publication 或中斷安全。

## consumer：12-byte snapshot 與 ID1657 路由

consumer 建立 80-byte frame，依序讀 32 個槽。fresh queue ID 非零時，先提出完整 12-byte copy 請求 `(SP+8,row,12)`；provider 正常返回後清原槽 ID halfword，再呼叫 `0x82d2(SP+8)`。snapshot 請求不根據 length 縮短，因而也涵蓋未由短 payload copy 填入的尾部。

| consumer 新 SP 位移 | snapshot 欄位 |
|---|---|
| +8..9 | ID halfword |
| +10 | length |
| +11..18 | 八個 payload bytes |
| +19 | tag |

snapshot copy 兩側有 encoded CSR `0x800` 的 clear／set 操作，來源 S2=`0x88`。沒有保存／恢復舊 CSR word 的本機序列；這裡只固定 instruction operands，不主張它具有何種實體同步或中斷效果。

filter scalar 非零就下一槽；零才 fresh 讀 snapshot ID。對 ID1657 這個非 ID1 分支，還需要：

- fresh 配置 pointer 的 +4 byte bit 3 未設；pointer 從 then-live S7 讀取，名義 S7=GP+84。
- 完整本機 `0x81aa` fresh 讀 GP+167，回覆非零。
- `0x12d8c` 呼叫 `0x14d2e(SP+8)`，後者 fresh mode=1 且重新取樣的 ID 仍為 1657，才接到既有 row18 寫入 case。

`length==4`、`b5 62`、特殊 opcode／參數比對，以及 response 副本 tag 清零，都位於 ID1 分支，不能當成這條路的欄位限制。queue 的原 ID、consumer 的快照 ID 與後續 mode tree 的重讀 ID，也不能在缺少保存證據時當成同一次不可變取樣。

## filter：<=8 不是零返回後的長度保證

filter 的兩個 descriptor 以 base=`0x2000c794`、stride 4 形成。各自依序檢查 fresh halfword +2 不等於 `0xfffe`、fresh byte +5 等於 2，以及 fresh byte +4 非零；沒有把它們當成同一份原子快照。

qualify 後，程式先讀 record length、把非零 descriptor flag 記入 S4，**再**檢查 length>8 是否略過 optional calls。length<=8 才可能於 `0x8356` 呼叫 copy，隨後於 `0x8368` 呼叫 `0x8a56`；後者使用重新讀取的 length+2。

S4 在入口設 0，兩次 descriptor 間沒有清零；最後先將 S4 放到 A0，才恢復 caller 的舊 S4。graph dominator 檢查確認非零 flag assignment 位於兩個 optional call 的所有本機控制路徑之前。

因此，在 required S4／context／frame 保存及無不利干擾的前提下，若曾 qualify，返回值會非零，即使 length>8 使 calls 全跳過。若兩個 descriptor 都不 qualify，任何 length 都可以返回零，甚至不必讀 record length。optional callees 的效果與保存仍未知，不能無條件排除它們改變 context 後造成零返回。

這解釋了為何「filter 有 <=8 比較」不等於「consumer 往 ID1657 派送時 length<=8」。特定 RX 來源的上限來自 RX 自己的 header guard。

## 條件性 RX → row18 串接與其他來源

若本 RX guards 通過、queue 有空槽、實際 copy 符合參考且所需 context／來源／frames 保存、consumer 讀到同一項目、filter／配置／probe 通過、mode1／重讀 ID1657 成立，則：

```text
RX frame+21 的 L bytes
→ queue row 的 payload；另寫 length=L、tag=low8(RX入口A0)
→ consumer SP+8 的完整12-byte P
→ row18 O=2000c290 的完整12-byte copy請求
→ 立即 C6a8(P)；另一次 C776 才 C6a8(O)
```

這條保存良好的來源鏈可將快取 length 限為 1–8，tag1／2 則仍需入口值證據。它沒有證明真實接收、實際 provider 綁定、所有欄位長期保存或唯一 writer。別名、IRQ、其他 writer、部分 provider 返回及 unknown ownership 都可能破壞上述等式。

另一條 `0x12c24 → 0x18d78 → 0x12bc8` 是獨立來源，本批沒有展開其欄位建構，不能套用相同限制。下一階段應分開核對該入口、格式分支、length 與 source footprint。

## 重播

```text
python analysis/check_v4160_rx_cache_ingress_static.py
python -O analysis/check_v4160_rx_cache_ingress_static.py
```

一般／`-O` 皆需精確重播 ledger。檢查全部 65,536 組兩-byte 標頭（16,384 組通過、每 ID 八種）、65,536 組 flags／length byte（8,192 組通過）、1,024 組 filter predicates、256 個 queue／capture 區間及 18 個指定原指令 mutation。這些是靜態證據與主機算術檢查，不是 target 或裝置功能測試。
