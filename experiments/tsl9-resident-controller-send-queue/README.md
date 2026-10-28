# 控制器傳送佇列與 descriptor pool

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_controller_send_queue.c)

新增 **2 個完整 SDK 候選本體，284 CODE bytes／101 指令**：controller enqueue `0x6A626..0x6A700`（218B／79指令）與pool lookup `0x57862..0x578A4`（66B／22指令）。C11／C++17原生物件與原指令、18筆重定位相符；保留原寄存器繫結、volatile存取、FENCE.I、variable SLL及條件式Xwchc。

|位置|已確認的靜態行為|
|---|---|
|`0x6A63A..0x6A670`|查找連線；不存在回2。零長度要求設共用flag20002FA8並回0；下一筆有效非零長度且flag=1時清flag，將傳入argument改為2|
|`0x6A676..0x6A67E`|保存4002420C控制word、寫0、執行FENCE.I。之後所有正常返回路徑有對應還原；實體暫存器／IRQ含義未證明|
|`0x57862..0x578A4`|依BufNumber與mode計算掃描終點；從16B pool找第一筆tag=FF54或FFFF，沒有「優先找所有exact match」的額外掃描。它不是heap配置器|
|`0x6A68E..0x6A6B4`|LBU讀node+10再SH寫回同位置；建立／追加連線+280/+284佇列，buffer存incoming pointer−2、length寫halfword+12、marker+9=0x81|
|`0x6A6B6..0x6A6D2`|由record+41產生 `low16(1 << (slot&31))`，向task0提出事件，忽略event setter回值後回0；不代表資料已由無線送出|
|`0x6A6DC..0x6A6FA`|pool lookup為NULL時，可能在控制word尚清0時呼叫staCB(1,0x5555)，正常返回後還原控制word並回7|

另核對既有pool initializer完整190B、APP config initializer308B與BLE_LibInit228B的原始／實際native參考。pool base是20003464，數量公式為 `mode==0 ? c+1 : 2*c`；APP名義BufNumber為8，**在設定保持前提下是9或16筆**。初始化仍受heap配置、16-bit大小截斷、post-call fresh count與啟動呼叫順序等條件限制，沒有證明live RAM範圍。

官方結構編譯期斷言確認BufNumber offset15、staCB offset52。APP先清64B config，未再明確覆寫staCB對應stack bytes，library再複製64B；**若期間／後續沒有改寫，staCB為NULL，便跳過這個錯誤callback**。這個條件式結果不代表所有可能的live callback目標已閉合。

原普通匯入 `0x6A626` 現在由真實218B本體解析，沒有空alias；新code的兩個普通匯入也由既有lookup／event setter解析。C/C++部分連結一致：**44,894 CODE＋412 DATA bytes／15,616指令**、3,203正大小FUNC、2,553重定位、**0具名普通UND**。父bytes／globals／symbolic relocation roles保留。

零UND不代表完整環境：間接callback、global lifetime、pool／heap鏈、head/tail一致性、buffer前綴、MMIO語義、task實際消費及無線送出仍有條件。沒有把入列成功當作OTA成功，也未新增pointer guard或重試。

APP正式來源仍 **162份、73,478／76,800B（95.67% 靜態byte覆蓋）**，不等於功能完成。SDK未連入APP或做最終原位址配置；既有4B啟動來源缺口保留。**沒有新BIN，實體ROM／RAM／IRQ／Flash／OTA相容性仍未證明**。未執行target、HOST model、ISA或硬體，未呼叫廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [未實作的新功能候選](feature-candidates.json)：相容性通過後考慮唯讀佇列／pool健康診斷，只提供彙總資訊。

已有固定本機輸入與LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-resident-controller-send-queue/verify-v1.py --tool-dir "$LLVM_BIN"
```
