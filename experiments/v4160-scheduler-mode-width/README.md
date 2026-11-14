# 排程器 mode 位寬的受限指令軌跡

對固定 v4.1.60 原始 BIN，以固定指令表執行從 `0x920e` 選定空槽後到 `0x91e8` 居民路徑選擇的片段。假設先前掃描選到空槽、輸入延遲非零；**不執行掃描、居民函式或實機**。

合成反例：index 0、callback `0x1333c`、delay 300 時，mode `0` 與 `0x100` 存入的 mode byte 都是 `0`，但前者選 `0x922c`、後者選 `0x91ea`；mask 為 1、換算值為 480。這是完整 32 位 mode 比較與低 8 位儲存的差異，不表示真實呼叫者曾傳入 `0x100` 或排程成功。

`verify.py` 執行 1,920 個合成軌跡，涵蓋 15 槽、多種 mode、延遲環繞和 task 值，並拒絕 18 個指令編碼變造。此處為既有指令的行為測試，不是新增原始 byte 覆蓋。

`free_scan.py` 另從 `0x9206` 執行固定指令表：假設前一輪比對未命中、`a5=0x2000be08` 且讀取成功且穩定，依序讀 15 筆的 `+4` word，選第一個零；全非零則在 `0x9234` 前得到 `a0=1`。窮舉 32,768 種佔用組合，將 32,767 個選槽結果接到後段投影，並拒絕 9 個指令變造。組合只檢查片段邊界，沒有執行前一輪掃描或證明輸入可達；尤其 callback 為零且有空槽時，不可假定前輪會未命中。

`match_scan.py` 模擬非零延遲入口的前一輪 callback 比對（`0x9196` 至命中或 `0x9206`），保持 `a5` 指向表首。98,304 組位元圖及 19,683 組混合表確認第一個相等項目優先於空槽；在穩定讀取下，callback 為零時只有全非零表才能未命中並進入空槽掃描。這是兩段投影的合成組合，不含命中後動作、其他入口或實機。

`match_update.py` 模擬命中後 `0x91a2–0x91d0`：先讀選中項目 `+8`，非零則以該值呼叫 `[0x40068]`；接著讀 `gp+166`，寫入 mode 低 byte 與新的 `+8` word，並產生索引 mask。片段沒有明示寫入 callback word，但 provider 可能有未知副作用，因此不能保證它未改變。1,800 組合成軌跡、6,000 組掃描接續及 16 個指令變造；provider 僅假定正常返回及保存必要暫存器，不證 target 有效或硬體行為。

`match_model.c` 是命中更新的 C 語意投影；`match_differential.py` 比對原指令軌跡，C11/C++17 各 85,536 組及四種語意變造。涵蓋全部低 16 位 mode，但不是 mode、索引與舊參數的完整笛卡兒積。Provider 副作用不在投影中。

`zero_delay_scan.py` 驗證零延遲時先掃 15 個槽位：32,768 種佔用組合與 8 種指令變造；若全滿會落到一般路徑，並非直接證明返回失敗。`zero_delay_insert.py` 再以 10,000 組合成軌跡接續首個空槽，記錄 callback word、零 mode byte、參數 word 寫入及從 `[0x40050]` 載入尾跳目標；21 種指令變造被拒。堆疊與其他讀取值由測試直接提供，未模擬記憶體別名、provider 或硬體。

`zero_delay_model.c` 將零延遲插入後的明示事件、保存暫存器與尾跳參數還原為 C 投影。`zero_delay_differential.py` 各以 C11/C++17 比對 30,000 個合成軌跡，含堆疊指標模 2³² 環繞，並拒絕四種 C 語意變造；讀取值獨立提供，不模擬別名或 trap。

`setup.py` 解碼 `0x9132–0x9136` 與 `0x9188–0x9194`：兩組 PC-relative 指令分別產生 `s2=a5=0x2000be08`，一般路徑並保留 callback，複製 mode、delay、argument 至保存暫存器；65,536 組合成輸入及指令變造通過。

`delay_precedence.py` 解碼 `0x913a` 的零／非零延遲分支，將掃描與後續更新以受限邊界組合。在穩定合成表同時有空槽與相同 callback 的 32,766 個案例中，零延遲先選空槽、非零延遲先選相符項；全滿案例組合了零延遲掃描、一般路徑設定及既有 callback 命中。這不是連續 CPU 執行，不能推論並行或實機結果。

`route_model.c` 組合成只回傳選槽路徑及索引的 C 模型，不執行實際記憶體操作；`route_differential.py` 比較各指令片段的邊界投影，C11/C++17 各 141,072 組，包括所有佔用位元圖、零 callback、重複 key 與四種語意變造。表格必須穩定，未驗證並行、provider、trap 或實機。

`resident_exit.py` 模擬共同尾段：mode 為零時讀取 `[0x40058]` 並呼叫，若 provider 正常返回則 `a0=(返回值==0)`，再還原堆疊及返回；mode 非零時先還原堆疊，再尾跳 `[0x4022c]`。131,072 組合成軌跡與 22 種指令變造通過；provider 替身、副作用、目標有效性及硬體均未驗證。

`resident_exit_model.c` 另以 C 投影共同尾段的路徑、還原暫存器、讀取順序及呼叫資訊。`resident_exit_differential.py` 各以 C11/C++17 執行 141,072 組比較並拒絕四種語意變造；假設非尾跳 provider 正常返回，不模擬其副作用。

`common.py` 單獨驗證含零延遲的共同換算：先以 32 位環繞乘 1000，再無號除以 625；131,072 組及 8 個指令變造通過。`full_zero_fallback.py` 以 20,000 組合成資料接續「零延遲、表滿、既有 callback 命中」各片段，涵蓋 240 種索引、mode、舊參數與 provider 返回組合；該情況換算延遲為零，但 mode 仍決定正常呼叫或尾跳。片段並非連續 CPU，假設 provider 正常返回、不修改共享狀態且讀取成功。

`full_exit.py` 將「表滿且 callback 不符」掃描接續至 `0x9234` 返回：20,000 組合成資料涵蓋零／非零 delay 與 mode，觀察 `a0=1`、六次堆疊讀取與返回；8 個指令變造被拒。此投影中未呼叫 provider，並非證明真實執行期間無其他並行活動。

`full_exit_model.c` 還原 `0x9234` 的一般尾聲，保留輸入 `a0` 並以提供的合成堆疊值還原暫存器；表滿路徑進入此尾聲時的 `a0=1` 已由 `full_exit.py` 單獨檢查。`full_exit_differential.py` 的 C11/C++17 各通過 70,000 組比較與四種變造，包含任意 `a0` 和堆疊指標環繞；讀取成功且互不別名，未在硬體執行。

`scaling_preimages.py` 對 32 位共同換算反推輸出為零的全部輸入：`gcd(1000,2^32)=8`，落在 0–624 的可達餘數共有 79 個，每個有 8 個原像，故共 632 個，其中 631 個非零；最小非零值 `8589935`（`0x0083126f`）的乘法環繞餘數為 408。原像與鄰值均比對原始指令受限投影；不表示呼叫者實際可傳入該值或 provider 如何處理。

`scaling_bounds.py` 在假設輸入限制為 16 位時，窮舉確認換算嚴格遞增、`0→0`、`65535→104856`；但尚未證明呼叫者有此限制。32 位算術第一次乘法環繞發生於輸入 `4294968`，輸出由 `6871947` 跳為 `1`；可達的全域最大輸出為 `6871947`，另有原像見證。這些是固定指令投影與數學結果，非實機驗證。

`event_tail_composition.py` 以 12,000 組合成案例接續原始 `0x13d88` 事件尾段及排程器片段：各 3,000 組直接分支、命中、插入與表滿。此呼叫點傳入 delay 35 或 100，對應共同換算 56 或 160；片段間重建狀態，假設穩定讀取及 provider 正常返回，不證實際可達或時間單位。

`data_delay_caller.py` 驗證資料選擇的原始呼叫點 `0xb2aa–0xb2f4`：前兩個呼叫均返回零、讀取成功且 clock provider 不修改堆疊等假設下，`[P+96]>>6` 對應 delay `0/60000/300000/600000`，尾跳 `0x9124(0xb254,0,delay,0)`，並將 clock 加 delay 的 32 位環繞結果寫至 `0x2000bef0`。2,048 組含全部 256 byte 值，26 個指令變造被拒；未知呼叫點是否可達、provider 與硬體行為。

`data_delay_model.c` 是該呼叫點的 C 語意投影；`data_delay_differential.py` 的 C11/C++17 各與原指令投影比較 65,536 組，涵蓋全部 byte 值及合成指標／clock 環繞，四種語意變造均被拒絕。測試假設合成讀取互不影響、不模擬記憶體別名或 provider 副作用。

`data_delay_entry.py` 檢查呼叫點的入口閘門：先呼叫 `0xf65c`，其結果非零即返回；否則呼叫 `0xd3e8`，其結果非零也返回，兩者均零才進入資料選擇。65,536 組合成返回值及 256 種 byte 接續測試通過，9 個指令變造被拒；兩個呼叫都以保留堆疊的正常返回替身模擬，不代表實際 provider 行為。

`model.c` 是選定空槽後的 C 語意投影；`differential.py` 的 C11、C++17 各 67,456 組與固定指令表比對，包含所有低 16 位 mode 值及四種語意變造。輸入 index 限制為 0–14，delay 非零；不執行實際讀寫或掃描。

```text
python -I -B experiments/v4160-scheduler-mode-width/verify.py
python -I -B experiments/v4160-scheduler-mode-width/free_scan.py
python -I -B experiments/v4160-scheduler-mode-width/match_scan.py
python -I -B experiments/v4160-scheduler-mode-width/match_update.py
python -I -B experiments/v4160-scheduler-mode-width/zero_delay_scan.py
python -I -B experiments/v4160-scheduler-mode-width/zero_delay_insert.py
python -I -B experiments/v4160-scheduler-mode-width/delay_precedence.py
python -I -B experiments/v4160-scheduler-mode-width/setup.py
python -I -B experiments/v4160-scheduler-mode-width/common.py
python -I -B experiments/v4160-scheduler-mode-width/scaling_preimages.py
python -I -B experiments/v4160-scheduler-mode-width/scaling_bounds.py
python -I -B experiments/v4160-scheduler-mode-width/full_zero_fallback.py
python -I -B experiments/v4160-scheduler-mode-width/full_exit.py
python -I -B experiments/v4160-scheduler-mode-width/event_tail_composition.py
python -I -B experiments/v4160-scheduler-mode-width/data_delay_caller.py
python -I -B experiments/v4160-scheduler-mode-width/data_delay_entry.py
python -I -B experiments/v4160-scheduler-mode-width/data_delay_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-scheduler-mode-width/full_exit_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-scheduler-mode-width/resident_exit.py
python -I -B experiments/v4160-scheduler-mode-width/resident_exit_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-scheduler-mode-width/route_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-scheduler-mode-width/zero_delay_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-scheduler-mode-width/match_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-scheduler-mode-width/differential.py --vcvars <vcvars64.bat>
```
