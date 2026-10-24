# 7B 記錄佇列、回呼與編碼

[English](readme.en.md)

原廠1787C–1798A，共270B／94指令／14個架構區塊；C11／C++17的246個非控制bytes與7個具型別參照，純資料原位址編碼後全部相同。保留16B佇列frame、32B建構frame、無frame編碼入口、AUIPC、兩次fresh count與呼叫後fresh索引／計數，以及word／halfword／byte寫入次序。

架構區塊要求原始相鄰配置與私有register契約，並非一般C API。正式收據為trial-v2；初次trial-v1因組譯器縮短原4B ADDI而未通過，保留本機未宣稱成功。現行明確指定4B asm port寬度。

```sh
python3 experiments/tsl9-record-queue/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-queue/build/trial-v2
```

LLVM_BIN指定現有LLVM工具目錄。只編譯並核對正常靜態產物，不執行目標／HOST model／ISA或硬體，不產生BIN；17666、installed ROM／ABI、原配置／記憶體／啟動／IRQ與OTA仍未證明。
