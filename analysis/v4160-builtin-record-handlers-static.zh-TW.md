# v4.1.60：兩種內建 record handler 的參數、清除與事件返回

日期：2026-11-26。承接 [post-config 註冊表](v4160-post-config-static.zh-TW.md)，展開其中literal0／literal1指向的兩種handler。前輪的 [回覆保存期](v4160-callback-reply-lifetime-static.zh-TW.md) 等既有證據仍重新驗證。[檢查器](check_v4160_builtin_record_handlers_static.py)／[ledger](v4160-builtin-record-handlers-static.json) 保存完整原指令、獨立operand guards、條件性CFG與回覆代數。

**兩種handler都有低16-bit掃描，但callback的空值檢查與清除條件不同。第一種在呼叫後重讀另一個record的+8欄位；第二種的一般分支直接呼叫record pointer，正常返回就清兩個word。第二種還優先處理bit15。** 這些是入口函式的靜態合約，未證外層dispatcher實際選用它們或傳入何種group／events。

全程離線讀檔、解碼與主機整數代數，沒有執行或模擬 target ISA、scheduler、record arena、queue、allocator、callback或provider。C重建覆蓋率未增加，原BIN與既有分析未改寫。

## 四個完整本體

range終點不含；每版本兩個130-byte本體。

| 候選／種類 | range | instructions | SHA-256 |
| --- | --- | ---: | --- |
| V1.31 literal0 | `432a4..43326` | 53 | `089d8b189f02f55d102f1dff78ed529c0466ed9b61a01159f8501835bf7d3f8a` |
| V1.40 literal0 | `43330..433b2` | 53 | `e7837a4729174d7691c7098e7feec36aa60651a6a8888a7e31ebf16588ce44f1` |
| V1.31 literal1 | `43326..433a8` | 51 | `4bbf8181a2860d9178a85965cf08dbe0964ffe2bff674f906965efdb2def911c` |
| V1.40 literal1 | `433b2..43434` | 51 | `fb4383055ffeee8c01e8f3867bb8391a4c39f881a6396f75920dba3a63a14220` |

共 **520 bytes／208 instructions／28個靜態store位置**。全部指令逐項核對opcode／operands／target，另核對完整hash、store census、GPR writes與scan SCC。新增標準SRA、signed BGE、compressed SRAI／XOR；沿用固定APP／carrier／SDK header、LLVM來源hash／Git blobs及28 vectors的條件性ISA解讀。signed BGE在共用CFG中只換成雙successor標記來算拓撲，原signed operands另有guard。

## 外層handler表與record arena不同

post-config在非零allocation正常路徑依序存入 `[literal0,literal1,literal1]`；它本身沒有呼叫這些handler。它使用fresh count與table pointer，所以不能由這三個store自動推定實際IDs固定0／1／2。

| 角色 | V1.31 pointer slot | V1.40 pointer slot |
| --- | --- | --- |
| record arena P | `2000322c` | `2000327c` |
| 外層handler table T | `200031c4` | `20003214` |

本輪handler根據arena pointer slot載入的base，從12-byte record讀出下一層callback；並非從T pointer slot再取literal handler。兩個pointer storage slots不同，不代表live pointer值必然不同或實際範圍不重疊。

下文以g命名完整入口A0，以E命名完整入口A1；g只是位址算式的名稱，未證上游實參域。若選中bit k，兩種handler都形成：

```text
R = (fresh P + 12*((g<<4)+k)) & 0xffffffff
callback_word = U32[R+0]
argument_word = U32[R+4]
```

所有shift／add／multiply按RV32寬度；本機沒有group、arena容量、pointer有效性或ownership guard。JALR會清target bit0，原pointer的非零測試也不是完整function-pointer驗證。

若對應post-config資料保持適用，其576-byte prefix可算成3組×16筆×12 bytes。這只說明名義佈局；不證明g必在0..2、arena實際有效、容量或外層dispatch已完成。

## literal0：可選callback與fresh flag條件

full E=0時，直接A0=E、RET，不建立frame。否則建立48-byte frame，保存RA／S0／S1／S2／S3，從k=0掃到15，找第一個low16 set bit。使用算術右移再AND1，不會把原event word的高16 bits截掉。

命中後保存R至S2、one-hot低16mask至S1、global base至S3，fresh讀callback word：

- raw callback word=0：跳過argument讀取與call，仍進入後段flag判斷。
- raw callback word非零：fresh讀R+4至A0，將完整E spill到SP+12，JALR callback；正常返回後fresh reload該word至A1。

call邊界A0為argument word，A1為full E；其他ambient暫存器也可被callee觀察，不能假設callee僅看A0。scalar A0 reply不作本機判斷；callback的記憶體或保存副作用仍會影響後續。

### flag檢查不是必然來自同一筆record

呼叫後（或raw callback=0路徑）重新讀arena pointer得P′，再讀：

```text
flag_address = (P′ + 12*k + 8) & 0xffffffff
```

**此算式沒有16*g項。** 不能改寫為無條件讀U32[R+8]。只有特定group／pointer保存關係成立時兩者才相同。

fresh flag=0才依序SW zero至 **then-live S2+0、S2+4**；flag非零則保留這兩個word。S2等同最初R、S3仍為global base、k保持原index等，皆需callee保存及無不利alias／外部介入。

它不清record+8，也不釋放arena。正常回覆以保存／重讀的E XOR low16(1<<k)形成，從已set的bit清掉一位；每次最多處理一個bit。

full E非零但low16全零時，掃滿16次、mask=0，返回原full E。這不是全32-bit掃描；高16 bits會在所需保存前提下留在返回值中。

每版本有8個store位置：5個frame saves、1個E spill、2個record clears。唯一scan SCC為相對入口offsets `18,22,24,116,118`；opaque callback可能不返回，不由這個有限scan保證整個handler終止。

## literal1：bit15優先與一般record分支

此handler先建立16-byte frame並保存RA／S0／S1／S2，即使E=0也有frame stores。它將E存S0，另作SLLI16／SRAI16再signed比較；這精確測試的是 **原bit15**，不是原bit31。

### bit15 set

bit15有優先權，即使其他較低bits也set，仍先走這條路徑：

1. 以未被本體改寫的入口A0=g，直接呼叫 `2000028c`；其他ambient參數仍可見。
2. 其A0回覆非零才直接呼叫 `431ba`（V1.31）／`43246`（V1.40），A0仍為該非零回覆。
3. 不論第一個callee回零或非零，若後續正常返回且S0等context保持適用，返回 full E XOR `8000`。

固定SDK header將 `tmos_msg_receive` 定於JT14／slot4006c，兩份slot值均為2000028c；`tmos_msg_deallocate` 為JT13／slot40068，值正好是上列兩個flash targets。AUIPC/JALR與compressed JAL的數值target均另驗證。receive的first-copy來源可映到V1.31 `404fc`／V1.40 `4053c`，本輪只固定其16-byte prefix provenance，**未展開完整callee效果或證明實機綁定**。

第二個callee的scalar reply不檢查，不能把bit15被切換視作接收／釋放成功的收據。這個分支不掃其他bits，也沒有證明所接指標與record arena或callback payload具相同ownership。

### bit15 clear

full E=0則走epilogue返回0。其餘從low16找第一個set bit；因bit15已排除，實際命中只能是0..14。high-only E仍會掃滿16次並返回不變。

一般record分支先讀R+0至A5、R+4至A0，接著直接JALR A5，**兩個load與call之間沒有null guard**。入口A1仍是full E，A2明示為16；其他register仍可能被callee使用。這不保證target有效或會返回。

callback若正常返回，依序SW zero至then-live S2+0、S2+4，沒有literal0的fresh P′／flag+8判斷。scalar A0 reply被忽略。回覆採保存的S0 XOR S1，所以不依賴callback後live A1，但仍需S0／S1／S2／SP／saved frame與code完整。

每版本6個store位置：4個frame saves、2個record clears。唯一scan SCC相對offsets為 `60,64,66,120,122`。clear發生在callback返回後；本輪未證重入或並行安全，也不把兩個word clears當作整筆12-byte record清零。

## 可確認與仍未知的界線

兩種handler都只回傳剩餘event mask的編碼結果；本輪沒有執行scheduler或建立record memory model。它們間接call的pointer／argument來自可改變的arena，callee正常返回、S/SP保存、frame／arena／global slots不互相破壞，以及外部writer皆仍是前提。

本輪確認literal指向何種完整函式與其入口合約；**沒有確認外層T dispatcher何時取出literal、實際g／E值、事件送達或固定task ID**。P／P′也不必然相同；clear的then-live S2需要獨立保存證據。任意callback或receive/free仍有未解析effects。

## 重播結果

```text
python analysis/check_v4160_builtin_record_handlers_static.py
python -O analysis/check_v4160_builtin_record_handlers_static.py
```

兩模式均實際輸出：

```text
PASS: 65536 lowest-bit masks; 196608 sign/high-bit cases; 48 group/record identities; 12 specified raw mutations
PASS: 4 complete handlers, 520 bytes/208 instructions/28 stores; pool/table distinction; conditional callback cleanup
PASS: exact ledger replay; slot aliases and bit15 priority; actual dispatch/ownership UNPROVED; NO target execution
```

lowest-bit cases窮舉U16的XOR／清bit恆等式；sign/high-bit cases為全部low16×三種high16模式；48筆geometry是g=0..2、k=0..15的主機位址關係，不是合法record或runtime事件的窮舉。

十二個raw mutations改零事件分支、arena slot offset、callback null branch／argument offset、flag offset、clear offset、XOR operand、bit15 shift／receive判斷、第二種callback read／clear／XOR；每個都需命中特定semantic guard，不以完整hash不符或任意exception代替。

預設只讀重算並精確比對JSON；`--write`只建立不存在的ledger。重播需十四個已發布Python dependency模組，本機固定APP、兩份carrier、SDK header及LLVM來源／vectors；candidate輸入未隨本次發布，僅clone repo不足以重跑。

後續可沿外層handler表的消費者、arena record producers及receive/free繼續追查實參與ownership；actual installed provider、最終RAM內容及硬體／外部writer條件仍保留未知。
