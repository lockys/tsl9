# 原始 trap／啟動數值契約

[English](readme.en.md) · [既有 LLE C/C++](../tsl9-resident-lle-callback-gateway/README.md)

本輪核對原始 V4.1.60 reset 的 **122 bytes／33 條指令**與兩份本機保存、固定 commit／SHA 的 WCH 官方標頭。新增的是 C11／C++17 **編譯期數值契約**，不是可執行功能、IRQ handler 或韌體 provider。

| 官方候選名稱 | 索引 | APP 向量 word 位置 | 原始數值 |
| --- | ---: | --- | --- |
| Ecall_M_Mode_IRQn | 5 | 0x804C | 0x8448 restore |
| Ecall_U_Mode_IRQn | 8 | 0x8058 | 0x8448 restore |
| BB_IRQn | 63 | 0x8134 | 0x1873E |
| LLE_IRQn | 64 | 0x8138 | 0x8498 wrapper |

表中是官方候選 enum 與 APP bytes 的數值對應，**不代表已證明 mtvec mode3 的實體 dispatch**。官方來源位置、行號與雜湊見 [來源證據](source-provenance.json)、[完整推導](evidence-v1.json)；沒有連線下載新文件。

## 新確認的限制

原始 reset（0x186AA..0x18724）組成 GP=0x20004000、SP=0x20010000、向量基址0x8038與 mtvec=0x803B，寫 CSR0x804=3。保存的 core 標頭只對 bit1 提供中斷巢狀啟用／停用註解，因此候選對應下的初始 bit1 為1。原始 restore（0x8448..0x8450）是 CSRRS mask32：它設定 bit5、保留其他位元；不能把它解釋成關閉 bit1。**bit5 與 mode3 的實體語意仍未知。**

若 reset 清零正常完成，GP+384=0x20004180 位於0x20004080..0x2000C958的清零區間，該 callback word 初始為零。原始 LLE wrapper 會直接呼叫載入的指標，因此必須另行證明 slot2→GP+384 綁定早於每次可能的 LLE dispatch，並證明 ROM 呼叫後 GP 仍穩定；本輪尚未證明此順序，也沒有改動 IRQ 政策。

## 驗證與使用

C11／C++17 實際物件相同，兩個獨立 ELF reader 核對完整物件；**零非空配置區段、零 relocation、零 provider／import**。先前真實候選本體與原生契約重新檢查通過，累計仍為 **9608 CODE＋256 DATA bytes／3367 指令**；0x57DAE／0x6020A仍未提供。新增功能實作 bytes=0，APP覆蓋率仍95.54%。

```sh
python experiments/tsl9-trap-profile-contract/build-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --trial native-v1
python experiments/tsl9-trap-profile-contract/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

`REFERENCE_ROOT` 指向本機保存的官方參考根目錄；相對位置與 pins 見來源證據。Trial 名稱必須未存在；保留既有產物時改用 `--replay experiments/tsl9-trap-profile-contract/build/native-v1`。工具 pins 目前為 Windows NDK LLVM，跨平台編譯尚未驗證；缺少輸入時停止，不自動下載。

仍缺實機 ROM／RAM／ISA、trap frame／向量模式、GP／alias／IRQ nesting、整體堆疊、4-byte 啟動來源缺口、Flash 與 OTA 證據。沒有執行韌體、HOST model、ISA 或硬體，沒有 API 流量、APP整合、新BIN；**尚未成功逆向出可用替代韌體**。可考慮未來在 OTA UI 顯示按 SHA 固定的相容性證據與未通過條件，此 UI 尚未實作。

[審核收據](audit-result-v1.json) · [摘要](summary.json) · [C/C++ 數值契約](trap_context_contract.c)
