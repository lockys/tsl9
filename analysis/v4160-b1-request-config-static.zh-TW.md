# v4.1.60：request 配置 leaf 與 RAM mode1 串接

延續 [request 清理鏈](v4160-b1-request-leaves-static.zh-TW.md)，本階段完整展開 request 的另一個直接 callee，並接通同一 caller 後續的既有 RAM service 證據。全部分析離線，僅使用原始位元組、operands、不可變 CFG 路徑、host scalar／區間算術；沒有執行或模擬目標 ISA、provider、RAM、polling 或硬體。

[驗證程式](check_v4160_b1_request_config_static.py)與 [JSON ledger](v4160-b1-request-config-static.json)保存完整證據。新增範圍如下；原始 sparse HEX 必須逐位元組捕獲，不以補零填缺口。

| 完整配置函式 | 範圍 | bytes／指令數 |
|---|---|---|
| V131 resident 候選 | `[0x63c54,0x63d6a)` | 278／95 |
| V140 resident 候選 | `[0x63d3e,0x63e54)` | 278／95 |

合計 **556 bytes、190 條指令**。另重用兩份完整 RAM service 共 500 bytes、request caller 共 656 bytes，不重算為新增範圍。這次證據不提高既有 C 重建覆蓋率。

## 配置 leaf 的入口與寫入

令 V131 `G=0x20003000`、狀態 `S=G+1300`、設定 `F=G+1344`；V140 的各欄位 offset 加 80。函式沒有 frame、callee、回圈，亦不定義 SP／RA／S registers。完整 CFG 為 DAG，唯一 RET 在 +0xa4；所有普通返回路徑都會先清 `S+4` byte。

先從 `G+1292` 捕獲 optional descriptor。非零時，依序把 descriptor+8 的 word OR 入 descriptor+4 所指 word，再把 descriptor+20 的 word OR 入 descriptor+12 所指 word。只有 descriptor 本身有非零 guard，兩個內層指標沒有 guard。這些寫入可能與後續讀取來源 alias，不能假設它們只影響無關物件。

接著讀取 `G+1296` 的 fresh flag bit0，捕獲動態物件指標 `P=[G+1288]`，建立 S 地址。P 沒有 null guard，函式後段也不重新讀取 P slot。模式判斷使用**完整入口 A0**：先測 A0&2，再判斷完整 A0 是否等於 1，沒有先縮成 byte。

- A0&2 非零：以 fresh `P+0` 清 bits12／13，再設 bit13；向 P+32、20、24、40、36、16 寫入對應 constants。A1 改為 `low32((entry A1<<7)+868)`，A0 返回值為 8192。
- A0&2 為零且完整 A0==1：向 P+32、20、24、40、36、16 寫入另一組 constants，再以 fresh `P+0` 清 bits12／13。A1 改為 `low32(((entry A1+5)<<3)+60)`，A0 保留為 1。
- 其餘 A0&2 為零值：使用同一組低模式 constants，清 bits12／13 後設 bit12。A1 改為 `low32(((entry A1+5)<<4)+60)`，A0 改為 4096。

共同尾段先向 `S+16` word 寫入上述 A1。若**入口 A2 非零**，再向相同 word 寫入 `low32(entry A2<<1)`；之後清 S+4 並 RET。共有 20 個編碼 store sites，不把它們當成同一條路徑全部執行，也不把返回 scalar 解釋為通用 success。

兩個容易漏算的匯流點已固定為 path 與 operand 證據：A0&2 分支的兩種 flag 路徑**都執行 +1247**；低模式的兩條 shift 路徑**都執行 +60**。

## 常數與 request 的四個實參

| P 欄位 offset | A0&2 非零 | A0&2 為零 |
|---|---:|---:|
| +32 | 589958 | 589955 |
| +20 | 137371633 | 135272705 |
| +24 | 202265 | 202276 |
| +40 | 10462 | 10430 |
| +36 | 16802576 | 16802576 |
| +16，flag0 | 3450079 | 3285712 |
| +16，flag1 | 4170975 | 4170446 |

request 使用 `(fresh F+0 bits4..5,255,0)`，因此沒有 A2 override。四個實參的本機算術如下：

| mode | P+0 bits12／13 的寫入 | S+16 寫入 scalar | 正常 A0 回覆 |
|---|---|---:|---:|
| 0 | 清兩位後設 bit12 | 4220 | 4096 |
| 1 | 清兩位 | 2140 | 1 |
| 2 | 清兩位後設 bit13 | 33508 | 8192 |
| 3 | 清兩位後設 bit13 | 33508 | 8192 |

caller 不根據此 scalar reply 分支，而是重新讀取設定 flags，再呼叫 RAM service。以上是指令寫入的來源與算術，沒有證明 aliased 記憶體或硬體後續讀回仍為這些值。

## 後續 RAM service 的 mode1 路徑

重用完整 250-byte／93 指令的既有證據：

| 候選 | 捕獲的 FLASH 來源 | first-copy 對應 RAM 入口 |
|---|---|---|
| V131 | `0x4292a` | `0x200026ba` |
| V140 | `0x429b6` | `0x20002706` |

完整來源範圍須符合候選 first-copy affine mapping 與 strict HEX，並不宣稱實際開機已完成 copy 或 installed RAM 相同。

request 傳入 `(1,independently fresh F+0 bits4..5,255)`。完整 mode1 路徑沒有 nested call，入口 A1／A2 在 A2 被覆寫前都未被讀取，因此這條路徑不依賴傳入 bits 或 255；普通返回時 A0 仍為 1。它也略過 mode0 的先行輪詢與 flash callee。

mode1 的實際順序：

1. 從入口先捕獲的 H0 讀 word+12，保存原值；將其 AND `0xffffdfff` 寫回 H0+12，再保留原始 `FENCE.I`。
2. 重新讀取指標 slot 得到 H1，向 H1+8 寫 8192，向 S+4 byte 寫 128。
3. 從另一個動態指標取得物件，第一次 fresh word+0 的 bits12..13 為 0 則選 406；否則再讀一次，第二次 bits 為 2 則選 1086，其餘選 446。即使第二次變成 0，也屬於 446，不能合併兩次 snapshot。
4. 將選定 scalar 寫入 H1+100，再將保存的 **H0+12 原值** 寫入 H1+12。不假設 H0=H1。
5. 捕獲 H2 一次，進入共同 polling：每輪先讀 fresh S+2 bit0，再讀 fresh S+3 bit0，任一設位即退出；否則讀 H2+100 word，為零退出，非零回到兩個 status tests。**這個迴圈內不重讀 H slot**，與外層 request 的其他輪詢不同。

沒有 timeout、進展或物理硬體語義證據。H0、H1、H2 與前一 leaf 捕獲的 P 均可能不同。即使前一 leaf 曾寫入 P+0，仍不足以斷言 RAM service 的 fresh reads 必見相同 mode。

## 驗證與剩餘工作

驗證涵蓋完整 operands／typed loads、20 個 store sites、CFG 每條邊與四模式分支 witness，拒絕 **190 個逐指令 mutation、8 個 typed-load mutation**。host scalar 檢查包括 65,536 個 mode 低 16 位值、request 四個固定實參、固定寬度 shift／加法與 16 對獨立 control snapshots。低 16 位域只是算術驗證範圍；完整入口 A0 的分支合約仍以原指令為準。一般與 `-O` 模式精確重放同一 JSON。

串接仍依賴候選 ISA／API／first-copy mapping、有效 code／frame／global／object extent、一般 callee 保存合約，以及沒有破壞性 alias、wrap、IRQ／DMA 或重入。硬體效果、實際 provider 綁定、polling 終止與完整指標保存期仍未證明。下一個主要缺口是完整 attempt helper `0x64794/0x6487e` 及其內層服務。

```powershell
python analysis/check_v4160_b1_request_config_static.py
python -O analysis/check_v4160_b1_request_config_static.py
```
