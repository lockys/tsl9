# 分派器功能處理區

[English](readme.en.md)

選用 `src/handlers.v4.c`：1505C–153BA，862B／339指令／93架構區段，另含32B相對表。實際106個重定位包含88直接控制、2 PC-relative、16 table；舊trial欄位 `RELA=88` 只計直接控制，並非全部重定位。

v1保留直接S0／SP／RA C變數造成的實際編譯失敗。v2保留組譯器把外部條件跳躍展開而改變長度的失敗；v3以明確型別控制重定位通過；v4加入真實table HI20／LO12介面。

局部probe仍有配置與完整控制盤點的驗證界線；最新三單元核對位於[完整分派器](../tsl9-feature-dispatch/README.md)。原始trial不改寫。沒有執行target、HOST模型、ISA、硬體或網路。
