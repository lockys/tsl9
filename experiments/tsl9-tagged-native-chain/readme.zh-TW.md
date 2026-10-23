# 標記傳送路徑的三區段原生整合

[English](readme.en.md)

五份真正C來源（fill、tagged、SPI write、register read、SPI leaf）以原有固定profile各自編譯為C11／C++17，再連結三個原PC區段：

| 區段 | 起點 | bytes |
|---|---|---:|
| fill | 0x8520 | 168 |
| SPI＋write／modify＋read | 0x16896 | 326 |
| tagged dispatcher | 0x16B7C | 246 |

合計**740B／260指令／58強FUNC；0UND／0RELA／0global ABS**，所有程式位元組符合固定官方ID2966 V4.1.60對應範圍。這是三區段的程式碼投影；ELF的可執行LOAD包含缺口共59,218B，區段間缺口與padding不是原完整映像。

`build/nominal-v1/{c,cpp}/verification.json` 記錄每語言12個實際編譯／IR／連結／讀取命令、MD二檔include closure、逐命令實際輸入雜湊、全部260列LLVM位址／位元組、完整ELF metadata及遞迴唯讀重播。新增fill／既有tagged／SPI write／SPI leaf正式證據均實際重播，五份原生來源重新編譯。每語言264項負向檢查（260指令＋入口＋三段可寫權限變更）通過。

對fill的31組computed案例（16個唯一目的位址）另核對真實SB／RET邊界、AUIPC原PC及alignment link RA=0x85BA。所有15個直接JAL均連到真正提供者；沒有ABS假提供者或原始opcode搬運器。

```sh
python -B experiments/tsl9-tagged-native-chain/check.py --build --out-dir experiments/tsl9-tagged-native-chain/build/local-v1 --llvm-bin "$LLVM_BIN"
python -B experiments/tsl9-tagged-native-chain/check.py --out-dir experiments/tsl9-tagged-native-chain/build/local-v1 --llvm-bin "$LLVM_BIN" --strict-firmware
```

第一個目錄必須全新；腳本需本機保留的fill verified-v1、tagged verified-v2及SPI write nominal-v3等原始證據，不會下載或捏造缺少產物。strict模式完成同樣檢查後仍回傳1，因韌體門檻尚未通過。

**尚未解決**：tagged仍從`[0x4004C]`新讀未知resident目標；0UND只描述ELF直接符號。實體配置、ROM／memory／IRQ與非同步行為、整機啟動及完整OTA映像尚未證明。既有1162B整合保持原樣，本輪未將740B鏈併入它。未執行目標／ISA／主機模型或硬體，也未產出可刷寫BIN。
