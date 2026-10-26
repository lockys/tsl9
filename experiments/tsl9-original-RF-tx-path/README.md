# 原始 APP RF 傳送、重試與候選執行層

[English](readme.en.md) · [唯一 CODE 組合](../tsl9-sdk-unique-code-ownership/README.md) · [RF 初始化銜接](../tsl9-original-RF-bridge/README.md)

新增 **1,778 bytes／620 指令、8 個完整候選 SDK 本體**，以保留原始暫存器情境的 C／assembly 編譯為 C11／C++17 物件。這些不是一般 HOST 可呼叫 API。

| 本體 | 原始範圍，end exclusive | Bytes／自身 frame |
| --- | --- | ---: |
| RF_Tx | 0x64CEC..0x64F04 | 536／48 |
| RF_Shut | 0x656C6..0x6575A | 148／16 |
| RF_SetChannel | 0x65F94..0x66056 | 194／0 |
| Basic TX callback | 0x64422..0x6448E | 108／16 |
| Auto TX callback | 0x6448E..0x645DC | 334／16 |
| ACK-phase callback | 0x645DC..0x646A8 | 204／32 |
| Clock／hop-like helper | RAM 0x20002D4C..0x20002DF2 | 166／32 |
| Index-like helper | RAM 0x20002C50..0x20002CA8 | 88／0 |

RAM helper 依固定 SDK copy mapping 追溯來源。名稱描述候選行為，不代表已證明時基、實體晶片或完整協定。

## APP 的直接證據

原始 sender `0x1753A`、RF task `0x17476`、completion `0x173EE`、retry `0x17442` 共 **430 bytes／147 指令**，同時與官方 APP BIN 及既有已編譯原址診斷 ELF 逐 byte 一致；19 個 PC-relative 資料位址由原始指令欄位獨立重算。

- `0x2000C7A8`：sender 寫入重試初值 50；retry 使用 `low8(previous−1)`，非零時尾呼叫 timer（event 1、原始時間值 2），為零則以 A0=1 尾跳 completion。時間單位與全程活性未證明。
- `0x2000C7A9`：同時作 sender 的非零拒絕條件與傳送長度 byte；存入 `low8(caller_A4+3)`。payload 複製長度來自 caller_A4，目的 `0x2000C7AD`；原碼沒有本地長度上限檢查，所有 callers 的 bounds 尚未確認。
- task 先呼叫 RF_Shut slot `0x401D0`，再呼叫 RF_Tx slot `0x401CC`，buffer=`0x2000C7AA`、length 取上述 byte、A2=A3=255。此路徑隨即以 event mask 覆寫返回 A0，沒有使用該 RF_Tx status。
- completion 先停止 event 2，再清除 retry／length。可選 callback word `0x2000C7A4` 在尾跳前清零，且先釋放自身 frame；不能改作仍保留 frame 的一般 C call。callback 作用未封閉。

sender 也呼叫 SetChannel slot `0x40200`，啟動 event 2／原始時間值 320，再設 event 1。SDK header／candidate table 將三個 RF slots 對應本輪完整實體本體；實機 ROM 身分仍未證明。

`N<=252` 只是不讓 `N+3` 超過 byte 表示的充分數值條件，且 `13+252<=268` 落於 constructor 清零長度；**不是已存在的 guard，也不是硬體最大 payload 證據**。

## 候選 SDK 與驗證

保留 return 後仍可達的分支與多個 cleanup；RF_SetChannel 的 `0x65FEA` 直接尾跳既有 `0x6434A`。三個數值 callback targets `0x64422`／`0x6448E`／`0x645DC` 均有本體。仍有 **4 個 opaque transfers**；TX 與 RAM helper 讀取的 clock-like word `0x200031E0` 不可混同 status callback word `0x20003550`。

C／C++ 物件相同；1,778 個原始情境 bytes、完整 CFG 自身 frame、52 個官方 Xwchc 正例與 40 個實際 port、兩個 ELF readers 通過。12 個具名匯入皆由前輪真實本體提供。累計唯一組合 **14,436 CODE＋256 DATA bytes／5,032 指令**，1,169 個 FUNC 區段、878 個 relocation，仍有 **19 個未提供的具名依賴**；區段數不是邏輯函式數。完整輸入 bytes／symbols／relocations 與原始 PC 唯一性通過。

APP 覆蓋率仍 95.54%、159 個正式 C/H；不代表功能完成率。未整合進 APP、未產生新 BIN、未執行目標／模型或操作硬體。4-byte 啟動來源缺口、ROM／RAM／ISA／IRQ、stack／alias、callback、Flash 與 OTA 相容性仍開放；**尚未成功重建可用替代韌體**。傳送長度／重試／回呼診斷可作後續功能，尚未實作 UI。

[C/C++](original_RF_tx_path.c) · [原始指令與位址](evidence-v1.json) · [完整收據](audit-result-v1.json) · [摘要](summary.json)

## 重現

需 spec 固定的本機輸入、先前 native artifacts、Windows NDK LLVM 與 trap 驗證的官方 header；不會下載缺少的輸入。

```sh
python experiments/tsl9-original-RF-tx-path/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-RF-tx-path/build/native-v1
python experiments/tsl9-original-RF-tx-path/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

建立新產物時，用 `--trial` 取代 `--replay`，第二行加 `--link-trial`；名稱均須未存在。跨平台編譯未驗證。
