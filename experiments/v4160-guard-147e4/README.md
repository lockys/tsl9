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
python -I -B experiments/v4160-guard-147e4/ingress_s11_provenance.py
python -I -B experiments/v4160-guard-147e4/ingress_loop_provenance.py
python -I -B experiments/v4160-guard-147e4/ingress_loop_wrap.py
python -I -B experiments/v4160-guard-147e4/ingress_argument_provenance.py
python -I -B experiments/v4160-guard-147e4/clock_wrapper_81b0.py
python -I -B experiments/v4160-guard-147e4/resident_clock_candidates.py
python -I -B experiments/v4160-guard-147e4/resident_ingress_composition.py
python -I -B experiments/v4160-guard-147e4/resident_clock_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/clock_gap_composition.py
python -I -B experiments/v4160-guard-147e4/clock_gap_start_composition.py
python -I -B experiments/v4160-guard-147e4/ingress_second_byte.py
python -I -B experiments/v4160-guard-147e4/ingress_third_byte.py
python -I -B experiments/v4160-guard-147e4/ingress_length_high.py
python -I -B experiments/v4160-guard-147e4/ingress_length_composition.py
python -I -B experiments/v4160-guard-147e4/ingress_length_high_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/ingress_command_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/ingress_prefix_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/clock_gap_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/ingress_a5_provenance.py
python -I -B experiments/v4160-guard-147e4/ingress_provenance_composition.py
python -I -B experiments/v4160-guard-147e4/ingress_length_initialize.py
python -I -B experiments/v4160-guard-147e4/ingress_length_initialize_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/ingress_length_route.py
python -I -B experiments/v4160-guard-147e4/ingress_length_route_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/ingress_length_route_composition.py
python -I -B experiments/v4160-guard-147e4/ingress_state_precedence.py
python -I -B experiments/v4160-guard-147e4/ingress_state_gate.py
python -I -B experiments/v4160-guard-147e4/ingress_state_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/ingress_state_store_composition.py
python -I -B experiments/v4160-guard-147e4/ingress_checksum_gate.py
python -I -B experiments/v4160-guard-147e4/ingress_checksum_differential.py --vcvars <vcvars64.bat>
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

`ingress_s11_provenance.py` 解碼 `0x8934` 的 `s11=gp+142`，若跨區段 `gp` 與 `s11` 保持不變，長度半字的兩 byte 相對於 counter `gp+138` 的兩 byte 偏移分別為 4、5 與 0、1，即使位址以 32 位元環繞也不重疊。65,536 個 gp、8 個環繞邊界、65,536 個計數／長度組合與四個位元組變造通過；這是分段投影，不證明暫存器穩定或實機行為。

`ingress_loop_provenance.py` 對 `0x8938` 的局部迴圈檢查與 `0x8962–0x896a` 輸入讀取解碼，再分段接續狀態選擇；由 `0x8934` 已設定 `s11` 的條件出發，該次直接路徑到 `0x89cc` 沒有改寫 `gp` 或 `s11`。65,536 個索引、450 個邊界與 18 個位元組變造通過，包含最佳化模式；不涵蓋先前迴圈、非同步改寫、trap 或實機。

`ingress_length_composition.py` 使用共享合成記憶體串接長度高 byte、低 byte 與狀態選路，窮舉 65,536 長度；假設 gp 穩定、`s1=gp+165`、`s11=gp+142`、存取成功及各片段依序抵達，得到長度 0/1–1040/1041–65535 分別設定狀態 6/5/0，checksum 為 command+高 byte+低 byte 的低 8 位。並非連續 CPU、完整封包或實機驗證。

`ingress_length_high_model.c` 是狀態 3 的 C 事件投影；`ingress_length_high_differential.py` 在 C11/C++17 各以 79,360 案比對固定指令投影，拒絕四種語意變造。checksum 輸入是先前寫入完成後的讀值；不代表原位址 byte-exact、存取異常或實機驗證。

`ingress_length_high.py` 固定指令投影狀態 3：依序寫 state=4、將輸入 byte 左移 8 位寫入 `gp+142` 半字，然後讀 checksum、寫兩者和的低 byte。65,536 byte/checksum、256 狀態、4 個合成別名邊界及 32 個 byte 變造通過；checksum 讀值取自前述寫入之後。未模擬未對齊異常，亦不證別名可達或實機行為。

`ingress_command_model.c` 建立狀態 2 處理的 C 事件投影；`ingress_command_differential.py` C11/C++17 各 77,056 次與原始固定指令投影比較，拒絕四種語意變造，涵蓋 byte 組合、位址環繞與合成讀寫別名。呼叫者提供前兩次寫入之後的讀取值；並非 byte-exact 或實機證據。

`ingress_third_byte.py` 固定指令投影狀態 2：依序寫 state=3、寫 command byte、讀 checksum、寫入兩者和的低 byte；65,536 組 byte/checksum、256 狀態與 26 個 byte 變造通過。checksum 讀值必須反映前兩次寫入，合成 `s1` 別名案例展示差異；若先前 `s1=gp+165` 且兩者保持不變，該讀取不與這兩個 byte 寫入重疊。別名可達性及實機未證。

`ingress_prefix_model.c` 將兩 byte 閘門與寫入事件表達為 C 語意模型；`ingress_prefix_differential.py` 在 C11/C++17 各與固定原始指令投影比較 69,376 案，拒絕四個語意變造。假設兩 byte 均被成功處理、狀態與 gp 穩定，沒有非同步或影響輸入的別名；不是原址 byte-exact 或實機驗證。

`ingress_second_byte.py` 將狀態零與狀態一的固定指令投影串接，窮舉 65,536 個 byte pair：假設連續處理成功且狀態穩定，只有 `55 7f` 會經兩個閘門寫入狀態 2 和清除 checksum；另測 256 狀態與 24 個位元組變造。這不證完整封包、連續 CPU 執行或實機行為。

`clock_gap_start_composition.py` 將時間差清除、迴圈讀取及 `0x8970` 狀態零入口分段組合：在成功存取、gp 穩定、無非同步寫入或影響狀態的別名下，清除後讀到 `0x55` 寫入狀態 1，其他 byte 走 `0x8a4c`。65,536 組舊狀態／輸入及 14 個位元組變造通過；不代表封包實際可達或實機驗證。

`clock_gap_model.c` 是時間差讀寫事件的 C 語意投影；`clock_gap_differential.py` 在 C11 與 C++17 各比較 458,827 組原始指令固定投影，並拒絕門檻、減法方向及位址三種變造。假定讀寫成功、輸入 prior 為當次讀取值；不代表原位址逐位元組相同或實機驗證。

`clock_gap_composition.py` 分段組合時鐘包裝與 `0x8908` 的時間差判斷：以 RV32 無號差值大於 299 決定是否清除 `gp+156`，並寫入 `gp+160`。262,144 個差值案例及 26 個位元組變造通過；9 個合成見證中，連續 resident 輸入使包裝值由 `0x0fffffff` 跳至 0，無號差值 `0xf0000001` 觸發清除。這不代表 resident 實際遞增或實機會發生，亦假設堆疊及存取正常。

`resident_ingress_composition.py` 條件式串接兩份參考 resident 投影、APP 時鐘包裝、時間差清除與狀態零入口，每份 65,536 個合成組合；檢查 299/300 邊界及 `0x55`／非 `0x55`。中間控制流與非零輸入長度是額外假設，並假設候選就是實機 resident（尚未證實）；不是連續 CPU 或硬體驗證。缺少任一候選會 SKIP，全部缺少則失敗。

`resident_clock_model.c` 建立候選時鐘函式的受限 C 語意投影；`resident_clock_differential.py` 對兩份 carrier 分別以 C11、C++17 各比對 262,144 案，拒絕三種語意變造。測試至少需要一份本地 carrier；缺少的候選各自 SKIP，全部缺少則明確失敗而非聲稱通過。這些參考 carrier 不在 main，非實機已安裝 ROM 證明。

`resident_clock_candidates.py` 對兩份可選本地 WCH 參考 carrier 核對全檔 SHA、`[0x4007c]` 指標及各 42 個函式 bytes，固定指令投影各執行 131,072 組含 callback 與零指標的合成案例，並拒絕逐 byte 變造。V1.31 指向 `0x43520`，V1.40 指向 `0x435ac`；缺少 carrier 時明確 SKIP。callback 假設正常返回並保留 s0、sp 和已存堆疊值，允許改變計數 word；這不是通用解碼器、實機 ROM 識別或 ABI 證明。

`clock_wrapper_81b0.py` 檢查原始 `0x81b0` 包裝函式固定指令；在 resident 替身正常返回且不修改保存的返回位址或 SP 的假設下，返回值為 `((resident_result*10) mod 2^32)>>4`，而 s2 取決於 resident 返回後的值。65,536 個值、90 個邊界及 26 個位元組變造通過；resident 的實際語義、stack 與硬體未驗證。

`ingress_argument_provenance.py` 解碼 `0x8900` 至呼叫 `0x81b0`：呼叫前 `s3=a0`、`s4=a2`、`s2=a3`、`ra=0x8908`，其中 `a3` 未被截斷。窮舉 65,536 個 a3 值、90 個完整位寬邊界及 8 個位元組變造。此結論止於呼叫點；callee 是否返回或保留 s2、上游 a3 的實際範圍及硬體可達性未證。

`ingress_loop_wrap.py` 解碼 `0x897e` 的完整 32 位 `s0` 遞增與返回迴圈，分段接續以 `s0` 低 16 位對完整 `s2` 比較的既有投影。窮舉 65,536 個遞增輸入、邊界與四個位元組變造，並對 s2=0、1、65535、65536、0xffffffff 做有限步數測試。合成 s2>65535 時，65536 步內低位環繞而比較不退出，但完整 `s0` 與資料位址繼續遞增。**假設每次狀態處理都返回且不改 s0/s2，且存取成功**；不能宣稱真實 caller 可達或實機無限迴圈。

`ingress_a5_provenance.py` 追蹤 `0x896a` 的 LBU 與後續狀態選擇，條件式證明透過該局部路徑到 `0x89cc` 時 `a5` 是零延伸 byte；65,536 個狀態／byte、54 個邊界及 22 個位元組變造通過。`ingress_provenance_composition.py` 分段串接長度初始化與選路：2,048 組解碼對照與 16,777,216 組算術配對表明此路徑下完整結果等於儲存的半字，因此先前高位 `a5` 的合成反例不能由此局部路徑到達；其他入口或中斷尚未排除。假設讀寫成功及區段間暫存器穩定，不代表完整執行或硬體驗證。

`ingress_length_initialize.py` 解碼 `0x89cc–0x89da`，以共享合成記憶體依序驗證清除 `gp+138` 半字、讀取 `[s11]` 半字、與完整 `a5` OR、將結果低半字寫至 `gp+142`。131,072 個值、63 個重疊／位址環繞與 14 個位元組變造均通過，也在 Python 最佳化模式測試。合成輸入 `a5=0x10000`、讀值為零時，完整 `a4=0x10000` 而儲存半字為零；這不表示實際呼叫可達。記憶體存取假設成功，包含未對齊與環繞位址，不代表硬體接受；後續分支由下列獨立投影測試。

`ingress_length_initialize_model.c` 提供 C 暫存器與寫／讀／寫事件投影；讀取值必須由呼叫者提供**首次清除後**的半字，以容許重疊。`ingress_length_initialize_differential.py` 以共享記憶體原始指令解碼器比較 C11/C++17 各 131,135 組，含重疊與環繞；四種運算、位址與截斷變造被拒。合成重疊例證實先清除再讀取；未證硬體可達性或實際 ABI，MSVC 有已知 `vswhere.exe` 警告。

`ingress_length_route.py` 解碼後續 `0x89da–0x89f6`：以完整 `a4` 判斷，0 寫 state 6、1–1040 寫 5、大於 1040 寫 0；65,536 個半字值、27 個完整暫存器／位址邊界及 28 個位元組變造通過，含最佳化模式。`ingress_length_route_composition.py` 分段串接初始化與選路，131,072 組通過；合成 `a5=0x10000`、讀值零時，儲存長度為零但選 state 0，不是 state 6。僅假設成功、穩定的存取，不證實完整呼叫可達或硬體行為。

`ingress_length_route_model.c` 將長度選路與寫入事件投影為 C，`ingress_length_route_differential.py` 在 C11/C++17 各與原始位元組解碼器比較 65,563 組，四種零值、邊界、截斷及位址變造均被偵測。這不是原位址 byte-exact 重建或實機驗證；MSVC 有 `vswhere.exe` 警告但編譯成功。

`ingress_state_precedence.py` 對原始 `0x89c8` 比較分支與 `0x89f6` 閘門做分段投影：若完整 `a4` 同時等於 `s8` 與 `s9`，先走 `0x89cc`，不進入 `0x89f6`；否則僅在 `a4 != s8` 時才檢查 `s9`。131,072 組 byte 狀態、200 個完整暫存器邊界及四個 selector 位元組變造通過，亦於 Python 最佳化模式執行。這不證明此局部入口或重複狀態實際可達，也不是連續 CPU 執行或硬體測試。

`ingress_state_gate.py` 解碼 `0x89f6–0x8a06`：完整 `a4` 與 `s9` 不同即到 `0x8a2a` 且不讀取計數；相同才從 `gp+138` 讀半字，無號值大於 1039 到 `0x8a4c`，否則到 `0x8a06`。全部 65,536 個半字、90 個邊界及 16 個位元組變造通過，包含 Python 最佳化模式。`ingress_state_store_composition.py` 對全部 65,536 個計數及四個不相等狀態，分段對照既有寫入投影；兩個投影均包含 `0x8a02` 比較指令，這是重複的邊界驗證而非連續執行。假設局部入口成立、讀取成功，不證明實機、並行或完整封包可達性。

`ingress_state_model.c` 另將該閘門做成 C 語意與讀取事件投影，`ingress_state_differential.py` 對原始指令解碼器在 C11/C++17 各比較 131,178 組，四種條件、邊界、位寬與讀取位址變造被拒。狀態不等時保留呼叫者提供的原始 `a2`，不能推論其真實值。未執行硬體、完整入口或原位址 byte-exact 比較。

`ingress_checksum_gate.py` 解碼緊接此前的 `0x8a2a–0x8a36`：`a4 != s10` 時跳過 dispatch 且不讀 checksum；相等時讀取 `gp+165` 的 byte，再與完整 32 位元 `a5` 比較，相等才到 `0x8a36`。65,536 個 byte 配對、4,096 個合成邊界與 12 個指令位元組變造通過；`a5` 的來源、局部入口可達性、讀取成功及實機行為不由此證明。

`ingress_checksum_model.c` 將這個閘門重建為 C 語意及讀取事件投影；C11/C++17 各與原始指令解碼器比較 74,752 組，含全部 byte 配對、32 位元暫存器及位址環繞邊界。三種變造（第一條件反轉、截斷完整 `a5`、讀取位址偏移）均被偵測。假設讀取成功，不模擬硬體、完整呼叫或原位址 byte-exact。

`ingress_payload_store.py` 從原始 `0x8a02` 解碼 payload 寫入：若輸入 index 無號大於 1039，跳至 `0x8a4c` 且不寫；否則依序寫入 `gp+138` 的遞增半字及 `0x2000b9d8+index` 的資料 byte。窮舉 65,536 個 index、105 個邊界與 30 個位元組變造；在此局部投影中，payload 寫入範圍為 `[0x2000b9d8,0x2000bde8)`。這不是完整封包路徑、物件邊界或硬體驗證。

`ingress_payload_transition.py` 解碼緊接 payload 寫入的 `0x8a20–0x8a2a`：重新讀取 `gp+142` 半字，若完整無號 `a4` 小於該值則到 `0x89a8`，否則到 `0x89dc`。三種 index 各窮舉全部 65,536 個讀取值、另有 105 個邊界及 10 個位元組變造，均通過。讀取的是當下的值；此投影不假設它等於先前長度，也不證明記憶體穩定或完整路徑可達。

`ingress_store_length_alias.py` 以共享合成記憶體串接寫入與重讀：假設 `gp=0x2000b94a`、index=0，payload 首 byte 與長度半字低位重疊，可將長度 `2` 改成 `0` 並改變分支。256 個重疊及 256 個 `gp=0x20004000` 不重疊對照通過；後者是啟動分析中的 gp 值而非實機量測，前者不表示該狀態實際可達。未模擬並行或其他副作用。

`reset_gp_disjoint.py` 另從原始 reset 兩條指令解碼 `gp=0x20004000`。**若後續 gp 不變**，1040 個 payload 索引不會與 `gp+138`、`gp+142` 的半字或 `0x2000bfb8` 重疊；8,320 組寫入／重讀條件案例與 8 個 reset 位元組變造通過。這不證明活體 gp、位址轉譯、provider 副作用或實機行為。

`reset_provider_arguments.py` 在 gp 保持 reset 值的條件下，對照 callback 的兩次 provider 參數：首次為 `(0x2000412c,0,3)`，後次為 `(0x2000bfb8,0,12)`。以第三參數作為假想長度時，這兩段與 ingress payload 的固定範圍互不重疊；65,536 個合成指標和三個 callback 軌跡通過。未知 provider 是否把第三參數解讀為長度，亦未知它實際讀寫何處。

`ingress_store_model.c` 將索引判斷、兩次寫入事件與重讀後分支重建為 C 投影；呼叫者須提供**寫入後**的半字值，不能假設沒有重疊。`ingress_store_differential.py` 以兩個原始指令解碼器作局部對照，C11/C++17 各 197,480 組通過，含 512 組以共享記憶體模擬器計算寫入後長度的重疊／對照案例；合成重疊案例也示範錯用寫入前長度會走錯分支。索引門檻、byte 遮罩、比較運算三種語意變造均遭拒；非原位址 byte-exact、非實機或完整函式 ABI。主機 MSVC 的 `vswhere.exe` 警告不影響本次編譯。

既有 `experiments/v4160-dispatch-148b4-model/payload_gate.py` 已檢查相關雙 byte 條件；此處補充獨立 C 投影、完整輸入暫存器及讀取事件。該範圍已有 inline-assembly 片段，並未因此增加正式原位址覆蓋或產出可刷韌體。
