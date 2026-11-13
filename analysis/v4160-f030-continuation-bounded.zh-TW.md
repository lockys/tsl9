# F016 → F030 → F038 的有界靜態路徑

以 76,800-byte `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`（SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）為參考，假設線性 base `0x8000`。以下按 `0xf016`、`0xee9a`、`0xbd46` 三個指定起點解碼，不表示已證明所有指令邊界、入口或可達性。使用本機 radare2 6.2.4 離線讀取 BIN；未執行或模擬韌體。

| PC | 原始 bytes | 靜態解碼與條件式效果 |
|---|---|---|
| `0xf016` | `4111` | `sp -= 16`；`0xf018` 保存進入時 s0 至 `[sp+8]`。 |
| `0xf01a`、`0xf01e` | `17d4ff1f`、`1304a4f6` | `auipc s0,0x1fffd; addi s0,s0,-150`，算得 `s0=0x2000bf84`。 |
| `0xf022`、`0xf024` | `06c6`、`26c2` | 保存進入時 ra、s1 至 `[sp+12]`、`[sp+4]`。 |
| `0xf026`、`0xf02a` | `a304b400`、`aa84` | 寫進入時 a1 的低 byte 至 `[s0+9]`；複製進入時 a0 至 s1。 |
| `0xf02c` | `eff0ffe6` | `jal ra,0xee9a`，呼叫時 ra 為 `0xf030`。 |
| `0xf030`、`0xf034` | `23059400`、`efc03fd1` | `sb s1,10(s0)`；`jal ra,0xbd46`，後者設 ra=`0xf038`。 |
| `0xbd46`、`0xbd4a`、`0xbd4e` | `17050020`、`1305b51c`、`8280` | 形成 `a0=0x2000bf11` 並 `ret`。 |
| `0xf038`、`0xf03a` | `8547`、`2300f500` | `a5=1`，將其低 byte 寫至 `[a0]`。 |
| `0xf03e`、`0xf040`、`0xf042` | `2244`、`b240`、`9244` | 從上述 stack slots 載入 s0、ra、s1；只有各槽仍保有原值時才是還原。 |
| `0xf044..0xf054` | `81465146814517050000130565e941016fa00f8d` | 設 a3=0、a2=20、a1=0、a0=`0xeee0`，回復 sp 後以 `jal x0,0x9124` 尾跳。 |

從 F016 順序進入、記憶體存取成功、EE9A 呼叫鏈正常返回、保留相關 s0/s1/stack，且前述 store 未破壞需要的保存槽時，F030 將原入口 a0 的低 byte 寫至 `0x2000bf8e`；BD46 正常返回後，F03A 將 1 寫至 `0x2000bf11`。EE9A 在 `0xee9e` 呼叫 BD50；讀取為零時跳至 `0xeed8` 的 epilogue，非零路徑另呼叫 `0x90b0`、`0xedf2`。不能假定這些呼叫必然返回或不改狀態。尾跳後是否返回原 caller 取決於 `0x9124`，不由本窗口證明。

本觀察也解釋兩個 ra 不可混同：F02C 連結到 F030，F034 連結到 F038，而 F040 從保存槽載入 ra；只有該槽在載入前未被寫壞時才等於 F016 的原入口 ra。保存槽可能與上述 byte store 或呼叫鏈的寫入重疊，不能單憑指令排除。前述純 C adapter 的標準 C 入口和尾呼叫並未證明能維持此 private state；BD46 的回傳 a0 也被 F038 使用。這不是完整 ABI、RAM owner、所有 caller 或純 C 替代證明，也不驗收整張 BIN。正式 owner 仍含 inline assembly；相關選區連結及候選實驗見 `analysis/v4160-f030-bd46-real-provider-selected-link.zh-TW.md` 和 `experiments/v4160-f030-purec-real-bd46-next/RESEARCH.md`。
