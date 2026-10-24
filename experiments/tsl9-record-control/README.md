# 記錄控制與事件啟動

[English](readme.en.md)

原廠1798A–179FC，共114B／44指令／12個架構區塊。C11／C++17物件保留98個非控制bytes與6個具型別控制參照，純資料原位址編碼後全等。保留32B frame之前的unsigned selector<=35 guard、7B記錄參數、SP+8／SP+12完整word讀取、GP+367／368條件寫入、GP+376／379與兩個resident間接呼叫。

這些是要求原始相鄰配置與私有register契約的架構C區塊，不是一般可獨立呼叫的C API。1787C仍為具名未解析提供者；RAM ownership、resident身分／ABI、原機啟動／IRQ與OTA均未證明。

```sh
python3 experiments/tsl9-record-control/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-control/build/trial-v1
```

LLVM_BIN指定現有LLVM工具目錄。只做離線編譯及正常靜態產物核對；不執行目標、HOST model、模擬器或硬體，不產生BIN。
