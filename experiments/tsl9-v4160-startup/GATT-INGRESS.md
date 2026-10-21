# 原 GATT 接收與命令路由片段

本輪新增原 ID2966 的7224B code與32B RO，包含888C回呼／跨呼叫解析器、14056整個router與必要direct callees/callbacks/有限派表分支。新增18配置、775項RELA、26個private NOTYPE0與2個有限OBJECT；原620配置、7308項語意RELA與所有符號metadata保持。未新增RAM storage/view或code view，31個真UND仍保留。

完整整合目前為70446 code bytes、3708 RO bytes、638配置、8083 RELA、539個symbolic relative32 expressions，另有7個明示original-VA固定表項。後者不是額外ADD/SUB紀錄，也不能宣稱任意重定位安全。

新增1A6A4五word表使用10筆ADD32/SUB32。1A58C七word表已在舊1A547的191B OBJECT中，從offset69重用；沒有重出storage或改舊bytes，也沒有虛構新符號實作原canonical。原位witness逐word與target instruction boundary核實；這是原VA配置的條件式契約。完整新raw CFG和consumer證據在本輪分析報告中。

原frozen `verify-data-anchor-extension.py` 完整CLI實際因把新10筆算入舊534組而拒絕，失敗stdout/stderr與spec hash保留於 `analysis/v4160-gatt-ingress-2026-10-21/integration-repair/`。原檔不修改。新入口先按plan的完整語意Counter核10筆新紀錄，再把其餘所有紀錄交給原gate；不忽略多餘／遺失／抵消的pair。其餘原main檢查保持，完成後再對actual object及witness驗原7word表。這是新的驗證入口通過，不能說未修改的舊CLI已通過。

```powershell
python -X utf8 -B verify-gatt-ingress-extension.py --spec evidence/gatt-ingress-integration.json
```

分析工作區需另加 `--firmware <原ID2966 BIN絕對路徑>`。W實際整合收據為 `build/data-anchor-extension-ffd4a69b972f49c49ac160191624e4ba/gatt-ingress-verification.json`；re-tsl9交付會在目的地重新驗證並記錄其新路徑。

可讀C11/C++17解析模型另見 `../tsl9-v4160-gatt-ingress-model/`。Clock helper、CCC slot與整個router仍是模型的顯式provider邊界；這與本native partial保留原指令是兩種不同證據。

候選官方header可證RV32結構offset與slot計算吻合，不能證明實際resident版本、註冊回呼ABI、GP初值、handle值或硬體SKU。實體Flash、ROM、stack/IRQ、更新與復原仍未證明。原生C/C++承載的保留指令不是完整高階原始碼恢復；numeric witness仍不是韌體BIN，`OTA_ready=false`。
