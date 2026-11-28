# v4.1.60：Fallback 保存延伸至 constructor 與 wrapper 尾跳前

接續 [APP 返回與首次登記](v4160-b1-fallback-app-static.zh-TW.md)，本輪將條件式 fallback 零值保存從 `0x19b30` 延伸至 wrapper 尾跳 `0x19b54` 的目標開始執行前。檢查器為 [check_v4160_b1_fallback_wrapper_static.py](check_v4160_b1_fallback_wrapper_static.py)，證據為 [JSON ledger](v4160-b1-fallback-wrapper-static.json)。

使用原始 bytes、CFG／def-use、固定區間及 frame 相對位置證書；沒有執行韌體、建立可變 target 狀態模型、操作硬體、重播或連線 target。重用既有 C 與函式證據，沒有增加 C 重建 bytes 或提高覆蓋百分比。

## 從登記回覆至設定服務

前階段在首次登記正常返回 `0x19b30` 時，條件式結論為 fallback=`0`、A0=`3`。本階段還要求 nominal `GP=0x20004000` 已建立且保持：

1. `0x19b34` 把低 byte `3` 存入 `GP+388=0x20004184`。
2. `0x19b38` 呼叫 constructor `0x19b56`，它建立 32-byte frame，準備 16-byte 設定。
3. 前 12 個直接呼叫的寫入限於已定位的固定控制地址及自身 frame。四次 `0x19272` 輪詢沒有本地 timeout，必須各自正常完成才有返回結論。
4. 第 13 個呼叫 `0x197b8` 尾跳完整 mode 3 `0x1929a`。其 36 個硬體地址 stores 投影為四個固定區間；其餘 stores 在自身 frame。GP+108 是讀取來源，沒有 GP-relative store。
5. `0x19bcc` 呼叫 fresh slot `0x40074`；本證書只接上符合兩版候選原指令的服務。

在來源、frame 與正常返回條件下，constructor 提供的 little-endian 16 bytes 為：

```text
c6 91 01 00 ff ff ff ff 80 3e e8 03 00 00 00 00
word0 = 0x191c6；word4 = 0xffffffff
U16+8 = 16000；U16+10 = 1000；byte12 = 0
```

設定服務的 optional hook 必須為 fresh 零值，或 `0x197b8` 且符合完整 mode 3／reader 證據；其他非零 hook 不在已關閉範圍內。這些是條件式分支證書，不表示每一種 hook／state 組合都在真實啟動中可達。

非零來源及四個非零欄位通過所選 gates；byte12=`0` 略過另一個狀態 gate。匹配的軟體 copy 請求複製 16 bytes 到固定設定欄位，再從 fresh 複製結果發布 reader `0x191c6`。若 fresh state+23=`0`，既有 specialized 算術路徑產生 `22`；非零時略過算術與該 byte store。來源、複製目的與後續 fresh loads 的一致性仍需保存前提。

## 立即 callback、返回與尾跳

這裡的設定登記服務與前階段的 `0x40080` callback table 登記不同：它保存 callback 指標後，會立即呼叫自己的 callback。兩版的完整服務及 callback 為：

| 本體 | V1.31 | V1.40 | 大小 |
|---|---|---|---:|
| 設定登記 wrapper | `0x43b0a` | `0x43b96` | 30 bytes |
| 立即 callback | `0x43d62` | `0x43dee` | 130 bytes |
| 共用相對原指令的算術 helper | `0x6df1a` | `0x6e10a` | 914 bytes |

Callback 從 fresh copied word 取得匹配 reader；reader 沒有 stores 或巢狀呼叫。完整算術 helper 沒有 stores、巢狀呼叫或自身 frame。一般 Q／delta 的數值未證明；在這些已核對本體中，它們只存入固定結果 word，沒有作為可寫目的指標解參考。Callback 的條件性 Q store 後，設定登記 wrapper 會把返回的 delta 無條件存回同一個 word。

設定登記 wrapper 強制返回 `0`，設定服務也強制返回 `0`。Constructor 還原 RA／SP 並轉送此零值；wrapper 隨後以保存的 task byte `3` 覆寫 A0。若所需 S1 與保存字保持，wrapper 在尾跳前還原 SP／RA／S0／S1，準備：

```text
A0 = 3；A1 = 8192；A2 = 192000
0x19b40：載入 fresh U32[then-live S1+88]
0x19b54：無 link 尾跳至該目標 & ~1
```

只有在載入時 S1=`0x40000`，才能稱它為 fresh `0x40058` 服務。候選 slot word 已核對，但未證明實際 installed 綁定，也沒有分析該目標開始執行後的副作用。

## 保存範圍與前提

每版重新檢查所有投影區間與 fallback；task byte 初次寫入後，其他所列區間也都避開 task byte：

| 區間類別 | V1.31 數量 | V1.40 數量 |
|---|---:|---:|
| Wrapper task byte | 1 | 1 |
| 前置 helpers 固定寫入範圍包絡 | 10 | 10 |
| Pre／optional mode 3 固定寫入範圍包絡 | 4 | 4 |
| Copy 控制 word 的保存／還原 | 1 | 1 |
| 所選設定服務 RAM 寫入／copy 範圍 | 3 | 4 |
| 設定登記與 callback 的固定 words | 2 | 2 |
| **合計** | **21** | **22** |

同地址重複 stores 在這裡以範圍包絡表示，數量不是執行次數。V1.40 多一筆進入 hook 前的固定清零。上述範圍在數值上避開 fallback `0x20003220`／`0x20003270`；這不能證明物理映射或硬體副作用沒有影響 RAM。

以 constructor 的 live SP 為 C，前置 pair、mode、provider、optional mode、登記及 callback 的子 frame stores 均在 C 以下；constructor 設定為 `[C,C+16)`，saved RA 為 `[C+28,C+32)`，wrapper frame 為 `[C+32,C+48)`。相對位置分離已檢查；實際 frames 仍須有效、owned、不回繞、不別名到 fallback／task／metadata／code，且保存字未被干擾。不同呼叫階段的子 frame 可重用位置，這不等於已證明其資料可在返回後繼續使用。

兩版各核對八個 resident sparse HEX 區間，包括設定本體、登記、callback、算術本體／lookup、copy 的候選來源及兩個 slot words。沿用原始 APP／candidate／SDK identity guards，缺失資料沒有補零。

驗證包含 557 筆原指令 mutation 拒絕、所有區間／frame 證書及 exact-byte ledger 比對；一般 Python 與 `-O` 都必須通過：

```powershell
python analysis/check_v4160_b1_fallback_wrapper_static.py
python -O analysis/check_v4160_b1_fallback_wrapper_static.py
```

結論保留前階段所有 source／getter／post-config I/O 替代路徑條件，以及 actual GP／provider、fresh fields／code／來源保存、正常輪詢／存取／返回、無不利 IRQ／DMA／reentry／外部 writer／MMIO／FENCE 副作用等前提。證書止於 `0x19b54` 尾跳目標開始執行前；`0x40058`、param774、RF、其他 hook／來源域及跨事件消費、保留與釋放期仍未完成驗證。
