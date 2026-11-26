# v4.1.60 `0x9454` 配置請求與 record 初始化

2026-11-26。僅使用本機原 APP（76800 bytes；SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`），離線執行 `0x9454`、wrapper `0x9410` 與本機 reset `0x93ee` 的原指令。未知服務與後續 `0x93aa` 不執行，不操作設備。

## 分支不是「大於 19 就拒絕」

`0x9454` 比較完整無號輸入 n，兩條路都會提出配置請求：

| 輸入 | wrapper count／請求 bytes | 非零返回指標 P 之後的 halfword stores |
|---|---|---|
| 0–19 | n+1／`6*(n+1)` | n 筆 `(3000,40,80)`；再於 `P+6*n` 寫 halfword 0 |
| >19 | 2／12 | `P+0=3000`、`P+2=n&0xffff`、`P+4=0`、`P+6=0` |

sentinel 只寫第一個 halfword，餘下四 bytes 不初始化。n=0 仍請求 6 bytes，卻只把 P 的前兩 bytes 寫零。本測試保留並核對其他 canary bytes，沒有補造零值或完整 record 初始化。

## 舊 word、清除與 reset 的順序

主 word 位址 `0x2000becc`，相鄰輔助 word 為 `0x2000bec8`。`0x9410` 先讀主 word：

1. 非零時，以其值作 A0 呼叫當次 `[0x40068]` 所載 target。
2. 正常返回後清主 word，再清輔助 word。
3. 呼叫 `0x93ee`，依序做合成 halfword 操作：`[0x4000042c]=0xffff`、`[0x4000043c]=0`、`[0x40000400]=old_u16&0xfffe`。
4. 然後才建立 `6*count` 的 A0，恢復 wrapper 的 S0／RA／SP，尾跳當次 `[0x40070]` target。

主 word 原為零時，不呼叫第一個服務、不清輔助 word，也不執行 reset，但仍會要求配置。測試分別在兩個服務入口檢查這些 word／控制值，確認順序而非只看最後結果。

「free／allocator」是槽位角色的描述性推定；本批沒有執行服務函式體、證明其安裝身分或實際資源生命週期。第一服務的 0、1、`0xffffffff` 返回值均不改變這段正常返回後的控制流程。

## 配置失敗與成功邊界

兩條分支都先將配置 target 的 A0 寫入主 word，才測試是否為零。零值時不寫 heap record、不進 `0x93aa`，恢復 caller S0/S1/RA/SP，返回 A0=0。

非零時按上表初始化合成 heap，恢復相同 caller 狀態，再尾跳 `0x93aa`。本批停在該入口，不聲稱後續套用完成或已產生最終返回值。

wrapper 自身的計算是 RV32 `6*count`；本批從 `0x9454` 提供的 count 只有 1–20 或 2。較大原始 n 在大分支仍只請求 12 bytes，且 record 內的 n 只寫低 16 位；不能把 n 當作這條路徑的配置數量。

## 重現與測試

```powershell
python analysis/test_v4160_record_allocate_cpu.py
python -O analysis/test_v4160_record_allocate_cpu.py
```

只需 Python 標準庫、原 APP 與已發布的有限 CPU；不需 SDK carrier。一般與 `-O` 均通過：

```text
PASS: 1024 parameter/old-pointer/allocation cases; 12 full-width cases; 16 reset-word probes; 3 free-return probes; 2 mutations; providers/apply NOT executed
```

1,024 組為 n 的全部 byte 值 × 主 word 零／非零 × 配置返回零／固定合成指標。另有 12 組完整 32-bit n、16 組 reset word 初值與三種第一服務返回值。合成 heap 有獨立 128-byte fixture，不會呼叫主機配置／釋放 API 或假裝 target 已真的配置足量空間。

逐例核對服務順序、請求 bytes、返回 PC／SP、服務入口的全域狀態、reset／主指標發布順序、完整 heap 與精確 stores，以及 caller 暫存器恢復。記憶體複本分別把 wrapper 的倍率 6 改成 5、record 的 40 改成 41，必須被請求／記憶體檢查抓出。原 APP 不變，共用解譯器未修改。

未知服務只接受指定的正常返回：刻意改寫 caller-saved 暫存器，保存 SP／S／GP、stack、全域資料、heap 及合成 MMIO。這些是明示前提，不是 ABI、實體配置大小、生命週期或 IRQ 安全的證明。也未把此函式接回完整 consumer 後續鏈。

本批沒有增加 C/C++ 重建 bytes 或重算覆蓋率。仍需離線追查 `0x93aa` 的套用流程、未知服務及其他 handlers，不能把配置請求或尾跳入口當作設備功能成功。
