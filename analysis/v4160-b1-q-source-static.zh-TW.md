# v4.1.60：Q 槽來源與選定初始化路徑的保存

接續[RF masked-word 回覆](v4160-b1-rf-reply-static.zh-TW.md)。本輪找到兩種具體來源：候選啟動 zero helper 可將 Q 槽清零；radio parent 可將 `0x40025000` 寫入同槽。另以原指令、呼叫接點與寫入區間核對 **從該 publisher 到 large 取樣 Q 的同一次初始化路徑**，在明確保存前提下，可將回覆特化為：

```text
fresh U32[0x400250d0] & 0xf0ffffff
```

這不是全域不變值，也不適用於未另證時序／槽位保存的較晚 postservice 呼叫。沒有證明實際執行了啟動或該初始化路徑、物理 MMIO 映射、硬體讀值或輪詢終止。

本輪重用既有完整 byte／CFG guard，新增指定 SW 編碼普查、來源接點與條件性寫入區間證書；**新增原始 byte 覆蓋為 0，APP C 重建覆蓋率不變**。

## 兩版的 Q 槽與來源

令 `G=0x20003000`：

| 候選 | Q 槽 | radio parent | literal store PC |
|---|---|---|---|
| V131 | `G+1424 = 0x20003590` | `0x64298` | `0x642cc` |
| V140 | `G+1504 = 0x200035e0` | `0x64382` | `0x643b6` |

完整 118-byte parent 在 `+0x2c` 形成 `0x40025000`，`+0x30` 形成 G，`+0x34` 將該指標寫入 Q 槽。這筆 store 在 `+0x64／+0x66／+0x6a` 三個 linked calls 之前；之後 parent 恢復 frame，於 `+0x72` 尾跳 RF 外層。

獨立完整 zero helper 的編碼寫入範圍分別為：

| 候選 | zero helper 的 FLASH bytes | 要求清零範圍（末址不含） |
|---|---|---|
| V131 | `[0x40292,0x402b0)` | `[0x20002ef8,0x20003618)` |
| V140 | `[0x402d2,0x402f0)` | `[0x20002f48,0x20003668)` |

兩版 Q 槽皆為該範圍的第 **423 個 word**。因此 matching helper 若適用並正常完成，可產生零來源；parent 若走到 literal store，可產生 `0x40025000` 來源。兩段 code 的存在不證明實際 startup 順序、執行時刻或後續槽值。這兩個值也不是所有可能 writer／值的窮舉。

重用[zero helper](check_v4160_fallback_initialization_static.py)與[radio parent／helpers](check_v4160_radio_config_chain_static.py)的完整 guard；涉及的 resident code 都再次與 strict sparse HEX 完整比對，缺口不補零。

## 指定 SW 編碼普查的結果與限制

對原始 APP BIN、兩版 resident BIN，以及兩份 **完整 sparse HEX 已捕獲區域**，逐一檢查每個 halfword-aligned、完整四 byte 的視窗。普查條件僅為標準 `SW` opcode／funct3，且 signed immediate 恰為 1424 或 1504。

| 輸入 | 符合視窗 |
|---|---|
| APP | 0 |
| V131 BIN／完整 strict HEX | `0x642cc: 2328d758` |
| V140 BIN／完整 strict HEX | `0x643b6: 2320d75e` |

兩筆均由完整 parent 本體 guard 確認為真正的指令邊界，base=A4=G，source=A3=`0x40025000`。BIN 與完整 sparse HEX 的命中清單一致，包含候選 contiguous BIN 末端之外已捕獲的 HEX bytes；未把未捕獲地址當成零。

**這是指定 encoding 的普查，不是所有有效位址 writer 的分析。** 其他 base register／ADDI 後的 store0、byte／halfword、copy／fill、computed pointers、不利別名、非同步 writer、runtime code 變動等均不在此搜尋的排除能力內。原始編碼視窗本來也可能落在 data 或重疊解碼；只有命中的兩處另經完整函式 guard 確認。

## 同一次初始化內的四槽保存證書

Parent 先建立 descriptor=0，以及 T、R、Q 三個 pointer 槽；在這條特定初始化路徑下，它們分別提供 `0x40024200`、`0x40024100`、`0x40025000` 的 memory-base 投影。檢查器核對後續選定路徑的所有 non-frame store 區間均避開這四個固定槽：

1. Parent 在指標建立後的固定 context stores，以及 registers／bulk／pulse／bits 的全部 49 個 projected word stores。
2. RF helper 在入口 A0=13、context state1 的 quick／slow 兩種原指令路徑；這些路徑不呼叫未閉合的 indirect callback，也不寫 context bytes8／9。
3. Descriptor 保持零時，reset 的兩條 readback 分支只包含已核對的六個 store；不套用任意 descriptor 的 pointer OR store 合約。
4. RF 外層走到 large call 前的六個非 frame stores。
5. Large 的 magic／非 magic prefix，直到 `+0x160` 重新捕獲 Q；magic word 與非 magic 的六個 byte 發布位址均與四槽分離。
6. 非 magic 三次呼叫的完整 mapped helper，只有一個 `T+100` store，沒有其他 nested call 或 frame。其等待仍必須退出。

重用[RF helper／reset／外層](check_v4160_rf_tail_return_static.py)與[完整非 magic service](check_v4160_nonmagic_service_static.py)。三次 mapped call 的 AUIPC／JALR 與 helper first-copy 來源也重新接通。

Ledger 每版有 **96 筆路徑分類的寫入區間**。這是 quick／slow、magic／非 magic 等分類的聯集，部分互斥路徑重複包含相同 stores；**不是一次執行的 store 次數**。每一筆都核對與 T／R／Q／descriptor 四槽的數值區間分離。

這個證書需要：對應候選 code 與所選分支、必要 callees 正常返回、polls 退出、frame 與必要 S／SP／RA 保存；所用 memory-base 投影有效，frames 不與受保護 RAM 重疊，`0x400xxxxx` 存取在實體上也不別名到 `0x2000xxxx`；且無 IRQ／DMA／重入／其他 writer 破壞槽位。**數值位址不重疊本身不證明物理映射無別名。**

## 能特化的讀取範圍

在上述 **同一次 parent 初始化、指標發布至選定 large 取樣** 的前提下，Q 槽未被分類的中間 stores 改寫，large `+0x160` 的 fresh load 可取得 `0x40025000`。將這條來源／保存證書接回前輪已驗證的公式，便得到名義地址 `0x400250d0` 的 masked fresh word。

Large 依然重新讀槽，不沿用 parent 曾經持有的 register 值。一般 RF／postservice 的其他進入路徑，仍只能使用 `fresh U32[held Q+208] & 0xf0ffffff`；較早曾經發布指標，不代表較晚任意呼叫讀到同一值。

也沒有因此證明 `0x400250d0` 的 fresh word 等於前一筆寫入或後一筆 packed store、代表硬體完成、具有某個實測值，或函式一定返回。原有 RF 早退保留入口 A0 的分類沒有改變。

## 驗證與後續

[檢查器](check_v4160_b1_q_source_static.py)與[固定 ledger](v4160-b1-q-source-static.json)保留完整來源 guard 身分、BIN／full sparse HEX 搜尋結果、zero 範圍、第423個 word、publisher、call spine、選定 CFG paths 與 96 筆區間分類。18 個 publisher／call／zero／capture 接點突變必須被拒絕，另有標準 SW immediate 的獨立 bitfield oracle。

```powershell
python analysis/check_v4160_b1_q_source_static.py
python -O analysis/check_v4160_b1_q_source_static.py
```

全程離線，沒有執行或模擬目標韌體、硬體存取、封包重放或 target network。仍需追查其他 computed／窄幅／copy／fill／alias writers、實際 startup 與跨事件順序、較晚 postservice 的 Q 保存，以及實體映射／readback／IRQ／poll 進展、同一物件的 N+12 writer 與完整配置保留／消費釋放／notification 保存期。
