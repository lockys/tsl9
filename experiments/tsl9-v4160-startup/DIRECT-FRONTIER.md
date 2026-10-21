# ID2966：84個直接入口與必要尾段

本輪只依76800B的ID2966／server V4.1.60 image，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。C11／C++17使用RV32 inline assembly保留實際指令及semantic relocations；不是原作者高階C/C++、完整函式邊界或C ABI的還原。伺服器版本不證實體TSL9硬體適用性。

## 真入口、尾段與共享配置

由前層actual ELF的143筆incoming direct RELA導出84個非ROM入口（82個direct-only與兩個mixed）。raw／r2核對1002條指令，共2992B／84個fragments，無舊453配置重疊、共享或未訪問holes。沒有以4K距離作函式或tail邊界判準。

七個真無link跳轉指向三個尚未提供入口10022／F47E／F9A4，另有1805A的直接與取址混合用途，因此追加四個必要followups，共264B。原84選擇定義不變。F47E／F9A4等到13D48的真控制引用綁到既有140B executable storage與真FUNC provider；舊17筆RELA完整保留，新module不重配、不重發。該區段SHA256 `32ef96a7aaa9a7a8d64bc93b5589b3dda7713a3b4d6cb4cb8129a9e02e4d1d23`，七個新encoded edges逐一核對。

1552A／EDF2／1805A三個原地址身份保持NOTYPE,size0，各有另名captured_body FUNC helper；helper size僅代表實際entry fragment，不推論完整函式extent或prototype。

## 六項有限分派

1805A由RAM2000C926讀byte；18072的unsigned guard把1808E分派索引限制為0..5。18076／1807A取1AB04表址，scale4／LW／add-base／JR。六個relative words共24B，四個不同目標為18090、180C6、180D4、180E2；必要case union共56B／20條指令，與先前94B reachable union合成[1805A,180F0)150B單section，沒有以span補入未訪問bytes。

每個word以初值0與同址ADD32／SUB32表示；六項原位結果逐word相符，保留RELA multiset及multiplicity。目前共14張relative tables及兩個self-PC有限域，合計16個有限分派域；不能將domain數全稱為table數。本輪沒有新增跨section fallthrough契約；舊六項固定配置契約仍保留，不能宣稱整體可任意搬移。

1AB04有限表不解除1AAE8的首次索引生命週期、alias／ROM writers或缺失744B。來源地址接近不代表物件相同或較大資料域已證明。

## 三個條件式複製來源讀域

既有19BF0 helper的182B完整CFG沒有external call或未知transfer。實際source loads為1／4 bytes，包含對齊prefix、9-word（36B）unroll及4B／1B尾段。caller給定N為96、94、106，形成19CA8..19D08、19D08..19D66、19D68..19DD2三個來源窗口，共296B。與舊配置均不重疊，19D66..19D68兩bytes不補入。

這是明列條件下的source-read證明：D為各caller實際SP目的式，要求D>=32及D+N不超過UINT32_MAX；整數區間核對涵蓋16種對齊類。實體SP、RAM有效性與ABI相容性仍未證明，不能把這些條件當已達成的硬體事實。carriers只保存已證明的有限來源bytes，不宣稱原完整物件extent。

1AB58目前只證明read偏移1..7，第0 byte未證。因現generic尚無適合的不連續read片段／address-anchor模型，本輪維持原base UND，不硬配8B、不用ABS或code view冒充資料provider。

## 實際編譯結果與證據

新增3312B code＋320B RO＝3632B，92個physical sections（88code／4RO），99個新globals＝88FUNC＋4OBJECT＋7NOTYPE。491筆新增RELA＝229control＋250正常PCREL（125pairs）＋12relative（6pairs）。三個literal地址views及table view亦保持NOTYPE0，OBJECT carriers另名；沒有新RAM或新existing-code view。

整合52874B code＋3008B RO＝55882B file payload；545個非空配置（544file-backed與原35160B NOBITS RAM）、6256RELA、533個module providers、兩個existing-code views、534個relative expressions、27個RAM views。舊453配置、568個allocated globals、3061個完整allocated locals（含空名SECTION）及5765筆semantic RELA須完整保留。

ROOT receipt：`build/table-extension-e1083b45264141229a6826f85a13b0b4/verification.json`，SHA256 `2001fc4b15274f6ce8b7c4ae9c21ab7e18f5010dc70f3a9cfc3ae2abc1e3063c`。C11／C++17 merged object一致，SHA256 `ee9b762e7803d84e9becdf17166cb4325093aca708a09e2df1467736ee3d2ce2`；numeric witness SHA256 `7d28b600ab830b05569a58c7025c4960940595b65d03c647a578736ba9be0172`。Witness只核原數字與bytes，不是missing providers或韌體。

Standalone final receipt：`native/build/f6a8f4f959354f0894700a8a08d53251/verification.json`，SHA256 `36c7c1a1f2e43498d33c5208282428854f39009ac6720ea34fe4f90c9d3075a4`。每語言22個actual negative fixtures均拒絕，包含control／own-LOW、relative初值與RELA multiplicity、NOTYPE型別變更、ABS假provider、零gap及三個copy-source bytes的突變。Strict standalone拒絕44UND；整合仍拒絕65UND，按實際引用為9AE4／F666兩個非ROMdirect-only、62materialized-only及ROM1，沒有mixed UND。

獨立整合審查重新解析actual object／witness與負例，保存舊symbol／storage／RELA多重集，掃描目前known direct及finite computed入邊是否繞過guard或有限讀域條件。目的地另做fresh編譯、與受審W產物比對、舊檔雜湊保護與README備份；最終結果見`../../analysis/v4160-direct-frontier-2026-10-20/integration-review/review.json`與`destination-verification.json`。

## 目標仍未完成

目前captured raw instructions有178個indirect calls、56個non-return indirect tails及436個RA returns；這是靜態site數，不是已知callee或執行次數。本輪新增未知間接site為8E86（取ROM40058後JR）及F498（incoming a5 callback）；其他舊runtime／IRQ契約仍未閉合。ROM slot地址不證callee內容或ABI，RAM存入的指標不證被指向物件extent。

1A430／1A454／1A478被存入RAM2000BF88，setter把17寫入BF86；EE30 consumer另讀BF84 counter與BF86 limit，guard通過後讀pointer＋2*counter。缺乏limit／pointer全生命週期與alias閉包，不能因常數17或來源間距36B宣稱固定34／36B表。F4D0／F578經incoming a5到F498，只證codepointer用途，未證實際ABI或函式extent。

MCU／PCB、BOOT／ROM、實體記憶體／stack／IRQ、必要功能完整性及原藍牙OTA接受條件仍須證據。使用者目前無法讀晶片印字，不據此猜硬體定案。全程離線，不執行或模擬RV32、不連硬體、不刷寫；`target_ready`、`native_bin`與`ota_verified`保持false，沒有可燒錄重建BIN。
