# 記錄複製、清除與完成回呼

[English](readme.en.md)

原C776–C7E8家族，114B／42指令／11架構區塊。三個入口為C776（16B frame）、C798（無frame清除尾跳）、C7AA（條件式32B frame）。C11／C++17的94個非控制bytes與7個具型別參照，純資料原位址編碼後全部相同。

```sh
python3 experiments/tsl9-record-consumer/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/trial-v1
```

保留GP+220的7B參數及不同的literal物件指標、status先寫再判斷、呼叫後fresh pointer／record讀取及還原後尾跳。只做離線編譯與正常靜態核對；callee ABI、memory ownership、原機／ROM／IRQ／OTA未證明，不執行目標、HOST model或ISA，不產生BIN。

整合已核對：重用真實82A8的42B與完整12A08的102B；主元件4424B code＋456B data／299RELA／22UND。詳見[分析](../../analysis/record-consumer-2026-10-24/README.md)。

~~~sh
python3 experiments/tsl9-record-consumer/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/providers-v1
python3 experiments/tsl9-record-consumer/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/component-v1
python3 scripts/check-record-consumer-publication.py
~~~
