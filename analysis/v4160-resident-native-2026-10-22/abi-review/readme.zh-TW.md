# Resident 原生三參數介面：獨立 ABI 審查

[English](readme.en.md)

已讀取實際 C11／C++17 ET_REL、IR、依賴檔與完整反組譯。最後三個公開入口使用三個 `uint32_t` 參數、回傳 `uint32_t`，直接執行 volatile 記憶體讀寫與真正 `FENCE.I`；沒有舊 context／sret、堆疊或巢狀呼叫。這是已驗證的局部進展，完整原始暫存器 ABI、配置位置與硬體相容仍未准入。

## 實際產物

| 介面 | 原始候選大小／指令 | 最後原生大小／指令 | 額外寫入的原始保留暫存器 |
| --- | --- | --- | --- |
| compare `200004BC` | 62B／19 | 52B／19 | A6 |
| fill `2000039C` | 46B／14 | 48B／16 | A3、A6、A7 |
| copy `20000332` | 58B／18 | 52B／17 | T0、A7 |

copy 原始程式本來會寫 A6；不能把它列成新增破壞。fill 的 A3 也是原始程式不寫的暫存器，因此上表包含 A3；原始 A3/A4/A5 等 scratch 的最終值差異另須評估。

三個公開入口合計 **152B／52 指令**。整個物件保留另外三個真實 context 演算法與五個真實 I/O 函式，合計另 **230B／86 指令**；全物件 **11 FUNC、382B／138 指令、0 RELA、0 UND**。未把未使用全域函式藏起來，也未連結、匯出 BIN、執行 RV32 或重跑未變的 HOST 測試。

第一次普通 C 版本的三個 wrapper 各 30B，但各建立 64B frame、經 CALL_PLT 呼叫共用演算法並使用本機 sret/context。其全物件為 320B／125 指令、3 RELA。一次有依據的修正是在 include 邊界加入 `always_inline` 宣告，並用空的三暫存器輸出橋保留回傳 A0 與原始完整 A1/A2。共用演算法本文未改，編譯 flags 只為實際 `FENCE.I` 加入 `zifencei`。第一次的來源快照／收據只屬歷史證據，不能在已改來源的目前根目錄宣稱成功重播。

## 獨立核對範圍

`review.py` 獨立讀取十一個真 FUNC 的每項指令欄位，與實際 LLVM 反組譯逐欄比對，核對完整 owner、直接分支邊界、暫存器寫入、記憶體寬度、IR、實際來源與工具、六個 `-MD` source/header/resource 輸入及四個命令的證據。Producer 唯讀 provenance 重播只是其中一層，不取代獨立 ELF／指令檢查。

三個最後公開入口有完整、固定版本的 operand／CFG inventory；它不是 CPU 狀態機或指令解譯器。由實際結構可確認：

- READ32 `4002420C`、WRITE32 零與 `FENCE.I` 均先於初始指標／長度測試；所有正常出口恢復同一個保存 word。
- compare 以完整 A1 比較 LBU，正常回傳 0／1；fill 依序寫低 byte、回傳前進後位址；copy 向前 read-before-write、回傳原目的位址。實際 RV32 add／迴圈保留模數位址行為。
- 最後入口完全不寫 SP、RA、GP、S 暫存器、A1、A2，沒有呼叫或額外 spill。IR 中的本機 context／sret 已消除，真正的三參數與空橋完整輸入也有核對。
- 每語言三個單一 raw operand 反例實際解碼後拒絕：比較來源 A1 被改、恢復錯誤保存 word、copy byte load 被改成 halfword。

以上正常記憶體／回傳值投影以前述位址可讀寫、存取正常返回為前提，不是所有狀態的等價證明。新增的 A3/A6/A7/T0 寫入是尚待 caller／觀察者證據釐清的義務；不能僅因一般 C ABI 容許 caller-saved 就自動忽略，也不能據此宣稱所有 conventional caller 都不相容。

原始 compare/fill 在 byte 存取前先改 A0，候選 compare/fill 在不同位置更新，故 fault／中斷時的 prefix 不同。原始／新程式的 scratch 結果值也不同。即使正常 A1/A2/SP/RA 投影成立，仍沒有已安裝 resident 身分、MMIO 故障、非同步等價或整體硬體證明。

fill 的 48B 超過原 46B。compare/copy 較短也不代表原始剩餘 10B／6B 區域已取得所有權。本輪沒有補齊 tail、固定地址、搬移呼叫、借用原碼或放寬配置檢查。

## 使用

預設模式只驗封存來源／摘要，不讀取發布排除的 build 產物：

```sh
python3 -B <case>/abi-review/check.py --project-root <ROOT>
sh <case>/abi-review/verify.sh --project-root <ROOT>
```

明確提供新原生 mode folder，實讀 object／IR／依賴與命令產物，另寫不可覆蓋的新收據；重播只讀取，不編譯或執行：

```sh
python3 -B <case>/abi-review/review.py --project-root <ROOT> --folder <MODE> --receipt <NEW-review.json>
python3 -B <case>/abi-review/review.py --project-root <ROOT> --replay <review.json>
```

`MODE` 必須含最後來源/profile 的 `verification.json`、`native.o`、`native.ll`、`native.d` 與實際四命令日誌。新收據寫在 MODE 之外，避免改變 producer 的實物集合。預設回報 `metadata_only=true`；只有實物模式回報 `actual_native_artifacts_read=true`。`selected.json` 是既有觀察摘要，不能代替新實物驗收。
