# V4.1.60 TX：header → copy loop 的 C 切片交接

靜態對照 [`header.c`](../experiments/v4160-tx-pure-c-subpath/header.c)、[`candidate.c`](../experiments/v4160-tx-copy-loop-pure-c/candidate.c)、[原始契約](transport-frame-2026-10-23/original-contract.md)和 [`transport_frame.c`](../src/native/receive/transport_frame.c)。PC 依既有[原始指令紀錄](transport-frame-2026-10-23/original-contract.json)，不是本次重新反組譯。兩個抽象記憶體型別**不能直接接合並聲稱 ISO C 等價**；受限共同物件和映射仍須設計及驗證。

## 切點與狀態

選中 bank `b=0/1` 後在 `0x8ace` 入口，令 `B=0x2000b18c`、`L=then-live s0`、`C=then-live s3`、`D=B+1062*b+6`。`L`、`C` 是 admission 呼叫返回後的值，不能假設保存了入口值。`0x8aec` 以半字寫 `0x7f55` 至 D；`0x8af0`、`0x8afa`、`0x8b00` 依序寫 `u8(L)` 至 D+4、`u8(L>>8)` 至 D+3、`u8(C)` 至 D+2。`0x8b0a` 是 header 出口與 loop 入口；`0x8b10` 以 `u16(a1)<L` 決定進入 `0x8b52` 複製或退出至 `0x8b14`。複製每次先讀 `[s1+a1]`，再寫 `[a5+a1+5]` 並更新 checksum；`0x8b14` 之後的完成、restore 和 tail transfer 不屬此兩候選。

| 狀態 | 交接 |
|---|---|
| `a1` | header 給 0；loop 後保留完整索引，非只保留低 16 位。 |
| `a4` | `((L>>8)+(L&255)+C)&255` 為初始 checksum；loop 累加實際逐次讀取的 byte。 |
| `a5` | header 輸出原始地址 D，loop 介面使用共同陣列中 D 的**索引**，不能直接傳入。 |
| `s0/s1` | `s0` 為同一 then-live L；`s1` 為原始來源地址，loop 需要其索引。不得以前置 guard 推定 post-call L。 |
| `a2/a3` | 分別為 b 和 B，loop 介面未回傳，但完成路徑仍需；整合層須保留。 |
| `a6` | header 不改變，入口值未知；loop 零次時原樣保留，非零次為最後一次 `D+舊a1`。若 loop 回傳索引，僅非零次可在有效映射下轉回地址，不能盲目轉換未知入口值。 |

## 共同物件與限制

- header 操作 `volatile struct tx_ram`，loop 使用單一 `volatile uint8_t` 陣列；僅將 struct 指標轉成 `uint8_t *` 並不足以證明 alias、生命週期、子物件邊界和指標算術合法。`uint8_t` 不保證是 character type；可另設合法 `unsigned char` 物件表示視圖，或明確證明特定實作契約，並相應改寫兩個候選。
- 設共同物件代表地址視窗起點 R，須以可逆 `index(x)=x-R` 轉換 D 和來源地址，證明每次實際存取落入同一有效物件，地址、索引與遞增不回捲。`L=0` 時原機不讀來源；即使受限整合要求 `s1` 可映射，也只是額外限制，不是原始指令必要條件。checksum 運算本身則須保留 modulo 2^32，不能要求一律不回捲。
- 寫 header 後才逐次讀來源；來源可 alias header 或 destination，前次寫入可影響後次讀取，不能使用來源快照或 `memcpy`。原始半字 `SH` 不能不加限制地視為兩次 byte store：little-endian 最終表示、volatile 事件、bus 寬度及中間觀察是不同問題。`volatile` 不保證原子性、同步或 DMA／中斷語意。
- 從 header 的 `a1=0` 出發，`L<=65535` 且無故障／干擾時經 L 次退出；`L>65535` 時比較值恆小於 L，原機無正常出口且完整索引最終回捲。有限 C 陣列契約排除後者，不能把早期 1039 guard 當作呼叫後 L 的保證。

本回合修正 header 兩處 checksum 加法，改以 `uintmax_t` 無號加總後轉回 `uint32_t`，避免特殊 C 實作的有號整數提升溢位；這不解決共同物件、private ABI、原址 relocation 或硬體問題。兩個候選尚未編譯或執行，Python 靜態檢查及事件例子不是 C 行為或完整 BIN 等價證據；沒有執行 target、模擬或操作硬體。
