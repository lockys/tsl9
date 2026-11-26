# v4.1.60 本機 clear／gate 與 response 派送

2026-11-26。只使用本機原 APP（76800 bytes；SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）與既有固定身分的 copy reference，離線執行原指令，不操作設備。

## `0x820c` 清除與 `0x821e` 判斷

`0x820c` 對完整無號 A0 做 `<=2` 檢查，只在索引 0／1／2 時清除 `gp+193/+194/+195` 的一個 byte。A0 保持原值，沒有 frame、call、配置讀取或舊狀態讀取；其他索引不寫記憶體。高位非零的 `0x10000`／`0x10001` 不等同索引 0／1。

`0x821e` 順序不同：先讀 `[U32[gp+84]+4]` byte；bit 3 設定就返回 0。否則完整 A0 必須 `<=2`，才讀對應的 `gp+193+A0` byte；值小於 3 返回 1，其他返回 0。沒有記憶體寫入。這是本機 gate 的數值條件，不是已證明的設備就緒狀態。

在 consumer 的 `b5 62 00` 分支，filter 返回零後沒有先改寫 A0，故 `0x820c` 收到的確實是 0，清 `gp+193`。新增 256 組從 consumer 入口、實際空表 filter、分類一路走到 clear，然後停在下一個 handler `0x9454`。此時 A0 是 payload 第四 byte、RA=`0x12d1a`，該 byte 沒有在分類前被限縮。

**沒有執行 `0x9454` 或其 allocator。** 靜態解碼顯示其 >19 路徑另請求兩筆配置空間，不能把它當成簡單拒絕；本批不將這部分納入已驗證行為。

## `0x12a08` 的本機派送

先呼叫 `0x81aa`：若返回零，只有 row ID=1 才繼續；若非零，不再要求 ID=1。接著實際執行 `0x821e(0)`，返回零則退出，否則讀 tag：

- tag 非零：以原 row 指標呼叫 `0x16b7c`，本批停在其入口，不執行 TX。
- tag=0：建立本機 record、以指定 SDK 參考原指令複製 payload，再停在 `0x18ca4(0x40006400,new_sp+12)`。

`0x81aa` 仍是明示合成返回：指定 0／1／`0xffffffff`，改寫 caller-saved 暫存器，保存 SP／S／GP、stack、row、配置、狀態與 CSR／MMIO。不執行它的函式體，也不推定其硬體用途。

## tag=0 record 的實際 footprint

`0x12a08` 配置 48-byte frame；以下是新 SP 的位移：

| 位置 | 寫入 |
|---|---|
| `+40`、`+44` | 保存 S0、RA 的 word |
| `+12..15` | row ID 的 zero-extended **word** |
| `+20..21` | halfword 0 |
| `+22` | row length byte |
| `+23` 起 | 參考 helper 逐 byte 複製 row payload |

中間 `sp+16..19` 沒有由這段程式初始化，測試保留並確認 canary，而非補零或聲稱整個 record 已初始化。handler 指標為 `sp+12`，但這不等於已驗證其後續解析／設備寫入。

這個分支沒有自己的 `length<=8` guard。本批只測 length 0／4／8，前批分類 response 則具有較窄的固定長度 4 前提；**不將入口測試的範圍當成此函式自身的保護**。來源 row、控制 word、精確 stack／payload stores 和返回 link 均核對，未知硬體 handler 未執行。

## 重現與結果

```powershell
python analysis/test_v4160_local_gate_dispatch.py
python -O analysis/test_v4160_local_gate_dispatch.py
```

需要標準庫、原 APP、既有 V1.31 carrier 與同目錄依賴；可用 `--carrier <path>` 指定相同身分的 carrier，不自動下載。一般與 `-O` 均通過：

```text
PASS: 65536 clear cases; 131072 readiness cases; 6 full-width probes; 1152 dispatch cases; 256 actual consumer clear/handoff cases; 2 mutations; hardware/TX/allocator NOT executed
```

65,536 組 clear 為所有 byte 索引 × 所有 byte 狀態；131,072 組 gate 再跨配置 bit 3 清／設。逐例檢查精確狀態讀取地址與配置讀取順序；另有六組完整 32-bit 索引 probes。

1,152 組派送為 4 個 ID × 4 個 tag × 3 個有效測試長度 × 3 種 `0x81aa` 返回 × 2 個配置狀態 × 4 個狀態 byte。這是獨立函式 fixture，不代表這些輸入全部由 RX 路徑產生。

兩個記憶體複本負向對照改錯 gate 的 `<3` 常數及 tag 分支極性，必須被返回／路由檢查抓出。原 APP／carrier 未改。共享有限 CPU 只增加 SLTIU 解碼，預設 PC 範圍不變；既有分類測試也重新通過。

指定 SDK reference 不等於 installed provider；正常返回／保存假設、合成 MMIO 與先前封存 README drift 的限制均保留。本批沒有新增 C/C++ 重建 bytes 或重算覆蓋率。後續仍需離線分析 `0x9454`、`0x18ca4` 及其他 handlers，不能把到達入口當成設備功能成功。
