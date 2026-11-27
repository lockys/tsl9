# v4.1.60：完整 common body、polling 與 RAM 尾跳

本階段完成 `54c08/54cd2` 的完整原始指令與局部控制流證據，接通先前直接 callbacks 的共用尾跳。新增 **2,440 bytes／886 條指令**，沒有將先前的 outer constructors、publisher、registrar 或 C 重建工作重複計入。

| resident 參考候選 | 完整範圍，不含尾端 | bytes／指令／stores | SHA-256 |
|---|---|---|---|
| V1.31 | `54c08..550cc` | 1220／443／76 | `f6d82412d3e42c00b82df3014ab03bc2156ceafa401066a1667cb499df78e5ca` |
| V1.40 | `54cd2..55196` | 1220／443／76 | `7b7d3b37bbed69f54e95d554b1e428cdf57f6aa1627c9c40de66f1290f890981` |

以下 `+offset` 均為函式入口相對十六進位位置。兩版 instruction boundaries 相同，但 callback literal、RAM 尾跳與其他 operands 的差異分別固定驗證，沒有使用統一位址偏移假設。

全程是離線原始 bytes／operand／CFG／整數檢查，未執行或模擬目標 ISA、copy、provider、callback、polling、MMIO、CSR 或裝置。[機器可讀證據](v4160-list-common-body-static.json) 使用 compact JSON，包含逐條指令、完整局部圖、calls、stores、SCC 與可重播的路徑證據。參考候選不等同原裝置的 installed resident。

## 入口與兩種退出

B=`200033b8/20003408`，N 為 entry A0。32-byte frame 保存 RA、S0～S5。

- fresh `U32[B+168]` 非零：直接走 `+204..+214` 的 frame restoration／RET，未保存 N 到 S0、未解參考 N，也沒有 nested call；本機 A0 保持 entry 值，沒有固定 success boolean。
- 該 word 為零：S0=N，呼叫 `63eda/63fc4(2)`，繼續 pointed-object 與 packet 欄位操作；本機沒有 N null guard。

通過後段 fresh gate `20003240/20003290` 的分流，決定另一組退出：

| 當次 gate | 後續流程 | 最後 transfer |
|---|---|---|
| 非零 | polling 退出後，呼叫 `63b0e/63bf8(flags)`，再呼叫 RAM `2000078a(callback literal)`，完成後續 pointed stores | ordinary RET；A0 保留 RAM callee 的回覆 |
| 零 | 跳過 polling，呼叫已驗證 registrar `(callback literal,0)` | 恢復 frame 後 JALR x0 尾跳 RAM `200026ba/20002706` |

callback literal 是 **`55480/5555e`，兩版差 222**；RAM 尾跳兩版差 76。沒有把它們當成入口差 202 的直接重定位。

## 唯一循環：讀取同一個 pointer snapshot

完整局部圖唯一非平凡 cyclic SCC 為：

```text
+1c2  A5 = U32[A3+100]
+1c4  A5 != 0 → +1c2；否則繼續
```

A3 是 `+15a` 從 `2000353c/2000358c` 載入的 pointer snapshot D1。迴圈每次重讀 **D1+100 的 word**，不會重新載入該全域 pointer slot。本機沒有遞減計數、call、backoff 或可證明的有限上限。

更早 `+2c` 從相同全域 slot 取得的 D0 曾被寫入 D0+100=160、D0+80=90，但不能據此假設 D0=D1，或保證 polling 最後讀到零。兩次 pointer snapshots 之間存在 copy calls、其他存取與未知干擾；即使物件相同，本機也沒有證明 external progress。

checker 驗證所有局部節點與邊，並以 dominance 證明 `+15a` 在 polling 入口前。edge witness 只證明編碼圖上可走的路徑；包含「走一次 backedge 再退出」的 witness，不代表實際輸入能讓這個順序發生，更不代表 polling 必定終止。

## 七個 copy callsites，八組參數合約

全部請求 RAM `20000332`。令 P_saved 為 `+9a` 保存到 S1 的 fresh `U32[N+76]`；P_fresh 則是後來各次重新載入的 N+76，不能自動認為相同。

| offset | A0：目的請求 | A1：來源請求 | A2 |
|---|---|---|---|
| `+0e6` | P_saved+4 | N+54 | 6 |
| `+31c` | P_saved+4 | N+54 | 6 |
| `+348` | P_saved+10 | fresh Q+20，Q=`U32[N+48]` | 6 |
| `+392` | P_saved+10 | N+62 | 6 |
| `+420` | P_saved+8 | fresh Q+20 | 6 |
| `+43c` | P_fresh+2 | N+54 | 6 |
| `+47e`，mode1 fallback | P_fresh+8 | N+62 | 6 |
| **同一 `+47e`，其他 low modes** | **P_saved+8** | **fresh `U32[N+40]`** | **fresh `U16[N+28]`** |

最後一列從 `+484..+496` 直接跳到 `+47a` 的 call pair，保留另一組參數。因此不能把七個 callsites 一律解釋成 6-byte copy。length 可表示 0..65535，本機沒有正長度、來源容量或目的容量 guard。

另一處 N+17=`(length+6)&63` 的 byte store **沒有改寫 A2**，也不能當成 copy 長度上限。若要滿足最大請求，目的 P_saved+8 起的可寫範圍需要另行證明；數值長度不是實際可達值或有效 buffer 的證據。

兩條 Q 分支先看 N+53 的 bit1，再讀 `U8[Q+18]`；**解參考 Q 前沒有 local null guard**。Q+18 非零的來源請求需 Q+20..25 可讀。fallback 的 N+61 只決定 header bit 是否寫入，沒有取消對應的 N+62 copy 請求。

這些都是原指令所形成的請求參數，未證明實際 copy provider、同步完成、回覆意義、不保存指標、重疊語義或物件存活期。先前 parent 在別處檢查過 N+48，也不能代替此函式重新讀取後的有效性前提。

## S4 改變用途；尾跳 A1 是 flags

S4 起初形成 global base 與 B，但 `+19a`／`+1a0` 將它改成兩個 fresh unsigned bytes 的 OR：

```text
flags = U8[N+100] OR U8[N+106]
```

完整 CFG 的 dominance 證據確認這兩個定義都在最終尾跳前。`+4b4` 先把 live S4 移到 A1，`+4b6` 才恢復舊 S4；不能把 A1 說成 B 或 caller 原 S4。

尾跳的本機合約為：A0=0、A1=flags（0..255）、A2=fresh `U8[N+17]`。A2 的 load 在 registrar 返回之後，RA、SP、S0～S5 均在 transfer 前恢復。RAM `200026ba/20002706` 的來源、本體、回覆與返回仍需追查。

沿用 [outer／registrar 證據](v4160-list-outer-objects-static.zh-TW.md)，matching `43b28/43bb4` 在 index0 只將 callback literal 寫入 `200031c8/20003218`，不呼叫該 callback。其本機 GPR 寫入不包含 S0／S4／SP／RA。若 N、frame、table 等互不重疊，且沒有其他干擾，這段可保存 flags 與後續 N+17 存取所需的狀態；仍未證明 lifetime。

## Pointed objects、fresh reads 與數值界線

選定路徑的固定 N accesses 最遠到 byte N+127，需要至少 128-byte 有效 N；B 的選定 word access 到 B+216，需要至少 220 bytes。D1 的固定 word accesses 到 +112，需要至少 116 bytes；另外兩個全域 slots `20003508/20003558`、`20003590/200035e0` 所指物件的存取到 word+44，需要至少 48 bytes。其他 callees、packet 與變動長度請求可能需要更多範圍。

這些全域 word 是 pointer-valued storage，尚未證明 referent 是有效 RAM 物件、MMIO 或特定板卡／RF register。多個 RMW 與 copy 可能因 alias、provider 副作用或中斷而改變後續觀察；不能將分開的 fresh reads 合成快照。

本階段另外驗證以下純整數界線，沒有執行目標算術程式：

- 65536 組 byte pairs：flags OR 在 0..255；packet byte 的 low6 packing identity 保留原 count 的低六位。
- 三種 encoded timing branches 的 768 個 byte cases 都能寫入 halfword；後續 fresh halfword 不預設仍等於剛寫入的值。
- 65536 個 halfword cases 的 `(h+359)//30` 最大 2196，對應乘 60 最大 131760。前面的 byte／halfword 乘積也在 word 範圍內；它們不證明物理時間單位或 polling 進展。

76 個 store sites 中有 7 個 frame stores。其餘 pointed／packet／global 操作未封閉 physical free、list unlink、ownership transfer 或保存期；callee 能否正常返回並保存 live S registers、SP、RA、frame 與後續仍需使用的物件，仍是明列前提。

## Constructor consumers 的新定位

獨立只讀探索找到 B+132 consumer `6a2a8/6a3c0`（每版 222B）及 B+152 consumer `69a22/69b3a`（每版 1214B）。它們確實有從函式槽位重讀後的間接呼叫，但完整 operand／CFG 證據尚未納入本次檢查點；不計入本次 2,440 bytes／886 guards。

較小 consumer 先保存舊 outer-pointer snapshot，之後可能呼叫 publisher／setup，卻仍以該舊 snapshot 決定是否配置；兩個 consumer 在真正間接呼叫前，都需另外證明 fresh function word 有效。這些將作後續完整驗證入口，未宣稱所有 callers、實際排程、installed provider 或物件保存期已封閉。

## 重播

[靜態 checker](check_v4160_list_common_body_static.py) 固定 443-row literal operand template 與 28 個 profile 差異。正常重播僅依賴已發布分析模組、原始輸入與本次 ledger，沒有 temporary inspection 檔案依賴。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_list_common_body_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_list_common_body_static.py
```

驗證內容：886 次指定 operand 變異拒絕、36 條選定 CFG walks、938 條 edge witnesses、唯一 polling SCC、dominance、byte／halfword domains 與 exact ledger replay。延續 [直接 callbacks 證據](v4160-list-direct-callbacks-static.zh-TW.md)，此階段補上完整本體，同時保留未知 provider、有限返回、extent 與 retention 邊界。既有 C 重建覆蓋率沒有改變。
