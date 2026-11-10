# ID2580 BOOT candidate event 0x2：copy 後至不可見 provider

範圍是靜態指令，不執行目標。原始 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin` 12288 bytes，SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`；base `0x1000` 僅分析座標。延續 [前段](../boot2580-w-event-continuation/README.md)，以下 event bit2 指 **mask 0x2**（第二個 bit），不是 mask 0x4。實際 dispatch、GP、slot 內容與 RAM 均未證明。反組譯使用既有 LLVM 18.0.2（工具 hash 見前段）；實際 bytes 由下方獨立完整 window hash 固定。假設呼叫按一般 ABI 返回、記憶體有效且無並行修改；任一 provider 可有未觀測副作用。

## 實際 BOOT 指令與分支

進入此路徑之前 task 比對通過，`14cc` 將 `lhu gp+0x7e` 放入 s1；`14bc` 把呼叫方 a0 保存在 s5，s3 為 `lbu gp+0x7c`。`1550..1554` 測試 s0 & 2；更高優先事件可先返回。`1560..156a` 讀 `0x200090a4` byte，零時 `1632..163a` 將 `0x200090a6` halfword 清零並跳至共同返回。

* `1570..158a` 呼叫 `[0x40128]`，a0=s1、a1=0x1b、a2=`lhu gp+0x76`、a3=a4=0，返回 a0 存至 `gp+0x78`；非零才繼續。零則 `1618..1630` 將 `0x200090a4` byte 減一（寫入低 8 bits），設定 a0=s3、a1=2、a2=2，再從 `[0x40058]` 呼叫，後跳共同返回。不能保證此呼叫成功或排程。
* `158c..15a0` 的 `[0x4004c]` 呼叫以剛返回的非零 a0 為目的、`0x200090aa + lhu(0x200090a8)` 為來源、`lhu gp+0x76` 為長度。`15a2` 開始覆寫 a5 而非檢查 copy 返回值；不證明 copy 確實執行或 buffer 有效。
* `15a2..15b0` 呼叫 `[0x4013c]`，a0=s1、a1=gp+0x68，**只測返回值 bit 0**。這和前段 bit1 路徑的「完整值恰為 1」不同。若 bit0=0，直接去 `15b2`；若 bit0=1，`15dc..15f2` 把 `lhu gp+0x2a` 寫入 `gp+0x74`，呼叫 `[0x400d4]`，a0=s1、a1=gp+0x74、a2=0。
* `15f4` 測試該返回值完整 a0 是否為零。非零走 `15b2`：呼叫 `[0x4012c]`，a0=gp+0x74、a1=0x1b；其返回值不被檢查。然後 `15c2..15da` 將 `0x200090a4` byte 減一，呼叫 `[0x40058]`，a0=s5、a1=2、a2=2，返回值亦不被檢查，再到共同返回。無法證實 free 或 retry 實際成功。
* `[0x400d4]` 返回零時 `15f6..1610` 取 `lhu(0x200090a8) + lhu(gp+0x76)`，將低 16 bits 寫回 `0x200090a8`；呼叫 `[0x40050]`，a0=s3、a1=1，返回值不被檢查。這是本 callback 可見的 offset 推進與下一事件呼叫，不是送達確認。
* 共同 `1612` 設 a0=`s0 XOR 2`，`1616` 跳 `149e` 恢復暫存器並於 `14b2 ret` 返回；不回傳上述 provider 的 status。這只在該控制流程與 provider 正常返回時成立。

## WCH SDK 的條件性交叉比對

獨立參考 [固定 commit 的公開 SDK header](https://raw.githubusercontent.com/openwch/ch32v20x/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h) SHA-256 `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c`，其 `BLE_LIB_JT(n)` 在候選表以 `0x40034+4*n` 計：6=`tmos_memcpy`、7=`tmos_set_event`、9=`tmos_start_task`、40=`GATT_Notification`、61=`GATT_bm_alloc`、62=`GATT_bm_free`、66=`GATTServApp_ReadCharCfg`。僅若實機表、ABI、資料結構與此 SDK 相符，才可將這些間接呼叫分別解讀成 copy、事件設定、延時重試、notification submit、配置、釋放與配置讀取。SDK header 將 notification 的 0 status 命名 SUCCESS，並明言 notification 不產生 ATT confirmation；該名稱不是實際無線送達證據，也不能用來證實真機 slot 身分、記憶體所有權或 provider 內部行為。`[0x4013c]` 候選機器碼及其限制另見 [provider 比對](../boot2580-w-provider-offline/README.md)。

**下一不可見邊界：** `[0x400d4]` 的 live 目標和其 status／ownership，及失敗後 `[0x4012c]` 的真實效果；即便返回零，後續 `[0x40050]` 的 live 目標和事件處理亦未知。不能推定 BLE 發射、接收、ACK 或持久化；無硬體操作、刷寫或目標執行。REA MCP/CLI 此環境未提供，以上為本地 LLVM 證據而非 REA Evidence。

## 重播及負測

`python -B analysis/boot2580-w-event-return-offline/check.py` 核對整檔及 SDK header hash、原始 `[144a,14c8)` 與 `[1550,163c)` window hash；對兩 window 每個 byte 各自翻轉一 bit 且繞過整檔 hash，確認 window gate 拒絕，另測各 window 截斷與 SDK 突變。這是完整性測試，不是反組譯語意或執行證明。前置段 `[14c8,1550)` 已由[前段 checker](../boot2580-w-event-continuation/check.py)固定；重播時一併執行。
