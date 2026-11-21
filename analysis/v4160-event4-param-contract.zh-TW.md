# 事件 4：回報的參數與下一次請求

`0x85c8` 對已知 handle 檢查 `(uint16_t)(interval-12)<=12 && latency==0 && timeout==200`。不符時只排程 `(該欄 task ID, 4, 4800)`，沒有把 handle 或原參數放進這三個引數。另一個來源 `0x8bfe` 則是在連線建立且取得空欄後直接送事件 4。

若事件真的交給 `0x8614`，0x8000、8 優先；對匹配的 task，1、2 也在 4 之前。到事件 4 時，handle 是這一輪從 `gp+148+4*bank+2` 讀出的半字，不是排程時保存的 handle。`0x886a` 以 `(handle,12,24,0,200,taskID)` 呼叫 `[0x401a8]`。參考 SDK slot 93 為 GAPRole_PeripheralConnParamUpdateReq，間隔單位 1.25 ms，即要求 15–30 ms。若服務正常返回並保持 s0，`0x886c` 將 a0 改為 `events ^ 4`，不檢查成功與否。這條路徑沒有先排除空欄值 0xfffe；不據此推論實際傳過此值。

`check_v4160_event4_params.py <decoded-bin>` 固定原檔 SHA，分開解碼兩端立即數、尾端事件位與參數寄存器。65536 個間隔值逐一相符；假設 task 匹配，65536 個事件遮罩中有 2048 個在本輪選到事件 4。這是局部靜態投影，非事件實際交付、更新成功或週期性重試證據。
