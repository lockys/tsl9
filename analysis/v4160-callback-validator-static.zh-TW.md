# v4.1.60 callback descriptor setup：ID 與第二條鏈表

本輪展開候選 resident V131 `0x4ce22`、V140 `0x4ceba` 各 256 bytes／100 instructions，合計 **512 bytes／200 instructions**。兩段都完整對回原始 sparse HEX，且逐指令固定 operands、分支、呼叫與返回；這是條件性靜態合約，未執行目標程式或模擬 RAM／heap／provider。未增加既有 C 重建覆蓋率，也未證明實際 installed provider。

可重播證據：[檢查器](check_v4160_callback_validator_static.py)、[固定證據帳本](v4160-callback-validator-static.json)。上游見 [callback writers](v4160-callback-list-writers-static.zh-TW.md)，初始化來源見 [ID11 outer tail](v4160-id11-outer-tail-static.zh-TW.md)。

## 入口、驗證與錯誤返回

入口 A0 是 descriptor D，內容為 D+0 的 U16 count、D+2 的 byte parameter、D+4 的 config pointer。函式沒有對 D 做 null 檢查。D+3 未被本函式的載入指令直接讀取，但包含在後述 8-byte provider copy 內；上游 descriptor 未給該 byte 指定值。

1. 首次讀取 count N0；N0=0 直接返回 2，尚未建立 stack frame。
2. 保存 config pointer Q，讀取 Q+0 byte 與 Q+4 word，以 `(ROM reference, 2, Q4, Q0)` 呼叫 matcher；V131 為 `0x44624`，V140 為 `0x446b8`。第一次返回 0 才重讀 Q0／Q4，換第二個 ROM reference 再呼叫；兩次均為 0 返回 2。非零返回的具體語意尚未展開。
3. 重新讀取 D+2，檢查 `((byte-7)&255)<=9`，只接受 7..16，否則返回 24。
4. 讀取 U16 counter K1；K1=0 返回 1。再讀取 count N1；若 `K1+N1>65536` 返回 1。原指令是有號比較，但兩個輸入零擴展後的總和不超過 131070，故此處不會因 signedness 改變判定。**總和恰好 65536 被接受**。
5. 透過 `0x20000040` 請求 12 bytes、tag `0x4702`；null 返回 19。接著呼叫 `0x2000039c(node,0,12)`，忽略其返回值。

原 A3 在 matcher 前被 Q0 覆蓋；這裡沒有把上游原 A3 callback 物件寫入另一物件 callback 欄位的直接 store。S-register、frame 及外部 callee 的保存行為仍是串接前提。

## ID 寫入與 counter 的第二次快照

fill 返回後，重新讀取 D0 為 N2，重新讀取 counter 為 K2；**N0、N1、N2 及 K1、K2 分別保留，沒有假設跨呼叫不變**。不會重新執行 N1/K1 的範圍檢查。

對 i=0..N2-1，迴圈每次重讀 D4，向 `fresh_config_pointer + 16*i + 10` 寫入 `low16(K2+i)`。這個迴圈沒有呼叫；N2 為 U16，因此索引迴圈本身有界，但 config 配置長度、每次 pointer 一致性、可寫範圍及無別名仍未由此證明。

N2>0 才將 counter 更新為 `low16(K2+N2)`；N2=0 不寫任何記錄 ID 或 counter，仍繼續發布節點。若所有快照一致，K1=1、N1=65535 是被接受的邊界，最後 counter 會變成 0；下一次呼叫的 K1=0 檢查則返回 1。這是算術條件，並非已觀察到的實際資料域。

## 第二條鏈表發布與外層部分成功

函式先寫 node+0=0，再透過 `0x20000332(node+4,D,8)` 複製 descriptor。若 provider 履行普通 byte-copy 合約，node+4 保存 descriptor 前四 bytes，**node+8 保存 D4 的 config pointer，並非上游原 A3 callback 物件**。

第二條鏈表 head 為 V131 `0x20002f88`／V140 `0x20002fd8`。空鏈表直接發布 head，非空則沿 node+0 找首個 null next 後接入，正常返回 0。遍歷沒有 count／cycle guard；有效、有限、無不利別名的鏈表及節點是返回前提。本函式沒有 free、rollback 或兩條鏈表的原子發布。

上游 append 在此返回 0 後仍可能出現：

- 原 A3=null：返回 0，但不建立主 callback 節點。
- fresh config+10=0：返回 2。
- 主節點配置失敗：返回 19。

上述情形發生時，第二條鏈表可能已發布。主節點的 node+8 原 A3 保存，與本函式第二條鏈表 node+8 config 保存，是不同合約。

已知 ID11 初始化直接把 counter 設為 1。若已知 wrapper 的 count=4、parameter=16、所有 fresh 來源與欄位跨呼叫保持、matcher 接受、配置／copy／鏈表存取正常，四個記錄在 config offsets 10、26、42、58 得到 ID 1、2、3、4，counter 變為 5，主 callback 節點 key 為首筆 config+10 的 1。這只是明確列出前提的串接例子，不是 runtime 綁定證據。在這個固定四筆且無別名的例子，ID store 區間不與 callback 物件的 +8 欄位重疊；不能泛化為所有 count 或所有 pointer。

## ROM reference 的來源界線

matcher 使用 V131 `0x6ea90`／`0x6ea9c`、V140 `0x6ec80`／`0x6ec8c`。這些地址超出 dense 候選 BIN 結尾，但原始 sparse HEX **有部分 bytes，亦有缺口**。帳本對每個地址保留 12-byte 診斷窗口，缺失 byte 記為 null，不補零；12 bytes 不是已證明的 table 範圍。

| 窗口 | 原始捕捉的 bytes（`??` 表示未捕捉） |
| --- | --- |
| 第一個 reference，兩版本相同 | `00 28 ?? ?? c9 2a ?? ?? 03 2a ?? ??` |
| 第二個 reference，V131 | `01 28 ?? ?? 05 2a ?? ?? 56 91 04 00` |
| 第二個 reference，V140 | `01 28 ?? ?? 05 2a ?? ?? ee 91 04 00` |

不能據此宣稱 table 完整、辨識 table 結構或推定 matcher 必定成功；也不能把 dense BIN 之外一概視為原始 HEX 缺失。

## 重播與尚未證明項目

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_callback_validator_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_callback_validator_static.py
```

檢查器固定原始影像身份、兩版本完整指令與原始 HEX backing，檢查 CFG／不可變路徑憑證，拒絕 200 個 instruction mutations 與 4 個 typed-load mutations，核對完整 U16 counter 域及 count／stride／wrap／frame 界線，最後逐 byte 重播 JSON 帳本。所有既有依賴一併重算，無目標執行、mutable target state、硬體或服務呼叫。

下一個可離線展開的缺口是 matcher 本體與部分 ROM reference 的用途、callback 物件 +8 欄位的其他 writers，以及 config／物件／鏈表的實際配置、provider 綁定和指標保存期。現有證據不保證 IRQ／DMA／重入下的保存、完整外層初始化成功或可用韌體。
