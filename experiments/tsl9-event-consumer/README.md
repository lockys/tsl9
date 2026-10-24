# 事件消費與回呼家族

[English](readme.en.md)

原廠17666–1787C，共534B／187指令／35架構區塊。C11／C++17物件的472個非控制bytes與23個具型別參照，純資料原位址編碼後全部相同。保留16B／32B／48B frame、共用還原出口、四個間接呼叫、呼叫後fresh GP／佇列存取與原生signed REM。

架構區塊需要原始相鄰配置及private register契約，不是一般C API。正式收據採trial-v2：trial-v1中原4B ADDI被編譯為2B而未通過；現行明確保留原寬度，舊輸出保留本機未宣稱成功。

```sh
python3 experiments/tsl9-event-consumer/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-event-consumer/build/trial-v2
```

LLVM_BIN指定現有LLVM目錄。僅編譯與正常靜態核對；不執行目標／HOST model／ISA，不操作硬體或產生BIN。1AAE8表格／初始索引界限、literal callback原位址、installed ROM／ABI及原機啟動／IRQ／OTA均未證明。
