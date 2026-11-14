# v4.1.60 dispatcher 閘門 0x147e4

`model.c` 將 APP 原始 `[0x147e4, 0x147f4)` 投影成 C 語意：先比較完整 32 位元 `a5` 與 255；不相等即跳 `0x1491a` 且不讀記憶體。相等才讀 `s0+1` 的 byte；若值為 255 則到 `0x147f4`，否則到 `0x1491a`。當 `a5` 來自先前的 byte 載入時，這相當於兩個連續 byte 均為 `0xff`。原入口與實際可達性不在本投影範圍。

`verify.py` 核對原 BIN 雜湊及 16 bytes，有限解碼 RV32 指令欄位與分支，C11/C++17 各測試 85,536 組，包括全部兩 byte 組合、完整 `a5` 高位與位址環繞；四個指令位元組變造和三個 C 語意變造被拒絕。讀取由成功的合成替身提供，未模擬 trap、MMIO、中斷或實機。

```text
python -I -B experiments/v4160-guard-147e4/verify.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/composition.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-guard-147e4/success_path.py --vcvars <vcvars64.bat>
```

`composition.py` 將既有 `experiments/v4160-dispatch-148b4-model/payload_gate.py` 的前置解碼與本 C 閘門分段串接，C/C++ 各 68,096 組通過；其中長度為 1 的 512 組在該投影中繞過閘門。此為合成穩定記憶體上的邊界重建，並不證明從完整入口可達或 byte 讀取安全。

`success_path.py` 額外在合成條件下串接成功閘門、`0x13ba6` 的三種設定結果與 `0x14800` 全 65,536 個半字前置判斷；C/C++ 均通過。這些是分段重建而非連續執行，並假設未執行的 `0x1070a` 正常返回、保留 `s0` 且不修改輸入資料。

既有 `experiments/v4160-dispatch-148b4-model/payload_gate.py` 已檢查相關雙 byte 條件；此處補充獨立 C 投影、完整輸入暫存器及讀取事件。該範圍已有 inline-assembly 片段，並未因此增加正式原位址覆蓋或產出可刷韌體。
