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

## `mstatus` 與向量設定的先後順序

原 `0x18704..0x1870C` 組成 `0x1888` 並執行 `CSRRS mstatus`；它將此 mask 與舊值 OR，而非將整個 CSR 覆寫成 `0x1888`。根據同一 WCH V4 手冊的 `mstatus` 欄位定義，該 mask 設置 MIE bit 3、MPIE bit 7 與 MPP bits 12:11=`11`；其他可寫位元保留原值。手冊描述 MIE 為機器模式中斷使能，MPP=`11` 用於返回後維持機器模式，`mret` 會依當時 `mepc`／MPP／MPIE 恢復執行與狀態。

此 OR 發生在 `0x1871C` 寫入新 `mtvec` **之前**；`0x1872C` 才寫入 `mepc=0x9008`，接著 `0x18730` 跳往 `0x40000`。因此，除非原本沒有可交付的中斷、或有其他有效屏蔽條件，不能單憑這個順序假設新向量設定前不會發生中斷；也不能直接推定一定發生中斷。candidate resident 的 `mret` 若要回到 `0x9008`，還需當時 `mepc` 未被改寫與相容 resident 路徑等條件。這是規格／原始指令的靜態對照，未讀取實機 CSR 或執行硬體。
