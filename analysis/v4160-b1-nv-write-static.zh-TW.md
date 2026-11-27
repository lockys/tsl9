# v4.1.60：完整 NV write wrapper 與 cache 更新界線

本階段完整核對 `4435c..445ba`／`443f0..4464e`，每份 **606 bytes／210 instructions**，合計 **1,212 bytes／420 instructions**。原始 sparse HEX 與兩份候選 BIN 的 body 全部一致；不含後續獨立函式。

[檢查器](check_v4160_b1_nv_write_static.py) 與[確定性帳本](v4160-b1-nv-write-static.json) 保存完整 operands、SHA-256、CFG、分支見證、兩個列掃描迴圈與全部 19 個 stores。分析僅讀原始 bytes，沒有執行或模擬目標、callback、NV／RAM provider 或硬體，也沒有建立可變目標記憶體模型。

## 返回零表示本機更新路徑完成，實際發布在另一個函式

入口將 `(ID,L,input)` 保存至 S2／S1／S3。與[已核對的 read wrapper](v4160-b1-nv-read-static.zh-TW.md)使用同一對設定 F 與 context C：

| 物件 | V131 | V140 |
| --- | --- | --- |
| F | `200031ec` | `2000323c` |
| C | `2000319c` | `200031ec` |

第一次捕獲 F+8 為零走 RAM 路徑；非零走 configured 路徑，依序要求 F+60、F+56 非零。**F+60 在本 body 中只作 guard，沒有被呼叫。**兩個 indirect sites 都重新載入 F+56，沒有新的 null guard，作為讀入 cache 的 callback。三個配置請求使用 `20000040`，共用 copy 使用 `20000332`；這個 wrapper 沒有 private release。

正常出口只有固定狀態 0／10，不能將 0 解釋成 NV 實際寫入、callback 寫入成功或資料已持久保存。匹配的 copy 遇 null 可以跳過 payload transfer，wrapper 仍忽略其返回並傳回零。

[既有 B1 updater](v4160-b1-downstream-static.zh-TW.md)的實際呼叫為：

```text
write_wrapper(0x7000+i,64,updater_SP+16)
返回後才另外呼叫 notifier 44310 / 443a4
```

Notifier 是較後的獨立呼叫，才可能經 F+60，並依 fresh context pointer 請求釋放及清除 context；其實際 binding、ownership、保存條件沿用先前的條件性結論。不能合併成「write wrapper 自己同步寫入並釋放」。

## Configured 低 ID：寫入 marker／key 後才 copy

ID<=511 時讀取 C+32。若 null，請求 `allocate(fresh_U16[F+12],78)`，先將結果寫至 C+32，再判斷是否為 null。配置成功或已有 pointer 時，fresh F+8 與 C+36 不同才請求：

```text
fresh_F56(captured_fresh_F8, fresh_U16[F+12] >> 2, fresh_C32)
```

不檢查 callback 返回，之後 fresh F+8 寫至 C+36。這與 read wrapper 的 temporary allocation 分支不同，不能共用其發布／釋放假設。

| ID | L guard | 相對 fresh C+32 的 header offset |
| --- | --- | --- |
| 2 | L=16 | `4*trunc_signed((fresh_U16[F+12]-64)/4)` |
| 3 | L=16 | `(fresh_U16[F+12]-44) & ~3` |
| 4 | L=4 | `(fresh_U16[F+12]-24) & ~3` |
| 256 | L<=8 | `(fresh_U16[F+12]-16) & ~3` |

其他 ID 或錯誤 L 返回 10，但此前可能已有配置、callback 或 owner 更新。對獲准的特殊 ID，令 H 為計算出的 header：先 SB `0x5a` 至 H+2，再 SH low16(ID) 至 H+0，最後請求 `copy(H+4,input,L)`；不要求舊 marker／key 有效，也沒有本機 input-null guard。

## Configured 高 ID：發布 cache，再按完整 key 查列

Page 算式與 read wrapper 相同：

- ID `512..0x6fff`：`captured_F8 + fresh_U16[F+12] * trunc_signed((ID-512)/6) mod 2^32`。
- ID `0x7000..0x7ffe`：`captured_F8 + fresh_U16[F+12] * (ID-0x7000) mod 2^32`。
- 更高 ID 返回 10。

若 C+32 null，配置 fresh U16[F+12]、tag78，發布結果到 C+32 後再判斷 null。C+36 與算出的 page 不同時，請求 `fresh_F56(page,fresh_size>>2,fresh_C32)`，忽略返回，再將保存的 page 寫至 C+36。掃描 base B 之後重新取自 C+32，不能假定它仍等於配置結果或 callback 收到的 pointer。

## 列掃描：raw 位移與對齊後 header 必須分開

初始 raw q=4，header 是 `H=B+4*(q>>2)`。marker U8[H+2] 為 `0x5a` 時，讀 U16[H+0] key 與 U8[H+3] next：

1. key 不同：下個 raw q=next。
2. key 相同：以 **signed** 比較 `S32(next-q)` 與原始完整 `S32(L)`。
3. 差值足夠才 copy；不足時 SH `255` 至 H+0，再以 next 繼續掃描。

這裡的 SH 寫入小端 `FF 00`，key 成為 **0x00ff**；不是寫 marker、不是 0xffff，也不能假定該 key 對所有 ID 都不可能再匹配。其他 header bytes 不在這次 SH 的直接寫入範圍。

掃描使用固定 B 的絕對位移。q 與 next 是 U8 域，但比較差值前的 q **沒有先對齊**；位址計算卻有對齊。B1 的 L=64 為正數，其 guard 等價於 next>=q+64；一般完整 L 則必須保留 signed 解讀。差值條件本身未證明 header separation 或完整 payload extent，因 copy 起點還會加上 4-byte header。

沒有 visited-set、次數上限、next 有效範圍或進展 guard。若之前寫過不足容量記錄的 key，後面才拒絕追加，先前寫入也沒有 rollback。

## 第一個非 5A header：configured 與 RAM 的追加界線不同

Configured 路徑要求：

```text
U32(q+L+4) < U32(fresh_U16[F+12]-64)
```

相等會返回 10，且沒有 size>=64 的額外 prerequisite；減法與加法均需保留 word modular 行為。

RAM 路徑由第一次 F+8=0 進入。C+32 為 null 才配置：

```text
allocation_size = low16(fresh_U8[F+14] * fresh_U16[F+12])
allocate(allocation_size,78)
```

結果先發布 C+32，成功後重新讀取 C+32 作為 B，沒有明確 fill／初始化、callback 或 owner 更新。其追加 guard 卻使用另一組 fresh reads 的**完整乘積**：

```text
U32(q+L+4) <= fresh_U8[F+14] * fresh_U16[F+12]
```

這次相等可接受。完整乘積最大 16,711,425，與配置的 low16 大小不是同一個值；另外兩次取樣也沒有相等證明。因此即使 guard 通過，也不能直接推出已配置足夠 buffer。

兩條追加路徑共用：

```text
step = U32((U32(L+3) & ~3) + 4)
new_next = U32(q+step)
SB 0x5a -> H+2
SH low16(ID) -> H+0
SB low8(new_next) -> H+3
copy(H+4,original_input,full_L)
正常返回0
```

容量 guard 使用 q+L+4，metadata 的 next 則經過 rounding 與 low8 narrowing；後者沒有新的範圍檢查。檢查器只驗證這些原始算式與分支，不宣稱它們確保有效 extent、可終止鏈表或完整交易。

## 保存期與後續工作

本機共有 19 個 stores：7 個 frame words，以及 12 個 cache／owner／header／key stores。原始 input 保存在 S3，轉交共用 copy，沒有直接寫成 global pointer；allocator 結果及 page／owner 會發布至 C+32／C+36。Ambient registers、alias、未知 callee 或其他 writers 仍可能保存 borrowed pointer，不能從本機 store 清單推得無逃逸或完整保存期。

尚需展開 worker `51f78 / 52020` 與 core、實際 F+56／F+60 及 config／context writers，核對 caller 可達的設定值與物件保存條件。這份帳本沒有提高 C 重建覆蓋率，也未驗證實機儲存或完整可用韌體。

## 重播

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_nv_write_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_nv_write_static.py
```

檢查拒絕 420 個逐指令 mutations 與 20 個 typed-load mutations，並驗證 65,536 組 raw q／next、B1 16／64 長度的 signed 條件、U16 長度域的 alignment、明列的乘積樣本及兩種邊界比較。Host scalar／interval 證書不執行目標指令；不可變 CFG 路徑的語法見證也不代表真實輸入或 provider 執行已可達。一般與 `-O` 模式逐 byte 重播同一份 JSON。
