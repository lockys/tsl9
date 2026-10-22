# BOOT ID2580 的 W 數值界線

[English](readme.en.md)

這是對實際 BOOT ID2580 原檔的離線靜態重讀，不以 command-adapter README 當作 guard 證明。固定原檔SHA256為 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`，12,288B，analysis base1000、檔案結束4000。選定命令本體21BE..235C為414B／144條指令，SHA256 `44702abb50c4489f378bb1036d8cf949817301e2e07d8af8434f7d6e119438d5`。

新checker從明確傳入的BIN重新解碼全部144條，對照已封存的原始bytes／順序，另檢查18列page guard operands、W／E控制流與5個新單欄位raw反例。舊18反例與HOST／Flash engine矩陣未重跑。scope額外只讀排程目標20E2的4B：LUI T1,8000；JR T1，沒有擴大BOOT／ROM分析。

## 原始位元組支持什麼

W先LBU liveGP+139 active、檢查完整長度1026；2210先讀payload+1低byte，2214後讀payload高byte。221C..2232透過位移／OR／低16截斷組成BE16頁號p。

| 指令位置 | 實際欄位／數值 |
|---|---|
| 2218 | LUI A4=`F7FF8000` |
| 222A／222E | A5=`20000+32=20020` |
| 2234／2236 | S0=`(p+20020)<<10`，即初始destination=`08008000+p×400` |
| 2238／223C | A5=`18000-100=17F00` |
| 223A | A4=`(destination+F7FF8000) mod2^32`，對原u16頁號等於p×400 |
| 2240 | **BLTU A5,A4→21E2**：offset大於17F00時拒絕 |

所以guard接受 **unsigned頁號0..95**；96的offset18000已被拒絕。這是從已核對operand得出的整數代數，不是CPU執行或指令模擬。原BE16範圍內destination不溢位，界線可直接化為 `p<=floor(17F00/400)=95`。

| 範圍 | 數值結果 |
|---|---|
| BOOT接受的初始頁面 | 96頁／98,304B，低位址8000..20000；Flash alias08008000..08020000 |
| 最後頁95 | destination0801FC00；四個256B quarter的最後起點0801FF00，完整頁結束08020000 |
| 原Runtime ID2966 | SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；76,800B=75頁，base8000、檔案EOF1AC00 |
| 超過目前Runtime EOF的guard數值區間 | 頁75..95，共21頁／21,504B（5400），低位址1AC00..20000／Flash alias0801AC00..08020000 |

**21頁不是free Flash。** 兩份BIN的file extent不是完整實體Flash佔用圖；guard常數不能測得Flash容量、NV／metadata保留區或其他root policy。以上也不是增加檔案長度、填入新程式或覆寫該區的授權／安全證明。

## 本體的寫入／驗證／結束限制

- 2256從4004C讀target，非對齊時225E間接call做對齊搬移。重疊copy與resident行為未證。
- 2272呼叫20E6；S2 offset在call前增加256，返回後比較live S2／S4。因此四次256B與後續有效位址需要相關callee正常返回及保存條件，guard不是所有可能opaque／非同步變更後的全域寫入上限。
- 2282先讀Flash32，2288後讀live RAM32；首個不符在228A轉epilogue，沒有Runtime FF／full-page echo。相符將A2/A3=0，tail到2AA0要求empty W reply；不等於實際BLE ACK已送達。
- 選定E段只有active讀取與判斷，清active後排192C／200、20E2／400，最後empty E tail。沒有在這段讀incoming payload／length／UID或整份image completion狀態。4B的20E2只證明數值跳8000，不能證明排程會執行、Flash alias、啟動環境或原機可用性。

這些原始局部控制流**未建立whole-image CRC／簽章／頁收齊驗證**。不能擴張成整個BOOT沒有upstream frame checks、metadata／root檢查；未在本scope重建它們，也未證實原機安裝這份ID2580。原機BOOT身分、實際Flash／NV所有權、MCU／resident、更新中斷復原與完整OTA仍未知。

## 可重跑介面

```sh
# 僅封存metadata／數值推導，不讀兩份BIN、不跑raw controls
python3 -B check.py --project-root ROOT

# 兩個檔案flag必須一起提供；實際讀BOOT與Runtime並跑5個raw controls
python3 -B check.py --project-root ROOT --boot ID2580.bin --firmware ID2966.bin
```

預設 `metadata_only=true`、`actual_BOOT_read=false`、`actual_Runtime_read=false`；明確提供兩檔才為false／true／true。checker同時辨識工作版 `apk-analysis/tsl9-` 與交付版 `analysis/` 的既有證據位置，不需要W歷史build。沒有編譯／HOST、原生執行、ISA／ESIL步進、硬體、網路、UID／VIN傳輸或新BIN。
