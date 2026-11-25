# v4.1.60 取樣迴圈至 queue：原指令的條件性串接

2026-11-26。原廠 `ID-2966-V4.1.60-decoded.bin` 共 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本次使用本機 radare2 RV32 解碼，再以有限指令解譯器串接取樣函式、[已驗證的 guard](v4160-ingress-queue-chain.zh-TW.md) 與 queue 呼叫點；不執行韌體、設備或未知 provider。

## 取得的合約

`0x16a7c` 配置 48-byte frame，RA/S0/S1/S2 分別保存於新 SP 的 +44/+40/+36/+32，入口 A0 存入 S1。以下 SP 均指此新 SP：

| 位址 | 原指令作用 | 本次驗證 |
|---|---|---|
| `0x16a92..0x16a98` | 比較完整 A0 與 1；寫 word 至 `0x40010814` | A0=1 寫 16，其餘寫 1；`0x10001` 不等同 1 |
| `0x16a9a..0x16aa2` | A0=3；將入口 A1 存至 `sp+12`；呼叫 `0x16896` | 第一個返回值不進 frame；第一次呼叫改寫 A1 不影響後續載入 |
| `0x16aa2..0x16aae` | 恢復入口 A1 至 A0，再呼叫 `0x16896` | 第二個返回值也被捨棄；S0=0、S2=13 已在此前設定 |
| `0x16aae..0x16abe` | A0=0，呼叫後 `sb a0` 到 `sp+16+S0`，索引增加至 13 | 恰好 13 次取樣，按序寫 `sp+16..28`；完整返回值只保留低 byte |
| `0x16ac2..0x16ac8` | 寫 word 17 至 `0x40010810` | 發生於 13 筆 frame byte 寫完之後、guard 之前 |
| `0x16acc..0x16afa` | 檢查 frame 並呼叫 queue | ID 由前兩筆 byte 合成；長度取第 5 筆低四位且僅接受 1–8；payload 指向第 6 筆起的 8 bytes；tag 保留入口 A0 |
| `0x16afe..0x16b08` | 恢復 RA/S0/S1/S2、SP，返回 | guard 拒絕與滿 queue 路徑均驗證呼叫者暫存器／堆疊恢復 |

MMIO 位址只作為已觀察的 word 寫入地址，不在缺少外設證據時命名其硬體用途。

## 可重現驗證

```powershell
python analysis/test_v4160_receive_frame_cpu.py
python -O analysis/test_v4160_receive_frame_cpu.py
```

需要標準庫、原 BIN，以及前兩批已發布的 `test_v4160_zero_id_queue_cpu.py`、`test_v4160_ingress_queue_chain.py`。檔案路徑從腳本所在位置解析。

一般和 `-O` 輸出均為：

```text
PASS: 3328 per-position byte cases; 15 channel/command cases; all-zero rejection; zero-ID call; full-queue return; 13-to-12 loop mutation detected
```

3,328 案例逐一改變 13 個位置的所有 256 種低 byte，額外設定非零高 24 位以檢查 SB 截斷；這是逐位置測試，沒有枚舉全部 `256^13` 組 frame。15 組入口 A0/A1 組合覆蓋完整值比較、原 A1 恢復與 tag 來源。每次合成傳輸返回都刻意改寫全部 caller-saved 暫存器，再提供指定的 A0 返回值；保留 SP、callee-saved 暫存器與記憶體。

每例檢查 15 次傳輸的呼叫點／參數、13 次 byte store 的地址／順序／低 byte、兩次合成 MMIO 寫入、guard 路由。通過 guard 且有空槽者再檢查 queue 的所有 bytes 與 provider 入口參數，隨即停止，不執行 provider。另驗證全零 frame 被拒絕、只有長度 byte 為 1 的零 ID frame 可達 provider，以及滿 queue 返回完整函式的 caller。

負向對照僅在記憶體複本把 `0x16aa6` 的 `li s2,13` 改成 12，必須被捕獲狀態檢查抓出。原 BIN 雜湊未變。前兩批 guard／queue 測試也重新執行並通過。

## 尚未證明

這次的 `0x16896` 是**指定返回值的 hook**，沒有執行它的等待迴圈或外設存取，也沒有模擬 MMIO 行為。15 次呼叫都正常返回且保留上述狀態，是明確前提；實機中斷、資料是否到達、逾時與成功收到零的來源差異仍未證。任意高 24 位只測試 caller 的 SB 寬度，不主張實際傳輸函式會產生那些值。

未知 `[0x4004c]` provider 仍未執行，不能由到達呼叫點推論複製成功或可消費項目。本批補強原指令證據，未增加 C/C++ 重建 bytes 或重新計算整體覆蓋率。後續可將 `0x16896` 的原指令與合成狀態樣本串入此路徑，區分不同逾時階段對 frame 的條件性影響。
