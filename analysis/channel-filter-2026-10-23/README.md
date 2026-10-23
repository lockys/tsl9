# 通道與 CAN 濾波器重建

[English](readme.en.md)

五個新 C 單元已放入 `src/native/receive/`。C11／C++17 的六段原位址程式共1242B、445指令，與官方V4.1.60完全相同；接入既有接收／分派路徑後為3166B、1104指令。

這只是局部程式證據。完整元件仍缺14D2E，另有17處不透明resident轉移、2處內部computed control；原位址ELF的67098B間隙、原硬體、啟動、ROM ABI、記憶體、中斷及OTA仍未證明，不能刷入。

- [來源、重現方式與功能推論](../../experiments/tsl9-channel-route/README.md)
- [實際摘要與完整範圍](summary.json)
- [分派器1912B／至少71外部目標](../feature-dispatch-frontier-2026-10-23/README.md)
- [公開收據來源與匿名化](publication-provenance.json)
- [獨立覆核與v1更正](independent-review.json)

v2每語言5903個負例通過，另保留原始v1。獨立覆核找出v1局部gate的漏RELA與SHDR／LOAD耦合缺口；v2已加入相應拒絕檢查。基準產物位元組不變，沒有將歷史收據改寫為成功的新版本。

值得新增「純離線濾波請求檢視器」，比較兩後端的ID截斷與通道差異。此候選尚未實作，不會把設定例程當作唯讀硬體診斷。
