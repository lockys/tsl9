# v4.1.60：RAM callback 入口算術與前兩次條件性間接呼叫

接續 [loaded hook 的兩個來源](v4160-loaded-hook-sources-static.zh-TW.md)。先前常數 caller 將 `0x20000d50` 傳給 hook setter；本輪依相同 first-copy 映射，驗證該地址的入口與第一段條件 CFG。兩份 resident 仍為**候選**，沒有建立實際 installed provider 或 callback 執行證據。

重點有兩項：入口的 `+999999` 必須保留 32-bit 回繞，不能一律視為一般數學向上取整；兩個向低地址跳轉的修正分支均匯入各自判定之後，本輪選定的 local graph 無循環。其餘 callback 與未知 callees 仍可包含迴圈、重新進入或不返回。

只做原 bytes／operands／條件 CFG 與主機端整數算術。未執行或模擬目標 ISA、RAM、stack、callback、resident、CSR 或硬體。既有 C 重建 bytes 未增加。

## 八個有界片段，並非完整 callback

| 片段 | V1.31 FLASH，end-exclusive | V1.40 FLASH，end-exclusive | 每份 bytes／指令 |
|---|---|---|---:|
| 入口 prefix | `0x40fc0..0x41012` | `0x41000..0x41052` | 82／26 |
| 第一次 call 與判定 | `0x41012..0x4102c` | `0x41052..0x4106c` | 26／7 |
| 兩個修正分支 | `0x41048..0x41054` | `0x41088..0x41094` | 12／6 |
| 第二次 call 與 field136 | `0x41054..0x41064` | `0x41094..0x410a4` | 16／5 |

兩份各 136 bytes／44 指令，合計 272 bytes／88 指令。每個片段均核對全部 operands 與 SHA-256，並在 FLASH 與映射 RAM 座標分別核對 PC-relative edges。兩份 entry 都映射至 `0x20000d50`，並與先前 caller 的 A0 常數相接。

入口 SHA-256 分別為 `ef4777186c30e11cc321d60304bd8c66e65518db9953a420b70f8bfd5f6b27c2`、`3b6115270fff9303beada863e7e709a802c30ed735000b9d4a164d6eb0b748ea`。其他片段的 hash、原指令與完整 local CFG 均存於 ledger。

APP 仍為 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。候選、SDK、sparse 與指令格式來源合約遞迴重驗。

## frame 與入口資料來源

prefix 先做 SP-=32，以八個 word stores 保存 RA／S0..S6：RA@28、S0@24、S1@20、S2@16、S3@12、S4@8、S5@4、S6@0。這不是包含所有 GPR 的 IRQ frame，也不證明之後每條 callback 出口都能恢復它。

| 來源 | V1.31 | V1.40 |
|---|---|---|
| fresh object pointer word → S0 | `0x2000345c` | `0x200034ac` |
| fresh unsigned factor halfword | `0x2000323c` | `0x2000328c` |
| nominal S3 base | `0x200033b8` | `0x20003408` |
| nominal S1 base | `0x20003234` | `0x20003284` |
| nominal wrap word `[S1+4]` | `0x20003238` | `0x20003288` |
| nominal service pointer word | `0x200031e0` | `0x20003230` |

object pointer 沒有 local null guard，就讀 `U16[object+134]` 與 `U32[object+144]`。factor 的 raw halfword `0x279e` 依已保存的官方 LLVM Xwchc 格式核對為 QK.C.LHU A5,8(A5)；另一個 object factor 是標準 unsigned LHU，另釘其 unsigned encoding。

這些是按原指令順序取值的 operands，沒有建立 coherent snapshot、有效物件型別或實際輸入範圍。frame／object alias、其他 writer 與存取條件仍是前提。

## 加法回繞會使 quotient 歸零

在上述 unsigned loads 與 RV32 算術前提下：

```text
a = loaded U16[object+134]
b = loaded U16[factor_source]
P = a*b
N = (P + 999999) modulo 2^32
Q = N unsigned_div 1000000
first_taken = (loaded U32[object+144] < Q)   // unsigned
```

兩個 U16 的乘積本身最多 `4294836225`，可放入 U32；但後續加 `999999` 可能溢位。加法溢位恰在 `P >= 4293967297`。

無溢位時 Q 等於 `ceil(P/1000000)`。有溢位時，回繞後 N 最多 `868928`，小於除數，因此 Q=0；unsigned word144 不可能小於零，該次第一條 BLTU 會走 fallthrough。這只是假設輸入成立時的指令算術結果，不證明實際資料可達溢位範圍。

具體主機端算術反例：

```text
a=b=65535
P=4294836225
P+999999=4295836224
N=868928
Q=0
mathematical ceil(P/1000000)=4295
```

因此不能把重建寫成沒有回繞的 ceiling helper。

## 第一次 call 與兩個有界修正

第一個 unsigned 判定若成立，從 RAM `0x20000d9e` 跳至 `0x20000dd8`：fresh load `[then-live S1+4]`、加到 A0，再跳 `0x20000da2`。它不重新執行原 BLTU。

在第一次 call 片段，先令 S4=`0x20003000`，fresh load service word 到 A5，再做 `S2=A0-Q`，隨後 JALR A5；沒有 local null guard。A0 是此時仍在 register 中的值，不能僅憑服務名稱替它命名參數或推定 scalar return 的意義。

若未知 target 正常返回，且所需 S1／S2 等保存條件成立：

1. 比較 unsigned S2 與返回後 A0。
2. 若 S2 小於 A0，從 `0x20000dde` fresh load `[then-live S1+4]`、加到 S2，再跳到 `0x20000db4`。
3. 在匯入點做 `S2-=A0`，以 32-bit signed S2<0 決定是否進入第二次 call。

第二個修正也不重新執行選擇它的 BLTU。兩個 wrap-word loads 位於第一次未知 call 的前後，不能假定值相同；之後的 nominal 地址也需要 live S1 保留原基址。

檢查器將八個片段合併成 conditional-normal-return CFG，驗證所有選定 nodes 由 entry 局部可達且無 back cycle。這項結論不涵蓋 call target 內部或未查 continuation。

## 第二次 call 的 target 與 field136 都重新讀取

第二次 call 入口 RAM `0x20000de4` 再讀 `[then-live S4+service_delta]`，然後 JALR；只有 S4 在第一次 call 後保留時，這才仍是表中的 nominal service word。兩次 target 的 raw pointer 可以不同，沒有 null guard 或身分相等檢查。

第二次 call 正常返回後才讀 `U32[then-live S0+136]`。這不是入口的 object snapshot；callee 可以影響 base、資料或返回條件。

- unsigned 返回 A0 小於 fresh field136：跳至外部 continuation。
- 否則做 A0-=field136，離開本輪選定 graph。

## 三個明確 cuts 與重播

| RAM cut | V1.31 FLASH | V1.40 FLASH | 來源 |
|---|---|---|---|
| `0x20000dbc` | `0x4102c` | `0x4106c` | 第一次減法結果 signed 非負 |
| `0x20000df4` | `0x41064` | `0x410a4` | 第二次返回後的減法 |
| `0x20000e8c` | `0x410fc` | `0x4113c` | 第二次返回值 unsigned 小於 field136 |

[檢查器](check_v4160_ram_callback_prefix_static.py) 與 [完整 ledger](v4160-ram-callback-prefix-static.json) 可重播：

```text
python analysis/check_v4160_ram_callback_prefix_static.py
python -O analysis/check_v4160_ram_callback_prefix_static.py
```

一般與 `-O` 模式均逐 byte 重現 ledger，核對原 operands／hash、八個保存欄位、雙座標 edges、合併 CFG 的無循環性與三個 cuts，以及 42 個指定 operand mutation。算術檢查另驗證閉式溢位界線、具體反例，並窮舉「一個 factor 固定為 65535、另一個遍歷 U16」的 65,536 個主機端算術 cases；沒有宣稱已窮舉所有 factor pairs 或驗證實際輸入可達性。

接續仍需展開三個 cuts、完整 callback 的迴圈／出口、service pointer 的寫入來源與實際語意、object／factor／wrap 資料來源，以及完整 frame／物件保存期。installed provider、登錄次序與 ECALL 路由仍未確定。
