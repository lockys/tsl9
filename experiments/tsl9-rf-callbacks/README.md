# RF task／status 回呼

[English](readme.en.md)

原碼17476–1753A，共196B／65指令／23架構區塊。C11／C++17的144個非控制bytes與16個具型別參照經純資料原位址編碼後全部相同。保留task16B frame／共用出口、signed低16-bit事件測試、四個間接呼叫、無frame狀態回呼與三個原始packet byte比對。

入口17476／174EE由原175E8建構器的AUIPC／ADDI編碼獨立計算；前次人工換算早16B的文件已更正。保留原始投影與收據，不把literal位址當成診斷連結已接通。

```sh
python3 experiments/tsl9-rf-callbacks/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rf-callbacks/build/trial-v1
```

僅離線編譯／正常靜態核對。173EE／17442、resident身分與ABI、原位址配置／實機／IRQ／OTA仍未證明；不執行目標、HOST model或ISA，不產生BIN。
