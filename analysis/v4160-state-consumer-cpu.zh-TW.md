# v4.1.60 GP+357 消費端 `0xcd6a`

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批離線執行原 `[0xcd6a,0xce88)`、getter `[0x81ee,0x81f8)` 及 setter `[0xa658,0xa664)`；在 `0xb6f4`／`0xfe6a` 入口停止，不操作設備。

## 輸入與狀態分類

I=入口 A0，C=入口 A1，M=`U8[GP+357]`。fixture 的 GP=`0x20004000`；M 是上一批 ID 2047 子命令 3 更新的欄位。

入口建立 32-byte frame，按 S0、A1、RA 順序保存到 `caller_SP-8`、`caller_SP-20`、`caller_SP-4`；令 S0=I，呼叫原 `0x81ee`。該 getter 只讀 `G=U8[0x2000bed5]` 到 A0，其他暫存器保持且不寫資料。之後才讀 M、從 frame 讀回 C。

M∈`{1,2,3,4,6,9,10}` 時走下述更新路徑。原碼先判斷 M≤10，再以 `1630 >> M` 的 bit 0 判定；M>10 不執行 SRL，不能把較大 byte 依低五位繞回為同一狀態。

## 更新路徑：清零與讀回是同一 cell

L=`U8[0x2000bf2b]`，R=`U8[0x2000bf2c]`。原碼不同 PC-relative 指令最後均落在相同 L／R，並非不同欄位。先 store L=0，再依 C／G／I 決定是否更新 L：

| C | G | I=0 時的 L | I≠0 時的 L |
|---|---|---|---|
| 0 | 1 | 6 | 6 |
| 0 | 2 | 2 | 2 |
| 0 | 其他 | 0 | 0 |
| 1 | 1 | 0 | 4 |
| 1 | 2 | 8 | 0 |
| 1 | 其他 | 8 | 4 |
| 2 | 1 | 6 | 4 |
| 2 | 2 | 8 | 2 |
| 2 | 其他 | 8 | 4 |
| 其他 | 任意 | 0 | 0 |

L=0 表示只做最初清零，沒有額外的零值 store。隨後重新讀取 L，因此其入口舊值不影響這條路徑：

- L=0：直接返回，不寫 R。
- L=2／6：store R=4，直接返回。
- L=4／8：store R=4，呼叫原 `0xa658`。該 12-byte setter store `U8[0x2000bed0]=1`，只改寫 A4／A5，沒有其他 callee。

setter 入口 RA=`0xcddc`、SP=`caller_SP-32`、S0=I、A1=C；A0=G，唯 C=2、G=2、I=0 的路徑已令 A0=8。測試在此入口檢查 frame／參數，再執行 setter 原指令，不提供合成返回。

setter 返回後按 S0→RA 恢復 frame，指定 A0=1，尾跳 `0xfe6a`，本批停在其第一條指令前。其他直接返回路徑按 RA→S0 恢復 frame，A0=G。此處的 store 或尾跳入口均不代表後續功能完成。

## 其他 M：第一個 `0xb6f4` 呼叫或返回

非上述狀態集合時，不讀寫 L／R、不進 setter；以下是第一個停止點：

| C | G | I | 結果 |
|---|---|---|---|
| 0 | 1／2 | 任意 | call `0xb6f4`，A0=6／7、S0=0 |
| 0 | 其他 | 任意 | 直接返回 |
| 1 | 1 | 0 | 直接返回 |
| 1 | 1 | 非零 | call，A0=7、S0=I |
| 1 | 2 | 0 | call，A0=6、S0=1 |
| 1 | 2 | 非零 | 直接返回 |
| 1 | 其他 | 0／非零 | call，A0=6／7、S0=1／I |
| 2 | 1／2 | 任意 | call，A0=6／7、S0=0 |
| 2 | 其他 | 0／非零 | call，A0=6／7、S0=1／I |
| 其他 | 任意 | 任意 | 直接返回 |

call 入口均保留 frame：RA=`0xce6e`、SP=`caller_SP-32`、A1=C。`0xb6f4` 本身未執行，其返回後路徑與保存／副作用合約仍待追查。直接返回時恢復 caller S0／RA／SP，A0 保持 getter byte G。

## 驗證與共享狀態序列

```powershell
python analysis/test_v4160_state_consumer_cpu.py --standalone-only
python analysis/test_v4160_state_consumer_cpu.py
python -O analysis/test_v4160_state_consumer_cpu.py
python analysis/test_v4160_zero_id_queue_cpu.py
```

僅需 Python 標準庫、原 APP 及既有測試模組；本批兩部分都不需 SDK carrier、合成 probe 返回或 copy provider 綁定。一般與 `-O` 的完整結果：

```text
PASS: 26880 state/category/input/getter cases; 393216 full category/getter pairs; 4608 old-cell probes; 3 mutations; original getter/setter; b6f4/fe6a NOT executed
PASS: 6144 original ID2047 producer-to-state-consumer chains; {'return': 3096, 'call': 2232, 'tail': 816}; shared globals; no SDK required
```

- 26880 組：M 全部 byte 值 × C=0／1／2／3／255／`0x10000`／`0xffffffff` × I=0／1／`0xffffffff` × G=0／1／2／3／255。
- 393216 組：C 與 G 的全部 byte 組合 × 三個 I × 兩個代表 M（0、1）。
- 4608 組：L 舊值全部 byte × C=0／1／2 × G=1／2／3 × I=0／1；同時變動 R 舊值及 setter 目標初值，核對精確 stores 與 canary。
- 6144 組：先執行上一批原 ID 2047 生產端（含 mode／ID 樹及實際 `0xcd4e`），保留同一 CPU 的 GP 狀態，再設定另一個函式呼叫的暫存器及 L／R／getter fixture，執行本消費端。GP+357 不重設；覆蓋八個 selector、H／J／K 的零／非零、三個生產端 getter 值、四個 C、兩個 I、四個 G。

**上述 producer→consumer 順序由 harness 明示指定，證明共享狀態的資料流相容，不證明真實韌體排程或控制流必然連續呼叫兩者。** 本批沒有執行 queue consumer 或聲稱 ingress 到此函式的完整可達性。producer／consumer 的原碼都執行，但 `0xb6f4`／`0xfe6a` 始終停在入口。

逐例核對 getter／狀態／stack 讀取順序、L 清零後再讀的數值、精確 stores、setter／callee／tail frame 與參數，以及整段 GP／L／R／getter fixture 的 canary。三項記憶體複本變異分別更改狀態 mask 1630→1631、把 L 清零 store 移到相鄰 byte、getter 改讀相鄰 byte，均須由指定資料存取或 getter 檢查抓出。

原 APP 未改。共用有限 CPU 只新增標準 RV32 SRL：`f5/f7=0`、shift count 取低五位；未知指令、未映射存取或執行範圍外目標仍失敗即停。既有 queue 回歸也通過。

既有 `src/native/receive/control_gates.c` 已重建此段 C；本批增加原指令與共享狀態證據，沒有新增重建 bytes 或重算覆蓋率。仍需追查 `0xb6f4` 的返回後流程、`0xfe6a`、本函式實際 caller 及其他 provider 綁定。
