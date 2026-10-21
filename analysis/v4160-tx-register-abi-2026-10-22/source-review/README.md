# TX 入口、堆疊與型別來源契約

[English](readme.en.md)

本份整理修復可讀 native TX 的來源契約，沿用已封存原始 `0x8A56..0x8B6E`、280 bytes／96條指令證據，沒有准入新替換，也不重跑未變更的 HOST 套件。`check-source.py` 讀取精確 ID2966 原始映像，驗證舊封存 decoder／契約、核對21筆入口／還原邊界，並拒絕7個實際 byte 變更控制。這些固定 PC 檢查是驗證原始義務，**不是**未來 compiler 產物的通用語意等價 checker。

## 最低可觀察義務

原始先設定 A5=1039，再於 `8A5A` 以 unsigned `A5<A3` 跳到 `8B6C` 提早RET。長度過大時 A0、SP 維持入口值，沒有堆疊寫入、GP讀取或不透明呼叫。即使 LLVM IR 的 C 分支早於第一個 volatile 存取，若 native prologue 在 guard 前仍會增加真正的寫入；無效堆疊或記憶體觀察者可區分。HOST 測試通過不能證明這個拒絕路徑的堆疊一定可寫。

有效輸入於 `8A5E` 才使 SP−32，`8A60/62/64/66/68` 依序把 S0／S1／S2／S3／RA 保存到 offset24／20／16／12／28，之後 `8A6A` 才讀 GP 相依的 handle。五個互不重疊的保存位置，在安靜且無 fault 的情況可有相同最終內容；逐點 fault／中斷前綴是更強義務。拒絕路徑新增保存，不能只當作保存順序差異。

成功時 `8B26/28/2A/2C` 先重新讀回 RA／S1／S2／S3，**之後** `8B32`、`8B36` 才寫 metadata SH；S0 於兩次寫入**之後**的 `8B40` 重新讀回。接著 `8B46` 讀32位元slot、`8B4A` 讀 unsigned byte handle，再使即時SP+32，於 `8B50` 不寫新link而跳至T1。把全部還原移到一般 epilogue，會跨過可能產生別名的寫入；普通回傳值正確不足以證明順序可交換。

有一個保持對齊的來源反例：live SP=`0x2000B170`、entry SP=`0x2000B190`、固定 buffer B=`0x2000B18C`，因此保存RA的 SP+28 正好是B。令原字為 `0x12340003`、穩定長度為1，B+2 的metadata SH寫7：提早RA讀回得到 `0x12340003`，延後讀回則得到 `0x00070003`。Header／payload／checksum均從此字之後才開始寫。這只是區間及小端halfword代數，沒有執行，也不宣稱實體硬體可到達該SP。即使callee維持SP／S，仍不能單憑此排除此反例，因為入口本身就可能具有此對齊值。

兩個slot呼叫分別在 `8A8E`、`8AB4` 寫link，形成raw RA=`8A90`、`8AB6`。未知callee可能觀察link，因此在沒有更窄callee契約前，改變link仍是實質ABI缺口。第二次呼叫取得第一次留下的A2／A3，而不是重新建立來源／長度。原始資料流重新觀察GP、S與SP；目前沒有證實ROM簽章或保存規則。

## 舊 C／IR 能證明什麼

舊native的 `TX_FRAME`、還原與pop巨集都是no-op，實際prologue／epilogue由LLVM決定。選定舊IR確實先分支、再讀volatile handle，但實際舊object仍以SP−32和五次保存開始。IR詞彙順序不足以安排compiler自行產生的frame存取。

`TX_FIXED` 只在asm operand的位置綁定暫存器。帶memory clobber的空volatile asm，不會替整個函式保留該暫存器、保證緊鄰下一條指令，或固定隱含frame布局。`TX_OBSERVE` 用output-only asm定義C變數，不能直接當成普通「未初始化C讀取」；但此抽象輸出也不證明預期舊值能跨過compiler allocation而保留，仍要核對實際機器產物。

Inline `jalr` 表達A0／A1／A2／A3／A5輸出及caller-saved clobber，卻沒有表達S0／S1／S2／S3／GP／SP可改變，因此compiler介面仍有保存前提。新增fresh observe，不能讓compiler自身spill／restore自動承受任意SP變更。數值HOST provider刻意容許更廣的不透明狀態變更；通過的trace無法把這項保證轉移給native。

型別 `volatile uint16_t`／`uint32_t` 存取仍有對齊與目標記憶體有效性前提，保留IR亦帶align2／align4。Unsigned運算可提供預期wrap，但volatile或memory clobber不能消除pointer／alignment要求，亦不能指定隱含frame存取位置。HOST中未對齊的合成數值位址，不代表實體C存取有定義；無須先宣稱全面undefined behavior，目前具體的frame順序及callee契約缺口已足以阻止准入。

## 有界實作選項

1. **無frame的typed dispatcher＋typed body：**先探查只需要入口A0..A3／A5的dispatcher，完成guard後以 `musttail` 轉移到獨立編譯body。實際產物須證明dispatcher沒有frame／spill、保留參數及提早回傳殘留、誠實的returning型別、真正tail轉移、整體ownership範圍與正確incoming／private角色。新增branch／body邊界並不自動透明，兩段能否放入280 bytes也未知。把asm guard放進既有有frame函式，不會自行限制prologue位置。
2. **明示數值SP／frame的custom port：**可在固定toolchain下審查少量frame／terminal intrinsic，但以RET／JRT1 asm再接 `__builtin_unreachable` 結束的C body，並非一般會返回的C函式。即使沒寫attribute，LLVM也可能推導noreturn；typed caller或LTO可能刪除後續程式，實體RET卻返回該處。因此必須採清楚獨立的machine-entry介面，不暴露普通C呼叫／LTO假設，並由實際產物證明沒有隱藏frame／spill／epilogue。手動SP變更仍超出一般compiler stack假設。這是可審查的目標擴充，不是portable-C解法或已證實ABI修復。
3. **保留暫存器旗標不代表ownership：**本機Clang help只將 `-ffixed-xN` 描述為保留暫存器，未表示asm可省略實際clobber。舊IR本來已有 `+reserve-x8/x9/x18/x19`，明列output仍會產生callee-save；刪除output將讓IR看不到變更。真正獨佔暫存器的custom profile也許可從機器產物審查，但排除allocation本身不足以認證普通extended-asm契約；RA／SP另參與隱含control／frame lowering。Parent的有限 `entry-plan/global_owned_s0.c` 探查提供反證：實際C、C++ IR用了 `llvm.read_register`／`llvm.write_register`，本次讀取的兩份16-byte object卻仍在SP−16的frame保存S0，並在RET前還原。該探查由parent編譯、本份只做靜態讀回；沒有執行目標，global register語法也未建立frame ownership。
4. **不要只靠label修補：**原始bytes複製、整函式asm、padding、改名數值alias，或把不同指令庫存交給保存順序permutation，都不能建立可讀來源語意。先做一次有限來源／profile探查、再檢查實際產物；不能由flag、大小、annotation或出現 `musttail` 字樣推論成功。

ADD／MUL交換來源操作數、位置改變但實際目標正確的PCREL配對，或等價分支predicate，可能在另外證明目標與控制後成立；對某些介面主張，整份opcode相同是更強要求。相反地，讓拒絕路徑增加寫入、讓RA讀取跨過可能別名寫入、改變callee看得見的link，則是在現有未界定介面下的真正行為差異。計算式／interior入口、實際stack可達性、ROM行為、非同步狀態、硬體及OTA接受度仍未知。

## 實際有限來源提示結果

新的canonical來源與舊演算法只有兩個 `TX_EXPECT` 包裝既有比較結果的差異；HOST巨集是identity並沿用舊的固定provider，native只加入分支期望metadata。Checker獨立核對這個精確來源差異，本份沒有新的HOST演算法需要重驗。實際讀取兩份canonical object：278 bytes／95個指令geometry，第二個gate位於relative `+0x5E`（raw link=`8AB6`），PCREL high anchor=`+0x80`。第一條仍會調整SP，因此這項改善尚未解除提早guard或延後restore的別名缺口。其餘2 bytes沒有被視為可用空間或補padding。保留的parent編譯觀察與本次raw／來源檢查分開；運送後不會暗中把metadata當作實際產物重播。

## 實際窄入口 adapter

本份也讀取了returning C dispatcher探查：18-byte入口加272-byte body，超出280-byte owner。下一個已實作選項使用僅兩個手寫assembly mnemonic、真正typed valid-only body及真正typed identity-return leaf。直接指向外部symbol的assembler分支最初展開成BGEU＋JAL：12＋270＋2＝284 bytes，因此已拒絕。核准修正版改用assembler產生的BLTU placeholder，並以恰一筆標準 `R_RISCV_BRANCH` 指到真正C leaf；沒有opcode encoder、複製原始指令、byte directive、padding或整函式assembly。

兩份實際修正C／C++ component皆已獨立讀取：entry8、body270、leaf2，於 `8A56`、`8A5E`、`8B6C` 緊鄰配置。連結後 `8A5A` 的guard確實指到 `8B6C` 的typed RET；拒絕路徑在RET之前只設定A5=1039，沒有改A0／RA／SP、沒有記憶體存取或新link，frame只在有效輸入fallthrough後出現。Entry.o於+4恰有一筆branch relocation；leaf IR真的返回context參數，機器碼也僅RET。每種語言5個實際code控制會拒絕錯誤limit、signed guard、錯誤branch目標、改寫A0，以及寫入link的leaf。另核對body精確抽取及5個獨立標記的來源文字控制；來源文字控制不冒充編譯語意負例。

公開assembly symbol誠實標示FUNC大小8，C body270、typed leaf2。這與原FUNC280 metadata角色不同，仍屬待處理的integration角色義務，**不是**已證實runtime失敗；沒有偽造extent／alias。本份pre-motion adapter仍有延後成功還原及不同保存順序，尚非完整ABI修復或full image。SRAM PCREL僅核對數值witness，未提供真正記憶體／provider實作。

具體下一步是另行聲明的load-order pass，只利用五個既有compiler產生的LW-SP字：把RA／S1／S2／S3移到兩個metadata SH之前；S0則只能在live length+6已被兩次store使用後才還原。Pass必須證明未錯誤跨越SP寫入、不透明呼叫、仍需目的暫存器值的操作、branch／interior入口或relocation，且保留其他指令相對順序與來源／object身分。只改五個位置卻沒有完整permutation／provenance證據仍不足。此產物明示為 **C/C++加native scheduling pass**，不是pure Clang或一般C介面保證；准入與本份原始／來源契約封存分開。原始保存順序／fault前綴、未知ROM行為及任意SP變化仍要獨立處理。

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/source-review/check-source.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

Shell包裝接受 `PYTHON`。本份沒有執行原始／重建RV32、ISA模擬、網路或裝置操作。保留來源／IR觀察及fingerprint與本次raw byte核對分開標示；不含generated build。

預設輸出為 `actual_native_artifacts_replayed:false`。需要重查窄的 **pre-motion** object／IR／linked-entry子集時，可重複指定 `--adapter-folder 實際PRE_MOTION目錄`，才回報實際讀回及每份5個byte控制。此入口不重播編譯recipe、不接受後續排程過的body，也不暗中使用workspace封存。`source-review.json`只保留精簡選定metadata，診斷object與log留在本機。另已讀取parent最小診斷：四份22-byte guard確實在frame前分支，兩份16-byte global-S0仍自動保存／還原；這些有限案例既不證明Clang普遍做不到，也未修好整個TX函式。
