# v4.1.60 `0x171de` 原指令、兩個槽位與 fresh reads

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批離線執行 `[0x171de,0x172b6)`、三個 getter 及原 `0xb6f4` 呼叫邊；所有資料及 provider target 均為合成 fixture，不操作設備。

## 原 getter 與 mode 15 guard

入口 frame=16 bytes，依序保存 RA／S0／S1 至 caller_SP−4／−8／−12。三個 getter 都只讀 byte 至 A0，其餘暫存器與記憶體保持：

| 原函式 | 來源 |
|---|---|
| `0x8440` | `U8[GP+364]` |
| `0xabf2` | `U8[0x2000bee0]` |
| `0x9fc2` | `U8[GP+172]` |

`0x8440` 返回零即恢復 frame 返回 A0=0，不讀 config。非零時讀 `[GP+84]` 指標，再讀 config+3 低 nibble；只有第一次低 nibble=15 才走額外 guard：

1. `0xabf2` 返回零：繼續。
2. 返回非零：重讀 config 指標及 config+8；bit4清除則返回，A0保留該 getter byte。
3. bit4設定：執行 `0x9fc2`，零則返回0，非零才繼續。

繼續時**重新讀 pointer／config+3**。第二次低 nibble=15才改成 N=1；第一次的 mode15 guard 不能套在第二次讀值上。256組 scripted read pairs 令兩次 nibble各取0–15，驗證重新讀取；scripted值只屬 fixture，不推論實際並行修改。

## 樣本槽位與第一個服務參數

令 R 為當次 `[0x40038]` target 正常返回的32-bit樣本。入口 RA=`0x17216`、SP=`caller_SP-16`、S0=N、S1=GP+84。A0仍是最後一個 getter byte：一般路徑為 enable byte，額外guard可留下0或GP+172 byte；A1／A2尚未由本函式設定。

| N | base | modulus |
|---|---:|---:|
| 0／1 | 2000 | 1001 |
| 2 | 3000 | 2001 |
| 3–14 | `5000*(N-2)` | 5001 |

原碼先算 `R % modulus`，再 fresh-read pointer及config+4。bit0設定才將餘數加至base，否則丟棄；即使bit0清除，樣本target仍會被呼叫。

令 delay 為所得值，第一個 `[0x40058]` target 入口：

- A0=`U8[GP+365]`、A1=1。
- A2=`floor(delay*1000/625)`，獨立oracle用等價的 `floor(8*delay/5)`。
- RA=`0x17252`、SP=`caller_SP-16`、S0=`delay*1000`、S1=`0x40000`。

在此nibble／餘數域內，delay≤65000，乘1000≤65000000，不發生RV32乘法回繞。65016組原指令餘數案例得到63001個不同A2，最小3200、最大104000；**這是離散輸出集合，不是該區間每個整數都可產生**。每個modulus的全部餘數都執行，但不證明真實provider會產生全部樣本或其分佈。

既有[40038靜態證據](slot-40038-offline/README.md)與[40058算術模型](slot-40058-offline/SCALING.zh-TW.md)已記錄相同來源及公式；本批補上APP原機器碼的有限CPU執行，不將SDK候選視為已安裝provider。

## 第一個服務返回後的第二個 tail

本批可選擇在第一個40058入口停止，或供給明示的正常返回，再執行原後段：

1. 從frame恢復caller S0。
2. **重新讀槽位40058**，不沿用第一次target。
3. 恢復caller RA、S1。
4. **重新讀GP+365 byte**，指定 A1=2、A2=80。
5. 恢復caller SP，尾跳第二個target；本批在其第一條指令前停止。

兩種正常返回前提分開處理：

- 40038樣本：保存S0／S1／SP／GP及全部記憶體；刻意改寫caller-saved暫存器，A0=R。
- 第一個40058：保存S1／SP／GP及已保存frame，明示允許修改40058槽位與GP+365。刻意破壞暫存S0及caller-saved暫存器，並給A0=0／1／`0xffffffff`等指定值；原碼仍恢復caller S0，且不使用該返回A0建立第二次參數。

hook memory writes在trace中標為`hook`，與APP原生stores分開。65536組初始／返回後GP+365 byte組合，以及更換第二個target的fixture，直接驗證fresh-load合約；不宣稱真實provider有這些副作用。兩個槽位的函式體均未執行，保存、返回、身分、單位與實際服務效果仍未證明。

## 原 `0xb6f4` 串接

160組直接沿原call進入 `0x171de`，包含A0=6／7及高位別名`0x101`／`0x10012`：

- 80組171de早返。B6F4後續用**完整S0**判斷≤11或=18；6／7停在`0x9fc8`，高位別名跳過該call，原SB將低byte寫入`0x2000bf0c`並恢復caller，A0=0。相鄰canary保持。
- 40組停第一個40058，兩層frame仍在。
- 40組在明示第一服務返回後停第二個tail target，171de frame已恢復，B6F4 frame仍在，link=`0xb70e`。

`0x9fc8`與第二個target始終不執行；不把入口低byte guard延伸成完整S0比較，也不聲稱B6F4所有後段已完成。

## 重現與結果

```powershell
python analysis/test_v4160_schedule_171de_cpu.py
python -O analysis/test_v4160_schedule_171de_cpu.py
python analysis/test_v4160_zero_id_queue_cpu.py
```

只需標準庫、原APP與既有有限CPU／downstream模組，不需SDK carrier。

```text
PASS: 41472 guard probes; 65016 original remainder cases / 63001 unique outputs; 65536 config-byte pairs; 320 word boundaries; 256 fresh-read pairs; 65536 task reload pairs; 96 reply/slot probes; 16 sample stops; 3 mutations; opaque targets NOT executed
PASS: 160 actual b6f4-to-171de chains; {'return': 80, 'first': 40, 'tail': 40}; 9fc8/second target stopped
```

41472組guard含enable全部byte、六個nibble、三種額外getter／config8／GP172值；另有config3×config4全byte組合、樣本跨1001／2001／5001與MASK邊界、兩次config3讀值不同、16組樣本入口停止，以及96組第一服務返回值／槽位變動。

逐段核對getter保持、參數／link／frame、精確資料reads／native stores／hook stores。三項記憶體複本變異將modulus1001改1000、除數625改624、最後task讀取改到enable欄位；必須由第一呼叫／fresh tail參數斷言抓出，不以解碼失敗充當通過。

原APP未改。共用CPU只新增標準RV32 DIVU／REMU；本callsite分母均為固定非零常數，通用解碼仍採標準除零結果。界外執行、未映射存取、未知指令繼續失敗即停；queue回歸通過。

既有`src/native/receive/rom_driver_family.c`已重建此段C；本批增加條件性原指令與呼叫合約證據，沒有新增重建bytes或重算覆蓋率。仍需追查槽位實際provider、保存／副作用合約及`0x9fc8`後續流程。
