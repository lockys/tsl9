# Resident 提供者與 RF 配置候選

[English](readme.en.md)

原廠1753A–17666，共300B／103指令／12架構區塊。C11／C++17物件的298個非控制bytes與1個具型別分支，經純資料原位址編碼後全部相同。保留A6／A7私有用途、frame前條件、16B／48B frame及八個間接呼叫。

```sh
python3 experiments/tsl9-resident-providers/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-resident-providers/build/trial-v1
```

LLVM_BIN指定現有LLVM目錄。只編譯及正常靜態核對；不執行目標／HOST model／ISA或操作硬體。SDK的RF_Config／RF_SetChannel僅為預設表項配置對照，並非已安裝ROM、實體MCU、ABI或OTA證明。架構區塊不是一般C API，原literal callback仍需原位址配置。
