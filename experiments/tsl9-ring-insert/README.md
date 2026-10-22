# Ring 與接收鏈原位重建

[English](readme.en.md)

[ring_insert.v3.c](src/ring_insert.v3.c) 重建官方ID2966 `[0x12BC8,0x12C24)`。C11／C++17原位連結後，完整92B／32指令與原廠相同。C表達index／stride／零擴展及fresh provider讀取；實體frame、slot記憶體與S0／S1透過明示架構ports保留，**不是一般C ABI**。

```sh
python3 -B experiments/tsl9-ring-insert/verify.py --language c --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-ring-insert/build/my-check/c
python3 -B experiments/tsl9-ring-insert/verify.py --language cpp --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-ring-insert/build/my-check/cpp
python3 -B experiments/tsl9-ring-insert/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-ring-insert/build/my-check/c/verification.json
```

輸出須為新目錄。`LLVM_BIN`指向本機既有工具；目前驗證已記錄的Windows NDK LLVM18，其他工具鏈未驗證。Windows可使用`python`；不自動下載工具或搜尋旗標。每語言40個負例；加上`--require-firmware-ready`必須exit1。

原位限制與證據：

- 五個真實FUNC為8／16／50／10／8B，native的3筆重定位指向真實定義；nominal ELF完成解析且無UND／RELA。
- PC=`0x12BD2`的AUIPC與ADDI共同得到`0x2000C038`；任意重定位會改變結果，不能把nominal證據套用到任意位址。
- 佇列為32格×12B；先寫ID16與length8，新讀`LW32[0x0004004C]`後以`JALR A5`呼叫。A1與完整A2仍傳入；ring本身不驗證指標或限制length。
- 呼叫後`SB S1,11(S0)`使用當下實體暫存器，成功出口保留resident的A0；滿表出口保留輸入A0。fresh frame還原順序不變。
- v1因編譯器要求被保留的SP而未產生物件；v2雖為92B，卻用A0作provider位址暫存。v3增加A5 base port修正；失敗來源與本機收據未覆寫。

[receive_graph.ld](receive_graph.ld)把七個已重建區域放回原位址。它覆蓋586個不連續程式位元組；ELF容器含其他header與gap，不能當成完整APP或BIN。完整驗證、來源整理與收據見[本輪分析](../../analysis/ring-and-receive-graph-2026-10-23/README.md)。

**尚不可燒錄。** 動態resident pointer的實際值／身分與保存契約、其他caller／IRQ／fault／memory ownership、實體晶片與完整韌體OTA均未證明。未執行target、ISA／MMIO模擬或硬體操作；沒有產生完整韌體BIN。
