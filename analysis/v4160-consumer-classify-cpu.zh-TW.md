# v4.1.60 consumer 零 filter 返回後的分類與副本

2026-11-26。只使用本機原 APP（76800 bytes；SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）與前批固定的 V1.31 copy reference；不操作設備、不執行 handlers。

## 分類取自 stack snapshot

消費端 `0x12cb4` 先看 filter A0：非零就跳下一槽，零才繼續。分類來源是已複製的 stack snapshot，不是已清 ID 的 queue 槽：

| 新 consumer SP 的 offset | 欄位 |
|---|---|
| `+8..9` | ID halfword |
| `+10` | length byte |
| `+11..18` | 八個 payload bytes |
| `+19` | tag byte |

在原 consumer，ID=0 已於更早處跳過；本批沒有把獨立 ID=0 fixture 當成正常可達分類路徑。

## ID=1 的精確條件

必須 length=4、payload 前兩 bytes=`b5 62`。不符合即下一槽。符合時看第三 byte：

| 第三／第四 payload byte | 分支 |
|---|---|
| `00 / 任意 byte` | 走 `0x12d0e`，第一個 handler 呼叫為 `0x820c` |
| `5a / 55` | 複製完整 12-byte snapshot 到 `sp+20`，修改副本，再呼叫 `0x12a08(copy)` |
| 其他 | 下一槽 |

`00` 路徑在第一個 handler 前沒有第四 byte 限制；本批在 `0x820c` 入口停止，沒有執行後面的本機呼叫。ID=1 路徑不讀下面的配置 bit 3，亦逐例核對資料讀取範圍。

`5a 55` 路徑以當次 `[0x4004c]` 載入的指定參考 target 執行原 copy body，參數 `(sp+20,sp+8,12)`。copy 正常返回後，原指令只修改副本：

- 副本 `+6`（第四 payload byte）從 `55` 改成 `56`。
- 副本 `+11`（tag）改成 0。

原 snapshot 的全部 12 bytes 保持不變；副本的其他 bytes 包含長度以外的尾部也被保留。測試核對精確 copy read/write/FENCE 事件、兩個 patch stores、完整副本及 handler 指標／返回 PC；不把它稱為已發出的回覆。

## 其他非零 ID

從 `[S7]`（consumer 設為 `gp+84`）讀 pointer，再讀其 `+4` byte。bit 3 設定就下一槽；否則呼叫 `0x81aa`，零返回跳過，非零才呼叫 `0x14d2e(sp+8)`。

本批不執行 `0x81aa`，只在入口停止後供應 0、1、`0xffffffff`，保存 SP／S／GP、stack、snapshot、queue、配置及 CSR／MMIO，改寫 caller-saved 暫存器，再執行原分支。這是宣告的測試假設，不是此函式實作／保存合約的證明。

## 重現與結果

```powershell
python analysis/test_v4160_consumer_classify_cpu.py
python -O analysis/test_v4160_consumer_classify_cpu.py
```

需要標準庫、原 APP、既有 V1.31 carrier 及前批同目錄依賴。可用 `--carrier <path>` 指定相同身分的本機 carrier，不自動下載。一般與 `-O` 均通過：

```text
PASS: 256 lengths; 65536 signatures; 65536 opcode/parameter pairs; 2304 other-ID cases; 282 actual consumer/filter compositions; response copy/patch; 2 mutations; handlers NOT executed
```

大矩陣從**明示 post-filter 狀態**開始，不假裝先執行整個 RX／consumer：

- 全部 256 種 length。
- 全部 65,536 個前兩 payload bytes 組合，固定其餘合法條件。
- 全部 65,536 個第三／第四 payload byte 組合，固定合法 signature／length。
- 三個其他非零 ID × 256 個配置 byte × 三種 `0x81aa` 返回值，共 2,304 組。

另外 282 組從真實 consumer 入口執行：指定參考 helper 複製／清 queue ID，再執行實際 `0x82d2`（合成表格的兩位置皆不合格，確實返回零），接上分類。覆蓋 256 個 opcode、八個 length／opcode 邊界與 18 個其他 ID／配置／probe 組合。

跳下一槽者繼續原掃描直到 caller 返回，核對 RA/SP/S0–S7；抵達 handler 者停在入口，核對 link／指標，不執行其函式體。兩者都核對 queue 只清 ID、snapshot 保留及控制模型狀態。

兩個記憶體複本負向對照改錯 signature 常數及副本 patch 的位置，必須被路由／完整副本檢查抓出。原 APP／carrier 未改，未修改共享解譯器；前批 detach 檢查也重跑通過。

SDK reference 仍不等於 installed provider；FENCE／CSR 沿用前批明示觀察模型。地址有效、保存狀態及無非同步干擾仍是前提；不證明 handlers、硬體、中斷或傳送效果。舊封存 README drift 亦未宣稱已解。本批沒有新增 C/C++ 重建 bytes 或重算覆蓋率，可接續逐一追查已定位的本機 handler。
