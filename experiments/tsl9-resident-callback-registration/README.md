# Callback 註冊、本體與 RF_Config 候選

[English](readme.en.md) · [先前 handler](../tsl9-resident-dispatch-handlers/README.md) · [trap 契約](../tsl9-trap-profile-contract/README.md)

新增 **1546 bytes／540 條指令、5 個完整候選本體**：

| 本體 | 原始範圍（end exclusive） | Bytes／自身 frame |
| --- | --- | ---: |
| Registration | 0x58EF2..0x58F14 | 34／0 |
| Conditional registration | 0x60856..0x6089A | 68／16 |
| Registered callback | 0x58C52..0x58E7A | 552／64 |
| Registered callback | 0x60516..0x60754 | 574／32 |
| Candidate RF_Config | 0x64BAE..0x64CEC | 318／16或拒絕路徑0 |

## 新確認的靜態鏈

0x58EF2在0x58F0E將0x58C52寫至RAM0x200034F0；0x60856在0x60892將0x60516寫至RAM0x200034F8。兩者的寫入均支配各自 local normal return，且兩個 callback 現有完整本體；尚未證明初始化函式在實機何時被呼叫。另有0x57CBE／0x5E8BC兩個 CODE值寫入0x20003450／0x2000343C，其本體仍未提供。

Callback0x58C52釋放64-byte frame後從0x58D3C直接尾跳至既有0x57DAE；0x60516釋放32-byte frame後從0x605E0尾跳至0x6020A。0x60738的AUIPC-T1／JALR-zero又尾跳至setter0x2000078A：**link register是zero，不能改成一般call或覆寫RA。** 本輪9組HI／LO分成8組call與1組tail，原始opcode／register bits皆核對。

保存的官方header將RF_Config列為表索引100；候選carrier的0x401C4確為0x64BAE。該函式先讀caller+16的callback，零值走無frame拒絕返回；其他路徑仍可能先拒絕。到達設定複製的路徑，會先對global0x20003540做zero32，再copy caller32。官方rfConfig_t宣告經RV32 C11／C++17編譯得size32、alignment4、rfStatusCB offset16，因此對應共享callback word0x20003550。

這是**條件式來源關係**：必須假設caller輸入有效、不與先清零的global區重疊、callee的記憶體／暫存器契約成立。實際caller callback值、原始APP是否使用此API、實機ROM／ABI身分均未證明。沒有把「header名稱對上」當成硬體連線證據。

## 驗證與限制

各entry CFG覆蓋全部本體指令；normal return與typed tail的自身frame均平衡，RF拒絕路徑保留不配置frame的行為。C11／C++17物件相同，1546原始bytes逐byte吻合；52個官方Xwchc正例、39個實際操作核對通過。145個正大小FUNC是編譯分割區段，不是145個邏輯函式。

累計不供載入物件含 **12272 CODE＋256 DATA bytes／4291指令**、1010個FUNC區段、1個OBJECT、753個relocations，完整保留輸入bytes／symbols／relocations並通過獨立ELF readers。追入新callback後展開 **11個真實未提供callee**；先前11個實際provider直接重用，沒有stub或ABS假函式。另有3個opaque call、兩個未提供數值CODE本體及其他RAM／descriptor依賴。

APP位元組覆蓋率仍95.54%，新增APP CODE=0。4-byte啟動來源缺口、ROM／RAM／ISA、GP／IRQ／frame／alias、Flash及OTA仍未確認。沒有硬體、HOST model或ISA執行、vendor API、APP整合或新BIN；**尚未成功逆向出可用替代韌體**。設定／callback來源診斷可列為未來功能，尚未實作UI。

[完整收據](audit-result-v2.json) · [摘要](summary.json) · [原始指令／來源](evidence-v1.json) · [C/C++](resident_callback_registration.c) · [官方結構ABI斷言](config_abi.c)

## 重現

需要spec固定的原始APP、SDK／官方指令文件、先前native artifacts，以及trap契約的本機官方header；不會自動下載缺少的輸入。

```sh
python experiments/tsl9-resident-callback-registration/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v2
python experiments/tsl9-resident-callback-registration/audit-v2.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v2
```

Trial名稱必須未存在；保留既有產物時第一行改用 `--replay experiments/tsl9-resident-callback-registration/build/native-v2`，第二行省略 `--link-trial`。工具pins為Windows NDK LLVM，跨平台編譯未驗證。
