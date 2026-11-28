# v4.1.60：RF 正常返回與後續本機 helpers 的 fallback 保存

接續 [role gate 兩分支](v4160-b1-fallback-role-static.zh-TW.md)，本輪只延伸其中的 gate 零分支：從第一個 RF call 前的 fallback=`0`，接過所選 RF 正常返回，再經本機 fill／clear／copy helpers，停在下一個 range helper 開始執行前。

檢查器：[check_v4160_b1_fallback_rf_static.py](check_v4160_b1_fallback_rf_static.py)；證據：[JSON ledger](v4160-b1-fallback-rf-static.json)。本輪使用原始 bytes、CFG／def-use 與固定區間證書，沒有執行韌體、建立可變 target 狀態模型、操作硬體、重播或連線 target。沒有增加 C 重建 bytes 或提高覆蓋百分比。

## Caller 實參與 RF 內部選路

Caller 仍是前階段完整 initializer，其實參為：

```text
(27, 328, 8*(k+14), 8*(k+138))
k = min(fresh U16[config64+16], 251)
```

這組實參不直接等於 RF helper 的選路條件。`0x64298／0x64382` parent 會先發布固定 pointer words，包括 Q=`0x40025000`、T=`0x40024200`、R=`0x40024100`、descriptor=`0`，並將自己的 state byte 設為 `1`。所選 tail 路徑通過兩次 fresh state 及另一個固定指標比較後，才明設 A0=`13` 呼叫下一層 RF helper。

因此證書保留各個 fresh 取樣時 pointer／state／frame 的保存條件，沒有把 caller 的 `27` 當作 helper 的 `13`，也沒有將先前 publication 自動視為之後的真實取樣結果。

## 同一次 RF 呼叫內的 Q 與 fallback

重用原始完整函式與所選分支證書，將以下 233 筆寫入區間逐一與受保護欄位比較：

| 分類 | 筆數 |
|---|---:|
| Parent 早期固定 publications | 6 |
| 至 Q capture 前的分類區間 | 96 |
| Q capture 後至 RF 正常返回的分類區間 | 131 |
| **合計** | **233** |

這是包含替代分支的保守區間集合，不是單次執行的 store 次數。所選範圍涵蓋 state=1 時 RF helper 的 T-low-bits 零／非零路徑、descriptor 零的 reset，以及 large helper 的實際 magic 或匹配 nonmagic helper 路徑。各路徑的必要 fresh 值、normal returns、wait 完成、saved words 與 memory-base projections 仍須成立。

在這些條件下，同次 parent 發布的 Q 可接到 large helper 的 `+0x160` capture，再保持至正常 RF 返回。回覆為：

```text
A0 = fresh U32[0x400250d0] & 0xf0ffffff
```

該遮罩清除 bits 24..27。Fresh load 不視為先前某筆 MMIO store 的 readback，也不推定為固定成功碼、U16 結果、硬體完成或校準正確。Tail 返回時自己的 state byte 已清為 `0`，fallback 仍條件式保持為 `0`。

每一筆 RF 投影都在數值上避開 fallback、config64／clock 來源的 96 bytes、role 物件 296 bytes、count／capacity／gate／table pointer、保守的完整 table 範圍、timer head／名義 timer node、small／remainder／large headers 及兩個 APP task bytes。對未建立 timer node 的前階段替代路徑，該區間僅是保守排除，不宣稱節點存在。

## 返回 initializer 後的 fill／clear／tail／copy

| 接點 | V1.31 | V1.40 |
|---|---|---|
| 第一個 RF call | `0x537b2 → 0x64298` | `0x53860 → 0x64382` |
| 正常返回 link | `0x537b6` | `0x53864` |
| 下一個 prefix | `0x53868` | `0x53916` |
| 本輪最終截止 call | `0x53896 → 0x43e8e` | `0x53944 → 0x43f1a` |

RF 返回後，完整 caller 的直線 suffix 先呼叫 fill wrapper 與 clear leaf，再還原 initializer 的 S0／RA／S1／S2／SP，尾跳至另一個 wrapper／prefix：

1. 匹配 fill 清除 `[B+156,B+184)` 的 28 bytes；正常 A0 前移至 `B+184`。
2. 清除 B+196 的 word 與 B+192 的 byte。
3. Initializer 釋放自己的 16-byte frame 後尾跳；下一個 wrapper 清除 B+200 的 byte 與 B+204 的 word。
4. 新 prefix 建立 32-byte frame，請求將 config64+24 的 6 bytes 複製至 B+232。
5. 在下一個 helper call 前設 A0=`0`、A1=`16383`。匹配 copy 不定義 A2，後續指令也不改 A2，因此仍為 `6`。

六個資料目的區間均在原本的 B296 物件內，另核對 fill／copy 共用控制 word `0x4002420c`，共七個範圍包絡。它們保留 fallback、上游來源／metadata／table／timer／task 範圍；物件中先前取樣保存的 B+193／B+201 也不受這些特定 stores 影響。

Copy 是六次有序的 fresh byte load／store，不是原子來源快照。匹配 RAM helpers 的完整原指令、first-copy 來源與 strict sparse HEX 已核對；這些仍是候選映射，沒有證明實際 installed provider。CPU 控制 word 的保存／回寫指令也不證明硬體狀態已恢復。

## 驗證與仍未關閉的邊界

134 筆 publisher／RF return／post-helper／capture／leaf／state 原指令變異檢查必須拒絕，並比對完整 ledger、233+7 個區間、fresh masked-word 性質及 reused original-body guards。兩種模式都必須通過：

```powershell
python analysis/check_v4160_b1_fallback_rf_static.py
python -O analysis/check_v4160_b1_fallback_rf_static.py
```

結論保留前階段 gate 零分支與 source／timer 條件，以及匹配程式／ISA／first-copy、有效且不回繞／不別名的 owned frames／objects／heap、保存字、正常存取／callee／poll 完成、無不利 MMIO／FENCE／IRQ／DMA／reentry／外部 writer 等前提。數值分離不能證明物理副作用分離，未知 RMW／DIV payload 的數值意義也沒有被補成已知硬體功能。

本輪截止時 fallback=`0`、gate=`5`、count=`6`，下一個 helper 實參為 `(0,16383,6)`；新的 32-byte frame 仍活躍。尚未執行 `0x43e8e／0x43f1a`，也沒有證明整個 initializer 已返回 gate／primary。非零 gate 分支的 outer initializer、後續登記／tail、實際綁定／來源保存與完整事件消費保留釋放期仍待分析。
