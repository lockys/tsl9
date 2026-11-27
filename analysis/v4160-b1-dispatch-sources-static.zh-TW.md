# Timer IRQ 名義介面、dispatch gate 與 pending 清零來源

接續 [retry／callback 派送驗證](v4160-b1-retry-services-static.zh-TW.md)，本輪將原始 SDK 的 JT120 宣告接至兩版候選的 RAM dispatcher，並補上第一道 gate 的產生來源及 task5 cleanup 的 pending 清零路徑。**尚未定位實際呼叫 JT120 的指令位置**，因此沒有把名義 API、表項存在或條件性來源當成實際執行證明。

[Python checker](check_v4160_b1_dispatch_sources_static.py) 與 [固定 JSON ledger](v4160-b1-dispatch-sources-static.json) 保存完整 operands、來源 hashes、選定 CFG、語法路徑、名義 ABI 與 literal 搜尋範圍。全程只讀原始 APP／候選 bytes 與 strict sparse HEX；沒有目標執行、模擬、可變 task／object／provider 模型、硬體或封包重播。

## 原始 header 將 JT120 命名為 TMOS_TimerIRQHandler

固定原始 `wchble_rom.h` 的宣告為：

```c
typedef uint8_t bStatus_t;
#define FUNCITON_BASE_ADDRESSS (LIB_FLASH_BASE_ADDRESSS+0x34)
#define BLE_LIB_JT(n) (*(uint32_t*)(FUNCITON_BASE_ADDRESSS+n*4))
#define TMOS_TimerIRQHandler ((bStatus_t (*)(uint32_t *time)) BLE_LIB_JT(120))
```

在 header 預設 library base `0x40000` 下，`0x40000+0x34+120*4=0x40214`。兩版候選該位置的完整 4-byte word 均為 `0x200009ba`。它分別以 FLASH `0x40c2a／0x40c6a` 為來源，first-copy 映射到已完整驗證的 RAM `[0x200009ba,0x200009ea)` dispatcher。

這補上的是 **候選 table 與名義 `bStatus_t(uint32_t *time)` ABI**。附近 header 註解仍寫 `param None`／`return None`；checker 依明確的 macro 型別宣告判讀，沒有把不一致的註解拿來否定實際參數。

若先前證明的條件性 pending literal `0x200013e8` 確實保留至 D+16，matching dispatcher 的成功尾跳會把 caller 的 A0 交給 selector。名義 `uint32_t *time` 與 selector 至少需要 4 bytes 可寫 Out 的條件相容；仍未證明實際 A0 的位址、初始化、保存期、呼叫順序或 query 是否保存輸出指標。

## 第一道 gate 是低位元組，不是登記成功判斷

令 `G=0x20003000`，兩版位置如下：

| 欄位 | V131 | V140 |
|---|---|---|
| context C | `0x2000319c` | `0x200031ec` |
| dispatcher 第一 gate：C+3 byte | `0x2000319f` | `0x200031ef` |
| base B | `0x200033b8` | `0x20003408` |
| pending：B+308 word | `0x200034ec` | `0x2000353c` |
| callback：D+16 word | `0x20003244` | `0x20003294` |
| cleanup 獨立 gate：C+88 word | `0x200031f4` | `0x20003244` |

重用 [first-role gate](v4160-first-role-gate-static.zh-TW.md)、[完整 initializer](v4160-role-initializer-fields-static.zh-TW.md) 與 [完整 registration leaf](v4160-task-registration-static.zh-TW.md)，核對下列連接：

1. `0x55bde／0x55d1e` 重新讀 C+3；零時呼叫 registration，然後以尚未改寫的 A0 回覆進入 initializer。
2. initializer `0x5362e／0x536dc` 在 `+0x14` 捕捉入口 A0 至 S0，再執行 `fill(B,0,296)` 與兩個清零 setter。
3. `+0x3a` 將 **S0 的低 8 bits** 寫到 C+3。matching fill／setters 的完整本體都沒有 S0 定義；這段沒有拒絕 255 的檢查。frame／globals 不別名與無外部干擾仍是條件。
4. dispatcher 只檢查 fresh C+3 是否為零，之後仍各自檢查 D+12 與 D+16。

registration 的完整 leaf 在 fresh count `n < capacity` 時回傳 n；否則回傳 255，且拒絕路徑略過兩個本機 store。故有兩個封閉數值反例：

- `n=0, capacity>0`：登記的正常回覆為 0，寫回的第一 gate 仍為零。
- `n>=capacity`：拒絕回覆為 255，寫回的第一 gate 非零。

所以 **C+3 非零不能單獨證明登記成功**，C+3 為零也不能單獨證明此前沒有登記。這是原指令與返回值合約的條件性推導，沒有聲稱實際 count／capacity 曾取這些值。

prefix 中匹配的 fill／三個 trailing word clear 共涵蓋 `[B,B+308)`；pending 正好位於 B+308，未被這些清零範圍覆蓋。這不代表整個 initializer、後續 callees 或其他 writers 都會保留 pending。

## Task5 cleanup 清的是 pending，D+16 仍是另一個 cell

重用 [完整 task5 object cleanup](v4160-task5-object-static.zh-TW.md) 的兩版 252-byte 本體及全部 local edge 見證；本輪特別串接 `+0x6c..+0xbc` 的 80-byte 尾段：

```text
先前 key-removal 呼叫正常返回
重新形成固定 B
fresh U16[B+180] 非零：直接至 epilogue
否則：
    U32[B+308] = 0               # pending
    U32[B+176] = fresh U32[D+4]
    若 fresh U32[C+88] 非零：
        X = fresh U32[C+32]
        若 X 非零：
            request private release(X)
            U32[C+32] = 0
            U32[C+36] = 0
epilogue；還原本函式 16-byte frame 並 RET
```

這裡的 B+180 是 key-removal **返回後重新取樣**，不能用呼叫前的計數代替。所選尾段沒有直接清零 D+16；但未知 key-removal、private release 或其他 callee 的副作用仍不能排除。pending 清零也不能證明 callback 已經被消費、排空或釋放。

尤其 **V140 的 C+88=`0x20003244`** 恰好等於 **V131 的 D+16**，兩者屬於不同版本的角色。每個版本內的 C+3、C+88、pending、D+16 都是不同 cell，不能跨版本因數字相同就合併其保存合約。

## 搜尋範圍與驗證

checker 對 76800-byte APP 及每版候選檔案的所有 byte 起點，搜尋完整 32-bit literals `0x200009ba`、`0x200009bb` 與 `0x40214`。APP 中均未找到；兩版候選各只在 `0x40214` 找到 dispatcher literal，正向命中另經 strict sparse HEX 核對。這是**檔案內 literal census**，不是完整 callgraph；沒有排除 table indexing、非相鄰暫存器運算、間接來源或缺失 ROM。

本輪選定來源窗口如下，全部來自既有已核對本體：

| 選定窗口 | V131 | V140 | 每版 bytes／指令 |
|---|---|---|---|
| gate 至兩次呼叫後的 cut | `[0x55bde,0x55bfc)` | `[0x55d1e,0x55d3c)` | 30／9 |
| initializer 至 C+3 store 後的 cut | `[0x5362e,0x5366c)` | `[0x536dc,0x5371a)` | 62／20 |
| cleanup 尾段至 RET | `[0x577ba,0x5780a)` | `[0x578fa,0x5794a)` | 80／24 |

合計 **344 bytes、106 條選定指令，另 8 bytes 表項**。它們不是本輪新展開的完整函式，checker 明列 `new_complete_body_bytes=0`。完整 gate 84B、initializer 426B、cleanup 252B、registration 48B、fill 46B 與兩個 10B setters 都重新核對其原始身份、operands 與來源。

```powershell
python analysis/check_v4160_b1_dispatch_sources_static.py
python -O analysis/check_v4160_b1_dispatch_sources_static.py
```

負向核對包含 **106 個逐指令變異、8 個 typed-load 變異、8 個表項 byte 變異與 4 個 SDK ABI 變異**。另以純 host scalar 恆等式核對全部 65536 個 U8 count／capacity pair，沒有執行 registration 或建立 task 狀態模型。checker 也重跑原有驗證鏈、固定輸入身份與 ledger。

接續仍需定位 JT120／dispatcher 實際 caller、A0 初始化與回覆使用，確認其他 C+3／pending／D+16 writers、實際 provider、呼叫順序、別名及完整消費釋放和指標保存期。本輪 **APP C 重建覆蓋不變**，既有約 95.75% 靜態重建快照仍不等於完整可用韌體或實機驗證。
