# v4.1.60：名義索引36設定與 extended ID 舊 stackword 候選

承接 [peripheral ingress 與 extended ID 缺口](v4160-peripheral-rx-ingress-static.zh-TW.md)，本階段把 raw vector 的名義索引 36 接到控制區的同索引寫入，並完整展開相關初始化／pin wrapper 與四個直接 RMW helpers。另以原 frame operands 找到數種可能落入 extended-ID 舊 word 的先前寫入。

這些結果仍是 numeric 設定順序與條件性位址重合，不是實際 IRQ 送達、硬體自動保存 GPR、stack 切換、實際最後寫入者或 RAM 初值證明。只解析 bytes、核對完整 operands／CFG／stores 與主機算術；沒有執行或模擬 target ISA、CSR、MMIO、IRQ、provider、stack 或 RAM。[檢查器](check_v4160_irq_setup_stack_sources_static.py) 與 [完整 ledger](v4160-irq-setup-stack-sources-static.json)。

## 完整本體

| 角色 | APP 半開區間 | bytes | 指令 | stores |
|---|---|---:|---:|---:|
| 控制區設定 | `0x9a42..0x9ad2` | 144 | 46 | 10 |
| pin record wrapper | `0x9a24..0x9a42` | 30 | 12 | 5 |
| peripheral 初始化 | `0x12d92..0x12e54` | 194 | 62 | 6 |
| RMW helper | `0x19124..0x19142` | 30 | 12 | 2 |
| RMW helper | `0x19142..0x19160` | 30 | 12 | 2 |
| RMW helper | `0x19160..0x1917e` | 30 | 12 | 2 |
| RMW helper | `0x1917e..0x1919c` | 30 | 12 | 2 |
| 合計 | | **488** | **168** | **29** |

七個本體皆固定完整 SHA-256、逐條 operands、可達局部節點、無局部迴圈及所有 stores，包含 RET 後的 cold blocks。`0x19124`／`0x19160` 是重用並重新核對的既有葉函式；既有 C 重建 bytes／覆蓋率不增加。先前只界定 `0x12d92` 的 46-byte prefix，本批擴為其完整 194-byte 本體。

APP 為 76,800 bytes、base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。先前 ingress／consumer／cache chain、完整 reset、SDK／candidate／sparse 證據亦重新驗證；candidate 不代表實際 installed provider。

## raw vector 與控制區寫入的數值連接

既有 `0x80c8` word=`0x12c24`，相對 reset 形成的名義 vector base `0x8038` 是第 36 個 word。`0x9a42` 的尾段依序寫入三組控制區位置：

| 數值索引 | priority byte 地址／值 | word 地址／值 |
|---:|---|---|
| 45 | `0xe000e42d` ← 0 | `0xe000e104` ← `0x2000` |
| 36 | `0xe000e424` ← `0x20` | `0xe000e104` ← `0x10` |
| 39 | `0xe000e427` ← `0x30` | `0xe000e104` ← `0x80` |

索引 36 同時滿足 priority offset `0x424−0x400=36` 與第二個 word 的 bit 4：`32+4=36`。這是原 operands 的數值吻合；沒有賦予 controller bit 官方名稱，也不主張三筆 word writes 可以按普通 RAM 或 write-one-set 語意合併為最終 enable bitmap。

在已固定的初始化序列中，`0x9258` 呼叫 `0x9a42`，之後 `0x9274` 才呼叫 `0x12d92`。這個順序仍依先前 calls 正常返回與必要 context 保存，不能當成 IRQ 必已啟用或實際發生。

## CSR800 與六個完整軟體 helper 呼叫

`0x9a42` 先保存 RA／S0–S2，設 S2=`0x88`，於 `0x9a50` 以 CSRRC、rd=x0 操作 CSR `0x800`，接著依序：

| callee | A0／A1 | fresh RMW 位址 |
|---|---|---|
| `0x19142` | `0x02020006,1` | `0x4002101c` |
| `0x19124` | `0x101d,1` | `0x40021018` |
| `0x1917e` | `0x02020006,1` | `0x40021010` |
| `0x1917e` | `0x02020006,0` | `0x40021010` |
| `0x19160` | `0x101d,1` | `0x4002100c` |
| `0x19160` | `0x101d,0` | `0x4002100c` |

四個 helpers 無 frame 或 callee，只改 A0／A4／A5；非零 A1 用 fresh word OR A0，零 A1 用另一次 fresh word AND `~A0`。在所需非別名、正常存取與 context 前提下，這些 encoded 指令不改 live S2。每次 readback 獨立，先設後清不代表恢復硬體先前狀態。

控制區 stores 後，`0x9ac2` 以同一 live S2 對 CSR `0x800` 執行 CSRRS，沒有讀回原 CSR 再恢復。主機位元代數是先清再設 `0x88`，最後等於 old OR `0x88`，不是對任意 old 都保持不變；此代數沒有給出晶片 CSR 的實體效果。

reset 另有 CSR `0xbc0` 的 source literal 31、CSR `0x804` 的 source literal 3，以及 `0x300/0x305/0x341` 的原 operands。這些 bytes 未建立本 IRQ 的硬體 frame 格式、實際 SP 或 GPR 保存／清零行為；reset 後的 resident／其他 writers 仍是保存邊界。

## 完整 `0x12d92` 與兩個 driver 邊界

初始化先提出既有兩個 fresh fill 請求：384-byte queue、228-byte cache table。其真實完成與 S0／frame 保存仍需 provider 合約。其後兩次呼叫：

```text
9a24(40010800,1000hex,18hex)
9a24(40010800,0800hex,48hex)
```

`0x9a24` 配置 32-byte frame G，保存 RA 至 G+28，以 G+4 為指標建立連續 12-byte record：SH 入口 A1、SH0、SW3、SW 入口 A2。再呼叫 `0x18f88(A0,G+4)`，正常返回才恢復 RA／SP。record 的存在不證明 driver 複製它或不保存該 stack pointer；其他 ambient 暫存器亦未抹除。

回到 `0x12d92` 的 48-byte frame I，呼叫完整本機 `0x8520(I,0,32)`，再 SW1 至 I+12、SH `0x0405` 至 I+4。fresh `U32[GP+108]` 的數值決定是否再寫 I+0：

| 取樣值 | I+0 的本機 SH 值 |
|---:|---:|
| 96,000,000 | 8 |
| 120,000,000 | 10 |
| 144,000,000 | 12 |
| 其他 | 沒有額外 SH；零值仍依賴 fill 成功及保存 |

不把 GP+108 的數值自動等同實際時鐘頻率。接著 `0x18ab0(0x40006400,I)`，scalar 回覆不測；若正常返回並保留必要 S0／context，再 fresh 讀 `0x40006414`、OR2、寫回同址。這個 base 與 ingress 相符，但不證明設定成功、bit 的實體意義或 driver 沒有保存 I。

`0x18f88`／`0x18ab0` 本批維持明示未展開邊界；未把七個已核對本體當成完整硬體初始化 closure。

## extended ID 的先前 word：四種條件性位址候選

令 **E 為實際 IRQ 入口 SP**。既有入口配置 H=E−32，record R=H+12，所以 caller 讀作 ID 的 word 位於 `[E−20,E−16)`。extended reader 沒有直接的 R+0..3 store。

producer 自己的 16-byte frame 在 E−48；保存 S1／S0／RA 的 words 分別位於 E−44、E−40、E−36，與該 ID word 不重合。不能拿 producer 的保存值直接填補 extended ID 缺口。

以下只固定「若先前函式與後來 IRQ 以相同 E 為各自入口 SP」的位址等式，不證明實際同 SP、順序、最後 writer 或內容：

| 先前函式／寫入 | 位址等式 | 候選內容與限制 |
|---|---|---|
| consumer `0x12c5e` 保存入口 S3 | `(E−80)+60=E−20` | **入口 S3**，不是 consumer 稍後設的 `0x40000`；值及 frame 保存未知 |
| pin wrapper `0x9a36` 保存入口 A2 至 record | `(E−32)+12=E−20` | 本初始化請求值依序為 `0x18/0x48`；需 driver／frame 保存，且返回後未被其他 writer 改動 |
| 完成的 `0x12d92` local fill32 的 I+28 | `(E−48)+28=E−20` | 只有 fill 成功、後來 driver／其他 stores 保持該欄位時，才可連到先前零值 |
| 同 E 的先前 standard IRQ `0x18d90` | `R=E−20` | standard ID word；之後 extended 本體不直接替換它，仍需無其他 writer |

consumer 是先保存 entry S3，之後才把自己的 live S3 設為 `0x40000`；檢查器以完整原 consumer body 的 `0x12c5e` store 核對這個順序，沒有用後來常數代替舊保存值。

reset 的名義初始 SP=`0x20010000`，zero 區間結束於 `0x2000c958`。若 IRQ 的 E 恰為該 SP，E−20=`0x2000ffec` 不在 reset zero 區間內。這不證明實際 IRQ 使用此 SP，也不推論該 RAM 為零、未映射或無效。

硬體 push／SP switch／nesting、其他 callees 的 stack 重用與非同步 writer 都會影響實際位置及內容。候選來源只能縮小下一步調查，不能決定 extended ID 必為某個值或已接收到 ID1657。

## 重播與下一個邊界

```text
python analysis/check_v4160_irq_setup_stack_sources_static.py
python -O analysis/check_v4160_irq_setup_stack_sources_static.py
```

一般／`-O` 皆需精確重播 ledger，通過 256 組 CSR 主機代數、三個控制區索引連接、512 組同 SP 位址見證、12 組設定分支邊界，以及 18 個指定原指令 mutation。這些是靜態證據與算術，不是 IRQ／硬體功能測試。

後續仍需追查 restore 入口 `0x8448` 的 frame 建立者及其與此 IRQ 的連結、兩個 driver 的 config 使用／保存合約、resident fill／copy 的 installed 身分，以及實際 E−20 最後 writer 與 context 保存條件。
