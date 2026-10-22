# ADC 設定候選：共享 C/C++ core 與原生靜態產物

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

已從指定 V4.1.60 原始韌體，重新讀取並解碼 **0x1892E..0x18986 的 88B／37 指令**，重建成可讀 C11/C++17。這是候選函式的數值位址與記憶體效果投影；ADC 名稱不構成實體硬體識別或可刷寫證明。

共享 API 為 `ml_result tsl9_adc_config_io(ml_io*,uint32_t base,uint32_t config)`，普通 include 已封存的 memory_leaves.h/io.h，只需要 read32、read8、write32 三個真正 typed port。正常完成回傳 {CONTINUE,base,1}；停在 callback 邊界回傳 {flow,0,0}，不加入 cleanup。原始程式保留 A0=base；u32 結果是這個重建介面的明示投影，不代表已知原始 C prototype。

## 精確效果順序

每個值在原位置重新讀取，不預取整個 config。下表 offsets 為十進位。

| 群組 | 依序讀取 | 寫回 |
| --- | --- | --- |
| 第一組 | WORD(base+4), WORD(config+24), WORD(config), WORD(config+28), WORD(config+4) | WORD(base+4) |
| 第二組 | WORD(base+8), WORD(config+12), WORD(config+16), WORD(config+8) | WORD(base+8) |
| 第三組 | WORD(base+44), BYTE(config+20) | WORD(base+44) |

全部 14 個效果的位址及運算依 uint32_t 回繞：

```c
new4 = (old4 & 0xe0f0feffu) | cfg24 | cfg0 | cfg28 | (cfg4 << 8);
new8 = (old8 & 0xfff1f7fdu) | cfg12 | cfg16 | (cfg8 << 1);
new44 = (old44 & 0xff0fffffu) | (((cfgByte20 - 1u) & 255u) << 20);
```

config WORD 保留完整 32 bits，不擅自裁切成欄位。config+20 是 BYTE，先減一並以 255 遮罩才左移；0 變成 255，可能影響 bits20..27。base/config 數值為 0 也沒有自行加入 null guard。HOST 的 diagnostic budget 只控制合成測試；原生 ports 不含這個人工限制。

## 已驗證範圍

C 與 C++ 各實際通過 **80 個合成案例／6864 個檢查**，涵蓋高位元 config、byte20={0,1,128,255}、base/config 位址回繞、數值零、config=base-8 alias、callback 在每個邊界改變記憶體、14 個 stop 點乘 HALT/TRANSFER/UNKNOWN，以及 budgets0..13。每種語言另實際編譯三個語意反例並由斷言拒絕：裁短移位 WORD、遺漏 BYTE 減一遮罩、讀錯 fresh WORD 位址。測試只操作合成 map，未把數值位址轉成 HOST pointer。既有 HOST matrix 沒有重跑。

native.c 普通 include 同一個 core，ports 使用真實 volatile 位址讀寫。入口 `uint32_t tsl9_adc_config_1892e(uint32_t base,uint32_t config)` 使用已有合理的 always_inline 與 A0/A1 empty-asm bridge。固定 NDK 27.1、-Oz、rv32imac_zicsr_zifencei、ilp32、禁止 machine outliner，沒有 flag sweep。

| 真正 global FUNC | bytes / 指令 | 註記 |
| --- | ---: | --- |
| tsl9_adc_config_1892e | 102 / 38 | 雙參數，無 context/sret、frame、call |
| tsl9_adc_config_io | 128 / 44 | 未選定的真實 context/sret core |
| ml_port_read32 | 8 / 4 | 未選定的真實 volatile port |
| ml_port_write32 | 6 / 3 | 未選定的真實 volatile port |
| ml_port_read8 | 10 / 4 | 未選定的真實 volatile port |

完整 ET_REL 為 **254B／93 指令、5 global FUNC、UND=0、RELA=0、ABS provider=0**，沒有假設 linker 已移除其他四個函式。C/C++ 五個函式的機器碼一致。公開函式 IR 保留 10 個 volatile WORD read、1 個 BYTE read、3 個 WORD write，順序與來源一致。

原生入口自行寫入 A2/A3/A4/A5/A6/A7；原始函式只有 A3/A4/A5，所以 **A2/A6/A7 是額外寫入**，正常 scratch liveout 與 fault/async 暫態也不能視為相符。102B 比原始 88B 多 14B。完整 ABI、固定配置、installed provider 均未證明。

**切勿在 HOST 執行 native.c：它包含真實 volatile MMIO。** 本輪只執行合成 HOST executable；native 僅編譯與靜態讀檔，沒有 RV32/ISA/MMIO/實體硬體執行，沒有 link 原生物件、objcopy、BIN 或刷寫。

## 執行與證據

```sh
sh experiments/tsl9-adc-config/verify.sh --project-root "$PWD" --tool-dir LLVM
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
python3 CASE/implementation/provenance.py --project-root ROOT --firmware ORIGINAL_V4160.bin
```

CASE 支援 workspace 的 apk-analysis/tsl9-v4160-adc-config-2026-10-22 與交付樹的 analysis/v4160-adc-config-2026-10-22。新 --build-root 必須是 model/build 下尚不存在的路徑，省略時用 UUID；預設產生 C 與 C++ 兩份 archive。預設 check 只驗來源與 metadata；顯式 receipt 才重讀真實 HOST executable、負例來源、native ELF、完整 IR、MD 及 disassembly，不重新執行或編譯。provenance 或 check --firmware 才重新讀原始韌體及有限指令 decoder，沒有模擬 CPU。

正式 W 產物為 build/verified-v1/{c,cpp}/verification.json。保留實際 compiler/hash、HOST 格式檢查、工具資源 stdint.h、六個實際 native MD inputs、全部 logs 和檔案清單。Python/sh 原始碼可跨平台；本輪 native 結果僅接受固定 Windows NDK tool hash。sh runtime 仍未驗證：先前 MSYS 啟動拒絕後，依限制沒有重試。新增來源及文件採 LF、單一 EOF newline 並檢查 Git 式空白；真實編譯器 raw logs 如含 CRLF，保留原樣作證據。

初次 build/first 的 raw 產物與 initial-probe-snapshot.py 保留為歷史。唯讀 replay 曾揭露 tuple/list 的 JSON 表示不一致；只修正 probe 序列化，再以完全相同 source/flags/tests 建立 verified-v1，兩份正式顯式唯讀 replay 均通過。舊初版 receipt 不是目前 probe 可 replay 的證據。
