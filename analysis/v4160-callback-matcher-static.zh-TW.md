# v4.1.60：callback matcher 的寬度與來源合約

本輪完整展開兩版本 matcher 及其短輸入展開 helper，新增 **328 bytes／140 instructions** 的原始指令證據；另重用既有 comparator／copy 共 260 bytes／82 instructions，不重算為新覆蓋。既有 C 重建覆蓋率不變。

| 本體 | V131 | V140 | 每版 bytes／instructions |
| --- | --- | --- | --- |
| matcher | `0x44624..0x4468a` | `0x446b8..0x4471e` | 102／43 |
| expand helper | `0x445e6..0x44624` | `0x4467a..0x446b8` | 62／27 |

[檢查器](check_v4160_callback_matcher_static.py) 與 [固定帳本](v4160-callback-matcher-static.json) 保留兩版完整 operands、SHA-256、CFG、不可變路徑憑證、原始 HEX backing、來源 bytes 及上游串接。全程只讀取檔案、解碼及檢查主機上的圖／整數／區間憑證，沒有執行或模擬目標程式、provider、比較、copy、RAM、MMIO、FENCE 或硬體。

## Matcher 只接受四組寬度

入口為 `(P=A0, L=A1, Q=A2, R=A3)`。L、R 是完整 word 比較，沒有 low8 截斷。函式建立 32-byte frame，保存原 P、Q 至 S1、S0；只有下列四組到達 `0x20000442` 比較請求：

| L／R | 請求順序與參數 |
| --- | --- |
| 2／2 | `compare(P,Q,2)` |
| 16／16 | `compare(P,Q,16)` |
| 16／2 | `expand(Q,SP)`；`compare(P,SP,16)` |
| 2／16 | `expand(P,SP)`；`compare(Q,SP,16)` |

其他寬度組合直接返回 0，沒有 helper／compare 呼叫。兩種混合寬度都**忽略 expand 的返回值**；只要呼叫正常返回，仍然進入 compare。最後返回 compare 的完整 A0，沒有額外轉換成 boolean。

兩個 expand 目標由壓縮 JAL 直接指定；compare 由 AUIPC／JALR 固定到 `0x20000442`，不是從輸入或槽位讀出的 function pointer。matcher 本體沒有 payload loads／stores，只有 frame 存取；它也沒有 null pointer guard。

## Expand：複製 template 後，交錯讀寫兩個 bytes

helper 入口 `(X=A0, Y=A1)`：X=null 於 frame 前返回 0；X 非 null、Y=null 則建立並還原 frame 後返回 0。兩條 null 路徑都沒有 child call 或 payload 存取。

兩個 pointer 非 null 時：

1. 請求 `0x20000332(Y, template, 16)`，不檢查返回值。
2. fresh 讀 X[0]，寫至 Y[12]。
3. fresh 讀 X[1]，寫至 Y[13]。
4. 固定返回 1。

四個 byte 存取採 Xwchc 原始編碼 `9c20`、`5ca4`、`9c30`、`5cb4`。一般 RISC-V r2 將其誤顯示為浮點指令；本檢查器使用既有目標 profile 解碼與原始編碼 guards，核對為 byte offsets 0、12、1、13。

兩個來源讀取在 copy **之後**，且 X[1] 讀取在 Y[12] store 之後；若來源／目的地 alias，不能視為一開始捕捉兩個 source bytes，也不能無條件套用 immutable template 結果。matcher 的 scratch 為 SP+0..15，保存區為 SP+20..31；helper 的 16-byte frame 位於 matcher SP 下方。區間不重疊仍需有效、無 wrap、無不利別名或外部干擾的前提。

一般混合寬度呼叫若短輸入 X=null，helper 不初始化 scratch 並返回 0；matcher 忽略此值，仍對 scratch 發出 compare。不能把 scratch 推定為零或把 helper 返回 0 當作 matcher 必然拒絕。

## 重用 comparator／copy，保留硬體與綁定界線

既有 [comparator 合約](v4160-comparator-tail-static.zh-TW.md) 以候選 startup first-copy 將 FLASH `0x406b2/0x406f2` 映射至 RAM `0x20000442`；copy 的 FLASH `0x405a2/0x405e2` 對應 `0x20000332`。本輪重新核對完整 bytes、原始 HEX 及 first-copy 範圍，沒有把映射當作已安裝 RAM 的觀察。

matching comparator 先保存、清零控制 word `0x4002420c` 並 FENCE.I，之後才檢查 pointers／length。任一 pointer=null 或 length=0 正常返回 **1**；兩個非 null、正長度時，第一對 fresh byte 不同返回 0，全部相同返回 1。這不是 ISO memcmp 的負／零／正返回。正常出口寫回原控制 word；硬體效果、異常恢復、原子快照與實際 installed binding 未證明。

matching copy 同樣具有控制 word／FENCE 指令；有效非 null 輸入下逐 byte 向前讀寫，無整體 source snapshot 或 memmove 保證。兩個候選 leaf 都沒有保存原輸入 pointer 的直接 store；這是局部指令性質，不代表外部 provider、MMIO、來源 bytes 中的指標或物件保存期已被排除。所有硬體相關指令均只作 bytes／CFG 分析。

## 串回 validator：真正需要的 ROM bytes 已完整捕捉

[前輪 validator](v4160-callback-validator-static.zh-TW.md) 每次 matcher 呼叫皆為 L=2，P 是固定 ROM reference，R 為 fresh config[0]，Q 為 fresh U32[config+4]。第一個 matcher 返回 0 才換第二個 reference，並重新讀取 config0／config4；兩次來源不一定一致。

| 來源 | V131 | V140 | 真正需要的內容 |
| --- | --- | --- | --- |
| 第一個 reference | `0x6ea90` | `0x6ec80` | `00 28`（little-endian U16 `0x2800`） |
| 第二個 reference | `0x6ea9c` | `0x6ec8c` | `01 28`（little-endian U16 `0x2801`） |
| template | `0x6e370` | `0x6e560` | 完整 16 bytes，兩版本相同 |

```text
template: fb 34 9b 5f 80 00 00 80 00 10 00 00 00 00 00 00
first:    fb 34 9b 5f 80 00 00 80 00 10 00 00 00 28 00 00
second:   fb 34 9b 5f 80 00 00 80 00 10 00 00 01 28 00 00
```

後兩行是完成普通 copy、來源保持、無不利別名條件下的資料憑證，沒有執行 helper 或觀察 RAM。

- config0=2：直接比較 reference 與 Q 的最多兩對 fresh bytes。
- config0=16：從 reference **只讀前兩 bytes**，用完整 template 展開後，比較 Q 與 scratch 的最多 16 對 fresh bytes。
- 其他 config0：本次 matcher 返回 0，沒有 reference payload read。若第一次讀到不支援值，第二次仍可能讀到不同值；不能將第一次值套用兩次。

前輪保留的 12-byte 診斷窗口確有 sparse HEX 缺口，但這裡實際需要的 reference 前兩 bytes 及獨立 16-byte template 全部已捕捉。這消除了**此 matcher 讀取範圍**的 ROM 來源缺口，未證明更大 table 範圍、布局或其他用途。

若 Q=null，在 matching comparator 及正常呼叫前提下，config0=2 的 direct compare 返回 1；config0=16 先展開非 null ROM reference，再因 compare 的 Q=null 返回 1。故非零 matcher 回覆本身不能證明 config4 指向有效非 null 資料。這只說明原指令的條件性合約，未觀察實際欄位值或建立測試輸入。

matcher 通過後，validator 尚有 parameter 7..16、counter、配置及第二條鏈表發布等 gate；其部分成功與保存界線沿用前輪合約。它不是完整 setup 或 [主 callback 綁定](v4160-callback-list-writers-static.zh-TW.md) 成功的保證。

## 重播與剩餘工作

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_callback_matcher_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_callback_matcher_static.py
```

檢查器驗證 140 個 instruction mutations、8 個 Xwchc offset mutations、65,536 組 byte-width pairs 與完整 U16 欄位拆合憑證，並逐 byte 重播 JSON 帳本。一般及 `-O` 模式都使用不依賴 assert 的 guards。

仍需追查 callback 物件 +8 的其他 writers、wrapper 實際 caller、欄位跨呼叫／IRQ／DMA／重入的保存、provider 真正綁定，以及兩條鏈表、config 與物件的配置及指標保存期。本輪未驗證實機功能或產生可用韌體。
