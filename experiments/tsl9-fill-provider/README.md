# 0x8520 填值提供者

[English](readme.en.md)

候選 `[0x8520,0x85C8)` 為168B／55條RV32指令。C擁有常數、遮罩、算術與volatile word／byte store；13個私有架構分區保留AUIPC、計算式JALR、RA及控制順序，並非獨立可呼叫的C函式。

- 短長度 n=0..15 的 computed JR 目標為 `0x8596-4*n`；n=0直接RET，其他由offset n−1向下寫至0。
- 未對齊 m=pointer&15（1..15）先藉計算式JALR寫入16−m個prefix bytes，T0保存原RA、暫時RA為0x85BA；回來才還原RA與調整pointer／count。
- 大區塊依序SW +0／+4／+8／+12，再advance16，以unsigned pointer<endpoint決定重複，最後仍反向寫byte tail。不可改成一般計數迴圈；指標環繞時投影可能不同。
- A0不改寫，SP／S／GP不改寫；A1 pattern expansion、A2 tail count、A4 tail base、A5與T0均有條件性退出殘值。只有有效、普通、非環繞記憶體上的最終內容可稱為memset類似，未使用libc替換。

`src/fill.v1.c` 實際編譯為168B，但LLVM將RA還原與A5調整對調；`fill.v2.c`只增加RA埠後的LIVE約束，編譯旗標不變。v1來源／量測保留。選用v2的 `build/verified-v1/{c,cpp}/verification.json` 實際編譯與唯讀重播通過：13FUNC、8pending RELA、0UND／global ABS；非重定位位元與55條typed指令符合原BIN。每語言94項負向檢查（55指令、13binding、8addend、13IR埠、5scalar／SSA／volatile變更），負向檢查關閉完整雜湊比較。

[整合證據](../tsl9-tagged-native-chain/README.md) 再證明原PC連續配置及31組computed案例（16個唯一目的位址）。AUIPC衍生的絕對T0／A3殘值依PC而變，不能將VMA0的部分物件當作原PC結果。

特定tagged caller以A0=SP+18、A1=0、A2=11呼叫，靜態路徑將SP+28向下清至SP+18，SP／S0–S3不變；下一次resident呼叫仍未知，不能延伸這項非干擾結論。

```sh
python -B experiments/tsl9-fill-provider/verify.py --build --out-dir experiments/tsl9-fill-provider/build/local-v1 --llvm-bin "$LLVM_BIN"
python -B experiments/tsl9-fill-provider/verify.py --out-dir experiments/tsl9-fill-provider/build/local-v1 --llvm-bin "$LLVM_BIN"
```

使用既有且雜湊相符的Windows LLVM，第一個輸出目錄必須全新。未執行目標／ISA／主機模型或硬體I/O；不構成普通ABI、非同步IRQ、實體記憶體、完整映像或OTA相容性證明。**未完成逆向，也未產出可刷寫BIN。**
