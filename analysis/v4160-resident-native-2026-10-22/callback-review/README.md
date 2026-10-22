# 原 App config field44 → 197F0：完整 source CFG 與局部依賴

[English](readme.en.md)

**197F0的正常call-return原碼範圍是364B／130指令，不只是舊112B前綴。** 其內有13個直接JAL、12個不同App callee，以及一個沒有在本body編入timeout的poll loop。尚未閉合全部callee效果，因此不能把config+52零值、SP／S／GP保存或正常返回延伸到整個callback之後。

確認的是原App設定欄位+44的數值197F0。`tsCB`／temperature名稱只屬先前header order的推論；本輪不把ADC-like數值位址或函式命名當成完整溫度語義證明。

## 實際 byte、range與metadata界線

官方 ID2966 SHA256：`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，base8000。

| 原碼區段 | 本輪範圍／指令 | SHA256 |
|---|---|---|
| Callback entry197F0 |197F0..1995C，364B／130|`ee7d9a35ebc31a363cc5f6efca0ce21d341099694f34aa90185be94995d826a4`|
| 8520限定fast path |8520..854A，42B／17|`98688760c7a23d3f8b23f4b6cdbb0dd285fd8562ff5ba950b5fd46fee5a7ae2d`|
| 19124完整MMIO leaf |19124..19142，30B／12|`ca3d4aef350f5c783ee6eeae7d25ba85b74055551058135024d07edf1804e864`|
| 1908C完整MMIO leaf |1908C..1909E，18B／8|`8a1f8aa217067a65d4a6cfa6420d03b423019f47471c699a98afc65062a01b0a`|

總計454B／167個逐指令欄位，另核對已封存的原App42B欄位44設定片段。19124重用既有IRQ原始source audit，實檔30B相同；沒有重跑舊94指令反例矩陣。

364B範圍由原始instruction partition、13個外部direct call、唯一內部backedge、1995A的RET及1995C的新SP-16 prologue共同界定；callee假設正常回到JAL之後的continuation仍須明示。不是用symbol size猜出來，也不是對任意異常控制流的函式邊界證明。

既有source-backed ELF中，197F0位於 `.text.tsl9v4160.conditional_runtime_197be` 這個548B／AX／PROGBITS owner內，offset50。`__tsl9v4160_conditional_code_197f0`與`__tsl9v4160_address_197f0`皆是真正global NOTYPE、size0；**沒有原FUNC364 metadata證據**。顯式ELF核對只驗這些roles及364B slice，不證明全ELF來源鏈或新native provider。初次使用既有ELF SHA256 `6ab2e06720dc9f9ea4fa531836605fed6d3b8832a7dfa008d76bd9bd0a54f7b2`，public CLI不硬綁此檔案路徑。

## 原主體的 frame、讀寫與回傳

197F0先SP-=128；依序存RA+124、S1+116、S0+120、S2+112至S11+76，共13個word。第一個call的明確參數為A0=當前SP+32、A1=0、A2=32。source沒有保留一般C函式型別或輸入API原型的證據。

接著用新literal40021000讀取+18、+4至S11／S10，再建立S1=40012400並讀+4／8／2C／30／34／0C／10／14至S9..S2，及+18／1C／20／24／28／38存到當前SP+4／8／12／16／20／24。這些全是原32-bit READ請求，沒有取得硬體實際數值。

S0於19858設40012000，後段原碼用live S0+404／408／42C／430／434／40C／410／414／418／41C／420／424／428／438做32-bit寫回；另於198EA重新建立literal40021000，對+18／+4寫回S11／S10。**live S0與保存值已經跨過多個未審callee**，故不能無條件把全部數值目的地或原MMIO狀態還原當成已證明。source也有當前SP範圍內的snapshot與config stores：SW32／36／40／44／48、SB52，以及conversion結果SW28等；它們的安全範圍依賴正常live SP與無alias前提。

198DC call18A66的A0結果存到當前SP+28。1991E重新讀SP+28到A4，19948將其送到A0；這不證明該值的溫度單位或物理意義。RA於19920從live SP+124重新讀取；S1/S2等readback與最後MMIO writes交錯，S0到1994E才讀live SP+120，最後S11於19956讀+76，SP+=128並RET。所有fresh stack reads可能受callee／alias影響，不能把source save/restore形狀當成整體callee-preservation保證。

主體沒有直接寫GP／TP／A6／A7；這不是其13個callee也保存它們的證明。未審callee可觀察ambient args／frame、改SP/S/GP、記憶體或不返回。

## 所有direct calls與poll

| Call PC | 真實目標 | 本body剛明確設定的參數（非完整實體signature） |
|---|---|---|
|19814|8520|A0=liveSP+32，A1=0，A2=32|
|1986E|19124|A0=512，A1=1|
|19874|1908C|A0=C000|
|1987A|188E2|A0=liveS1|
|19896|1892E|A0=liveS1，A1=liveSP+32|
|1989E|18986|A0=liveS1，A1=1|
|198A6|18A98|A0=liveS1，A1=1|
|198AC|18A6E|A0=1|
|198B8|189AE|A0=liveS1，A1=16，A2=1，A3=7|
|198C0|18996|A0=liveS1，A1=1|
|198CA|18A8E|A0=liveA5，A1=2|
|198DC|18A66|A0=liveS0+400|
|198E6|188E2|A0=liveS0+400|

198C4先MV A5,S1；poll每次198C6把A5送至A0。18A8E返回後，198CE／198D2將A5重新設定40012400；若A0==0，198D6 BEQ回198C6，故後續迭代的A0使用新literal。沒有encoded counter／timeout；可能不返回或永遠得到零，正常完成尚未證明。本body沒有其他indirectcall，唯一JALR是末端RET；direct call指向的是原App位址，不是已證明的resident provider。

## 只閉合三個小依賴

8520的實際carrier FUNC長度是168B，但本輪**只證42B restricted path**。若callback entry SP16對齊、A0=liveSP+32是非wrap有效32B、A1=0/A2=32、正常無干擾存取，前三個branch不離開fast path；masked length32與remainder0使四個SW（offset0／4／8／12）以步幅16跑兩組，覆蓋當前SP+32..63，然後8548 RET。無callee／SP/S/GP寫入；A0保留原dest，A2=0，A3/A4是end，A5=0，T1=15。這是從guard與loop步幅的閉式來源論證，不是CPU／ISA執行。未對齊、非零fill值、餘數／短長度會去其他分支，包含computed JR，**沒有被此restricted proof閉合**。

19124完整30B是fresh READ32／WRITE32 40021018；A1非零時OR entryA0，零時AND ~entryA0，無callee或SP/S/GP/RA寫入。其caller A1=1。1908C完整18B是READ32 40021004，`old & FFFF3FFF | entryA0`後WRITE32，亦無callee或SP/S/GP/RA寫入。

因此在上述restricted path／normal／noalias／noasync條件下，第一個尚未在此scope閉合的依賴是 **1987A→188E2**。沒有繼續擴查整條ADC-like鏈；這也不能將config+52零值延伸到callback返回。

## 重跑與界線

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --firmware ID2966.bin
python3 -B check.py --project-root ROOT --firmware ID2966.bin --image-elf EXISTING_SOURCE_ELF
```

預設metadata_only=true，actual原FW／ELF flags皆false。顯式FW重讀454B／167欄位、原App42B並跑4個真實single-field byte反例：初始32長度、fast-fill第四word offset、poll backedge、SP pop128；皆拒絕。只有給ELF才核對548B owner與NOTYPE roles／slice，仍是局部view而非whole-build replay。

工作區 `apk-analysis/tsl9-*`與交付`analysis/*`皆可用；IRQ source audit是既有封存來源依賴，沒有歷史build硬依賴。沒有產生原BIN opcode或native provider、沒有新compiler/HOST samples、CPU/ISA/ESIL執行／模擬、硬體、網路或UID讀取／傳送。已安裝resident、完整ABI、全部callee效果、callback後config值與OTA相容性仍未知。
