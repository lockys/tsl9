# V4.1.60 reset 記憶體與 CSR 契約

依原ID2966 `186AA..18734` 的138B reset與`1AB60..1ABE0`的128B初始化資料，重建可讀C11/C++17語義。舊BOOT模型不適用此新版Runtime；本工程沒有跨版本補常數。

依序讀32個source word並立即寫入GP區，之後清零`20004080..2000C958`的8758個word。保持每次live source read與store順序，不把初始化資料當host快照。`initial_gp=20004000`、`initial_sp=20010000`只是原指令的初始數值，不配置實體RAM/stack，也不承諾callee後寄存器未變。

CSR順序為write BC0=31、write804=3、set MSTATUS bits1888、write MTVEC=803B；要求clock helper1874A返回後，才write MEPC=9008、要求handoff到40000。MSTATUS的set不等於overwrite，這些值也不證晶片規格或物理中斷行為。Clock／ROM與所有記憶體／CSR操作均由顯式合成provider提供；模型不把普通provider return視為實體成功。

最後的`RC_TRANSFER/RC_ROM_BOUNDARY`代表停在原unconditional jump的分析邊界，不是reset正常return或ROM接受證明。未知效果、HALT／TRANSFER與觀察預算耗盡保留先前效果；callback若改寫初始化RAM，模型不偷偷恢復資料。因此reset後初值不能直接套到registration時或裝置目前狀態。

```powershell
.\verify.ps1
.\verify.ps1 -Cpp
```

先驗原BIN與兩個source範圍，再以MSVC `/W4 /WX`執行host合成記憶體測試。沒有CPU/韌體執行或模擬、沒有target指標轉host指標、沒有BLE/Flash/網路I/O，`OTA_ready=false`。原138B指令另外已由native工程保留，本模型不是替代ROM、driver或可燒錄BIN。
