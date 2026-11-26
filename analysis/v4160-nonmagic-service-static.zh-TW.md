# v4.1.60：非 magic 服務、六個來源欄位與 magic setter

接續 [magic 路徑與後續 leaves](v4160-post-rf-leaves-static.zh-TW.md)，本輪將大型callee的三次服務呼叫，接到first-copy中的完整輪詢helper，核對非magic路徑的六個byte來源，並找到可產生magic的SDK setter。這提供候選來源及條件式返回合約，仍未證明APP實際呼叫setter的順序或provider已安裝。

程式：[check_v4160_nonmagic_service_static.py](check_v4160_nonmagic_service_static.py)。證據：[v4160-nonmagic-service-static.json](v4160-nonmagic-service-static.json)。只核對原bytes、operands／CFG／重定位、區間及整數等式；不執行或模擬ISA、RAM、MMIO、服務或裝置。C重建覆蓋率不變。

## 服務的完整來源與映射

| 版本 | 候選flash範圍 | first-copy後RAM範圍 |
|---|---|---|
| V131 | `43062..43098` | `20002df2..20002e28` |
| V140 | `430ee..43124` | `20002e3e..20002e74` |

右端不含。兩版均54 bytes／16指令，全部位於各自既有first-copy範圍內。程式分別在flash與RAM座標解碼，核對原bytes相同、branch相對offset與全部operands一致。三組AUIPC／JALR的實際靜態目標均為該版RAM入口。

緊鄰的flash `43098／43124` 是另一個JAL stub，並非本helper的一部分；本輪沒有跨入該stub或後面的ECALL。來源映射合約仍需要實際RAM保留相同code，不能僅由候選bytes斷言目前installed內容。

## 輪詢合約：兩份fresh狀態，三種退出

令R0為入口fresh `U32[2000353c／2000358c]`，Q0為另一個fresh `U32[20003590／200035e0]`。當它們分別保持 `40024200`／`40025000` 時：

1. +14對R0+100寫 **6000十進位，即1770十六進位**。這只固定CPU寫入資料，不指定時間單位。
2. +24 fresh讀Q0+144為V1。左移5後作signed BGE zero，相當於檢查原V1.bit26是否為0。
3. 只有V1.bit26為1，+36才再次fresh讀Q0+144為V2。左移6後的signed BLT zero，檢查的是這份V2.bit25。

| 狀態條件 | 後續 |
|---|---|
| V1.bit26=1且V2.bit25=1 | 直接RET，不讀R control |
| V1.bit26=0 | 不讀V2，改fresh讀R0+100 |
| V1.bit26=1且V2.bit25=0 | 改fresh讀R0+100 |

後兩種情況，R值為0才RET，非0則回+24。V1／V2是兩次不同取樣，不能合併成同一word的雙bit測試。helper只定義A2..A5，沒有frame、callee或RA／SP／GP／S／A0／A1定義。

唯一循環SCC為offsets `24,28,32,36,40,44,48,50`；loop不重載Q／R指標槽，也沒有store、軟體countdown或timeout。每輪未滿足雙取樣bit條件、R又一直非零時，CFG容許永久等待。初始SW6000不證明硬體會遞減或終會清零。

## 非 magic 路徑的三次呼叫與六個bytes

大型callee `6645c／6659a` 的完整340-byte／117指令前綴全部逐指令核對。fresh magic不等於 `12345678` 時，由+116續行至+120，三次呼叫分別位於JALR offsets `160,226,302`。

若每次helper都在所需mapping／正常存取／無不利干擾及等待退出前提下返回，則它保存large所需S registers、SP與frame。每次返回後重新取Q，分別fresh讀Q+144與Q+148，依序發布六個bytes：

| 呼叫offset | `fresh U32[Q+144]&63`目的 | `(fresh U32[Q+148]>>10)&127`目的 |
|---:|---|---|
| 160 | `20002fa6` | `20002fa7` |
| 226 | `20003595` | `2000358c` |
| 302 | `20003594` | `20003584` |

上表為V131，V140地址全部加`0x50`。每一個fresh來源都是各自的原指令取樣，沒有原子snapshot保證；兩種資料範圍分別為0..63及0..127，均可存入byte。

這六個固定byte目的，另與前輪B296、ctx metadata、table／node／task、所需pointer槽及本helper的RAM code範圍核對分離。前綴自己的SP+12保存來源地址；helper不改該frame，首次返回後才載回以完成第二個byte store。

第三組發布之後，非magic路徑接到+340的既有共同組裝段，沿用前輪A5穩定基址、frame／scratch分離與普通RET證據。非magic路徑不消費magic word。三次服務等待都完成、來源／mapping／frame保留且無不利MMIO／非同步作用時，可建立large的條件式返回，A0回覆仍opaque。外層tail尚須後續wait leaf實際退出。

## SDK setter：一個已定位的magic producer

原SDK header將 `RFEND_TXCtuneSet` 定義為 `bStatus_t (*)(uint8_t *pParm)`、`BLE_LIB_JT(130)`；固定槽運算為 `40034+130*4=4023c`。兩份候選該槽的word分別指向：

| V131 | V140 | bytes／指令 |
|---|---|---:|
| `663a6..66412` | `664e4..66550` | 108／36 |

setter的完整本機CFG無環，沒有frame／callee，也不定義RA／SP／GP／S registers。

| 輸入條件 | 行為 | A0返回 |
|---|---|---:|
| pointer=0 | 不讀來源、不store | 1 |
| 非零pointer，初次source byte0不等於6 | 不store | 1 |
| tag6，已載入byte1／byte2都非零 | 寫六個bytes，再寫magic=`12345678` | 0 |
| tag6，已載入byte1或byte2為零 | 寫同六個bytes，再寫magic=0 | 0 |

接受tag6後，source bytes1..6依序寫至V131地址 `20002fa6,20002fa7,20003594,20003584,20003595,2000358c`；V140全部加`0x50`。magic目的為 `20003588／200035d8`。

source bytes1／2在任何store之前已載入A2／A3，直到magic判斷均未改變。因而marker判斷使用的是這兩個已載入值；後面的source4..6是較晚fresh reads，若來源與目的alias，不能假定它們仍等於入口時的內容。原指令沒有額外buffer length／pointer範圍檢查，本輪結論以所需來源存取有效為前提。

## 有限encoding候選清單的界線

在APP與兩份候選檔，每2-byte位置只掃描指定4-byte encodings：標準SW且immediate為1416／1496，以及LUI `12345000`。

* APP未出現這些指定候選。
* 每份候選的SW清單只有setter兩個magic stores，以及large的magic消費清零。
* 每份候選的LUI清單只有setter形成常數及large比較常數兩處。

這是指定encoding／對齊的候選清單，可能包括data或重疊解碼，並非完整有效地址或可達writer分析。它不排除GP、重設base、pointer-derived writes、copy／fill、間接或非同步寫入、其他映像等來源。固定SDK槽證明有這個候選producer，沒有證明APP曾呼叫它，更沒有證明它在第一次large入口前執行。

## 可重現檢查與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_nonmagic_service_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_nonmagic_service_static.py
```

核對原APP、SDK、兩份候選及既有證據鏈，一般與`-O`均要求ledger逐bytes一致。兩版合計370個逐指令operand mutations均被拒絕；另檢查兩個PC座標重定位、精確poll SCC／繼續等待的循環、65,536個high-half signed-shift案例及65,536組byte1／byte2 marker條件（65025組非零marker、511組清零），以及固定目的區間。

下一步追查setter的實際caller與執行順序、所需RAM保存及等待進度；initializer其他callees／tail、實際provider與後續物件保存期仍待釐清。
