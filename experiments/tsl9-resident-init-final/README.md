# 補齊 initializer 的外部直接目標本體

[English](readme.en.md) · [前輪 state constructor](../tsl9-resident-address-state/README.md) · [原 initializer](../tsl9-resident-init-5362e/README.md)

[C/C++](resident_init_final.c) 新增兩個完整本體，共 **38 CODE bytes／11 指令**。實際 C11／C++17 物件相同；2 個正尺寸 FUNC、2 筆 HI／LO relocations，正規化至原位址後與原 SDK bytes 全部一致。不是恢復出的原廠 C 原始碼。

| 完整範圍（半開） | Bytes／指令 | 原始作用 |
| --- | --- | --- |
| `0x57AC4..0x57AD8` | 20／6 | A0=`0x20003454`、A1=0、A2=28，尾跳 RAM `0x2000039C` memset provider |
| `0x63704..0x63716` | 18／5 | word zero → `0x2000347C`；byte zero → `0x20003478`；RET |

兩者自身 frame=0，沒有新的 CSR 或 opaque call。`0x57AD0/0x57AD4` 的 AUIPC t1／JALR zero,t1 是 **無 link 尾跳**，沒有把它改成一般 C call。新本體保留 incoming SP／GP／RA／saved registers 的指令關係；正常返回仍要求原 memset provider、有效記憶體、原 ROM／callee／IRQ／alias 等契約。

28-byte request 為 `[0x20003454,0x20003470)`，另外兩次 request 分別為 `[0x2000347C,0x20003480)` 與 `[0x20003478,0x20003479)`。它們都在前輪296-byte state request `[0x200033B8,0x200034E0)` 內，**不是新增 RAM 容量或整個 state 在返回時全零的證明**。相鄰 `0x57AD8`／`0x63716` 函式未選入。

## Caller 的完整直接目標清單

原 initializer 在 `0x537B6`／`0x537BA` 呼叫本輪兩個 providers；`0x537C6` 釋放16-byte frame 後，`0x537C8` 再尾跳前輪 `0x5E758`。從完整 caller bytes 獨立解碼的全部外部直接目標為：

`0x43E24`、`0x55BD4`、`0x55C48`、`0x57AC4`、`0x63704`、`0x64298`、`0x5E758`。

驗證器逐項核對完整本體證據、每個 byte 的既有或新增 provider，以及完整 caller 的 target set 相等；**7 個直接目標均有完整本體**。這只封閉直接目標本體清單，沒有封閉遞迴／間接呼叫、callback、memory effects、異步 IRQ 或初始化成功條件。

[init_final_abi.c](init_final_abi.c) 的 RV32 widths／數值位址／request bounds assertions 已以 C11／C++17 編譯；物件相同，allocated bytes=0，沒有 runtime provider。

## 組合與使用

實際非載入 ET_REL 組合為 **21,408 CODE＋256 DATA／7,331 指令**，1,377 正尺寸 FUNC、1,040 relocations。兩個真實缺口使具名依賴 **11→9**，memset import 已有前輪真實 provider；沒有新具名依賴或 stub。所有 input bytes／symbols／relocations 完整保留，原始 CODE 位址不重複，兩個獨立 ELF readers 一致。

[證據](evidence-v1.json) · [完整驗證](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-init-final/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機 APP／SDK、前輪 native artifacts 與 Windows NDK LLVM；無下載，其他平台未驗證。APP保持159 C/H、95.54%位元組覆蓋率，**不是功能完成率**。4-byte啟動來源缺口、實體 ROM／RAM／ISA／IRQ／Flash／OTA 相容性及 binding 前無 dispatch 仍開放。

未連入 APP、未產生 BIN，沒有 target／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。唯讀 initializer coverage／清零請求診斷是後續功能候選，尚未實作，不將靜態 coverage 當作初始化成功。
