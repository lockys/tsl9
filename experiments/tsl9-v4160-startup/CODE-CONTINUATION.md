# ID2966：47個直接用途入口與原地址身份

重做：`python verify-extension.py --spec evidence/code-continuation-integration.json`。沒有給 `--spec` 時仍驗證舊core-flow，不能把該結果當成最新整合。來源限定76800B的ID2966，伺服器標籤V4.1.60，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；對使用者硬體的適用性尚未證實。

## 新增的實際程式

從前一階段實際ELF的直接控制重定位選出47個缺少本體的ordinary entry：44個原call名稱，加上13346／17666／197B8三個沿用address名稱的身份。ROM40000另列，沒有為它虛構本體。47個入口全部經raw指令與r2有限CFG核對，新增4372B、1526條指令、47個連續物理code sections。沒有與舊136個allocations或本輪其他root重疊，沒有hole、unsupported、解碼差異或budget／linear-boundary截斷。

這是C11／C++17加RV32 inline assembly的真實指令表示。它保留既有機器層行為與引用，不表示已還原原作者的C型別、原型、完整邏輯函式extent或外部callee ABI。11個root有外出明示控制邊，實際目標維持既有provider或真UND；未知間接目標仍未知。

| 原身份 | 本輪原身份型別 | 共用同一配置的指令本體標籤 | 捕獲範圍，末端不含 |
|---|---|---|---|
| address_13346 | NOTYPE，size0 | captured_body_13346，FUNC，672B | 13346..135E6 |
| address_17666 | NOTYPE，size0 | captured_body_17666，FUNC，58B | 17666..176A0 |
| address_197b8 | NOTYPE，size0 | captured_body_197b8，FUNC，6B | 197B8..197BE |

因此本輪有47個FUNC labels及3個原NOTYPE views，合計50個exported providers，**不是50個已證原始函式**。NOTYPE views沒有額外storage，也沒有被升格為C-callable宣告。FUNC size只描述實際entry fragment。

293筆新RELA由229筆直接控制引用及32組正常AUIPC／own-LOW pair構成：JAL100、BRANCH59、RVC_JUMP26、RVC_BRANCH44、HI32、LO_I22、LO_S10。沒有self-PC特例、非零direct-control addend或舊code interior引用。7筆非零PCREL addend引用真RAM carrier的5個內部地址；14個舊RAM view的metadata維持其原角色，沒有提供RAM內容或新配置。

## 真正整合結果

新spec沿用凍結core-flow baseline，保留callback、readonly、frontier與direct-expansion四個舊module，再加code-continuation。沒有修改generic verifier或舊spec。前一層全部實際storage、符號view與898筆semantic RELA須保留，而非只比較總數。

目前為16372B code、459B RO，共16831B file-backed payload；183個非空allocations含原35160B NOBITS RAM，27個RAM views不變；共1191筆RELA。composite module providers有145個，其中95個來自前層，只有50個是本輪新增。

嚴格最終link仍拒絕61個UND／61個不同原位址。從actual ELF引用用途分類為36個ordinary直接控制目標、24個尚只有materialized用途的身份與ROM40000。ROM也有直接控制引用，但缺少resident實作／ABI證據；24個取址身份不能僅憑名稱判定為資料物件或callback。新增真callee也揭露新依賴，所以UND由69減為61，並不等於只剩8個重要問題。

W本輪fresh receipt：`build/extension-eb46b3d5c531432a8406c2a844792041/verification.json`，SHA256 `1c95f5cb5960a767ee58ca4e0e488f60cc4d58c4b9ad5d2e2efb1a2591c1db85`。C／C++ merged object皆為 `6cca5e2805b1bd9b6efde3ac1f4b43ddd8827d290b22645dfa4cfc3e9e07a333`；numeric witness皆為 `e83abdbbc234aeaec36dcf1dc0716ff303eb6255e1fba322a8445e2f1a2ea156`。witness僅使用缺失身份的原數字核對原位bytes，不是實作、可執行韌體或可刷寫產物。

## 首次讀表的條件式證據

1AAE8的index來自17832的LBU gp+370；17844先讀表，1785A才mod7，17868才SB寫回。正常reset於186EE逐word清零20004080..2000C958，確實覆蓋20004172，因此正常完成reset後該byte為0。已知writer若到達，對LBU的0..255域可證寫回0..6。

全image的38399個2-byte對齊位置掃描及有限alias形態檢查，不能證明沒有其他writer。已捕獲code仍把RAM指標交給未知ROM；多步alias、外部callee、interrupt／DMA及非正常entry未閉合。因此「正常reset且只有此writer且GP保持」之下的歸納成立，**實際全生命週期index<=6仍未證實**。

不能把後續mod7倒推為首次讀表範圍，也不能直接提供7-word table。原檔1AAE8至末端1AC00只有280B；u8的保守1024B視窗超出檔案744B。這是尚未閉合的證據域，不是已觀察到硬體越界；沒有補零、借其他版本或把相鄰initializer併成同一object。

## 驗證界限與交付

單元audit包含實際ELF負例：漏relocation、LOW addend偏移、額外零byte配置、缺失callee偽ABS provider、captured FUNC改ABS，以及三個原address view逐一改為FUNC。拒絕這些負例只證明所列靜態檢查覆蓋它們，不證明原機功能完整。

交付資料位於 `../../analysis/v4160-code-continuation-2026-10-20/`；其中獨立review核對實際產物與舊層保留，`destination-verification.json`另記目的地fresh編譯、舊檔hash保護及兩邊實際object／witness一致。來源與analysis內的W歷史絕對路徑是取證來源，不是可攜重播承諾；支援目的地入口見REPLAY-NOTES。

實體MCU／PCB、原BOOT／ROM、記憶體與stack／IRQ契約、全部功能和原藍牙OTA接受條件仍未證。未網路、未執行或模擬RV32、未接觸硬體、未刷寫；尚無可燒錄的重建BIN。原完整goal保持未完成。
