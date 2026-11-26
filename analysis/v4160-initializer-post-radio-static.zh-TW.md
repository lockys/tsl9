# v4.1.60：initializer 後段清零、尾跳與六個bytes搬移

接續 [非 magic 服務與 setter](v4160-nonmagic-service-static.zh-TW.md)，本輪從前面 RF 呼叫鏈**條件式正常返回**的位置，接通 initializer 剩餘兩個小callee與尾跳，將保存證據推到新函式的第一個範圍helper呼叫前。這不代表等待已實際完成，也不代表initializer已回到gate／primary的發布流程。

程式：[check_v4160_initializer_post_radio_static.py](check_v4160_initializer_post_radio_static.py)。證據：[v4160-initializer-post-radio-static.json](v4160-initializer-post-radio-static.json)。只核對原bytes、operands／CFG、既有provider合約與byte區間等式；不執行或模擬目標ISA、RAM、MMIO、fill／copy或裝置。C重建覆蓋率不變。

## 完整小本體與新的截止點

| 項目 | V131起點 | V140起點 | bytes／指令 |
|---|---|---|---:|
| fill wrapper | `57ac4` | `57c04` | 20／6 |
| clear leaf | `63704` | `637ee` | 18／5 |
| tail wrapper | `5e758` | `5e842` | 20／5 |
| 新函式入口前綴 | `53868` | `53916` | 50／17 |

三個小本體完整，入口前綴則只核對到包含第一個新call operand的50 bytes，語意截止在call執行之前。所有列出的指令均有operand guards；完整426-byte initializer作為既有caller證據重用。

令B為 `200033b8／20003408`，F為前輪設定基址 `200031ec／2000323c`。前輪第一個後續call在initializer+388，若它按前輪明示的magic／非magic、等待退出、mapping與frame保存條件正常返回，link就是initializer+392。接下來本機順序為：

1. +392呼叫fill wrapper。
2. +396呼叫clear leaf。
3. +400..406載回S0／RA／S1／S2，+408將SP加16。
4. +410以JAL X0尾跳tail wrapper。

此路徑不經另外兩段前置分支可達的尺寸fallback code。initializer本身仍沒有普通RET。

## fill wrapper：28-byte清零的返回鏈

wrapper重新形成 `(A0,A1,A2)=(B+156,0,28)`，不依賴前一callee留下的參數。AUIPC T1／JALR X0將控制尾交給 `2000039c`，沒有新增RA link或建立frame。

重用既有46-byte fill原指令合約，並核對候選first-copy來源與pointer身分。當實際RAM code相符、所需存取正常且無不利MMIO／FENCE.I／非同步干擾時，28次byte writes清除半開區間 **`[B+156,B+184)`**，正常返回A0為B+184，即 `20003470／200034c0`。

fill只定義A0／A4／A5；因此wrapper傳入的initializer返回鏈與所需S／SP保存條件可以接回。這裡的CPU control snapshot寫回仍不能當作硬體完成證據。

## clear leaf 與 tail wrapper

clear leaf只定義A5，順序SW0到B+196、SB0到B+192，然後普通RET；不改A0。tail wrapper也只定義A5，順序SB0到B+200、SW0到B+204，然後尾跳 `53868／53916`。

這些目的與fill範圍都位於B296之內；另逐一核對它們與F96、ctx count／capacity／gate、table pointer／table、名義node及task bytes分離。

尤其，**B+193與B+201不被改寫**。它們是早前initializer將同一fresh來源byte存入的兩個位置，不能把「清B+192／B+200」擴大解讀成清除鄰接byte。這裡保留的是原取樣欄位，不是重新宣稱目前F來源仍具有相同值。

## 六個bytes搬移與frame交接

到達 `53868／53916` 時，initializer自己的16-byte frame已釋放。新函式再配置32-byte frame，保存RA／S0／S1／S2／S3，並將S1設為`4000`十六進位。

第一個mapped copy呼叫要求：

| 參數 | 值 |
|---|---|
| A0目的 | B+232，即 `200034a0／200034f0` |
| A1來源 | F+24，即 `20003204／20003254` |
| A2長度 | 6 |
| 呼叫目標 | `20000332` |

重用既有58-byte copy完整合約，核對候選first-copy來源與固定目標。來源與目的六個bytes區間不重疊；目的也不碰B+193／B+201或上述metadata。copy按source+0..5的順序取樣並寫入destination+0..5，沒有原子snapshot保證。

copy只定義A3／A4／A5／A6，**保留A0／A1／A2**；這與會推進A0的fill不同。它也不改S1，因此返回後的新函式可用S1−1形成A1=`3fff`，再設A0=0。

| 版本 | 語意截止call PC | 目標 | 實參 |
|---|---|---|---|
| V131 | `53896` | `43e8e` | A0=0、A1=16383 |
| V140 | `53944` | `43f1a` | 同上 |

截止時新32-byte frame仍在，尚未證明目標helper或後面的重試／比較流程返回。沒有把tail wrapper跳到新函式，誤記成initializer已返回gate或primary。

## setter caller 的有限模板搜尋

本輪另在原APP的每2-byte位置，檢查指定4-byte encodings：標準LW immediate572，以及標準ADDI immediate572或520。這些涵蓋部分以`40000+572`或`40034+520`形成setter表槽`4023c`的常見模板，結果均為零候選。

scanner另有三個正例fixture，確認每種指定encoding能被辨識。零候選只適用於這三個模板；沒有推導實際base，也不涵蓋其他rebasing、GP、傳入base、計算index、長距離／非相鄰定義、memory-derived地址或跨函式資料流。因此本輪仍未證明實際APP setter caller或其執行順序。

## 可重現檢查與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_initializer_post_radio_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_initializer_post_radio_static.py
```

核對原APP、SDK、兩份候選及既有證據鏈，一般與`-O`要求ledger逐bytes一致；兩版共66個逐指令operand mutations均被拒絕。另核對caller links、尾跳不新增RA、provider保存集合、28／6-byte界線與APP模板正例。

下一步展開 `43e8e／43f1a` 及後續helper，追查新函式的重試與返回條件；實際setter caller、RAM provider保存、硬體完成及物件保存期仍待釐清。
