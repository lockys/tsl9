# ID2966 十個直接呼叫本體

重做入口：`python verify-extension.py --spec evidence/frontier-integration.json`。來源固定為 ID2966／伺服器標籤 V4.1.60，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本輪以 C11／C++17 加 RV32 inline assembly 保存十個原始本體；沒有恢復或猜測原 C 函式原型。

## 新捕獲範圍

| 原半開範圍 | bytes | 可證數值行為 |
|---|---:|---|
| 18E1C..18E86 | 106 | 40010400 加 caller offset 的 ordered32-bit mask RMW；本地未限制 offset 上界 |
| 1904A..19076 | 44 | 40010008+(a1&FC) 的 nibble 清除與另次讀取後 OR；a0 本地未限為4bit |
| 19124..19142 | 30 | 40021018 的 mask set/clear |
| 19142..19160 | 30 | 4002101C 的 mask set/clear |
| 19160..1917E | 30 | 4002100C 的 mask set/clear |
| 1917E..1919C | 30 | 40021010 的 mask set/clear |
| 196C4..1971E | 90 | 參數位址的16-bit欄位組合、clear與copy；既有caller提供40013000 |
| 1971E..1973C | 30 | 參數位址16-bit bit40 set/clear，保留 RET 後可達尾段 |
| 199E2..19B16 | 308 | 三個ROM slot呼叫、三個自旋停留點、stack欄位、6B copy與MMIO操作 |
| 19B16..19B56 | 64 | ROM slot呼叫、返回byte存RAM、直接呼叫，再經40058 slot間接尾跳 |

762B、十個物理配置，與先前所有配置及彼此均無 byte 重疊。原 bits 的有限 CFG 與 r2 逐指令核對無 holes、unsupported、預算截斷或未納入的本地直接分支；callee 若正常返回才會抵達其 continuation，這不是執行觀察。18E1C、1971E 的可達 RET 後尾段，以及19B54的 `c.jr t1` 均保留。

33筆新語意重定位分為19個直接控制轉移、7組 AUIPC/own-LO pairs（14筆）。本體新增四個間接 callsite 與一個間接 tail site；實際指標值及 ABI 仍未知，tail 不計作 call。

六個新 Flash materialized addresses `1AB1C/1979A/197BE/197F0/197B8/1995C` 只有原取址證據，仍為真實 UND；傳入 ROM 的地址／參數不能證明完整物件大小、callback 原型或 ROM 服務語意。`2000418C` 僅成為既有單一35160B NOBITS carrier的 NOTYPE、size0 view；未新增資料、值或型別。

## 整合與驗證界限

本輪 composite spec 以凍結的 core-flow 為建置基線，帶入未修改的 callback／readonly modules 及新 frontier module。這避免改動舊驗證器或舊 spec；獨立審查另外對前一 materialized actual object 的全部storage、globals／local views與554筆semantic relocation multiset作保留比較。預設不帶 `--spec` 的 `verify-extension.py` 仍驗證舊 core-flow 範圍。

整合7068B code、459B RO、63個allocations、587筆relocations及27個RAM views。相對前一 materialized stage，只有十個新FUNC本體／762B；composite modules共有24個exported providers，其中另外14個來自未修改的前一層，不把它們重複計為本輪新增。

嚴格最終連結仍拒絕83個不同數值位址的 UND：71個直接code targets、11個opaque Flash addresses、ROM40000。原84項中，十項現由真實本體提供，同時暴露三個新直接callee與六個opaque references，所以剩餘計數只減少一項。它是有限捕獲範圍的前緣，不是整份韌體的總缺口。全部已捕獲程式有83個間接 callsites、另有1個間接 tail site，不能以直接依賴數量代表完整功能閉包。

原位數值 witness 僅為檢查配置及逐byte比較而填入未解析地址；它沒有提供缺少的程式／資料，不可執行或燒錄。C11與C++17的靜態編譯與ELF一致不能證明原機可啟動。

generic composite gate 的 actual ABS 反例仍選原callback的 NOTYPE view。standalone另保留「缺失callee18F56加上size0的ABS STT_FUNC冒充provider」反例，並新增真正captured18E1C的object symtab反例：僅把st_shndx改成SHN_ABS，保留STT_FUNC、size106、st_value0與所有body／relocations，再交同一provider gate要求拒絕。三種角色分開報告，不把generic的view反例誇大為新FUNC的整合測試。

本輪交付、獨立審查與目的地fresh核對見 `../../analysis/v4160-frontier-2026-10-20/`；以其中 `destination-verification.json` 確認D交付完成及實際artifact hash一致。hardware-observations只描述數值與局部流程，不推定精確周邊／SKU。

實體晶片印字／PCB仍未知；BOOT、resident ROM版本／ABI、實體RAM／stack／中斷、完整功能／資料閉包與原藍牙OTA驗收仍未證實。未執行或模擬RV32、未發網路請求、未接觸硬體或刷寫，未產生可燒錄的重建BIN。原完整goal仍未完成。
