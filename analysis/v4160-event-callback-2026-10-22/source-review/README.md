# 原始事件 callback 8614：來源契約

[English](readme.en.md)

官方 ID2966 V4.1.60 韌體的 `0x8614..0x888C` 共632 bytes，SHA-256 為 `3e21432057f673abea404541e0745937d894448b492478b5fed5775e91b398bf`。檔案基底是 `0x8000`，實際讀取範圍為 file offset `0x614..0x88C`。

`instructions.json` 保留217條完整指令欄位；新的小型 raw decoder 只解單一指令，與獨立 LLVM 文字欄位逐一比對。共有26個直接控制邊、64個記憶體指令、15個間接 JALR 呼叫。26個 raw control 先驗證「改變後仍是可解碼、同寬且語意欄位不同的指令」，再確認完整來源契約拒絕它；不是靠檔案 hash 不同來拒絕。沒有 CPU 狀態、ISA 執行器、模擬或裝置操作。

`contracts.json` 記錄人工核對的流程、寬度、frame、15個呼叫參數和限制。輸入 A0 是完整32-bit context，A1 是完整32-bit事件字；前者不會先截成 byte。優先序如下：

1. LOW16(A1) 的符號位，mask `0x8000`。
2. mask `0x8`，即 bit3；此路徑在 lane lookup 之前。
3. 新讀取 GP+0x94／GP+0x98 的 byte，與完整 context 比對，選 lane0／lane1；不匹配即回傳0。
4. lane 匹配後依序處理 masks `0x1`、`0x2`、`0x4`；其他情況回傳0。

各完成路徑回傳的是 **live S0 XOR 該 mask**，不是統一成功碼，也不能直接改寫為清空所有 flags。未知 callee 若改變 S0，XOR 的來源也會改變。

mask0x8000 先呼叫 live slot 以取得指標。非零時無條件讀取第一個 byte 到 A4；type0xB0 才呼叫另一 slot，參數包含指標+8與指標+4的 byte。之後使用 live S1 呼叫 release 候選 slot。這些名稱只是用途推論，沒有證實 SDK 身分。

mask0x1 路徑使用 stride1062 的 buffer 與 stride8 的 descriptor。第一個 gate 必須返回 **恰等於1**，再把 total-cursor 截成16-bit、符號延伸；非正值清除 pending16-bit長度。容量 slot 的結果則先減3再截16-bit。後續 signed compare、descriptor SH、buffer SB10 與下一個 opaque call 的順序，全部保留來源證據；把它簡寫成 min(length,capacity) 需要額外的 callee 保存條件。

mask0x2 在 count byte為0時只清除 pending16-bit長度。非零時取得指標並先 SW 到 descriptor+4，**然後才做 null check**。複製來源由新讀 cursor與 live S3/S9 組合，長度也重新 LHU；複製後才重新讀 GP/gate。這裡只測 gate 返回值的 **最低位**。成功路徑從 fresh GP+0x2A 寫 descriptor，再呼叫另一 slot，零回傳才以16-bit寬度更新 cursor。失敗／空指標路徑使用8-bit count decrement，並呼叫另一個排程候選 slot。

mask0x4 的已指定呼叫參數為 `(S5,12,24,0,200,S4)`，target在A6。mask0x8 使用 `(entry A0,0,0x19DE0)`。其他參數不能擅自補零；A4等 scratch 寫入也可能留在 callee 看得到的值中。`assigned_args` 與 C 模型的 argument mask 是明示投影，並未宣稱完整 raw A0..A7／非同步 prefix 相等。

frame先減48，依原順序儲存 S0、RA、S1..S9。共同 epilogue 從 **當下 live SP** 重新讀回 RA、S0..S9，最後 liveSP+=48、JR fresh RA。未知 opaque call 可以改變 GP、S registers、SP或frame記憶體；因此「回到 entry SP」「保存原 caller RA」「callee 一定返回」都不能無條件成立。正常 C ABI 保存規則只是一個有標示的條件模型。

原 carrier 有36個 owned RELA（26 control、5組HI/LO），全部addend0；24個私有角色包含19個 control target與5個 PCREL anchor。外部只有三個來自 init_8e88 的 address HI20，offset64／250／272，皆指向真 `__tsl9v4160_address_8614` NOTYPE0。沒有記錄到直接 JAL incoming；這不排除間接／computed references。註冊呼叫與 buffer-init 的更完整證據由獨立 entry-plan 提供，這份契約不把位址註冊宣稱為實機執行。

預設只讀官方 BIN、保留的欄位與來源 metadata。額外指定 `--original-object` 才重讀原 carrier 的真實節區／符號／RELA，旗標數量會明確區分。這個選項驗證的是仍含原 callback 的 carrier，不能用來冒充新 native replacement 的驗證。

```sh
python3 -B check-source.py --project-root /project --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python3 -B check-source.py --project-root /project --firmware /absolute/ID-2966-V4.1.60-decoded.bin --original-object /absolute/source-integrated.o
```

`source-reconciliation.json` 對四個凍結 C/H source 作唯讀調和與身分核對。它明示 HOST 的 return_address 是 saved-frame bookkeeping，不會逐次更新成 opaque call 的實體 link，正常 C return 也不是對該數字實際 JR。純來源契約與 C/HOST/native 的調和記錄分開保存；原指令證據通過不代表 C 程式已 fit、具完整 ABI、可燒錄或相容 OTA。未知 ROM、硬體、非同步行為與安全的裝置更新均未在此驗證。
