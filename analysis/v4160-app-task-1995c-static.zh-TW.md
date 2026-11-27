# APP 0x1995C：事件優先序、訊息清理與登錄來源

接續 [message receive／unlink／條件性釋放](v4160-message-receive-static.zh-TW.md)，本輪核對原始 V4.1.60 APP 的完整 `0x1995C..0x199E2` 本體：**134B／49 指令**，SHA-256 `f091e186b336f48c8ce3719606bd99403fe3965445529d252be0da22a5cfef5c`。APP 仍為 ID-2966、76,800B；兩份 resident V1.31／V1.40 均為參考候選，不是原機 installed binding 證據。

## 完整事件分派

函式建立 16B frame，保存 RA／S0／S1；以 S0 保存完整入口 event word E。三個 stores 都只寫自身 saved-frame words。本機 CFG 無環且所有指令均有從入口到唯一 RET 的語法路徑，但這不保證 nested callees 或硬體等待會返回。

| 優先序 | 入口 E 條件 | 呼叫與參數 | 正常返回 |
| --- | --- | --- | --- |
| 1 | bit15=1 | fresh receive(entry task)；nonnull reply M 再 fresh deallocate(M) | full E XOR `0x8000` |
| 2 | bit15=0、bit0=1 | 無服務呼叫 | full E XOR `1` |
| 3 | 前項皆不符、bit13=1 | fresh `0x401EC`；direct `0x197B8`；fresh `0x40058`(fresh U8[GP+388],8192,192000) | full E XOR `0x2000` |
| 4 | 前項皆不符、bit14=1 | fresh `0x40058`(fresh U8[GP+388],16384,1600) | full E XOR `0x4000` |
| 其餘 | 四個 handled bits 都是 0 | 無服務呼叫 | **0** |

每次正常呼叫只處理最高優先的一個 handled bit。判斷只依 E 的 low16；handled path 的 XOR 保留完整 high16，而未命中任何 handled bit 的分支返回 0，不會原樣返回其他未處理位元。

callee 的 scalar 成功／錯誤碼都未被測試。消息為 null、cleanup 沒有效果、timer 返回非零狀態，均不會在這個函式產生另一種 status 返回。上述 E 的意義依賴 S0／frame／SP／RA 及 nested normal-return 保存；fresh slots 還須 S1 保持 `0x40000` 才能解釋成所列固定 slot。

## 訊息路徑接回前輪合約

`0x19974` 讀 fresh slot `0x4006C`，`0x19976` 呼叫 receive。這時 A0 仍為入口 task；nonnull reply 未經轉換，直接傳給 `0x1997A` fresh 讀取的 `0x40068` 所指 deallocator。中間沒有 body 解參考、copy 或 direct pointer store，不能把這個 caller 說成四-byte payload parser。

若 slots 符合候選，前輪 receive／unlink 會摘下第一筆 matching M，清 next、把 marker 還原成 255，再返回 M；public deallocator 的 marker guard 因而可成立。前輪針對 M=H+16 的 same-header release，仍需要保留 nominal heap、H／R headers、account、nonalias 與正常返回等前提，不能從本 caller 的返回值推定所有實際訊息已成功 free。

## bit13 的 direct callee 是 mode 3 wrapper

原始 `0x199A8` bytes 為 `ef f0 1f e1`：linked JAL 的實際目標是 **`0x197B8`**，link 為 `0x199AC`。`0x197F0` 是另一個 config+44 callback，並非此 callsite 的目標。checker 有專門的錯誤 callee 回歸向量，避免混用兩條呼叫鏈。

重用 [mode 3 完整 frame 合約](v4160-mode3-frame-static.zh-TW.md)：`0x197B8..0x197BE` 只有兩指令，先強制 A0=3，再無新 link 尾跳 `0x1929A`。其完整 1,066B／329i 本體在要求的正常返回、reader、frame／MMIO nonalias 與無干擾前提下，保存所需 S／GP／SP／RA，回到 `0x199AC`。

相對於本 task 入口 SP=U，task frame 在 `[U-16,U)`；mode child own frame 在 `[U-96,U-16)`，其 saved words／scratch 與 task 的 saved words 分離。這是區間與原指令保存證明，不是執行校正演算法；mode 的 signed 算術、polling 與 reader 迴圈仍無物理完成保證。

## BLE_RegInit 與再次排程的界線

SDK raw header 的 `BLE_RegInit` 為 JT110，slot 算式 `0x40034+4*110=0x401EC`，prototype 為 `void(void)`。原指令沒有在此呼叫前重建參數：它可觀察到的 ambient A0 是先前算出的 **E XOR 1**，A1 仍為 E，並非入口 task。prototype 不是未知 installed provider 忽略所有其他暫存器的證明。

兩候選 slot words 分別是 `0x641B0`／`0x6429A`，對應既有完整 RF outer-tail 232B／79i 本體，不是前面的 generator。本輪重新核對其固定 body，但不把啟動階段的 state=1、magic、descriptor、slot 或 polling 完成條件直接套用到這次事件呼叫。

在 mode 正常返回後，task 重新設定 timer event／delay，從 then-live GP+388 取 fresh unsigned task byte。bit13 的 A2=192000，bit14 的 A2=1600；兩處均為 U8 task，不能套用 signed LB。重新排程結果被 mask XOR 返回覆蓋，不能據此宣稱 timer 已成功建立或日後一定再進入本 task。

## 登錄 task3 與 resident builder task5 是不同來源

重用 [首次登錄鏈](v4160-first-registration-chain-static.zh-TW.md)與 constructor 來源：wrapper `0x19B26/0x19B2A` 算出 `0x1995C`，交給 fresh `0x40080`；nominal old count=3、capacity>=14、table=`0x200047F4` 時，candidate registration 寫 entry3=`0x20004800`，value=`0x1995C`，count 改為 4，返回 3。wrapper `0x19B30/0x19B34` 將 low8(reply) 存到 nominal GP+388=`0x20004184`。拒絕登錄的 255 也會被存入；task3 結論需要 admitted-path 前提。

threshold builder 讀的則是 resident context C+3：`0x2000319F`／`0x200031EF`，不是 `0x20004184`。它是 role gate／task 欄位，不能只因為用途是 task 就把它當成 APP 保存 task ID 的同一個儲存格。

進一步重用 [first-role gate](v4160-first-role-gate-static.zh-TW.md) 的原始 writers：在已選定第二次登錄使 count=5、fresh C+3=0 的分支，下一次登錄 handler `0x5352C`／`0x535DA`，返回 5、count 改為 6；initializer `0x5362E`／`0x536DC` 的 `+58` 將保存的 5 寫到 C+3。這只是 initializer 62B prefix 的有界證明，不保證其後續與整個 gate 已返回。

**若這兩組選定值都保持到使用當下，APP 保存的是 task3，threshold builder 使用的是 task5，兩者不相等。** 因此本輪的 APP receive／free 能力，不能直接當作 threshold 四-byte 訊息已派送到此 task 的證明。fresh gate 非零時會跳過該次登錄／初始化；值域、其他 writers、執行順序與實際 dispatch 仍需另證。

## 重播與限制

[checker](check_v4160_app_task_1995c_static.py) · [精確 ledger](v4160-app-task-1995c-static.json)

```powershell
python -B analysis/check_v4160_app_task_1995c_static.py
python -O -B analysis/check_v4160_app_task_1995c_static.py
```

49 條新指令各有一個變異拒絕、兩個 GP+388 LBU→LB 變異，以及一個誤連 `0x197F0` 的 JAL 回歸向量。純 bitstring 算式核對全部 65,536 個 low16 event 與五組 high16 向量共 327,680 案例。low16 優先序分布為：bit15 32,768、bit0 16,384、bit13 8,192、bit14 4,096、none 4,096；不把這個有限資料域當作真實事件可達性。

普通／`-O` 需與同一 ledger 逐 byte 相符，固定 APP、兩份 candidate、SDK raw header 與 Xwchc 來源向量。新分析只增加一個完整 APP 本體的靜態合約，沒有提高既有 C 重建覆蓋率。未執行 target ISA、原韌體、provider、callback、MMIO、可變 event／queue／heap 模型或硬體；GitHub 僅新增本輪三份分析檔。實際 provider、table invocation、task-byte 保存／writers、其他 consumers 與物理進展仍待釐清。
