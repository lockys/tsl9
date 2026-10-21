# ID2966：補上9AE4與F666真實指令

固定來源為ID2966／server V4.1.60、76800B，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本輪仍是C11／C++17內嵌RV32指令與semantic relocations；不是原作者高階C/C++或完整ABI的還原，沒有執行原始或重建指令。

從前層actual6256筆全型別S+A RELA掃描，兩區間的incoming僅1557E→9AE4及B192→F666，各一筆JAL。raw／r2各核對四條指令：

| 入口／範圍 | 已確認靜態指令行為 | 證據限制 |
|---|---|---|
| 9AE4..9AF0，12B | LUI／LI／SW／RET，將數值2寫向計算地址40010814 | 不據此命名周邊功能或宣稱硬體行為 |
| F666..F672，12B | LI／AUIPC／SB／RET，將1存向2000BF99 | 真RAM carrier＋7F99；實體RAM／SP契約未驗證 |

兩個physical code sections無舊545配置重疊、共享或holes；沒有call、tail、未知indirect、literal、finite dispatch或跨section fallthrough。兩個FUNC各size12，只表示實際fragment。F666使用R_RISCV_PCREL_HI20(23)及自己的LOW12_S(25) anchor，引用既有OBJECT35160B RAM carrier＋0x7F99，不建立新RAM／view、ABS假storage或一般C prototype。

## 實際編譯與保留結果

新增24B code、2個FUNC、2筆RELA，無RO。整合52898B code＋3008B RO＝55906B file payload，547個非空配置（546file-backed及原35160B NOBITS RAM）、6258筆RELA、535個module providers，原27個RAM views、兩個existing-code views及534個relative expressions不變。

ROOT receipt：`build/table-extension-fbae5cf1888447b5b1efbf9f1554c67c/verification.json`，SHA256 `683de1114eed1142b700e74e5b261035e020088f9bf0a2225dd0409eed52e7ee`。C11／C++17 actual object一致，SHA256 `27102f00c7398039e34d0aacf9af6843ddcb444861ae5de27163c5dbfd6353a7`；numeric witness SHA256 `8de01eb17483fc740132941f2ba5c3905975d49aad114614ccd3a62b061ae48d`。Witness只核數字與原bytes，不供應missing providers、不當韌體。

Standalone final receipt：`native/build/3e43d9cd5d194ef0b1efa4aa27123169/verification.json`，SHA256 `6a2d869077bfade87bb43e181148ad0caf6e7ea2fdb4b54c0e6078c915b2198a`。兩語各8個actual negatives均拒絕：LOW型別錯I、HI addend／target、LOW anchor addend、captured FUNC改ABS、code byte突變、missing RAM改同值同size的ABS OBJECT、額外storage。Standalone嚴格連結因真RAM carrier UND失敗，不能把numeric地址當實作。

前層545個配置及其bytes/type/flags、667個allocated globals、3461個完整allocated locals與6256筆semantic RELA須保留；只將9AE4／F666兩個原FUNC UND轉成正確section-backed FUNC12。新指令僅增加兩個RA returns，沒有新known direct/computed guard入邊，不改16個既有有限分派域或原六項布局契約。

完整獨立審查見目的地`../../analysis/v4160-residual-code-2026-10-20/integration-review/review.json`；目的地fresh編譯、hash readback、README備份及舊檔保護見同目錄`destination-verification.json`。它們與本輪來源／standalone證據分列，不能拿W編譯代替D驗證。

## 直接引用里程碑與仍缺的證據

目前已捕獲程式的具名直接UND只剩resident ROM40000；62個materialized-only UND仍全部保留，strict final link仍失敗、沒有最終ELF／BIN。這不等於全部功能或runtime targets已實作；callback、ROM slots、IRQ／memory ABI及未捕獲區域仍有獨立缺口。

1AB58僅證read+1..7，不補byte0或8B物件；1AAE8首次索引／alias與缺744B不變。三個copy來源的有效目的地址／no-wrap條件仍不是實體RAM或stack驗收；1A430／454／478的limit／pointer生命週期仍未證。前層有限表／域用語勘誤亦保持原seal與獨立更正文件。

MCU／PCB、BOOT／resident ROM、實體記憶體／stack／IRQ、必要功能完整性、原藍牙OTA封裝／接受條件均未完成證明。全程離線，不執行或模擬RV32、不連硬體、不刷寫；`target_ready=false`、`native_bin=false`、`ota_verified=false`。完整goal仍未達成。
