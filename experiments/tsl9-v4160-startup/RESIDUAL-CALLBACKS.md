# 條件回呼與新版 Runtime reset

本階段沿用 ID2966／V4.1.60 原始映像，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。C11/C++17 的 native source 保留原 RV32 指令及重定位；可讀 reset 語義模型另外位於 `../tsl9-v4160-reset-contract/`。兩者均不是可燒錄成品。

```powershell
python verify-gatt-ingress-extension.py --spec evidence/residual-callbacks-integration.json
```

驗證沿用已固定的 GATT adapter 與完整 baseline，各階段入口和規格均保留。新 module `residual-callbacks` 增加 `85C8..8614` 的76B及 `8B90..8C82` 的242B，共109條原指令、24筆直接控制重定位。兩個公開於 ELF 的私人名稱均為 GLOBAL NOTYPE／size0，不宣稱原 C 函式型別、回呼 ABI 或可任意重定位。

原始 `19DE0` 記錄的三個 word 是 `8B90,0,85C8`。task868A 的 bit8 分支在887A取記錄位址，8884呼叫 nominal401A4；候選 WCH header 可解釋其形狀，但實際 resident 的讀取範圍、呼叫方式及版本仍未知。原始 `19DEC..19DF9` 是13B AD-like資料，包含 `TSL9`，不能當另一組函式表；`19DFC` 的 `0,888C,0` 則由另一處呼叫傳給 nominal40130。這三個地址的 canonical 契約不因同址有私人 storage 就變成已解析。

85C8讀取 GP+150／154 的16-bit值並檢查參數條件，部分路徑 tail 到 nominal40058。8B90依狀態、事件碼及相關 RAM 值更新兩個候選連線槽，會呼叫既有8B6E與13E0E片段；某路徑以247作為傳給 nominal400D8 的數值參數。候選 SDK 名稱有助理解，但不能證明真實 BLE 狀態、MTU、ROM ABI 或硬體上的執行結果。未知間接呼叫保留未知。

整合規格要求70764B code、3708B RO、640個配置、8107筆 RELA；539個 symbolic relative32與7個原VA固定表項保留。新 module 不增加 RO、RAM view、code view或 symbolic table。嚴格連結仍須拒絕原31個真 UND，不能以 ABS、stub或跨版本補碼使其通過。

目前已表示的 code＋RO為74472B，來源映像共76800B；差額2328B仍未配置。這個數字是來源位元組覆蓋，不是功能還原率。其他6個候選 code gap共1720B沒有取得足以接納的已知入口證據，不以 pointer-like bit pattern推定可執行入口。`1AB44..1AB46` 有條件式 LHU reader，但其初始化指標在後續呼叫中的有效性仍未閉合，本階段沒有把它硬補成完整物件。

入口8000的原 `JAL x0` 跳往186AA，略過8004..8038的12個NOP32與1個EBREAK。這只能證明正常入口略過該52B，不能證明任意間接入口不存在，也不能證明最終燒錄映像可以省略它。未以填洞方式消除缺口。

reset 可讀模型依原138B startup與128B initializer，保留32次live讀取後立即寫入、8758次清零、CSR write／SET的差別、clock返回後才設定MEPC，以及最後無本地return的40000跳轉邊界。C11及C++17 host測試各5組／459392項檢查，僅使用合成provider；測試選取13個中止位置，不宣稱所有執行前綴、實體CSR舊bit、硬體重啟或ROM接受都已驗證。

來源與獨立審查位於工作區 `apk-analysis/tsl9-v4160-residual-image-2026-10-21/`；交付後同一組證據位於專案 `analysis/v4160-residual-image-2026-10-21/`。原晶片／PCB／ROM、實體記憶體、IRQ ABI、未知資料域、BOOT/root及藍牙 OTA 接受仍是必須分別證明的條件。沒有執行或模擬目標RV32，也沒有網路／硬體／燒錄操作，`OTA_ready=false`。
