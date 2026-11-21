# 參考 SDK 對描述元的命名

`wchble_rom.h`（SHA-256 `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c`）的 `BLE_PAControlInit` 是 `void (*)(blePaControlConfig_t *)`，取 `BLE_LIB_JT(109)`。預設表基址不是 `0x40000`，而是 `0x40000+0x34`，因此槽位是 `0x401e8`。V1.31 參考 carrier 的該 word 為 `0x640b8`。SDK 註解要求 role 初始化後再呼叫、參數是全域變數；這是 API 使用約定，不證 APP 曾呼叫。

以 RV32 C11 真編譯[檢查程式](check_v131_pa_descriptor.c)，六個欄位各 4 bytes、結構共 24 bytes。Clang IR 先從十進位 `262632` 載入 i32，轉成函式指標，再原樣傳入 p；沒有執行該呼叫。重跑：`clang --target=riscv32 -ffreestanding -std=c11 -O1 -I <header-dir> -S -emit-llvm analysis/check_v131_pa_descriptor.c -o -`。

將[原指令的兩組遮罩](v4160-type3-descriptor-setter.zh-TW.md)對回 SDK 欄位：

| 路徑 | 第一次：對 txDisableGPIO 所指 word 做 OR | 第二次：對 rxDisableGPIO 所指 word 做 OR |
|---|---|---|
| `0x640b8` 設定非空 D | `rx_pin` (+20) | `tx_pin` (+8) |
| `0x63eae` 片段，非空 D | `tx_pin` (+8) | `rx_pin` (+20) |

上述欄位名來自參考 SDK，不代表實際 GPIO 位址或腳位；不能依命名把 setter 的交叉遮罩改成同側。兩處均不以 `txEnableGPIO` (+0) 或 `rxEnableGPIO` (+12) 當這兩次寫回的目的。未找到 APP 的實際 D，也未證明裝置 ROM 的版本。
