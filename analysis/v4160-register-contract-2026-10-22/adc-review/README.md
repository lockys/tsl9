# 原始韌體 0x188E2 的有界相依契約

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

這是原始 ID2966 V4.1.60 的靜態來源分析，不執行指令、模擬處理器、編譯、連結、產生 BIN、連網或接觸硬體。`ledger.json` 保留每列原始位元組與解碼欄位；`check.py` 重讀已封存的上一輪 callback 與解碼器，不另造編碼器，也不更改舊分析。

實際 callback 在 `0x19824/0x19828` 建立 S1=`0x40012400`，`0x19878` 將其送入 A0，`0x1987A` 呼叫 `0x188E2`。前面已封存的 0x8520 限定路徑、0x19124 與 0x1908C 契約不被重新擴大。

`0x188E2..0x1892E`（右界不含）實際 76 bytes／25 列：SP 減 16、RA 存於新 SP+12。A0 等於 `0x40012400` 時，A0 改為遮罩 `0x200`，A1=1，於 `0x188F8` 呼叫唯一小型相依 `0x19160`；返回後重新建立 A0=`0x200`、A1=0，還原 RA、SP，再於 `0x18906` 以無連結跳躍尾呼叫相同相依。第二條已完整涵蓋的分支接受 `0x40012800`，改用遮罩 `0x400`（呼叫位址 `0x1891C`）。不符合兩個常數時，直接還原 RA、SP 並於 `0x1892C` 返回。沒有編碼迴圈。

唯一相依 `0x19160..0x1917E` 實際 30 bytes／12 列。A1 非零時，在 `0x19166/0x1916A` 對 `0x4002100C` 做 32-bit 的讀取、OR A0、寫入；A1=0 時，在 `0x19172/0x1917A` 重新讀取同一位置、AND ~A0、寫入。這是兩次獨立的讀改寫，不能宣稱整個暫存器還原成最初值；其他位元可能在兩次讀取間改變。相依沒有巢狀呼叫、堆疊或 RA 寫入。兩個函式均沒有 S0–S11、GP、TP 寫入。

有效、不與程式或其他保存資料別名的 16-byte 堆疊、正常記憶體／MMIO 存取、沒有非同步暫存器或堆疊更動等前提下，這條相依鏈會還原入口 SP、RA，保存 S、GP、TP。接受分支的 A0 返回值為第二次讀取值 AND ~遮罩，A1=0；A4/A5 是暫存值。不符合常數的分支不改 A0/A1。A2/A3/A6/A7 沒有自有寫入。這些結論只涵蓋已列出的來源，不能推出整個 callback 保存契約。

邊界來自實際入口呼叫、所有來源分支與已封閉的尾相依及最後 RET，不以 FUNC 大小認定。下一個實際入口 `0x1892E` 的第一列讀 A0+4。可選既有 ELF 中，0x188E2 是 462-byte 擁有區段內的 NOTYPE/size0 符號；checker 只比對此處 76-byte 與 19160 的 30-byte 原始碼片段，不能推出整個 ELF 來源或實際已安裝韌體身分。

預設只查中繼資料，兩個 actual-read 旗標皆為 false：

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin --image-elf /absolute/ADDRESS-WITNESS-ONLY.elf
```

明示原始 FW 時要求整檔 SHA256=`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`、長度 76800，讀回新範圍 106 bytes／37 列及既有 callback 364 bytes。五個反例直接翻轉實際位元組，保持指令類型及其他欄位，只改分支目的、遮罩、SP 還原量、MMIO offset 或 store 來源暫存器；均必須被來源契約拒絕。沒有執行這些反例或重跑舊 94-case 矩陣。

ADC／reset 的語意名稱仍是位址與呼叫脈絡的推論；板上晶片、實際副作用及硬體成功均未證實。下一個未封閉來源是 `0x19896→0x1892E`，不是整條 ADC 呼叫鏈已完成。config word52 的 callback 後生命期、完整 ABI、BLE OTA、BOOT、實體相容性與可刷寫性仍未證實。
