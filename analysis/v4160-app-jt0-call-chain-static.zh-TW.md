# v4.1.60：原 APP 的 resident 交接與每輪 JT0 呼叫鏈

日期：2026-11-26。承接 [JT0 初始來源與 return-mask](v4160-dispatch-origin-mask-static.zh-TW.md)，本輪把固定 APP 的入口、reset、main、初始化序列、主迴圈與旗標服務，接到兩份候選的 JT0／dispatcher 證據。[檢查器](check_v4160_app_jt0_call_chain_static.py)／[ledger](v4160-app-jt0-call-chain-static.json) 保存全部操作數、完整 body hashes、條件性 CFG、呼叫／link 與 direct stores。

**APP 明確把 `9008` 作為 MEPC 寫入 operand，再跳 `40000`；main 先呼叫初始化序列，才進每輪 fresh 讀 JT0 的迴圈。** 這是原指令的靜態串接，不是實機 boot trace。實際 resident 身分、MEPC／JT0 保存、callee 正常返回及硬體效果仍未證明。

既有 [main-loop config reentry](v4160-main-loop-config-reentry.zh-TW.md)、[兩個直接服務](v4160-main-loop-two-services.zh-TW.md) 已有局部窗口。本輪新增完整五個本體的逐指令 guards、兩候選來源鏈與同一份可重播 ledger；不是新的 C 還原覆蓋率。全程本機讀檔、解碼與主機算術，沒有執行或模擬 target ISA／CSR、boot/copy state、scheduler、callee、callback 或 MMIO。

## 固定 APP 與完整範圍

APP 為 76800 bytes，base=`8000`，end-exclusive=`1ac00`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。下表位址為十六進位，終點不含。

| 完整本體 | range | bytes／instructions／stores | SHA-256 |
| --- | --- | --- | --- |
| reset 至 resident handoff | `186aa..18734` | 138／37／2 | `9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d` |
| main caller | `9008..901a` | 18／8／1 | `87dd87b4471d5281a6185185b66e454ac79136553f837e3c9a3c2abdfb85ead5` |
| 初始化呼叫序列 | `9250..9290` | 64／19／1 | `9c9a241ad1ffb34eab4267c3368c9b5cbd459e1d9f111621eb4716087f8cf60b` |
| JT0 主迴圈 | `8180..81aa` | 42／15／5 | `c440bafcc9fdbe370d24fbcd3bd0c67e8162ceaa776a64ea6f34f1d509b6f72f` |
| 旗標服務 | `17002..17040` | 62／21／5 | `dd6b0fa91982cf653657b71e2d2bfaf2d6349ccc12f2b31561483e40572b0c69` |

合計 **324 bytes、100 instructions、14 個靜態 memory-store 位址**，包含 frame 與 loop stores，並非執行次數。另固定 APP `8000` 的4-byte入口 transfer `JAL X0,186aa`；連該指令是328 bytes／101 instructions。CSR 操作另外列出，不計為 memory store。

全部五個本體的每條 opcode／operand／target 都有 guards；CSR 額外解碼 rd、rs1、funct3、CSR number，區分 CSRRW／CSRRS，不執行其效果。所有 call fallthrough 都表示明示假設的正常返回；external tail edge 另列，不當成 RET。

## reset：資料區間與 CSR operands

reset 的 PC-relative constants 固定：

| operand 用途 | 數值／區間 |
| --- | --- |
| GP | `20004000` |
| SP | `20010000` |
| initialized-data source | `1ab60..1abe0`，128 bytes |
| initialized-data destination | `20004000..20004080`，32 words |
| zero destination | `20004080..2000c958`，8758 words |
| CSR `bc0` write operand | `1f` |
| CSR `804` write operand | `3` |
| CSR `300`（mstatus）OR-set operand | `1888` |
| CSR `305`（mtvec）write operand | `803b`，由 `8038 OR 3` 形成 |
| CSR `341`（mepc）write operand | `9008` |

copy／zero 的 range 是依比較、加4及初始常數得到的半開位址區間，沒有建立 RAM 狀態或執行 stores。128-byte APP 來源完整存在，其 hash 另存 ledger。這兩個**已列目的區間**與 JT0 `[20000000,20000004)` 分離，不代表所有初始化 callee、stack alias、computed store、IRQ 或其他 writer 都不能碰 JT0。

reset 在 `18720` 呼叫 opaque hardware initializer `1874a`，link=`18724`。只有它正常返回，才有以下交接：

```text
18724  AUIPC T0,ffff1000
18728  ADDI  T0,T0,-1820       # 數值 9008
1872c  CSRW  MEPC,T0
18730  JAL   X0,40000         # 不寫新 link
```

本輪固定的是原 bytes 與 operand 數值，沒有證明 CSR 在實機的可寫性、權限、trap、實際返回目的或 vendor 特有效果。跳 `40000` 也不證明該處實際裝了哪一版 resident。

## 與兩份候選的條件性往返

既有來源鏈重新驗證：兩候選 `40000` 入口到各自 startup，initializer 在 copy 前寫 `U32[20000000]=200007d0`，其完整 dispatcher 來源分別是 `40a40`／`40a80`。候選 startup 最後有明確 MRET external exit：

| 候選 | startup | MRET PC | initial JT0 writer |
| --- | --- | --- | --- |
| V1.31 | `6de7e` | `6debe` | `6de1c` |
| V1.40 | `6e06e` | `6e0ae` | `6e00c` |

若 resident 確實安裝、初始化與 code copy 完成，MEPC 保持適用且 MRET 按所需語義返回，APP 才可接回 `9008`。候選第二段 sparse source 仍各缺最後四個 bytes，既有缺口沒有被本輪解除。初始 JT0 的明確來源，也不能替代後續保存或實機 installed identity 證據。

## main 與初始化 tail

完整 main 建16-byte frame、保存 RA，`900c` C.JAL `9250`（link=`900e`），其正常返回後 `900e` JAL `8180`（link=`9012`）。兩個 call 前沒有額外參數設定。

`9250` 建16-byte frame、保存 RA，依序呼叫以下14個 targets；它們之間沒有本機參數設定或回覆分支：

```text
18834, 9a42, 1973c, 9f4c, 131c2, 8e88, 9b4e,
9958, 9f12, 12d92, 14c8a, 154a6, 17040, 173a2
```

之後恢復 RA／SP，於 `928c` **tail→17bf6**。恢復 frame 不等於整個初始化已返回；還需要各 call、saved frame／context 與 tail 的合約。這14個 callees 與 tail 也位於 resident JT0 初始 store 和 APP 首次讀槽之間，不能從已知初值推斷當時 word 未變。

main 雖保留 `9012..901a` 的返回 suffix，`8180` 本體沒有本機 RET 路徑，所以不能宣稱正常迭代會抵達該 suffix。

## 每輪 JT0 call 與兩個後續服務

`8180` 建16-byte frame，保存 RA、S0、S1、S2，設名義 S2=`20000000`、S1=`40003000`、S0=`aaaa`。每輪六個 instruction starts 是：

| APP PC | 原指令角色／正常續行 |
| --- | --- |
| `8198` | fresh U32[then-live S2]→A5 |
| `819c` | 間接呼叫 A5，數值 target=`raw & ~1`；沒有本機 null guard；link=`819e` |
| `819e` | 直接呼叫 `17002`；正常返回到 `81a2` |
| `81a2` | 直接呼叫 `12c58`；正常返回到 `81a6` |
| `81a6` | SW then-live S0 至 then-live S1 |
| `81a8` | 無條件 jump `8198`，不寫 RA |

首輪槽位基底由本機 S2 assignment 建立；往後仍需中間呼叫保存 S2。重新 load 不代表重新讀到相同 word，亦不能把每輪 target 固定為候選 `200007d0`。名義 `40003000` 的32-bit store 值為 `0000aaaa`，其實際 MMIO／裝置效果未證。

整個 loop 本體不設定 A0，也不檢查三個 calls 的 scalar reply；ambient registers 可被 callees 觀察。局部 CFG 沒有走到 main suffix／config 的控制邊；opaque callees 仍可能自行 reenter 初始化、改寫狀態或不正常返回，不能由此推出全呼叫鏈的缺席證明。

`12c58` 在本輪 ledger 是**固定 call target 與 opaque 副作用邊界**，不是第六個完整本體；其既有記錄 consumer 證據沒有在本輪擴大成無副作用保證。

## `17002`：兩次獨立旗標讀取

完整旗標服務先讀 U8[GP+360]，測 bit0。命中則先清 bit0，再以 A0=1 call `16b0a`，正常返回後清 GP+361。接著**fresh 再讀** U8[GP+360]，測 bit1；命中則先清 bit1、A0=2 call 同一 callee，正常返回後清 GP+362。

名義 GP 保持時，上述 byte 地址為 `20004168..2000416b`。第二次判斷不可沿用第一次 snapshot，後續清 byte 也不可說成在未知 callee 返回前已完成。兩個 bit 都未命中才沒有子呼叫；`16b0a` 的內部 effects、GP/SP/frame 保存及重入仍需獨立證據。此本體正常返回時不統一設定 scalar A0。

## 重播與發布範圍

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_app_jt0_call_chain_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_app_jt0_call_chain_static.py
```

兩模式精確重播同一 JSON；RuntimeError guards 不依賴可被 `-O` 關閉的 assert。主機驗證包含65536對獨立 flag read 算式、65536個 bounded pointer low-bit cases，以及15個指定原指令單 bit 變異在預期 guard 失敗；沒有建立 register machine、可變 RAM、boot 或 event-memory 模型。

本輪另核對20個 transitive Python dependencies 與 GitHub main blob 身分。完整重播仍需要本機固定 APP、兩份候選主 carrier／HEX、34個 sidecars、saved reader、raw SDK header 與 LLVM Xwchc sources／vectors；只有 clone repo 不足以完整重播。這些候選來源不隨本輪上傳，也不下載新來源。

只發布新 checker、ledger、本文；保留原 BIN、既有分析、C 原始碼與本機 Git index。未閉合的部分包括 `1874a`、14個初始化 callees／`17bf6` tail、`16b0a`／`12c58` 的後續 effects，以及實際 JT0／MEPC／context 保存、provider 身分與 node/record ownership。
