# RF 完成回呼與重試

[English](readme.en.md)

原碼173EE–17476，共136B／45指令／7架構區塊。C11／C++17的126個非控制bytes與3個具型別參照，純資料原位址編碼後全部相同。保留先停止事件再清理狀態、16B frame／可選callback尾跳、清除callback pointer的次序，以及無frame計數遞減／遮罩／重排程。

```sh
python3 experiments/tsl9-rf-completion/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rf-completion/build/trial-v1
```

只編譯及正常靜態核對。byte計數可由0 wrap至255，原碼保留，不宣稱實機有有界重試；callback／resident ABI、原位址／記憶體／硬體／IRQ／OTA均未證明。不執行目標、HOST model或ISA，不產生BIN。
