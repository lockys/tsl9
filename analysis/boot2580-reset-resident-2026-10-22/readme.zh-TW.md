# ID2580 BOOT reset → resident：離線來源核對

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

本範圍實讀官方 ID2580／V1.0.00 的 12,288-byte BOOT，SHA256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`，分析基底為 `0x1000`。沒有修改原檔或舊 seal，沒有執行 HOST 模型、目標、MMIO、ISA／ESIL 或網路。這是可複核的來源邊界，沒有產生 C provider、元件或 BIN。

`0x1000` 的原始四 bytes `6f10903d` 是 `JAL x0,0x2BD8`。本輪完整覆蓋 reset `[0x2BD8,0x2C62)` 的 **138 bytes／37 指令**，以及獨立的相鄰 `0x2C62` MRET 四 bytes。連同 vector 合計 146 個來源 bytes／39 列。reset SHA256 為 `508c690e19a7da9fb6c880c11b696f4065aef3f7e2a7cb8097fb0ac33c91bbe3`。

[ledger.json](ledger.json) 保存全部連續 PC、原始 bytes、暫存器／立即值／分支／記憶體／CSR 欄位。沿用封存 typed decoder 與 ORI 欄位定義；CSR operand 在本地解碼，避免依賴未發布的歷史 helper；另外實際呼叫既有 radare2 的靜態 `pDj`，38 列 reset／MRET 的 bytes 和每個運算元全部一致。只解析反組譯文字，未評估輸出附帶的 ESIL。七個實際原始 operand 變異均被拒絕；沒有只靠整檔 hash 充當這些負例的判定。

## 實際數值與順序

| 來源 | 局部原始效果 |
| --- | --- |
| `2BD8..2BE8` | GP 設為 `20004000`、SP 設為 `20010000` |
| `2BE8..2C0C` | 以 end-exclusive word loop，從 `[3E90,3EF8)` 向 `[20004000,20004068)` 複製 104B／26 words |
| `2C0C..2C26` | 以 end-exclusive word loop，清零 `[20004068,200099A0)`，22,840B／5,710 words |
| `2C28` | WRITE CSR `BC0` = 31 |
| `2C2E` | WRITE CSR `804` = 3 |
| `2C3A` | CSRRS SET MSTATUS mask `1888`，保留其他既有位元；不是覆寫為 `1888` |
| `2C4A` | WRITE MTVEC = `103B`（`1038 OR 3`） |
| `2C4E` | JAL RA → `2C78`，link `2C52`；clock callee 位於本reset範圍之外，另有來源核對 |
| `2C52..2C5E` | 若 clock 正常返回此 continuation，再重新形成 `1A52` 並 WRITE MEPC |
| `2C5E` | JAL x0 → `40000`，沒有新增 RA link，也沒有本地 return/fallthrough |
| `2C62` | 原檔相鄰 MRET；**不是**前一條 JAL 的 fallthrough |

兩條本地 store 指令只有 `2C00` 的 copy store 與 `2C1C` 的 zero store。以無干擾且普通存取正常完成的局部數值路徑推導，它們的 write union 是 `[20004000,200099A0)`，不含 nominal slot `4004C`。這不宣稱全 BOOT／Runtime 沒有 slot writer，不排除 physical alias，也不宣稱 clock 或後續 resident 不會寫入它。

另份[clock來源核對](../boot2580-clock-2026-10-22/README.md)已涵蓋完整callee：只改寫SP／A2–A5，普通返回復原16B frame。這個來源投影仍以正常存取與無非同步干擾為條件，不保證實體時鐘ready或正常返回。MSTATUS／MTVEC寫入在clock之前。vendor CSR 的硬體語意、中斷、trap、MRET 的 privilege 效果、RAM／stack／程式碼映射及 coherence 仍未知。

## 對 0x4004C 的意義與下一個最小缺口

原始 BOOT `2C5E→40000` 與 Runtime `18730→40000` 共同支持「兩者使用 nominal resident entry」；它們不提供 slot 的實際內容。BOOT 檔案分析範圍僅 `[1000,4000)`，Runtime 僅 `[8000,1AC00)`，兩份檔案皆未包含 `4004C` 的實體內容。

既有公開 SDK 候選 HEX 的 `4004C` 四 bytes 是 `32030020`，即 `20000332`。這個 slot 是 HEX 內的資料；其 bootstrap 把被指向的函式複製至 RAM，不能混稱為 BOOT 寫入或安裝 slot。候選身分仍不等於原機 resident。

clock來源邊界已另行核對。下一步可將本輪BOOT的 **MEPC=1A52** 與既有候選 entry 的「不自行寫 MEPC、以 MRET 交接」契約組合成條件式來源關係。不得直接套用 Runtime 的 MEPC=9008，或以相鄰 MRET 宣稱 BOOT 已返回／啟動。這些工作已有本機原檔與候選 HEX，不需要網路或目標執行；仍不能自行提升 installed identity 或硬體 OTA 為通過。

## 唯讀複核

```sh
python3 -B analysis/boot2580-reset-resident-2026-10-22/check.py \
  --project-root /path/to/tsl9-reversed \
  --firmware /path/to/ID-2580-V1.0.00-decoded.bin
```

由專案根目錄執行，`--project-root` 指向來源樹。此 CLI 實讀 BOOT、重解全部列、核對已留存獨立靜態運算元與七個 raw negatives，不寫檔、不重跑舊矩陣。可另給既有 `--r2-exe`，重新取得相同靜態文字。來源核對不代表通過硬體驗證。
