# v4.1.60：硬體 leaf、初始化尾跳與首輪 A0 來源

日期：2026-11-26。接續 [APP resident/JT0 呼叫鏈](v4160-app-jt0-call-chain-static.zh-TW.md)，展開 reset 的 `1874a` 與初始化尾跳 `17bf6`，再追到 `17b92` 的兩條正常 RET，並固定中間 helper `1798a` 的完整合約。[檢查器](check_v4160_init_tail_hardware_static.py)／[ledger](v4160-init-tail-hardware-static.json) 保存全部原指令、操作數、條件性 CFG、stores、巢狀呼叫與來源串接。

**硬體 leaf 有兩個無本機計數逾時的等待迴圈，不能保證返回。若初始化沿本輪確認的尾跳鏈正常返回且 context 保存，首輪 JT0 call 前的 A0 則可限定為最後一次 U8[GP+378]，範圍0–255。** 這個 byte 範圍結論不需要把 JT0 的實際 target 認定為候選 provider。

本輪補上與當前證據鏈的完整 guards，不將先前已有的硬體／初始化分析報成首次發現。全程離線讀檔、解碼與主機位元算術，沒有執行或模擬 target ISA、CSR、MMIO、boot/copy state、provider、timer 或 callback。原 BIN、舊 ledger 與 C 原始碼未改寫，C 重建覆蓋率不增加。

## 四個完整本體

以下地址為十六進位，range 終點不含。

| 本體 | range | bytes／instructions／stores | SHA-256 |
| --- | --- | --- | --- |
| hardware leaf | `1874a..18834` | 234／93／21 | `e0debe8b77025cfb56144045a0aa7524b7a2cd2ad0bd3daa2d880408ad9758f5` |
| late init | `17bf6..17c4e` | 88／30／3 | `2610037e76c76f2f6d393773b5ab1251f86c3cb2201ab972da78778ab8a1a3df` |
| tail return | `17b92..17bc4` | 50／17／2 | `9f5b6868f32f0296af6e11a1089470c89e95cbeeb98db464f0ed114cc152ed3c` |
| select/schedule helper | `1798a..179fc` | 114／44／4 | `0969013e78bab8c5a4124628d5a3c7bf3a5d017f5fabed9be493fdcc1e3b065e` |

合計 **486 bytes、184 instructions、30個靜態 memory-store 位址**，含 frame／scratch stores，並非執行次數。全部 instruction boundaries、opcode／operand／target 逐項固定，完整 hash 另檢查；每個本體的條件性圖覆蓋全部指令。`18830/18832` 是 hardware 的 cold 尾段，不在 `1882e RET` 提早截斷；`17bc4` 開始的相鄰入口則不屬於 `17b92`。

## `1874a`：可限定直接寫入，不能保證硬體等待結束

前輪 reset 的 `18720` call→`1874a`，link=`18724`。此完整 leaf **無子呼叫、無 SYSTEM/CSR 指令**，encoded GPR writes 僅 `[SP,A2,A3,A4,A5]`，沒有 RA、GP、S-register、A0／A1 writes。

建立16-byte frame，SP+8／SP+12 是 counter／status scratch；沒有保存 RA。正常路徑在 `1882c` SP+=16、`1882e JR RA`。在有效 code／stack／MMIO、無外部 context 改寫等條件下，正常返回保持入口 A0，不能把它當作硬體 status。

全部43個 memory-access 位址可分類為：

- 33個 MMIO sites：18 loads、15 stores；原 operands 的固定 base=`40021000`，只用 word offsets0／4／8。
- 10個 SP sites：4 loads、6 stores，僅 scratch+8／+12。

在 stack 有效且與 JT0 不重疊的條件下，本體沒有直接 JT0 store；沒有 CSR341/MEPC 指令寫入。但 MMIO 的實體副作用、IRQ、reset、非同步 writer 或硬體 context 保存仍未證明，不能擴成整機 JT0／MEPC retention 保證。

開頭及 setup 分支有多次 fresh-read RMW。`187de`／`187e2` 甚至各有「讀回同值再寫回」的 store；保留它們，不因數值相同就當作 MMIO no-op 刪除。

### 三個 poll 與重新分類

| 範圍／回邊 | 原條件 | 終止限制 |
| --- | --- | --- |
| `187a2..187b8`，`187b4→187a2` | fresh reg0 & `20000` 存 scratch，counter++；status非零或counter=4096就離開 | stable、nonalias、無 writer 的 scratch 前提下最多4096輪；不是整個函式 timeout |
| `18806..18810`，`1880c→18806` | fresh reg0 的 SLLI6 結果非負則回跳，即等待bit25=1 | 無本機計數 timeout |
| `18824..1882c`，`18828→18824` | fresh reg4 &12，直到等於8，即 bits3:2=2 | 無本機計數 timeout |

第一次 poll 離開後，`187bc` **fresh 再讀 reg0**，透過 SLLI14／signed BGE 測該次 bit17。bit17=0 經 cold 尾段把 scratch 設0；bit17=1 則寫1。`187ca` 又 fresh 讀 scratch，等於1才進 setup 與後兩個 polls，否則走 epilogue。

不能從第一次 poll 的舊 status 推斷這次分支；達到4096輪也不表示整段一定返回，因為 fresh bit17 仍可能讓它進入後面的無界等待。bit 名稱僅描述指令測試位置，本輪不指定真實 clock、oscillator 或 PLL 效果。

## `17bf6`：fill、register、cancel、schedule，再尾跳

前輪 `9250` 的 `928c` tail→`17bf6`。它建立16-byte frame、保存 S0／RA，S0 名義值=`40000`，依序提出：

| PC | 當次呼叫／本機動作 |
| --- | --- |
| `17c0a` | fresh `[40048]`，參數 `(then-live GP+376,0,3)` |
| `17c1c` | 重讀 `[40048]`，參數 `(2000c8ac,0,115)` |
| `17c2a` | fresh `[40080]`，A0=`176f8`；正常返回後 low8(A0) 寫 GP+379 |
| `17c38` | `90b0`，A0=`178f8`；本輪保留為 opaque callee |
| `17c40` | `1798a(A0=1,A1=0)` |
| `17c4a` | 恢復 S0／RA／SP 後 tail→`17b92`，不寫新 link |

固定 raw SDK header 的 aliases 分別為 JT5 `tmos_memset`、JT19 `TMOS_ProcessEventRegister`；兩候選 slot 內容重新核對。這是參數與候選槽位證據，不表示 fill 已完成、函式表成功登記或實機使用相同 provider。

兩次 `[40048]` 是不同時間的讀值；後續 slot 讀取需要 S0 保持／恢復。第一次請求名義上只涵蓋 GP+376..378，不含隨後存 reply 的 GP+379；不能因此推定進尾端時 GP+378 一定仍為零。中間 callees、provider、外部 writer 與 alias effects 仍可能改值。登記回覆只被 SB 截低8位，沒有 invalid-task-ID guard。

## `1798a(1,0)` 的具體排程請求

完整 helper 先比較完整 unsigned A1 是否大於35；大於就不建 frame 直接 RET。否則建立32-byte frame、保存 RA，再依入口 A0 是否非零分流。

此處 caller 明確設定 `(1,0)`，因此在指令與 context 保持前提下，選中非零分支：

```text
U8[GP+376] = low8(entry A1) = 0
target = fresh U32[40058]
A0 = fresh U8[GP+379]
A1 = 2
A2 = 2
indirect call target
restore RA/SP; RET
```

header 對應 JT9 `tmos_start_task`。這裡沒有對 task、provider pointer 做本機有效性／null guard，也不檢查排程回覆；數值2沒有推定物理時間單位。正常返回 A0 可仍為 provider scalar reply，但外層 `17bf6` 接著尾跳，`17b92` 的 byte 重讀會覆蓋它，不能當作初始化成功收據。

為保持完整 body，另一個 A0=0 分支也固定：用 fresh U32[GP+100] 與 `7*entry A1` 組來源，要求 `[4004c]` 複製7 bytes至SP+8；再依 stack word bits 選擇寫 GP+367／368，並呼叫 `1787c(SP+8)`。此支不是上述 `(1,0)` caller 的選定路徑。複製請求不等於已完成；後續 word read 也不代表整個 word 均由7-byte請求初始化。

## `17b92`：兩個 RET 都重讀 byte

入口 fresh 讀 U8[GP+378] 只作分支判斷：

- 非零：跳 `17bbe`，**再讀一次** U8[GP+378]→A0，`17bc2 RET`；不建立本機 frame。
- 零：建立16-byte frame、保存 RA，清 GP+377；呼叫 `9124(176a0,0,100,0)`。正常返回後恢復 RA，**fresh 再讀** U8[GP+378]→A0，退框並 `17bbc RET`。

兩條正常回覆都是最後讀到的 byte，不是入口 predicate snapshot，也不是 `9124` 或排程 provider 的 scalar reply。本文沒有推定100的物理時間單位或 `9124` 的完整效果。

在 frame／GP／RA 保存與所需 callees 正常返回條件下，RA鏈為：`9250` 恢復 `900e` → `17bf6` 恢復 `900e` → `17b92` 返回 `900e`。接著 main 的 `900e` JAL→`8180`；到首次 `819c` 前沒有設定 A0 的指令，所以：

```text
first call at819c 的 ambient A0 = 最後一次 U8[then-live GP+378]
範圍 = 0..255
```

這只限定首輪被呼叫目標看到的 register，不表示它使用此值；也不需要預先證明實際 JT0 指向候選 dispatcher。後續迭代還經 `17002`、`12c58`，不能沿用這個來源或範圍。異常返回、重入、IRQ／writer、code/context 損壞等未包含在這條正常續行合約中。

## 重播與剩餘邊界

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_init_tail_hardware_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_init_tail_hardware_static.py
```

兩模式精確重播同一 ledger；RuntimeError guards 不因 `-O` 關閉。驗證包含131072個 signed-shift/bit identities、4096個 counter equality cases、256個 reg4 poll predicates，以及17個指定原指令單 bit 變異於預期 guard 失敗。這些是主機算術與 bytes 檢查，不是硬體輪詢、timer、register machine 或 mutable memory 模型。

發布前核對21個 transitive Python dependencies 與 GitHub main blob 身分。完整重播仍需固定 APP、本機候選 carriers／HEX、34個 sidecars、saved reader、raw SDK header 與 LLVM Xwchc sources/vectors；只有 GitHub clone 不足以完整重播。無下載、安裝、服務啟動或候選輸入上傳。

本輪只發布新 checker、ledger、本文，保留原 BIN、舊分析與本機 Git index。仍需展開 `90b0`／`9124`、callback `176f8`／`178f8`／`176a0`、其餘13個初始化 calls 與 provider／ID 保存合約。硬體 poll 出口、實機 MMIO／CSR效果、installed provider、JT0／MEPC retention 與 node/record ownership 仍未閉合。
