# ID2966：後續直接入口與四張有限分派表

最新入口為 `python verify-table-extension.py --spec evidence/post-table-code-integration.json`。同一 verifier 不給 `--spec` 時仍是前輪 table-cases 階段；原 `verify-extension.py`、舊 spec 與舊 sealed 證據均保留。

唯一原始映像是 ID2966／伺服器標籤 V4.1.60，76800B，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。該標籤不能證明檔案對使用者實體 TSL9 的完整硬體適用性。程式為 C11／C++17 搭配 RV32 inline assembly，保留已證原始指令；這不等於恢復原作者高階 C/C++ 原始碼或 ABI。

## 入口與真實配置

前輪 actual ELF 的 69 個 ordinary direct UND 已逐一用 raw／r2 CFG 捕獲。另有原先只取址的 `1069E`，本輪直接控制引用 `A062`、`B03E`、`B064` 證明其入口角色，捕獲 `1069E..106C0` 的34B，唯一直接 call `106A8 -> ED00` 仍是真外部依賴。

原始70入口共12468B／78個物理 code fragments。四個 split roots `BD88`、`DBCC`、`DEF2`、`FA62` 的未走訪區段不整段複製或補零；root-local holes 也不能一律當作全域缺失，因部分已由其他 root 或舊 storage 捕獲。共享 tails 只配置一次，保留實際指令邊界與相鄰關係。

`__tsl9v4160_address_1069e` 保持原 NOTYPE、size0 身份，在真 code section 內建立 view；另以 `__tsl9v4160_captured_body_1069e` FUNC 表示34B入口 fragment。其餘69個FUNC同樣只表示captured entry fragments，size不能當成原邏輯函式完整範圍或原 C prototype。

## 四張新增相對表

| JR consumer | unsigned guard | table base | index | bytes |
|---|---|---|---|---:|
| C158 | C144 | 19E08 | 0..17 | 72 |
| C1BC | C1A8 | 19E50 | 0..10 | 44 |
| C2A4 | C290 | 19E7C | 0..10 | 44 |
| DBFE | DBEA | 1A0DC | 0..23 | 96 |

每處均有原始 guard、scale4、LW、add-base 與 JR 指令證據。64個word／256B讀取聯集共有49個不同目標，其中三個已在初始70入口捕獲內，46個新 case targets 用真本地指令 labels 表示，沒有另稱46個原作者函式。

必要 case CFG 增加978B／293條指令、七個code區段：`C184..C194`、`C1BE..C27A`、`C2A6..C2B6`、`C2C0..C308`、`C318..C35A`、`DC00..DC22`、`DC36..DE80`（末端不含）。`C318..C35A` 超出舊BD88盤點span，依真可達證據續捕獲，不以舊span硬切。`D8E2`、`D90E` 真callee保留未提供義務。

本輪新增13446B code、256B RO，共13702B／89個配置（85code＋4RO）。79個defined globals＝70FUNC＋4OBJECT＋5NOTYPE；四個OBJECT只是有限consumer讀取視窗，不能當作原完整資料物件範圍。

## 重定位與相鄰限制

每個table word有初值0及同址一筆ADD32(35)／一筆SUB32(39)，保完整RELA list與multiplicity。核對式為 `(initial + target + target_addend - base - base_addend) mod 2^32`，結果須等於原word；不能複製原delta後再加減一次。

1615筆新增RELA＝945筆直接控制＋542筆正常PCREL（271 pairs：194 I-format、77 S-format）＋128筆relative32（64 pairs）。217個實際HI sites引用既有真RAM carrier，沒有新增RAM storage。新四表與先前22項合計86個relative32 expressions；既有12B7A code view及27個RAM views維持原section身份與型別。

`C2A8 -> C19C` 指向真本地label：C19C在C194 section的offset8，不能用其他section的FUNC加offset或ABS數字冒充。所有控制核對使用symbol value加addend。

五個跨section fallthrough必須保持原位相鄰：`C190 -> C194`、`C276 -> C27A`、`C2B2 -> C2B6`、`C304 -> C308`、`DC1E -> DC22`。它們沒有可重定位immediate，本輪不宣稱整個程式可任意搬移。

## 實際整合與驗證

Fresh W receipt：`build/table-extension-2767800224b5423e908e515501c1a862/verification.json`，SHA256 `86ca0554708a6f058d7d86caaf0c1c5c7828a93fcd3676c3264c0a74949ab84d`。

整合34146B code＋803B RO＝34949B file payload；315個非空allocations（314個file-backed與原35160B NOBITS RAM），3174筆semantic RELA，281個module providers，另計舊code view1個。C11與C++17 actual merged object同為 `4ce1796cef520fb8c94b62e078ae3538a58745200cde038037a35f679a8051b4`；原位 numeric witness同為 `1e4cf2265fbb3cc9d6f13e63b726a2c72e7310234a797a226902c201f95273f2`。witness只核原數字與bytes，不提供缺失實作，也不是韌體。

Standalone嚴格link拒絕113個UND；整合嚴格link拒絕116個UND。兩者範圍不同，不能直接以數量當成功能完成率。整合符號名稱為66個call、49個address與1個ROM身份；名稱本身不證用途，應以actual引用及獨立review分類。新增body能揭露新義務，不能用ABS、stub、假RET或numeric witness將它們假閉合。

Standalone每種語言17個actual ELF反例均被拒，包含額外同址且數值互相抵消的ADD／SUB pair、raw-delta重複編碼、PCREL／SUB addend變更、typed NOTYPE views、captured FUNC改ABS、missing callee改ABS與未證零填配置。metadata逐檔回讀；同址pair即使link後所有bytes相同，仍因semantic multiset不同被拒。ROOT另核實際strict失敗、relative words與舊code view反例；獨立review核舊226配置、global／local identities及1559筆semantic RELA保留。目的地另做fresh C／C++編譯與SHA回讀，結果見 `../../analysis/v4160-post-table-code-2026-10-20/destination-verification.json`。

## 仍未確認

四個新finite dispatch不消除另六處unknown indirect：五處取用ROM slot4004C的未知callee，`10846`調用傳入callback，皆不能猜ABI。原有間接義務、1AAE8首次index生命週期、RO物件完整範圍及原機契約仍保留。1AAE8正常reset與已知writer不足以證全生命週期index域，缺失表bytes不補零、不借其他版本。

MCU／PCB印字目前不可讀；BOOT／resident ROM、physical memory／stack／IRQ、完整必要功能及原BLE OTA封裝／接受條件未證。全程離線，不執行／模擬RV32、不連硬體或刷寫；`target_ready`、`native_bin`、`ota_verified`均為false。完整重建goal保持未完成。
