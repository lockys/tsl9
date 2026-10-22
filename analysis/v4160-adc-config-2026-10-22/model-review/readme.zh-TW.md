# ADC1892E 獨立模型與原生審查

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

本輪獨立讀取實際 ID2966 V4.1.60 的 `0x1892E..0x18986`：88 B、37 列，只有 A3/A4/A5 被原始指令寫入，A0/A1/SP/RA 等暫存器由每列原始指令保持。這是來源證據，不證明目前硬體安裝的韌體身分。`source-ledger.json` 由實際原檔及既有封存 raw decoder 建立，沒有使用 producer 的演算法作為測試預期。

原始 14 個效果依序為：讀 base+4；讀 config+24、+0、+28、+4；寫 base+4；重新讀 base+8；讀 config+12、+16、+8；寫 base+8；重新讀 base+44；讀 byte config+20；寫 base+44。每個位址以 u32 加法換算。三個遮罩由原始 LUI/ADDI 位元欄位推導為 `E0F0FEFF`、`FFF1F7FD`、`FF0FFFFF`。config 七個欄位讀完整 32 bit，不先截斷高位元；config+4 左移 8、config+8 左移 1。最後 byte 先減一、再 AND 255、左移 20。別名與 callback 修改要求保留順序及新鮮讀取，不能預先快照 config。

獨立 HOST harness 對真正 C/C++ core 與合成 typed I/O 各跑 74 個案例、2904 個檢查：高位元、byte 0/1/255、u32 位址換繞、config=base/base-8/base-12 別名、callback 動態改變稍後 register/config、全部 14 個位置各三種停止 flow，以及診斷 budget 0..13。停止 callback 的效果僅被嘗試；停止寫入不提交，也沒有後續讀寫或整理。每語言三個實際編譯的語意反例（遮罩 bit、錯誤截斷 config word、漏掉 byte 減一）均因 assertion 失敗而拒絕。此測試不是 CPU 或暫存器執行模型。

HOST 逐 TU 記錄 compiler 回報的 sourceDependencies、實際資源 header hash、compiler/linker 與來源 hash，並在每次執行前後驗證本機可執行檔的格式、位元寬度與 machine。只有這個合成 harness 被執行。初期過深的反例複製樹觸及 Windows include 長路徑限制，失敗 archive 保留；最終使用單一反例 core 搭配真正 header，沒有修改測試預期或演算法標準。

實際原生 C/C++ ET_REL 的公開入口各 102 B / 38 指令，全部五個真實 global FUNC 共 254 B / 93 指令；四個未使用函式仍計入，包括 128 B core 及三個真正 volatile I/O ports。全部配置、raw operand、LLVM 靜態反組譯、UND0、RELA0、ABS0、雙 u32 參數到 u32 結果、沒有隱藏 context/sret、沒有 frame/call 均逐項核對。選定 IR 的 14 個 volatile 效果與 SSA 資料相依獨立匹配原始公式；最後 byte 的最佳化算式等價於 `((byte-1)&255)<<20`。每份原生物件三個 raw operand 與兩個 IR 修改控制均拒絕。

原生入口保持 A0/A1，但額外寫入原始會保持的 A2/A6/A7，且正常 scratch 結尾值不同。原始 A3 是讀到的 config+8 左移一，A4 是舊 base+44 與 `FF0FFFFF` 的 AND，A5 是最後寫入值。新版本 A2 是最後寫入值、A3 是 byte 欄位、A4 是 `0FF00000`、A5 是 config+8 左移一、A6/A7 是先前 base+8/+4 讀值。因此只接受正常已映射效果與結果的條件式投影，完整原始 ABI 不成立；102 B 也超過原始 88 B，沒有固定位置准入。caller 的額外暫存器讀寫追蹤由相鄰 source-review 另行提供，不能用單一 caller 的 dead 值推論原始完整 ABI。

`host.py --project-root ROOT --language both --build-root NEW` 建立新 HOST archive；`host.py --project-root ROOT --replay RECEIPT` 只重讀 archive。`native.py --project-root ROOT --folder PRODUCER_BUILD/c --receipt NEW.json` 建立實際原生審查收據；`--replay NEW.json` 重新讀取實物。`check.py --project-root ROOT` 只檢查封存來源與歷史摘要，並不冒充重新編譯或重讀實際 build。來源路徑支援 W 的 `apk-analysis/tsl9-*` 及 D/P 的 `analysis/*`。

未執行原始韌體、native MMIO、RV32/ISA/ESIL、硬體、網路、link native 或輸出 BIN；沒有重跑舊矩陣。sh runtime 因既有 Windows/MSYS 啟動限制維持未驗證。原生 ABI、板上晶片、非同步或 fault prefix、整個 callback、BLE OTA、Flash/NV 與可燒錄性仍未證實。
