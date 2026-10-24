# 記錄解碼與狀態寫入

[English](readme.en.md)

選定原C6A8–C776的206B／75指令，以及FAF8–FAFE的6B／2指令。兩個入口皆無frame；保留GP+220 fresh word讀取、unsigned mask／乘法、目標byte保留位元與12A08無連結尾跳。

GP+224的完整word讀取包含先前7B複製之外的一個byte，不將它縮窄或宣稱buffer界限已證明。目標offset2、7、8及4–6仍為原始欄位，座椅／免打擾語意未確認。

只做離線C11／C++17編譯及正常靜態核對；不執行目標、HOST model或ISA，不產生可燒錄BIN。

實際C/C++核對通過：212B／77i／17區塊；主元件4636B code＋456B data／309RELA／20UND。詳見[分析](../../analysis/record-decode-2026-10-24/README.md)。

~~~sh
python3 experiments/tsl9-record-decode/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-decode/build/trial-v1
python3 experiments/tsl9-record-decode/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-decode/build/component-v1
python3 scripts/check-record-decode-publication.py
~~~
