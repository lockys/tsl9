# v4.1.60：發布後服務的 APP provider 與快取回覆串接

接續[物件來源與發布後服務](v4160-b1-object-source-static.zh-TW.md)。本輪把 `0x43edc／0x43f68` 的兩個指標讀取，接回 APP 設定的 field44／48、完整 APP callback 與巢狀 frame。新結論是：**只有在 getter 匹配 `0x197f0` 且回覆保存條件成立時，第一個回覆 X 才可縮小為 U16，原差值才可特化成 `|X−L|`。** Optional hook 匹配 `0x197b8` 時則強制 mode 3，不以傳入 X 作 mode。

兩版 resident 仍為參考候選。這些串接沒有證明實際 installed provider、當次 fresh 槽值、初始化順序或實機功能。本輪重用既有完整原指令 guard，新增的是來源／呼叫／frame／快取的跨函式證書；**新增原始 byte 覆蓋為 0，APP C 重建覆蓋率不變**。

## APP 來源與候選目的槽

完整 APP builder `0x199e2` 傳給初始化入口的設定指標是 `C=then-live SP+16`：

| 欄位 | pointer 形成 | word store | code pointer |
|---|---|---|---|
| C+44 | `0x19a92 AUIPC`、`0x19a96 ADDI` | `0x19a9e → SP+60` | `0x197f0` |
| C+48 | `0x19aa4 AUIPC`、`0x19aa8 ADDI` | `0x19ab2 → SP+64` | `0x197b8` |

兩個來源 word 在後續本機 direct frame stores、UID 輸出 `SP+8..13` 及六 byte 搬移目的 `SP+40..45` 之外。這裡核對的是來源形成與本機不重疊，仍依賴必要 frame／context、有效存取、callee 返回與無外部干擾。

若匹配初始化入口通過 validation、64-byte fill／copy 正常完成且無破壞性來源別名，兩個 word 的目的與發布後服務的讀取槽一致：

| 候選 | 初始化入口 | copy destination K | getter K+44 | optional hook K+48 |
|---|---|---|---|---|
| V131 | `0x43c7e` | `0x200031ec` | `0x20003218` | `0x2000321c` |
| V140 | `0x43d0a` | `0x2000323c` | `0x20003268` | `0x2000326c` |

原指令是 64-byte copy 請求，不能稱為原子發布。初始化的八個固定 defaults 不碰 +44..51；copy 後的其他 calls、動態 stores、wrapper 的 fresh `[0x40080]` 呼叫及外部 writer 仍有保存缺口。不能將「有來源」直接寫成「當次呼叫必是該 pointer」。也不要把 V131 的 `0x20003218` getter 槽與另一候選 V140 同址的 registrar slot 0 混用。

重用[完整 builder／UID](check_v4160_config_buffer_source_static.py)、[既有 field48 來源證書](check_v4160_optional_hook_origin_static.py)與 initializer guard；兩版 resident 228-byte initializer、106-byte service 都再次與 strict sparse HEX 完整比對，缺口不以零補齊。

## Getter `0x197f0`：傳入 A0 不作物件來源

匹配這個 APP callback 時，服務雖未重設入口 A0，callback 在 `0x197f8` 已把 A0 改成自己的 `SP+32`，交給 `0x8520` 清除 32-byte local scratch。不能把服務原先傳入的值當作此 callback 的 N／buffer pointer。

重用[完整 APP44 callback](check_v4160_app44_callback_static.py)、兩個讀取 leaf 與[完整軟體呼叫閉包](check_v4160_app44_closure_static.py)。這包含 callback 的 364 bytes／130 instructions、11 個完整 helper 本體，以及 poll／result leaf。這些原指令已閉合軟體直接呼叫目標，沒有因此閉合 MMIO 的實體副作用或輪詢進展。

Callback 的正常回覆路徑是：

```text
0x198dc  呼叫 result leaf 0x18a66
         leaf 讀取 fresh U32[entry A0+76]，取低 16 位
0x198e0  將該回覆保存到 then-live SP+28
0x198e6  呼叫 reset helper
0x1991e  重新載入 then-live SP+28 到 A4
0x19948  A0=A4
```

因此，**在保存的 result word、SP、必要 register、有效存取及 nested calls 正常返回等條件下**，X 落在 0～65535。`0x4001244c` 是對應 context 下的名義讀取地址，不代表已知硬體值。這不是一般 monotonic clock 合約，也沒有由此取得 poll timeout。

## 同一個 halfword 快取

初始化入口在 `+0xba` 呼叫 field44 callback；正常返回後在 `+0xc0` 將回覆低 16 位寫入：

| 候選 | 初始化的 halfword store | 快取地址 M+8 |
|---|---|---|
| V131 | `0x43d3e` | `0x200031a4` |
| V140 | `0x43dca` | `0x200031f4` |

發布後服務於 `+0x24` 重新讀取的 L，正是這個 halfword；後段 `+0x5a` 寫回也使用同一地址。這接通了固定快取欄位，沒有證明初始化先於某次服務，或該值跨過其他 writer 後仍保持。

服務順序依然是先呼叫 getter，再 fresh 讀快取 L。如果 getter 的本機 frame／MMIO 與受保護 RAM 分離且無外部干擾，其回覆 X 才能與所讀 L 形成上述 U16 條件族。沒有把兩次獨立硬體／RAM 取樣合成原子快照。

## 差值的條件性收斂

原服務對任意完整 U32 回覆仍是：

```text
D = low16(max_unsigned32(X,L)) - low16(min_unsigned32(X,L))
L != 0 且 signed D > 20 才進後段
```

若 X 由匹配 APP getter 正常返回並保持 U16，則 L 也是 U16，這時才有 `D=|X−L|`。門檻仍嚴格大於 20，D=20 不進後段。上一輪完整 U32 的反例仍保留，不能將本輪特化套到未知 provider。

L=0 的當次 local 路徑跳過後段與快取寫回；沒有用本體外的 writer／IRQ 行為來推定下次狀態。即使此分支回傳 X，也不等於硬體操作已完成或整個服務一定返回。

## Optional hook `0x197b8`：mode 固定為 3

若 fresh hook 槽仍為 `0x197b8`，服務 `+0x54` 傳入的 A0 此時是 X，但兩條 wrapper 原指令立刻將它替換為 3，再以 `JAL x0` 尾跳 `0x1929a`，保留原 call link。Mode 3 是輸入參數，**不是其返回值**。

重用[完整 mode callee／frame 證明](check_v4160_mode3_frame_static.py)的 1066 bytes／329 instructions，以及完整 90-byte reader。六個 reader call、13 個 RA／S saved words、scratch word、MMIO stores 與循環均由既有 guard 核對。內部輪詢與 reader waits 仍沒有必定完成保證。

## 巢狀 frame 與外層保存值

令發布後服務入口 SP=0；服務配置 16-byte frame 後，兩個 APP callback 都以 SP=−16 進入。以下均為相對此入口的 byte 範圍，含兩端：

| 區域 | 範圍 |
|---|---|
| service 保存 S2 | −16..−13 |
| service 保存 S1 | −12..−9 |
| service 保存 S0 | −8..−5 |
| service 保存 RA | −4..−1 |
| getter 的 128-byte frame | −144..−17 |
| getter helper 額外保留的 16-byte frame | −160..−145 |
| optional mode 的 80-byte frame | −96..−17 |
| optional mode 的 13 個 saved words | −68..−17 |
| optional mode scratch word | −84..−81 |

因此這些 encoded local stack 範圍避開 service 的四個 saved words。Getter 路徑的名義最大 stack depth 為從服務入口向下 160 bytes；不是整個系統 stack 容量或整段韌體最大深度的證明。

在相符 code／正常返回、有效非別名 frame、MMIO 與 RAM 實體分離、無異常 writer／IRQ 等前提下，matching APP callbacks 可保存外層所需的 SP／S／RA；optional mode 返回後，服務 S0 中的 X、S1 的快取地址與 S2 的 K base 仍可接續使用。這不能推成 heap、N 或其他 payload 完整保存期。

## 整個服務仍不能限為 U16 回覆

Provider 槽為零時的 frameless RET 仍保留入口 A0。Matching getter 返回後，若未進後段，服務正常返回 X，這個分支才有條件性 U16 界限。

若進入後段，`+0x56` 對 `0x641b0／0x6429a` 的 linked call 接收 then-live A0：未呼叫 optional hook 時是 X，呼叫 hook 時則是 hook 回覆。**RF callee 回覆才是服務最終 A0**，尚不能套用 U16 或 success=0。`+0x5a` 寫回快取的仍是 service S0 所保存的 low16(X)，不是 hook／RF 回覆。

## 重播與未證明項目

[檢查器](check_v4160_b1_provider_app_static.py)與[固定 ledger](v4160-b1-provider-app-static.json)保存來源、完整 guard 身分、兩版 copy／call／cache 地址、回覆資料流與 frame 投影。29 個 source／field／call／result link 突變必須被拒絕；393216 個 U16 X／L 邊界族在 host 整數上核對特化與嚴格門檻，沒有建立可變 target buffer／provider／callback／MMIO 模型。

```powershell
python analysis/check_v4160_b1_provider_app_static.py
python -O analysis/check_v4160_b1_provider_app_static.py
```

全程離線，沒有執行或模擬目標韌體、硬體存取、封包重放或 target network。後續需確認實際 startup／copy／provider／槽位及快取保存、RF 在本 callsite 下的回覆資料流、同一物件的 N+12 writer、事件與 IRQ 順序，以及完整消費釋放與 notification 指標保存期。
