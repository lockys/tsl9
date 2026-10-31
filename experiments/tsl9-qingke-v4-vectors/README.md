# CH32V208 青稞 V4 中斷向量對照

[English](readme.en.md)

原 ID2966 V4.1.60 reset 的 `0x18718..0x1871C` 將 `0x803B` 寫入 `mtvec`，即 BASE=`0x8038`、MODE=`3`。使用者提供的原板近照顯示晶片印字 CH32V208GBU6；[WCH 產品頁](https://www.wch.cn/products/CH32V208.html)列 CH32V208 使用青稞 V4C 核心。

[WCH 青稞 V4 手冊](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf)第 3.2 節說明 MODE=`0b11` 使用向量表中的 handler 絕對位址，表項以中斷編號乘 4 偏移。依此官方契約、原始 APP 的 BASE 與既有 [IRQ enum／向量證據](../tsl9-trap-profile-contract/README.md)，可得到下表：

| 官方 enum | 編號 | `0x8038+4×編號` | 原 APP 表項值 |
| --- | ---: | --- | --- |
| USB_LP_CAN1_RX0 | 36 | `0x80C8` | `0x12C24` |
| EXTI9_5 | 39 | `0x80D4` | `0x16FB6` |
| TIM3 | 45 | `0x80EC` | `0x979E` |
| BB | 63 | `0x8134` | `0x1873E` |
| LLE | 64 | `0x8138` | `0x8498` |

這收斂了先前文件中「mode 3 官方語意未知」的限制：**官方 V4 規格已提供 mode 3 的解讀**。但它仍是依晶片標記、官方手冊與原 APP bytes 所作的條件式對照，沒有觀察實際 `mtvec`、PFIC 狀態、向量重映射、IRQ delivery 或執行順序。WCH 手冊對 VTF 等功能另有機制，不能把一般向量公式當成所有可能中斷路徑均已證明；slot binding／ROM 與 IRQ 相容性仍待驗證。沒有執行韌體或硬體操作。

## `INTSYSCR` 的啟動設定

原 reset 在 `0x186FE` 載入 3，於 `0x18700` 將其寫入 CSR `0x804`。依同一 WCH V4 手冊第 3.2 節，該 CSR 為 `INTSYSCR`：bit 0 `HWSTKEN=1` 請求啟用硬體壓棧，bit 1 `INESTEN=1` 請求啟用中斷巢狀；但 bits 3:2 的 `PMTCFG=0` 在手冊表中對應無搶占位／無巢狀。不能單從 bit 1 設置便宣稱實機一定會發生巢狀中斷。

該寫入數值的 bit 4 `HWSTKOVEN` 與 bit 5 `GIHWSTKNEN` 均為 0；手冊將 bit 5 描述為用於中斷上下文切換的全域中斷與硬體出棧關閉控制，並說明中斷返回後自動清除。這補上舊[數值契約](../tsl9-trap-profile-contract/README.md)對 bit 5 官方語意的缺口，並不代表後續 `0x8448` 或中斷返回在實機已被觀測、所有控制位元在後續保持不變，或可由此證明堆疊／IRQ 安全。
