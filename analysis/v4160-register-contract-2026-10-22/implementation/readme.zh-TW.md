# Resident 記憶體葉函式：完整暫存器保留配方

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

這輪實際編譯 C/C++，以原始葉函式的可寫暫存器加上 A0/A1/A2 三個顯式輸入，推導每個入口唯一的完整配置集合。**配方仍未符合原始 ABI**：雖然避免上一輪額外寫入的可配置 scratch 暫存器，編譯器改用 RA、16-byte stack frame；fill 也暫時改寫 A2。這是保留失敗結果的原生編譯實驗，沒有可燒錄 BIN。

| 選定入口 | 原始 bytes | 新 bytes / 指令 | 自身寫入 GPR | 完整 ET_REL bytes / 指令 |
| --- | ---: | ---: | --- | ---: |
| compare 200004BC | 62 | 60 / 23 | RA, SP, A0, A3, A4, A5 | 454 / 171 |
| fill 2000039C | 46 | 68 / 24 | RA, SP, A0, A2, A4, A5 | 492 / 187 |
| copy 20000332 | 58 | 64 / 22 | RA, SP, A3, A4, A5, A6 | 418 / 155 |

六個實際 ET_REL 均成功編譯；每種配方的 C/C++ 選定函式機器碼相同。每份完整物件誠實保留 11 個真正 global FUNC，其中 10 個不屬於該次選定入口；它們沒有被當成 linker 已移除。所有物件 UND=0、RELA=0，沒有 ABS provider。表格的完整大小包含未選函式。

可配置暫存器全集為 x5..x31；從中排除「原始 own-written GPR ∪ x10/x11/x12」後，將其餘全部以官方 help 支援的 -ffixed-xN 保留。compare 允許 x10..x15，fill 允許 x10/x11/x12/x14/x15，copy 允許 x10..x16。x0/x1/x2/x3/x4 另外檢查；RA/SP 並未因其專用角色而自動獲准改寫。fill 的輸入 A2 可供編譯器配置，但原始 own-write 契約仍禁止其暫時改寫；兩種集合沒有混淆。

原封不動包含已封存的 native.c，後者原封不動包含共同演算法。配方維持固定 -Oz、rv32imac_zicsr_zifencei、ilp32、禁止 machine outliner 等原有設定，只增加各入口推導出的唯一保留集合。不試其他 mask，不加入假 provider、數值 ABS、手工 encoder 或 opcode 模板。未做 visibility/internalization 改寫。

每個葉函式的 stack/RA 改寫發生在 guard MMIO 之前，原始函式則沒有 frame；即使正常返回恢復，暫態暫存器、stack、fault/async prefix 仍不等價。正常 scratch liveout 與 A0 在 byte fault 前後的時序另由獨立 ABI review 判定。full ABI、固定配置、installed provider、硬體 OTA 均未證明。fill/copy 超出原始 extent；compare 較短也沒有證明剩餘位元組可覆寫。

**只編譯及靜態檢查，切勿在 HOST 執行：程式包含真實 volatile MMIO 與 FENCE.I。** 本輪沒有執行 HOST 測試矩陣、RV32、ISA 模擬、MMIO 或實體硬體，也沒有 link、objcopy、產 BIN、刷寫或第三方網路操作。

## 可攜入口與證據

```sh
sh experiments/tsl9-resident-register-contract/verify.sh --project-root "$PWD" --tool-dir LLVM
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay LEAF/LANGUAGE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt LEAF/LANGUAGE/verification.json
```

CASE 為 workspace 的 apk-analysis/tsl9-v4160-register-contract-2026-10-22，或交付樹的 analysis/v4160-register-contract-2026-10-22。Python/sh 可跨平台；這輪僅接受既有 Windows NDK 27.1 固定工具 hash，沒有宣稱其他工具鏈結果相同。新 --build-root 必須是 model/build 下尚不存在的路徑，省略時使用 UUID；每次產生三入口乘 C/C++ 六份檔案。default check 只讀來源與 metadata，不代表已讀物件；顯式 --receipt 才校驗實際物件、IR、MD、完整反組譯、工具、編譯資源標頭與全部日誌，且不重新編譯或執行。

實際保留結果在 build/reserved-bank-v1-portable/{compare,fill,copy}/{c,cpp}。初次 build/reserved-bank-v1 的原始輸出與 initial-probe-snapshot.py 保留作歷史診斷：其後只修正 probe 的交付目錄查找與 compile 前 help 檢查，使用完全相同 mask/source/flags 重新建立上述正式 receipts。舊 receipts 不能冒稱目前 probe 的 replay。來源演算法與配方沒有第二種語意 profile。
