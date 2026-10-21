# ID2966：F4D0與F578回呼本體

固定來源為ID2966／server V4.1.60，76800B，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。C11／C++17以RV32 inline assembly保留指令及semantic references；不是原作者高階C/C++、完整函式extent或C ABI的還原。沒有執行原始或重建RV32。

## 為何捕獲這兩個地址

前層actual ELF仍有62個materialized-only UND，98組真HI／own-LOW引用。F68C／F6BE取F4D0，F6F0／F722取F578；四條wrapper尾端F6AC／F6DE／F710／F742到F47E。raw register／branch證據顯示，entry a2非0且a4為0的路徑才到F498 C.JALR a5（RA為F49A），沿路a5未改。a2為0的另一支則保存該值跨F1C2，再以a0交90B0；不能把所有取址用途都當作直接呼叫。

這證明四條已知路徑的條件回呼來源，沒有觀察到執行，也未證任意incoming a5、所有其他caller或ABI。兩個canonical地址原為NOTYPE,size0，因此保留原身份，另以captured_body FUNC helpers保存實際entry fragments。

| 捕獲範圍 | bytes | 指令 |
|---|---:|---:|
| F4D0..F578 | 168 | 54 |
| F578..F630 | 184 | 61 |

共352B／115條指令／兩個physical code sections，沒有holes、共享、舊547配置重疊、新unknown indirect、finite dispatch或literal窗口。沒有以4K或第一個RET擅定整體函式邊界。

## 真實引用與舊storage

六個JAL只到82A8、9124、F1C2，各兩處；它們已是actual executable storage的真provider。本輪逐一綁舊section／size／flags／bytes／provider／完整RELA，不重配舊body或重發舊RELA：

| 真provider | bytes | 舊RELA |
|---|---:|---:|
| 82A8 | 42 | 4 |
| 9124 | 300 | 15 |
| F1C2 | 594 | 78 |

16組正常AUIPC own-LOW為9個I型及7個S型；14組使用既有真RAM carrier＋原offset，另兩組重新取自己的canonical地址並交9124。沒有新增RAM或RAM view，沒有把原NOTYPE地址升成FUNC或推論prototype。

## 實際編譯結果

新增352B code、0RO、兩sections、4globals（兩個FUNC helpers與兩個NOTYPE0 canonical地址）。44筆RELA＝12control（6JAL、1branch、4RVCbranch、1RVCjump）＋32正常PCREL。沒有新relative expressions、existing-code views或跨section fallthrough契約。

整合53250B code＋3008B RO＝56258B file payload，549個非空allocations（548file-backed及原35160B NOBITS RAM）、6302筆RELA、539個module providers，原兩個existing-code views、27個RAM views及534個relative expressions不變。原16個有限分派域及六項固定布局契約仍保留，不能宣稱whole program任意可搬移。

ROOT receipt：`build/table-extension-c0d5de329b174882b7261bdce816e4ab/verification.json`，SHA256 `d4317cde86dbfcb0d5d0822119c7a9d5d9767af9789e0559fe26e89396fb22e8`。C11／C++17 actual merged object一致，SHA256 `cee66d13661baa0868a472e4c8f608cf521143abb03ae72e2725bdd0c0d36772`；numeric witness SHA256 `5af1ab5199b5a4890baa6529cd5265642e98cdad05e8d473c601838a15a99a9e`。Witness只核原數字／bytes，不提供missing providers或韌體。

Standalone final receipt：`native/build/b4494a3ada44425bb61a0071951b11eb/verification.json`，SHA256 `612b4d073ffd4676070b94c20afd12442db11f46c2d2a3d72d977e7d5e2f3b62`。每語言12個actual negative fixtures均拒絕，包含control／own-LOW錯誤、兩個canonical地址type-only改FUNC、captured FUNC改ABS、missing callee／RAM改ABS及額外storage。Standalone strict因三個parent callees與RAM共4個真UND失敗；整合則仍拒絕61UND＝ROM1 direct＋60materialized-only。

獨立審查須保留全部舊547配置及bytes/type/flags、669個allocated globals、3466個完整allocated locals與6258筆semantic RELA，再核新本體、四條條件consumer路徑及current已知入邊。最終獨立review及目的地fresh編譯／hash readback見`../../analysis/v4160-callback-bodies-2026-10-20/integration-review/review.json`與`destination-verification.json`。

## 設定值勘誤與未知extent

前層文件把1A430／1A454／1A478的setter概括為寫17，描述過簡。新逐分支raw證據確認前兩支為17，第三支EFF8取1A478後，F008實際LI53，再經EFBE寫BF86，應分列17／17／53。原source、receipts及sealed文件不改；本輪`materialized-review/review.json`的erratum保存精確原PC／路徑。

這些只是各setter路徑的觀察值，沒有BF86 limit／BF88 pointer全生命週期、alias或IRQ ordering閉包，不能據此宣稱34／106B完整表。舊分析並未以統稱17建立這些表的provider，因此此更正不改舊code／RO bytes或既有編譯結果。

1AB58仍只證read+1..7，byte0未證、base仍UND；one-past data-anchor僅是未實作模型評估，不套用code view或ABS來閉合。1AAE8首次index／alias與缺744B不變，三個copy來源的有效目的地址／no-wrap條件也不是實體RAM／stack驗收。

## 仍未完成的完整目標

本輪沒有新增unknown dependencies，不表示所有callback來源、ROM slots、IRQ或功能已閉合。實體MCU／PCB、BOOT／resident ROM、Flash／RAM／stack／IRQ、必要功能完整性及原藍牙OTA封裝／接受條件仍需證據。使用者目前無法讀晶片印字，不猜硬體定案。

全程離線，不執行或模擬RV32、不連硬體、不刷寫；strict final link保持fatal，`target_ready=false`、`native_bin=false`、`ota_verified=false`。沒有可燒錄重建BIN，完整goal仍未達成。
