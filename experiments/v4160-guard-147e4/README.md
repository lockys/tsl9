# v4.1.60 dispatcher 閘門 0x147e4

`model.c` 將 APP 原始 `[0x147e4, 0x147f4)` 投影成 C 語意：先比較完整 32 位元 `a5` 與 255；不相等即跳 `0x1491a` 且不讀記憶體。相等才讀 `s0+1` 的 byte；若值為 255 則到 `0x147f4`，否則到 `0x1491a`。當 `a5` 來自先前的 byte 載入時，這相當於兩個連續 byte 均為 `0xff`。原入口與實際可達性不在本投影範圍。

`verify.py` 核對原 BIN 雜湊及 16 bytes，有限解碼 RV32 指令欄位與分支，C11/C++17 各測試 85,536 組，包括全部兩 byte 組合、完整 `a5` 高位與位址環繞；四個指令位元組變造和三個 C 語意變造被拒絕。讀取由成功的合成替身提供，未模擬 trap、MMIO、中斷或實機。

```text
python -I -B experiments/v4160-guard-147e4/verify.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/composition.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/success_path.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/alias_witness.py
python -I -B experiments/v4160-guard-147e4/provider_setup_10032.py
python -I -B experiments/v4160-guard-147e4/provider_setup_composition.py
python -I -B experiments/v4160-guard-147e4/ingress_dispatch_8a36.py
python -I -B experiments/v4160-guard-147e4/ingress_checksum_gate.py
python -I -B experiments/v4160-guard-147e4/ingress_payload_store.py
python -I -B experiments/v4160-guard-147e4/ingress_payload_transition.py
python -I -B experiments/v4160-guard-147e4/ingress_store_length_alias.py
python -I -B experiments/v4160-guard-147e4/reset_gp_disjoint.py
python -I -B experiments/v4160-guard-147e4/reset_provider_arguments.py
python -I -B experiments/v4160-guard-147e4/ingress_store_differential.py --vcvars <vcvars64.bat>
```

`composition.py` 將既有 `experiments/v4160-dispatch-148b4-model/payload_gate.py` 的前置解碼與本 C 閘門分段串接，C/C++ 各 68,096 組通過；其中長度為 1 的 512 組在該投影中繞過閘門。此為合成穩定記憶體上的邊界重建，並不證明從完整入口可達或 byte 讀取安全。

`success_path.py` 額外在合成條件下串接成功閘門、`0x13ba6` 的三種設定結果、三個 `0x1070a` 指令投影，以及 `0x14800` 全 65,536 個半字前置判斷；C/C++ 均通過。這些是分段重建而非連續執行。`0x1070a` 內部呼叫仍以正常返回、保留被呼叫者保存暫存器且不修改輸入資料的替身處理，並假設輸入不與其他寫入重疊。

`alias_witness.py` 說明不重疊假設有實質影響：在合成位址 `s0=0x2000bfb6` 且首四 bytes 為 `ff ff 01 00` 時，`0x1070a` 內已解碼的 byte 寫入會將後續半字由 `0x0001` 改成 `0x0000`，使前置判斷從 `0x14848` 改至 `0x14812`。另窮舉低、高 byte 各 256 個值；高 byte 案例的半字位址不對齊，僅為假定讀取成功的算術投影，不能假設硬體接受。針對既有 ingress C 模型所提供的固定 payload 位址 `0x2000b9d8`，全部 65,536 個半字對照均未與這個 byte 寫入重疊。兩種情況都假設替身返回且沒有其他輸入修改；前者不表示實際呼叫者能提供該位址，後者亦未證明實際裝置一定走該 ingress 路徑。

`provider_setup_10032.py` 解碼 `0x1070e` 呼叫與 `0x10032–0x10044` 的六條指令：讀取 `[0x40048]`，以 `(gp+300, 0, 3)` 為參數、保留返回位址尾跳至指標（清除目標最低位）。測試涵蓋 65,536 個 gp 值、75 個邊界組合與 18 個逐 byte 變造；未執行 provider，不能推論其清除記憶體或會返回。該段已在既有 state-access 原始位址驗證中，不是新增正式覆蓋。

`provider_setup_composition.py` 將此邊界與 `0x1070a` 的替身投影分段串接，16,396 組通過；首次與後續對 `0x40048` 的讀取可各自提供不同值，不能預設相同。假設 `gp=0x2000be8c` 時兩次 provider 的目的位址算術上均為 `0x2000bfb8`，但未確認實際 `gp`、provider 副作用或其返回。

`ingress_dispatch_8a36.py` 解碼原始 `0x8a36–0x8a4c`：在此局部入口成立且讀取成功時，`0x8a48` 呼叫 `0x14056`，其中 `a2=0x2000b9d8` 由 PC-relative 指令形成、與 `gp` 無關；另核對 `0x14068` 是 `s0←a2`。全部 65,536 個長度、3,072 個合成輸入邊界及 22 個位元組變造通過。此為分段靜態與指令投影，未證明 checksum 閘門通過、完整入口可達或中間狀態無變化。

`ingress_checksum_gate.py` 解碼緊接此前的 `0x8a2a–0x8a36`：`a4 != s10` 時跳過 dispatch 且不讀 checksum；相等時讀取 `gp+165` 的 byte，再與完整 32 位元 `a5` 比較，相等才到 `0x8a36`。65,536 個 byte 配對、4,096 個合成邊界與 12 個指令位元組變造通過；`a5` 的來源、局部入口可達性、讀取成功及實機行為不由此證明。

`ingress_payload_store.py` 從原始 `0x8a02` 解碼 payload 寫入：若輸入 index 無號大於 1039，跳至 `0x8a4c` 且不寫；否則依序寫入 `gp+138` 的遞增半字及 `0x2000b9d8+index` 的資料 byte。窮舉 65,536 個 index、105 個邊界與 30 個位元組變造；在此局部投影中，payload 寫入範圍為 `[0x2000b9d8,0x2000bde8)`。這不是完整封包路徑、物件邊界或硬體驗證。

`ingress_payload_transition.py` 解碼緊接 payload 寫入的 `0x8a20–0x8a2a`：重新讀取 `gp+142` 半字，若完整無號 `a4` 小於該值則到 `0x89a8`，否則到 `0x89dc`。三種 index 各窮舉全部 65,536 個讀取值、另有 105 個邊界及 10 個位元組變造，均通過。讀取的是當下的值；此投影不假設它等於先前長度，也不證明記憶體穩定或完整路徑可達。

`ingress_store_length_alias.py` 以共享合成記憶體串接寫入與重讀：假設 `gp=0x2000b94a`、index=0，payload 首 byte 與長度半字低位重疊，可將長度 `2` 改成 `0` 並改變分支。256 個重疊及 256 個 `gp=0x20004000` 不重疊對照通過；後者是啟動分析中的 gp 值而非實機量測，前者不表示該狀態實際可達。未模擬並行或其他副作用。

`reset_gp_disjoint.py` 另從原始 reset 兩條指令解碼 `gp=0x20004000`。**若後續 gp 不變**，1040 個 payload 索引不會與 `gp+138`、`gp+142` 的半字或 `0x2000bfb8` 重疊；8,320 組寫入／重讀條件案例與 8 個 reset 位元組變造通過。這不證明活體 gp、位址轉譯、provider 副作用或實機行為。

`reset_provider_arguments.py` 在 gp 保持 reset 值的條件下，對照 callback 的兩次 provider 參數：首次為 `(0x2000412c,0,3)`，後次為 `(0x2000bfb8,0,12)`。以第三參數作為假想長度時，這兩段與 ingress payload 的固定範圍互不重疊；65,536 個合成指標和三個 callback 軌跡通過。未知 provider 是否把第三參數解讀為長度，亦未知它實際讀寫何處。

`ingress_store_model.c` 將索引判斷、兩次寫入事件與重讀後分支重建為 C 投影；呼叫者須提供**寫入後**的半字值，不能假設沒有重疊。`ingress_store_differential.py` 以兩個原始指令解碼器作局部對照，C11/C++17 各 197,480 組通過，含 512 組以共享記憶體模擬器計算寫入後長度的重疊／對照案例；合成重疊案例也示範錯用寫入前長度會走錯分支。索引門檻、byte 遮罩、比較運算三種語意變造均遭拒；非原位址 byte-exact、非實機或完整函式 ABI。主機 MSVC 的 `vswhere.exe` 警告不影響本次編譯。

既有 `experiments/v4160-dispatch-148b4-model/payload_gate.py` 已檢查相關雙 byte 條件；此處補充獨立 C 投影、完整輸入暫存器及讀取事件。該範圍已有 inline-assembly 片段，並未因此增加正式原位址覆蓋或產出可刷韌體。
