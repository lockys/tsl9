# ID2966：main 與直接 callee 原生整合

最新入口為 `python verify-dependencies.py`。來源固定為 ID2966／伺服器標籤 V4.1.60，76800B，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。這是 C11／C++17 加 RV32 inline assembly 的指令表示，沒有宣稱恢復原始 C 語法、型別或完整韌體。

## 本輪新增的真實本體

| 原入口與半開區間 | bytes | 已確認的本地控制流／限制 |
|---|---:|---|
| main `9008..901A` | 18 | 依序呼叫9250、8180；若返回，還原entry時ra後RET；ROM交接時ra未知 |
| `81B0..81CA` | 26 | 讀取ROM區域的function pointer並間接呼叫；沒有供應ROM本體 |
| `93EE..9410` | 34 | 原MMIO指令；不以數值地址推定實體外設功能 |
| `12BC8..12C24` | 92 | 保留RET後仍可達的分支；恰接舊IRQ入口12C24，無重疊 |
| `18D78..18E1C` | 164 | 保留完整本地CFG及後段可達分支 |
| `18E86..18E90` | 10 | 原store與RET |
| `19272..19282` | 16 | 原輪詢分支與RET；未改成有期限的成功回傳 |
| `19282..19296` | 20 | 19296尾跳所需的相鄰實體leaf，另配置一次 |
| `19296..1929A` | 4 | 尾跳19282，沒有虛構RET或一般呼叫prologue |

新增384B程式，其中main18B、八callee bodies366B。七個原UND入口由section-backed FUNC提供；相鄰19282是另一個真本體。直接呼叫、內部分支與PCREL資料引用均保留semantic relocation。原指令中GP=20004000的約定保持，沒有把每個原始立即數都假命名成資料或函式。

新增的`__tsl9v4160_data_2000c038`是既有35160B NOBITS carrier的section-relative、NOTYPE、size0 view，offset8038；沒有配置新RAM或把數字當資料值。連同原七個views共八個。Reset的靜態指令要求複製128B到20004000..20004080、清零20004080..2000C958；這只描述原指令在其存取成功時的效果，未觀察原機執行，亦不證明後續runtime內容。

## 整合與驗證結果

| 階段／獨立入口 | code | RO | relocs | 該階段明示UND |
|---|---:|---:|---:|---|
| `verify.py` reset | 138 | 128 | 14 | vector、clock、main、ROM |
| `verify-platform.py` clock | 372 | 128 | 21 | vector、main、ROM |
| `verify-vector-platform.py` vectors／IRQ | 1322 | 456 | 211 | main、ROM、七callee |
| `verify-dependencies.py` main／callees | 1706 | 456 | 223 | 8180、9250、ROM40000 |

最新整合26個非空allocated sections、2162B file-backed bytes及同一個35160B NOBITS carrier。所有captured byte在數值配置中對回同版本原地址，舊reset／clock／initializer／vector／handler bytes保持，未重複配置。211筆舊引用加main兩筆及callee十筆，共223。C11與C++17物件及數值witness各自逐byte相同。

驗證包含每個新直接分支／jump的獨立原bits解碼、所有新relocation位置／型別／target、真實FUNC provider、八個同section RAM views與沒有重疊的原始區間。實際修改ELF把main provider變成ABS的反例會由相同provider gate拒絕。Standalone callee audit另拒絕改壞ROM間接call指令、遺漏19296尾跳relocation、錯把LO12_I換成S的反例；詳見其獨立收據。

嚴格最終link仍精確拒絕三個未實作入口，不產最終ELF或BIN。`ADDRESS-WITNESS-ONLY.elf`僅把這三個缺少入口填上原數字，沒有提供程式，禁止當韌體執行或燒錄；它沒有覆蓋九個本輪真provider。

## 仍需追查的執行層

`8180`的已觀察42B loop會讀RAM0 function pointer、呼叫17002及12C58，再把AAAA寫到40003000並跳回。`9250`的已觀察64B呼叫鏈有14個直接call及尾跳17BF6；遠端tail與callee語意尚未閉合。下一輪應增加這些真本體並追其依賴，不能只填入口數字。

整合中至少六處間接呼叫仍依賴runtime pointer；其中本輪81BA取自ROM表slot4007C，12C0C取自另一ROM表slot4004C。兩者都是原LUI／C.LW解出的數值地址，沒有取得slot內容或target本體。前輪四處為84DA、98F8、994C、18744。已觀察但尚未納入元件的8180 loop另含819C間接呼叫。三UND僅是此局部直接依賴數量，不涵蓋這些動態target、initializer raw pointers或整份韌體缺口。

12BC8另以PCREL形成2000C038的資料base，本地迴圈index0..31、stride12，觀察到slot+0的LHU／SH、+2及+11的SB，及傳slot+3為a0。此條件範圍是2000C038..2000C1B8共384B，位於既有carrier中；不等於已恢復原始型別。C038不是12C0C的function pointer來源，兩種引用不可混為一項。

精確MCU／PCB／實體RAM與stack、resident ROM／BOOT、IRQ契約、BLE OTA及ID2966硬體適用性仍未證實；使用者目前無法讀取晶片印字。全部驗證是本機編譯與靜態byte／ELF取證，不執行或模擬RV32、不連線裝置、不刷寫。

證據：`../../analysis/v4160-dependencies-2026-10-20/`（交付後）；其中main-review、callees與integration-review各自保留來源、範圍與限制，最終讀回收據另列目的專案fresh build結果。
