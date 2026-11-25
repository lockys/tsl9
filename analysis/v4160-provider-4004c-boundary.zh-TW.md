# v4.1.60 `[0x4004c]` 槽位邊界與 NV caller

2026-11-26。原廠 APP `ID-2966-V4.1.60-decoded.bin` 共 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批僅做本機靜態掃描與有限指令解譯，不執行 provider，不操作設備。

## 身分與來源仍有界線

APP 的本次名義映射為 `[0x8000,0x1ac00)`；槽位 `0x4004c` 不在其中。從 APP 的槽位 load 可以確認取址與呼叫參數，不能直接讀出該槽位的安裝值或 provider 函式體。

既有 [V1.31 resident copy reference](resident-copy-reference-2026-10-21/source/README.md) 已記錄另一份本機 SDK carrier 的候選：該候選槽位值是 RAM 位址 `0x20000332`，其初始化搬移的條件性映射對應 carrier `0x405a2..0x405dc`。該歷史文件同時明示沒有設備安裝身分證據，並記錄第二初始化來源缺尾端四 bytes。因此本次沒有把它認定為 v4.1.60 的實際 provider，也沒有拿它填入 APP 或本測試的合成槽位。

該參考 helper 還包含 `0x4002420c` 的保存／清零、`FENCE.I`、逐 byte 操作與條件性恢復，不能在未知安裝身分時當成無條件標準 `memcpy`。本次未重新驗收該歷史套件；以上為指向既有證據的索引。

## 有限形式掃描

新增 `check_v4160_provider_4004c.py` 掃描整個 APP 的每個 halfword 對齊位置，只匹配以下**相鄰**形式：

1. `lui base,0x40`，base 不是 x0。
2. 緊接 `lw reg,76(base)` 或 `sw reg,76(base)`，包含對應 RVC word load/store 編碼。

結果為 **41 個 load 候選、0 個這種形式的 word-store 候選**。這不是完整 CFG 或所有 writer 的普查：可能包含資料／指令中段的巧合編碼，並漏掉非相鄰取址、其他基底計算、較窄寫入、別名、外部 resident、中斷及硬體副作用。不能從 0 個 store 候選推出全域無 writer，41 個 load 也不等於 41 次實際呼叫或相同 provider 身分。

候選 load 位址：

```text
82ac 8400 92c2 9ce4 9e60 9e88 a0d8 ae66 c77a d1d6 d23e d2c4
1132a 12934 12a44 12c02 12e58 12eea 12f4c 13056 130da 1313c
131c6 1320c 1323c 1326c 1329c 132cc 142b6 14332 14950 14aa2
14bec 14c18 16bee 16d0a 17796 179a8 17a3c 1858e 1979e
```

其中 queue 的 `0x12c02` 已有[原指令串接驗證](v4160-transfer-receive-chain.zh-TW.md)。本次另用 radare2 離線解碼並解譯 `0x1979a..0x197b8` 的 NV caller，確認另一個已存在 C 重建的參數合約。

## NV caller 的原指令合約

| 位址 | 作用 |
|---|---|
| `0x1979a..0x1979e` | 形成 `0x40000`，讀取 `[0x4004c]`；發生在配置本函式 frame 之前 |
| `0x197a0..0x197a4` | 配置 16-byte frame，目的指標暫存 A4，保存 RA |
| `0x197a6` | A2=`入口 A1 << 2`，採 RV32 截斷，例如 `0x40000000` words 變成 0 bytes |
| `0x197aa..0x197ae` | A1=入口 A0；A0=入口 A2；以剛讀得的 A5 間接呼叫，跳轉目標清除 bit 0 |
| `0x197b0..0x197b6` | provider 正常返回後恢復 RA、將 A0 設零、恢復 SP 並返回 |

即三個入口參數 `(source, words, destination)` 被投影為 `(destination, source, (words*4) mod 2^32)`。provider 的返回 A0 被捨棄，caller 的 0 返回值本身不是複製成功證據。參見既有 [nv_read_registers.c](../src/native/nv/nv_read_registers.c)；本次沒有把既有 C 換名當作新重建。

## 重現與測試

```powershell
python analysis/check_v4160_provider_4004c.py
python -O analysis/check_v4160_provider_4004c.py
```

使用 Python 標準庫、原 BIN 和已發布的 `test_v4160_zero_id_queue_cpu.py`。腳本從自身路徑定位 BIN，可在其他工作目錄執行。

```text
PASS: 41 adjacent load candidates; 0 adjacent word-store candidates; 252 NV-wrapper boundary cases; fresh-pointer reload; 2 mutation controls
```

252 個 NV caller 案例為 3 個 source × 7 個 word count × 3 個 destination × 4 個合成 slot value。涵蓋零值、RV32 左移回繞、奇數指標清 bit 0，以及把已知 APP 位址 `0x19bf1` 當成純數值的 target。所有案例都在 target 停止，不執行零地址或任何目標函式，也不宣稱這些指標或長度實際可達、有效或安全。

重用同一個解譯器記憶體物件並逐例更換 slot value；逐例確認原指令在入口 SP 未變時重新讀 slot、完整 A0/A1/A2、返回 PC、唯一的 pre-call stack store。接著只合成「SP／堆疊未改、provider 返回 A0=`0xdeadbeef`」，重跑 caller epilogue，確認最終 A0=0 與 RA/SP 恢復；這不是 provider ABI 的證明。

兩項記憶體複本負向對照：把 `0x1979e` 的 C.LW 改成 C.SW，掃描結果必須變成 40 load 加 1 store；把 `0x197a6` 的 shift 2 改成 1，NV 參數檢查必須失敗。原 BIN 不變，一般與 `-O` 均通過。

本批沒有新增 C/C++ 重建 bytes 或重算覆蓋率。下一步可離線交叉核對較早 SDK carrier 的 slot／初始化證據，或擴充特定已確認 caller 的資料流；仍須保留「參考候選不等於設備已安裝 provider」的界線。
