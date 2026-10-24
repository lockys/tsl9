# 原始位址與控制流程位置驗證

[English](readme.en.md)

已由實際連結器將目前 C/C++ 的 **13,864B code＋674B data** 配置到官方 V4.1.60 原始位址；全部 **14,538B** 與 **930 筆 relocation** 對應吻合。C11／C++17 診斷 ELF 相同，SHA-256：`471defe5103e82e57c855e2ab6f4a9638edce55caa1880deedff6a5d2e8c587e`。

此產物是**入口 0、只有 PT_NULL、沒有 PT_LOAD 的 ET_EXEC 診斷 ELF**，不是 OTA BIN。95 個來源 UND 仍代表未重建實作；診斷僅以另外命名的 local／hidden／NOTYPE ABS 位址常數保留其參照，沒有提供函式本體。65 段只合併原址相鄰、同類與同對齊的已知區塊，未補未知空洞。先前 `ld.lld -r` 的 ET_REL 段址會歸零，不能當作原址證據。

| 核對項目 | 結果 |
| --- | --- |
| 具大小 code／data 區塊 | 1,196／7；位址、長度與全部 bytes 相同 |
| 指令／直接轉移 | 4,832／805；788 筆控制 relocation＋17 個同一區塊內的原始分支 |
| 直接目的地 | 709 次指向已重建指令；96 次仍只指向未重建提供者的參照位址 |
| 一般後續／可能的呼叫返回位置 | 4,447／286，全部有真實已重建指令 |
| 暫存器間接轉移／MRET | 213／10；實際目的地與上下文未證 |
| 啟動區 EBREAK | 原廠 `0x8034` 是 EBREAK，`0x8038` 起為 328B 向量資料；例外／除錯處理與恢復位置未證 |

保守末端檢查的 812 個可能後續位置中，811 個連到 code，剩餘一個即 EBREAK 邊界。逐指令檢查將 trap 與一般後續位置分開，因此「一般後續位置缺口 0」不表示 trap、間接呼叫、IRQ 或整體 CFG 已閉合。未觀察執行或可達性。

[完整摘要](summary.json) · [原生連結收據](../../experiments/tsl9-original-layout/build/original-v3/measurement.json) · [逐指令證據](../../experiments/tsl9-original-layout/build/flow-v2/c-flow.json) · [仍缺的提供者](../callback-flow-2026-10-24/next-providers.json)

在專案根目錄，以已安裝且符合 pin 的 LLVM 目錄重查：

```sh
python3 experiments/tsl9-original-layout/build-v3.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/original-v3
python3 experiments/tsl9-original-layout/verify-flow-v2.py --replay experiments/tsl9-original-layout/build/flow-v2
```

下一步重建原始 `19BF0` 及其實際依賴；clock `18834`、fields `1973C`、IRQ `9A42` 的不精確候選維持未綁定。硬體、resident、ABI、啟動／RAM／IRQ、OTA 仍未通過。本輪未改動 C/C++、未產生 BIN、未接觸硬體／網路、未 commit／push。

可擴充方向：已建立離線重建覆蓋檢查；唯讀延後事件診斷仍是候選，尚未加入韌體，`2000C794` 的使用者功能意義與時間單位未確認。

