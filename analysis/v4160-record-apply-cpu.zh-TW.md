# v4.1.60 `0x93aa` 狀態啟用與配置後串接

2026-11-26。使用 76800-byte 原 APP，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。在有限 RV32IMC 解譯器中執行原指令；所有資料、MMIO 與服務返回都是本機合成模型，不操作設備。

## 原指令的條件與效果

`0x93aa` 依序讀 `P=U32[gp+84]`、`U8[P+2]`、`U8[0x2000bec0]`，將兩個 byte 做 OR。兩者都是零時直接返回；任一非零時，依序執行：

| 順序 | 操作 |
|---|---|
| 1 | `U8[0x2000bec2]=0` |
| 2 | `U8[0x2000bec1]=0` |
| 3 | `U32[0x2000bebc]=0` |
| 4 | `U16[0x40000424]=0` |
| 5 | 讀 `U16[0x40000400]`，寫回 `old_u16 OR 1` |

條件來源 `0x2000bec0` 本身不清除。兩個 byte 讀取都發生，沒有短路或 NULL guard；即使第二個來源已為非零，無效的 P 仍會在前一個 byte 讀取時失敗。測試以 P=0、第二來源=1 得到 `unmapped access 0x2 size 1`，沒有替原碼補出防護分支。

此 leaf 不呼叫其他函式、不建立 stack frame、不讀 `0x2000becc` 主指標或 heap records。只有 A4/A5 被改寫：零條件時兩者為零；成立時為 `old_u16 OR 1` 與 `0x40000000`。A0、RA、SP、GP、S 與其他暫存器均保持。這證明的是合成 MMIO 上的讀寫寬度／順序與 bit 操作，不是硬體功能、時序或 IRQ 行為。

## 接回 `0x9454`

沿用上一批的配置 fixture 與明示正常返回服務：`[0x40068]` 返回指定值，`[0x40070]` 返回零或固定合成 heap 指標；兩者改寫 caller-saved 暫存器並保存 SP／S／GP 與記憶體。服務函式體與實際 provider 綁定仍未執行或證明。

本批從 `0x9454` 執行，保留先前的配置請求、reset 與 record 初始化原指令，到 `0x93aa` 入口檢查可達性，再由同一 CPU／記憶體繼續返回 caller：

- 配置返回零：直接返回 A0=0，不到 `0x93aa`，不產生其五項 stores。
- 配置返回非零：恢復 S0/S1/RA/SP，再尾跳 `0x93aa`。是否產生 stores 只看上述兩個 byte；不重新檢查 records。
- `0x93aa` 返回後 A0 仍是配置服務指標，不能把它重新命名為此 leaf 產生的成功碼。兩個 byte 均零時，非零配置指標同樣可以正常返回而不做啟用 stores。
- 有舊指標時，前一段 reset 先把控制 bit 0 清零；若這次條件成立，leaf 再把 bit 0 設回一。條件為零則保持 reset 後的控制值。

串接測試核對服務順序／請求／continuation／SP、主／輔助指標、啟用來源、到達與返回路徑，並確認 leaf 執行前沒有其專屬 stores。leaf 前後比較全部記憶體區域，包含 heap 和 canary，確保這一步沒有修改 records；配置初始化的完整預期值另由上一批 `test_v4160_record_allocate_cpu.py` 回歸核對。尚未接回完整 consumer 上游。

## 重現與驗證

```powershell
python analysis/test_v4160_record_apply_cpu.py
python -O analysis/test_v4160_record_apply_cpu.py
python analysis/test_v4160_record_allocate_cpu.py
python analysis/test_v4160_zero_id_queue_cpu.py
```

新的 apply 測試只需標準庫、原 APP 與上述兩個既有測試模組，不需 SDK carrier。一般與 `-O` 輸出：

```text
PASS: 65536 activation pairs; 65536 control words; 16 A0 probes; 4096 allocation/apply chains; null-config guard; 2 mutations; providers NOT executed
```

65536 activation pairs 覆蓋兩來源 byte 的所有組合；另 65536 control words 覆蓋控制 halfword 全值，確認 ORI 只設定 bit 0。16 組 A0 探測包含 0／1／合成指標／`0xffffffff`；4096 組串接為所有 byte 參數 × 舊指標零／非零 × 配置失敗／成功 × 四組啟用來源。

兩項記憶體複本變異分別讓 OR 忽略設定來源、將 ORI 的 bit 0 改為 bit 1，必須被精確 stores 檢查抓出。原 APP 未改；共用 CPU 僅新增標準 RV32 ORI 解碼，仍以 `put` 限制為 32-bit。未知指令、區域或目標繼續採失敗即停。

本批增加的是原指令驗證，沒有增加 C/C++ 重建 bytes 或重算覆蓋率。仍待釐清 provider 身分／保存合約、全域狀態的後續消費及 `0x18ca4` 等 handlers。
