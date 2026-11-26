# v4.1.60：完整 candidate config gates 與預設發布路徑

本輪補齊 `[0x40074]` 候選入口的完整函式。非空設定的四個必填欄位與 state gate 均已核對；空設定會跳過 copy、建立部分預設欄位，再發布 `0x20000986`。因此 service word 的來源不僅是先前 APP reader `0x191c6` 的條件性串接。

這是原 bytes、解碼 operand、控制流與主機整數代數驗證。未執行或模擬韌體、provider、callback、RAM/frame、MMIO 或裝置；也未驗證實際 installed candidate。C 重建覆蓋率未增加。

## 原始證據與完整邊界

承接 [service pointer 串接](v4160-service-provider-link-static.zh-TW.md) 與 [第二個 selector](v4160-second-selector-static.zh-TW.md)。驗證程式為 [check_v4160_config_gates_static.py](check_v4160_config_gates_static.py)，可重播證據為 [v4160-config-gates-static.json](v4160-config-gates-static.json)。來源 APP、兩個 candidate、SDK header、稀疏 HEX 與官方 Xwchc 向量沿用既有固定雜湊及驗證鏈。

| 候選 | FLASH 範圍（右端不含） | bytes／指令 | state base | copied config | service word |
|---|---|---:|---|---|---|
| V1.31 | `0x43f46..0x44022` | 220／76 | `0x200031ec` | `0x20003234` | `0x200031e0` |
| V1.40 | `0x43fd2..0x440b6` | 228／78 | `0x2000323c` | `0x20003284` | `0x20003230` |

完整函式 SHA-256：

```text
V1.31 9aa8ba0cd9adc48d5f3fbfad68dc2ca6f2875fbd1e9c04c3283439cdbba8dc6a
V1.40 2e8dedeaeb6223cc57ec01b518faf261846305d7f925429bd01b80398283a893
```

兩版均包含 RET 之後的 default 區塊，且該區塊有入口分支可達，最後跳回 publication。所有本機節點在條件性 CFG 中可達，沒有本機出口缺口或迴圈；唯一 terminal 是恢復 RA/S0/SP 後的 RET。四個 call 都只建立「正常返回時」的續行邊，不代表 callee 必定返回或整個函式必定終止。V1.40 另有入口 `SW zero,[0x20003294]`，且 prologue 排列有差異，不能只用單一位移套用兩版。

## Optional hook 在設定檢查之前

函式建立 32-byte frame，保存 RA、S0。先 snapshot `U32[state base+48]`（`0x2000321c`／`0x2000326c`），令 A1=入口 A0。hook 非零時，把 A0 存到 `SP+12`，呼叫 hook，再由該 saved word reload A1。hook 的 A0 返回值未拿來決定 gates。

下文 C 表示 then-live A1。若 hook 改動 saved word，C 可能不同於原 APP 傳入指標；本機 save/reload 指令不證明 frame 保存期。V1.40 的額外清零也發生在 hook 與 gates 之前。

## 非空設定的 gates

依序 fresh load，要求以下值非零：

1. `U32[C+0]`
2. `U32[C+4]`
3. `U16[C+8]`
4. `U16[C+10]`

上述任一失敗會在本機直接返回 A0=1。如果 `U8[C+12]` 非零，另外讀 `b=U8[state base+21]`，要求 `(b&3)+(b>>2)<=2`。完整 byte domain 的通過集合恰為 `{0,1,2,4,5,8}`；C+12 為零就跳過這個 gate。這個檢查讀的是既有 state byte，並非 C+12 本身的數值上限。

這些指令沒有建立輸入 buffer 長度、指標範圍、snapshot 一致性或實際可達欄位關係。失敗路徑沒有後續本機 copy/publication/registration，但前面的 hook 與 V1.40 初始清零可能已發生。

## 16-byte copy 要求與 fresh publication

gates 通過後，call `0x20000332`：A0=copied config、A1=C、A2=16。只能確認這個呼叫要求；callee 的 copy 語意、暫存器保存、指標保存與實際綁定仍待原 body 驗證。

在正常返回且必要狀態保存的前提下，函式 fresh load `U32[copied config]`，再存到 service word。沒有直接使用 callee 返回 A0，也不能僅憑 call 參數就認定目的區已含原輸入副本。依候選 first-copy 映射，`0x20000332` 對應 FLASH `0x405a2`／`0x405e2`；此處只記錄映射，未把該 body 納入本輪新增完整函式範圍。

## 空設定：部分 defaults 加上 MMIO 寫入指令

C=0 會跳過非空 gates 及 copy request，執行：

| 本機寫入位置 | 值與寬度 |
|---|---|
| `0x200031b8`／`0x20003208` | word 0 |
| copied config+0 | word `0x20000986` |
| copied config+4 | word `0xffffffff` |
| copied config+8 | word `0x00327a12` |
| copied config+12 | byte 0 |
| `0x40024268` | word `0xffffffff` |

little-endian 解讀下，word+8 形成 `U16[+8]=31250`、`U16[+10]=50`。僅 bytes 0..12 在此初始化，13..15 沒有本機清零。MMIO 只記錄 encoded address、值及寬度，未實際寫入，也未推定硬體含義。

default 區塊隨後直接跳到 fresh publication load，因此在無外部改動等前提下，service word 可由內建 default `0x20000986` 提供。這仍不是 installed provider 或函式語意的證明。

## 發布後與返回合約

fresh `U8[state base+23]` 非零時跳過算術 call；否則讀 fresh `U16[copied config+8]`，形成 `(A0,A1,A2,A3)=(1400*h,0,1000000,0)`，呼叫 `0x6df1a`／`0x6e10a`，把返回 A0 的低 8 bits 寫到 state base+23。全部 halfword 值的乘積都不超過 91,749,000，不發生 U32 乘法溢位；尚未賦予該 helper 除法或時間單位語意。

最後，以 A0=`0x43d62`／`0x43dee` 呼叫 `0x43b0a`／`0x43b96`；正常返回後明設 A0=0，再 restore/RET。這個本機返回值不證明 provider 或硬體操作成功。

所有跨 call 推論都依賴正常返回、有效 frame 與必要的 SP/S0/保存欄位保持；別名寫入、interrupt、reentry、其他 writers 與資料保存期仍未知。多次 fresh loads 並非同一時刻的 snapshot。

## 重播與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_config_gates_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_config_gates_static.py
```

檢查涵蓋完整原始 operands/CFG、四個 calls、frame、nullable/default 匯流、256 種 byte gate、65,536 種乘積範圍、default 欄位代數及 62 個 operand 變異拒絕；JSON 必須逐 bytes 重播一致，並沿用既有來源驗證鏈。

後續仍需展開 `0x6df1a`／`0x6e10a`、`0x20000332` 的原 body 與保存合約、APP 完整 config 建構、實際 candidate 綁定，以及 registration/callback 的更廣副作用與物件保存期。
