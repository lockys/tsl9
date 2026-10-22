# Resident memory：真正 volatile native adapter

[English](readme.en.md)

這輪只編譯與靜態檢查；**不可在 HOST 執行此 adapter**，它含真正的 volatile MMIO 與 FENCE.I。已封存的共享 C 演算法透過普通 source include 使用，沒有把原始 bytes、opcode template 或 callback stub 編入新實作，也沒有 link／BIN／硬體／RV32 或 ISA 執行。

三個 public entry 都接受三個 u32、回傳一個 u32。第二個且最後一個 profile 的實物如下：

| entry | 原始 candidate bytes | 新 entry bytes | 尚存差異例 |
| --- | --- | --- | --- |
| compare 200004BC | 62 | 52 | 額外改寫原本保留的 A6，scratch liveout 不同 |
| fill 2000039C | 46 | 48 | 額外改寫 A3／A6／A7，且超出原範圍 2B |
| copy 20000332 | 58 | 52 | 額外改寫 T0／A7，其他 scratch 值也不同 |

三個 entry 的總和是 **152B**。它們實際無 frame、call、context 或 sret，沒有寫入 A1／A2／SP／S／GP／RA；MMIO load-save、zero store、FENCE.I、null/count tests、fresh byte effects 與保存值 restore 都存在。這些是有界 contract 改善，不是完整原始 register／fault／async prefix ABI。compare／copy 更短也不代表未使用尾端已獲所有權，fill 更不能直接放回原 46B 範圍；固定 placement 與 installed provider 仍未准入。

整份 ET_REL 仍真實保留另外八個 global functions **230B**：三個 context／sret 版本的共享演算法（64／62／64B）與五個真正 I/O 函式（10／6／8／8／8B）。沒有把它們隱藏或假稱已由 linker 移除。總計 **382B／138 指令、0 UND、0 RELA**；這個總數不是三個 entry 的大小。

## 兩個實測 profile

第一個普通 C wrapper 每個 30B，但配置 64B frame 並呼叫共享 context／sret 函式，A1／A2 被改寫；整份物件 320B／125 指令／3 CALL_PLT。這是真實失敗診斷，sources／recipes 留在本機 build/ordinary-v1，不以當前來源假稱舊 receipt 的 current-root replay。

唯一第二次適配只增加 source always_inline declarations，與 A0／A1／A2 的空 asm read/write 返回邊界 bridge。共享演算法的 body 完全未改；context 已由實際 IR／機器輸出消除。I/O 函式是真正 volatile byte／word 存取；只在操作正常完成後回 1，硬體 fault／trap 不會被偽造成 cleanup。新增 zifencei 是為了這個真 FENCE.I，其餘 pinned -Oz profile 不變。沒有第三 profile 或 flags sweep，舊 HOST 演算法測試不重跑。

## 可攜入口與證據

```sh
sh experiments/tsl9-resident-memory-native/verify.sh --project-root "$PWD" --tool-dir LLVM --language both
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
```

fresh CLI 可給 `--build-root NEW`，只能是 model/build 內新目錄；省略時用 UUID，各 mode 留 verification.json、object／IR／MD／完整 disassembly 與實際工具 logs。預設 check 只有來源／metadata；明示 receipt 才重讀 archives、全部五份來源加 resource header、完整 recipes／tools／artifacts，缺檔即失敗，replay 不執行或編譯 adapter。

CASE 是發布的 analysis/v4160-resident-native-2026-10-22，或工作副本 apk-analysis/tsl9-v4160-resident-native-2026-10-22。Python／sh 入口可攜，但本輪量測只准入既有固定 Windows NDK LLVM hashes。兩份 SDK candidate 的地址與原始契約是條件式參考，不能視為 physical installed ROM。完整原始 ABI、provider readiness、實體／OTA 證明保持 false。
