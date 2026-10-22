# 原生記憶體 IO 與三參數 C/C++ 入口

[English](readme.en.md)

本輪沿用上一輪封存的可讀 C 演算法，以真實 volatile byte／word IO 與 FENCE.I 實作原生 port，提供三個 uint32 參數、單一 uint32 回傳的 C11／C++17 入口。**僅編譯與靜態核對，沒有執行這些 IO、RV32 或硬體，沒有 link／新 BIN。**

[原生 C/C++](../../experiments/tsl9-resident-memory-native/README.md) | [實際編譯](implementation/README.md) | [獨立 ABI 審查](abi-review/README.md) | [原 App callback](callback-review/README.md)

## 已修正與仍未符合的 ABI

第一個普通同 TU 版本實測三入口各 30 bytes／64-byte frame，內部仍傳遞 context／結構回傳，並改寫 A1／A2。整個物件 320 bytes／125 指令／3 個真實 CALL_PLT，未解析符號為零。

只做一個針對該差異的來源調整：讓共享演算法與 IO/helper 在入口內 always_inline，並用窄的 A0／A1／A2 真實暫存器邊界維持參數回傳契約。當前 public 入口如下：

| 入口 | bytes | 已核對範圍 |
| --- | --- | --- |
| compare | 52 | 正常 A0 為 0／1，完整期望值比較 |
| fill | 48 | 正常 A0 為前移後位址 |
| copy | 52 | 正常 A0 保留原目的位址，向前逐 byte 複製 |

三入口合計 **152 bytes／52 指令**；沒有 context／sret、call、SP／RA／GP／S／A1／A2 明示寫入。全物件還保留八個未被三入口呼叫的真實 global functions，共 230 bytes；總量為 382 bytes／138 指令，UND 與 RELA 均為零。這八個函式不是虛構 provider，這個總量也不能當成三個入口的大小或已連結映像。

**完整原始 ABI 仍未符合。** compare 額外改寫 A6，fill 改寫 A3／A6／A7，copy 改寫 T0／A7；原 scratch liveout 值也不同。compare／fill 在可能 fault 的 byte 存取前後更新 A0 的時機不同。fill 的 48 bytes 大於原 46 bytes，較短的 compare／copy 也不代表擁有原函式剩餘空間。不能原位替換或把正常回傳核對當成 transient／IRQ／fault／實機等價。

原始 copy 使用 A6，與 compare／fill 的 scratch 範圍不同。各函式的來源契約與反例分開列於 ABI 審查，不套用單一暫存器清單。

## Callback 的有界來源

原 App config+44 的數值目標 0x197F0，已由來源 CFG 界定 364 bytes／130 指令至 0x1995C（右界不含）；ELF 只有 size0 的 NOTYPE entry，不能假稱原本有 FUNC364 metadata。該入口有 13 個呼叫點／12 個不同目標，以及一個沒有明示 timeout 的輪詢迴圈。

第一個 0x8520 呼叫的 aligned32-byte 私有 stack 填零路徑可縮小範圍；19124、1908C 的兩個小 RCC leaf 也已讀取。這些不構成整條 ADC／callback 的保存證明；下一個未閉合依賴是 0x1987A→0x188E2。`tsCB`／temperature 名稱仍為 header 推論，不能宣稱呼叫後 config+52 或整個初始化保持零值。

## 驗證與剩餘工作

固定 Windows LLVM 以新增的 zifencei 支援實際 FENCE.I，其他既有 recipe 不作 flags sweep。預設 metadata 與明示 actual object／FW／ELF 讀取分開；ELF callback 檢查只涵蓋既有 548-byte owner 中的來源子集，不是完整映像 provenance。歷史 ordinary profile 在來源變更後只保留真實歸檔，不以當前來源冒充舊版 replay。

共享演算法未改，未重跑前輪 HOST 矩陣，也不在 HOST 執行這個 direct-MMIO port。沒有數值假 provider、原始 opcode 產碼、填補缺失程式或第三個來源 profile。Python／POSIX shell 入口可攜；只有固定 Windows 工具的編譯結果已實測。

完整 register／prefix／IRQ ABI、placement／Flash-NV 所有權、已安裝 ROM／BOOT／原板型，以及 BLE OTA 接受與恢復仍待證明。現有 550-byte OTA 實驗及既有 BIN 保持不變。前輪的離線設定診斷仍是值得新增的提案，尚未加入原機功能。
