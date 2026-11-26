# v4.1.60：RAM JT0 初始來源與 return-mask 寫入鏈

日期：2026-11-26。接續 [完整外層 dispatcher](v4160-event-dispatch-static.zh-TW.md)，本輪閉合兩個靜態來源：initializer 明確寫入 RAM JT0；stop-task 明確更新 dispatcher 返回時所讀的同一 halfword。[檢查器](check_v4160_dispatch_origin_mask_static.py)／[ledger](v4160-dispatch-origin-mask-static.json) 固定兩版全部 startup、initializer、stop-task 指令與相互關係。

**JT0 指標先發布，才呼叫搬入程式本體的 helper。stop-task 的遮罩更新不以 timer 命中或 clear-event 成功為條件。** 這些是候選原指令的條件性合約，仍不證明實際 installed provider、完整 boot、呼叫可達性、指標保存或 ownership。

本輪全程只讀本機來源、解碼、建立條件式圖與驗算主機位元算式，沒有執行或模擬 target ISA、copy state、loader、scheduler、node list、provider、callback 或 MMIO。原 BIN、既有 ledger、C 原始碼未改寫，C 重建覆蓋率不增加。

## 六個完整本體

區間終點不含；位址均為十六進位。

| 候選／body | source range | bytes／instructions／stores | SHA-256 |
| --- | --- | --- | --- |
| V1.31 startup | `6de7e..6dec2` | 68／18／1 | `98fe32a0b24638e9f678c2112dbae4fa05ad6e45d2a9fb84bedb67c3831880b0` |
| V1.40 startup | `6e06e..6e0b2` | 68／18／1 | `be10a8a9345b43c9581cade65059b0aa39b9e6cf46953b5179b7cd909aaa926c` |
| V1.31 initializer | `6de0c..6de7e` | 114／32／4 | `7a0cf58801fabb3dcb9d26fcece3d01b2f41276dacce4130daff0e663559927f` |
| V1.40 initializer | `6dffc..6e06e` | 114／32／4 | `e5a738246f7b39ca8dc057596acaf0040bb6673935fac8015ef1dba8af84c74e` |
| V1.31 stop-task | `439a8..43a14` | 108／39／9 | `b7039b31b68bfe6aeae2e453d4b159efab81edade95c9f3079a56898444ff098` |
| V1.40 stop-task | `43a34..43aa0` | 108／39／9 | `ef68aa1e9331e08e48880f35aa3b1d0ec25d2f781fa60289d78a07330beec866` |

合計 **580 bytes、178 instructions、28 個靜態 store 位址**，含 frame stores 與 loop 內單一 store 位址；不是執行次數。initializer／stop-task 的既有完整身分與 caller 合約沿用且重新驗證，本輪補上全部操作數與明確的 JT0／dispatcher return-mask 串接，不把既有成果當成新 C 進度。

## startup：固定參數與形式 CFG 的差別

startup 前 40 bytes 的五組 AUIPC/ADDI 分別建立 GP=`20004000`、SP=`20010000`、seed source=`40280/402c0`、A1=`20000010`、A2=`20000040`。檢查器逐組固定 registers 與數值目標，並固定完整本體 hash。

相對 startup 入口，以下加數為十進位：

- +40：BGEU A1,A2，若成立直接到 +64 MRET。
- +44／+48：LW T0,0(A0)，SW T0,0(A1)；+52／+54 分別把 source／destination 加4。
- +56：BLTU A1,A2，成立則回 +44。
- +60：JAL initializer，link=入口+64；+64 固定為 MRET `73002030`。

在已固定 A1<A2、有效來源與目的存取、code/context 保存及正常有限 loop 進程前提下，seed interval 為 48 bytes／12 words，再進 initializer。這是來源範圍與控制條件的靜態推導，沒有執行 copy 或建立 RAM 狀態。

**不帶常數前提的形式 CFG 仍有 +40→MRET 的 skip edge。** 因此不能說 initializer 的 JT0 store 無條件支配每條形式 CFG 的 MRET 路徑。MRET 另列為外部 exit；其 CSR、返回目的與硬體效果沒有證據，不能稱普通 RET 或已完成應用程式啟動。

## initializer：JT0 的具體初始 store

固定 header 的 `RAM_BASE_ADDRESSS=20000000`、`BLE_LIB_RAM_JT(n)` stride=4，加上既有 `TMOS_SystemProcess` RAM JT0 alias，對上 initializer 的明確常數與 store：

```text
+2   LUI  A4,20000000
+8   LUI  A5,20000000
+12  ADDI A4,A4,2000 decimal      # 0x7d0
+16  SW   A4,0(A5)               # U32[20000000]=200007d0
```

兩版 +16 原 bytes 都是 `98c3`；實際 source PC 為 V1.31 `6de1c`／V1.40 `6e00c`。該 store 前沒有 branch 或 call。另兩筆同 base 的 stores 是：

| initializer offset（十進位） | RAM slot | V1.31 word | V1.40 word |
| --- | --- | --- | --- |
| +16 | `20000000` | `200007d0` | `200007d0` |
| +26 | `20000004` | `2000251c` | `20002568` |
| +48 | `20000008` | `20002e34` | `20002e80` |

JT0 word 精確等於前輪完整 dispatcher 的 RAM 入口 `200007d0`，其兩版 flash source 分別為 `40a40`／`40a80`。JT1／JT2 在本輪僅固定字面值，未展開其 handler 合約。

JT stores 全在第一個 copy pair +62/+66 之前；第二個 copy pair 是 +94/+98，最後 +106/+110 恢復 frame 後 tail 到 zero helper `20000022`。**初始指標發布早於 code copy，不表示發布當時 code 已就緒，或外部呼叫者不會過早取用。**

seed 目的 `[20000010,20000040)`、first-copy 自 `20000040` 起、second-copy 自 `20002e70/20002ebc` 起、zero 自 `20002ef8/20002f48` 起，已列四種目的區間都與 JT0..JT2 的 `[20000000,2000000c)` 不相交。這只是已列地址區間的算術結果，不能擴成全程沒有 computed store、stack alias、其他 writer 或中斷影響。

## 完整 sparse 來源缺口仍保留

本輪重新解析固定的兩份完整 HEX，比對 34 個既有 sidecars、checksum／record 身分及來源覆蓋率，沿用 [sparse boot coverage](v4160-sparse-boot-coverage.zh-TW.md) 的嚴格 reader，不拼接填洞影像。

| 候選 | 第二段要求但未捕獲的 source word | 對應 RAM |
| --- | --- | --- |
| V1.31 | `6eb2c..6eb30` | `20002ef8..20002efc` |
| V1.40 | `6ed20..6ed24` | `20002f48..20002f4c` |

各缺最後四個來源 bytes。後續 zero helper 的第一筆 store 會要求覆蓋同一目的 word，**不能倒過來證明先前 read 已成功**。缺少 HEX record 也不等於物理 flash 沒有值或必然 fault。JT0 初始 store 已有具體來源，完整 boot、pointer retention 與 installed 綁定仍未閉合。

## stop-task：另一個 return-mask writer

令 M 為 metadata base：V1.31=`2000319c`，V1.40=`200031ec`。slot `4005c` 的 `tmos_stop_task` 分別指向上表兩個 stop-task；slot `40054` 的 `tmos_clear_event` 指向 `4358a`／`43616`。header alias、完整 lookup／clear-event 合約與 body hashes 都重新驗證。

stop-task 保存完整入口 task 到 S2、event 到 S0，建立 32-byte frame 並保存 RA、S0..S3。它先保存控制 word `4002420c`，寫零、FENCE.I，再：

1. 直接呼叫 RAM lookup `20000314`，以完整 task／event 作精確比對；正常返回 Q 保存於 S1。
2. Q 非零就 SH zero 至 Q+2，令 node mask 歸零；此處沒有 free。lookup 自己不讀 task count；終止與有效 node 存取仍是前提。
3. 以保存的 task／event 呼叫 clear-event；正常返回的 scalar A0 **沒有被檢查**。
4. fresh 讀 cursor=U8[M]，與**完整**保存 task 比較；相等才讀 U16[M+64]、OR 保存 event，再 SH low16 回同一欄位。
5. 恢復外層保存的控制 word。若保存 lookup reply S1 非零，返回0；否則返回6。這不是 clear-event／mask-update 成功的收據。

| 語義 | V1.31 PC | V1.40 PC |
| --- | --- | --- |
| node+2 清零 | `439d4` | `43a60` |
| clear-event call | `439dc` | `43a68` |
| fresh cursor read／比較 | `439e2`／`439e6` | `43a6e`／`43a72` |
| return-mask LHU／OR／SH | `439ee`／`439f2`／`439f4` | `43a7a`／`43a7e`／`43a80` |
| return-mask storage | `200031dc` | `2000322c` |

return-mask 更新只有 cursor==task 這個局部分支條件，**不要求 lookup 命中，也不要求 clear-event 回覆0**。例如「lookup 未命中所以返回6」與「同 task 時更新 mask」在此局部條件式相容；這不是已證明真機可達的 trace。

clear-event 獨立檢查 full task < fresh U8[M+1]。成立時對 fresh pending base+2*task 作 `old_U16 & ~event`，返回0；不成立不讀寫 pending table，返回3。它沒有固定 M+64 store；但 dynamic pending pointer、lookup node、frame 或其他存取的 alias 尚未全面排除，因此不能據此宣稱整條 call 絕不碰 M+64。

既有完整 lookup／clear-event 的 encoded GPR write sets 都沒有 S/SP，支持這條 caller 的局部保存需求；不等於證明 callee 存取不會 alias saved frame、物件有效或不存在外部 writer。控制 word 的實體 MMIO／中斷效果仍未證。

## 接回 dispatcher：抑制的是 reply 重新併入

前輪 dispatcher 在 handler call 前清 U16[M+64]，正常返回後於 `2000090c` 重讀同一半字。若 handler 期間經上述 stop-task 寫入，且 mask／context／地址保存至返回讀取，令讀到 C=C0|event，則：

```text
result = low16(H | (handler_reply & ~(C0 | event)))
```

event bit 不會從 handler_reply 重新併入；**H 中已存在的相同 bit 仍由 OR 保留**。它不是強制 pending 清零，也不是跨 read-to-store 的 atomic 更新；H 讀取之後的外部寫入仍可能被覆蓋。dispatcher 在 clear 前後、handler 返回後會重讀 cursor／table base，不能把這些快照無條件等同入口 task 或原選取地址。

本輪只驗證具體 stop-task writer 與 dispatcher clear／reload。沒有建立全 ROM 所有直接、computed、bulk 或 alias writer 的排除證明，也沒有證明 APP handler 實際以何種 task／event 呼叫 stop-task。

## 可重播與發布界線

需要固定 APP、兩份主 carrier／完整 HEX、34 個 sidecars、raw SDK header、saved HEX reader 及既有 LLVM Xwchc 來源／vectors；全部沿用原始 bytes identity guards。本輪不下載、不安裝、不啟動服務、不上傳候選輸入。只有 GitHub clone 而沒有本機候選來源，不足以完整重播。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_dispatch_origin_mask_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_dispatch_origin_mask_static.py
```

兩模式精確重播同一 JSON，RuntimeError guards 不因 `-O` 關閉。主機檢查包含 262144 個 OR identities、1048576 個指定 reply/pending 邊界組合的 mask merge cases、768 個 full-task/cursor cases，以及 17 個指定原指令單 bit 變異。這些是位元／位址／operand 驗證，不是 target loader、register machine 或可變 event-memory 模型。

發布前核對 19 個 transitive Python dependencies 與 GitHub main 的 blob identity；本輪只新增 checker、ledger、本文，保留原 BIN、舊分析與本機 Git index。尚需追查實際 installed provider、JT0 後續 writer／保存、真正的 APP caller／重入條件、opaque tail／callees、node/record ownership 及硬體效果。
