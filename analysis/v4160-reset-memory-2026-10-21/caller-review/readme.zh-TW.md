# Reset 記憶體 helper 呼叫端審查

**新增以 RET 結束的 C leaf 記憶體 helper，並不能直接取代原始 reset fallthrough。** 它需要已連結的入口 adapter、正確暫存器結果，以及經原始 CSR／clock／ROM 邊界的接續證明。A0、A1 仍帶到未知 ROM 邊界，僅測記憶體或一般 `void` C 結果不足以證明它們的值。

本唯讀審查涵蓋原始 ID2966 runtime SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，保留 **372 原始位元組、130 條指令**：reset `0x186AA..0x18734`（138／37），以及包含 cold tail 的 clock `0x1874A..0x18834`（234／93）。既有 reset／clock source map 與 resident candidate map 以 hash 綁定參考。舊 sixty-fifth-round 的 148 位元組／40 條獨立 reset 證據是**重定位後的原生布局**，不能拿來替代原始 reset 的 PC pair 或指令數。

## 原始正常上下文

Reset 前四條指令依各自原始 PC 的 AUIPC／ADDI anchor，建立 GP=`0x20004000`、SP=`0x20010000`。記憶體片段 `0x186BA..0x186F8` 為 **62 位元組、17 條指令**，以 fallthrough 進入與離開，沒有 CALL、RET。它將 `[0x1AB60,0x1ABE0)` 的 32 個 word 複製到 `[0x20004000,0x20004080)`，再把 `[0x20004080,0x2000C958)` 共 8,758 個 word 清零。

| `0x186F8` 記憶體片段結束暫存器 | 原始正常值 | 下一個相關使用點 |
|---|---|---|
| A0 | `0x2000C958` | 保留至未知 ROM 邊界 |
| A1 | `0x2000C958` | 保留至未知 ROM 邊界 |
| A2 | `0x20004080` | Clock `0x1875E` 先覆寫，才讀取 |
| T0 | `0x3A1`，最後從 `0x1ABDC` 讀取的 word | 立即於 `0x186F8` 被 LI 覆寫 |
| RA | 入口原值不變 | `0x18720` clock JAL 先覆寫，才有正常路徑讀取 |
| GP | `0x20004000` | 在已審查 reset／clock 路徑保持不變 |
| SP | `0x20010000` | 用於 clock 的實際 16-byte frame |

複製／清零次數與終點值是正常固定上下文下，由靜態迴圈推導的算術結果，不是執行 RV32 的證據。原始記憶體片段不設定其他 GPR，也不存取 SP。來源 postcondition 與較窄的本地存活性是不同宣稱：A2／T0／入口 RA 在正常路徑先被覆寫，但這不證明任意非同步觀察者都看不到它們。

## Clock 與 CSR 接續

原始順序為：`0x186FA` 寫 CSR `0xBC0=31`；`0x18700` 寫 `0x804=3`；`0x1870C` 設定 MSTATUS 的 `0x1888` 位元；`0x1871C` 寫 MTVEC=`0x803B`；`0x18720` 呼叫 clock `0x1874A`、設定 RA=`0x18724`；如果 clock 返回，才於 `0x1872C` 寫 MEPC=`0x9008`，再於 `0x18730` 終結式跳轉 `0x40000`。SET_BITS 不是整個 MSTATUS 賦值。這些運算元不證明自訂 CSR 意義、特權可用性或中斷排除保證。

Clock 沒有 CALL，也沒有明確參照 A0／A1／T0／GP／RA；`0x1882E` 的 RET 隱含讀取入口 RA。A2 首次出現是在 `0x1875E` 定義 `LUI A2,0x20`，因此在使用前已覆寫記憶體片段的 A2。Clock 於 `0x18754` 將 SP 減 16，存取 frame 偏移 8、12（正常位址 `0x2000FFF8`、`0x2000FFFC`），於 `0x1882C` 還原 SP 後 RET。部分 poll 路徑沒有原始 timeout；正常返回是本審查的前提，不是已驗證保證。

原始終結跳轉的正常狀態包括 GP=`0x20004000`、SP=`0x20010000`、A0=A1=`0x2000C958`、A2=`0x20000`、T0=`0x9008`、RA=`0x18724`、MEPC=`0x9008`。A3–A5 是 clock 路徑的結果，不是記憶體 helper 建立的值。實機 ROM 與所需輸入尚未綁定；既有 resident candidate 只是候選，其初始化行為不能證明實際 ROM 的輸入已無關或會接受此狀態。

## Adapter 還需證明什麼

Adapter 必須提供真正的 C-helper 返回 link，並將返回接到 `0x186F8` 或明確連結的等價位置。一般 JAL link 是實際呼叫位置的下一個 PC，不會自動成為 `0x186F8`。只還原最終 SP，不證明新增堆疊寫入有效或等價。原生 helper／adapter 仍需核對暫存器 write-set、GP／SP、記憶體界線，以及不存在隱藏呼叫或未解析 libc helper；A0／A1 必須產生原始結果或在未知 ROM 邊界前另外適配。

本地正常路徑 deadness 只允許有限範圍地處理舊 A2／T0／入口 RA，不代表整個 reset-entry、非同步中斷或 ROM ABI 等價。Clock 呼叫若被重定位，其自然 RA link 也會改變；原始 ROM 邊界 RA 是 `0x18724`，需維持必要邊界，或證明實機 ROM 忽略差異。Leaf helper 測試不能解決此問題。

應保留原始 CSR／控制流程次序，以及不設定 link 的終結 ROM 跳轉。相鄰 `0x18734` 的 MRET 不是原始 jump 後的正常 fallthrough，直接跳到 main `0x9008` 也沒有重現未知 ROM 初始化。`0x40000` 的 absolute symbol 同樣不提供 resident 實作。實機 ROM 身分、實體 RAM／堆疊、MMIO／clock、中斷、特權、完整連結配置與 OTA 相容均未證明。

`audit.py --image <原始 BIN> --r2 <radare2 路徑>` 可輸出來源審查，不執行原始程式、ISA 模擬、網路或裝置 I/O。`caller-contract.json` 區分來源值、本地存活性及整合待證事項；`verification.json` 保留原始指令證據。
