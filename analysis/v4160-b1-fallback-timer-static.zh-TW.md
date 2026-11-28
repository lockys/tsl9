# v4.1.60：Timer 與第二個 task 的條件式 fallback 保存

接續 [constructor 至 wrapper 尾跳前](v4160-b1-fallback-wrapper-static.zh-TW.md)。本輪將已驗證的尾跳參數 `(3,8192,192000)` 接到匹配的 `0x40058` 候選服務，封閉兩個分別成立的 timer 路徑，再接至 setup 的第二個 task 登記。結論止於 `0x8eb6` 的 fresh 服務目標開始執行前。

檢查器：[check_v4160_b1_fallback_timer_static.py](check_v4160_b1_fallback_timer_static.py)；證據：[JSON ledger](v4160-b1-fallback-timer-static.json)。全程為原始 bytes／CFG、封閉整數與區間／frame 證書，沒有執行韌體、建立可變 target 狀態模型、操作硬體、重播或連線 target。沒有增加 C 重建 bytes 或提高覆蓋百分比。

## Timer 入口與算術

| 項目 | V1.31 | V1.40 |
|---|---|---|
| 候選 `0x40058` 目標 | `0x43728` | `0x437b4` |
| 完整本體 | 332 bytes／113 指令 | 332 bytes／113 指令 |
| Timer head word | `0x200031e8` | `0x20003238` |
| Fallback word | `0x20003220` | `0x20003270` |

Task 3 在 fresh count=`4` 時通過 admission。服務捕捉的 fresh reader 指標仍須是匹配的 `0x191c6`，copied 設定在各次取樣時須保持 period=`0xffffffff`、h=`16000`。

兩次算術的 numerator 為 `h*192000+800`，divisor=`1600`。重用已驗證的 50-node 原指令路徑及 startup 整數域證書，兩次 quotient 都為 `1,920,000`。第一次通過 threshold `0xfe363c7f`；匹配 reader 的正常回覆 R 仍是未知 32-bit 值，不假設其為 coherent／單調／實體時間計數。

在 period 與 h 保存的條件下，deadline 可寫為：

```text
deadline = (R + 1920000) mod (2^32 - 1)
```

新證書把完整 U32 R 域分成三段：不減 period、總和恰等於 period、以及 32-bit carry 後減 period。每段以 affine 關係和端點界線證明原本的一次減法等同這個 modulo；沒有把此特化推廣到任意 period 或輸入。

## 路徑一：空串列、名義 small block 配置成功

這條路徑另要求 fresh head=`0`，且保持到 lookup 與插入取樣；small head 為有效、owned 的 free block `A=0x200043ac`，next=`B=0x200045ac`、size=`504`、tag=`0`，sentinel／accounting／其他所需 headers 均匹配並保存。

Lookup 是無 stores／巢狀呼叫的 30-byte leaf；空 head 使其返回 `0`。服務隨後請求 allocator `(16,0xff03)`：

| 結果 | 值 |
|---|---|
| 配置 header | `0x200043ac`，payload size 16、tag `0xff03` |
| 回傳節點 | `0x200043b4` |
| Remainder header | `0x200043c4`，size 480、tag 0、next B |
| Accounting 變化 | `−24`，依原 U16 更新規則 |
| Timer 正常回覆 | `1` |

完整 16-byte 節點欄位為 byte0=`3`、byte1=`1`、U16+2=`8192`、word4=`0`、word8=`deadline`、word12=`0`。

原指令會先發布 head，再初始化節點欄位。因此必須保留無不利 IRQ／DMA／reentry／其他 writer 觀察或修改中間狀態的前提；這不是已證明的原子發布、事件送達或跨事件保存期。

Earlier post-config 確有將 head 寫為零的原指令來源，bootstrap 也有 small header 的來源證據；本輪沒有宣稱已排除這些來源到 timer fresh 取樣間的所有 writers。這些新鮮值與 ownership 仍是額外條件。

## 路徑二：獨立的 small sentinel／零 fallback 失敗返回

這條替代路徑要求 fresh small head **等於 sentinel E**，與前述 free A 成功條件分開處理。它是獨立 fresh 值條件下的 CFG 證書，不表示已從本次名義啟動路徑證明可達。

Core 對 16-byte 請求選取 small list，於 sentinel 讀到保存的 fallback=`0`，略過其間接 callback 並返回 `0`。Timer 在 allocator 返回零至再次載入同一 fallback word 之間沒有 store；若 frame／control／外部效果也保持該槽為零，便再略過 timer 自己的 failure hook，正常返回 `0`。

兩版的 core 與 timer CFG 路徑均已核對。這不證明任意搜尋必定終止，也沒有關閉非零 fallback、既有節點更新、非空串列 append 或其他配置失敗情況。

## 返回 setup 與第二個 task

兩種路徑正常返回時，timer 的 48-byte frame 還原 RA／S0..S7／SP；allocator 的子 frame 為 16 bytes。若保存的原 caller RA 正確，便接回 setup `0x8eb0`。下一個呼叫不檢查 timer 的 `0`／`1` 回覆，而是呼叫 `0x907a`：

1. 匹配 fill 清除 `[0x2000be08,0x2000bebc)` 的 180 bytes。
2. 匹配 task 登記接收 callback `0x901a`。fresh count=`4`、capacity=N0、table=`0x200047f4` 保持時，全部 67 個 N0 值（14..212、間隔 3）均接受。
3. 在 `T+16=0x20004804` 保存 callback，count 改為 `5`，返回舊 count `4`。
4. APP 把 byte `4` 存到 nominal `GP+166=0x200040a6`，返回 `0x8eb2`。

在所需 GP／S0／frames 保存時，`0x8eb6` 的下一個間接呼叫參數為 A0=`4`、A1=`0`、A2=`5`。目標來自 fresh `[then-live S0+416]`；只有 S0=`0x40000` 才能稱它為 `0x401a0` 服務。本證書止於該目標執行前。

## 區間驗證與限制

每版的成功路徑及後續 task 共檢查十個寫入範圍包絡：控制 word、timer head、兩個 small headers、16-byte node、accounting、180-byte fill、第二個 callback word、count byte、第二個 task byte。它們在數值上均避開 fallback 與第一個 task byte `0x20004184`。失敗替代路徑的 timer/core 自身 stores 僅為 frame／control。

兩版各有八個 resident strict sparse HEX 區間核對，包含完整 timer／lookup／core／算術／lookup table／fill／task 登記與 `0x40058` word。沒有以補零填充缺失來源。

重用的 300 筆原指令變異檢查，加上本輪 50 筆 timer 來源／分支／call／node／fallback 變異檢查，全數必須拒絕；另檢查 65,536 個 wide-product／carry 關係、startup h 域與完整 U32 deadline 分段。一般 Python 與 `-O` 都必須通過 exact-byte ledger 比對：

```powershell
python analysis/check_v4160_b1_fallback_timer_static.py
python -O analysis/check_v4160_b1_fallback_timer_static.py
```

仍保留所有前階段前提，以及匹配 installed code／provider／first-copy、所需 fresh fields、有效且不回繞／不別名的 owned frames／heap／globals、保存字、正常 reader／存取／callee 完成、無不利物理 MMIO／FENCE／IRQ／DMA／reentry／外部 writer 效果。數值區間分離不證明實體副作用分離，輪詢也未證明必定退出。實際 head／header 保存、其他串列／fallback 路徑、`0x401a0` 與後續 APP／RF、完整消費與釋放期仍待釐清。
