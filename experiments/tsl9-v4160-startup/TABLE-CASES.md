# ID2966：三張相對表與可達分支本體

最新入口：`python verify-table-extension.py --spec evidence/table-cases-integration.json`。原`verify-extension.py`及舊spec保持不變；它們各自的舊階段結果不能代替本輪。來源只用76800B的ID2966／伺服器標籤V4.1.60，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，對實體硬體的完整適用性仍未證實。

## 已證的有限分派與實際捕獲

前輪已核1A680與1A6B8的unsigned guard、scale4、LW、add-base與JR，各讀28B／7 entries，分別有6與7個不同原目標。本輪從這13個目標追raw／r2 CFG，並保留caller先前已捕獲的入口與tail。

15362又出現nested dispatch：1534A的LBU經15356 SRLI2、15358 ANDI7，再scale4，於1A6D4讀8個word，經add-base／JR轉移。索引可證0..7，32B讀取聯集；8項有6個不同目標15364、1536C、15370、15394、153B0、153B4，後者重複三次。這些目標已續走，補上原先未解析的86B。這是固定原image的局部有限域，沒有執行RV32或證明任意異常entry／可變table／硬體狀態。

| 新code物理範圍，末端不含 | bytes | 與原捕獲的關係 |
|---|---:|---|
| 12B58..12B7A | 34 | 原12B24入口後的未走訪區段 |
| 12B82..12BC8 | 70 | 真computed targets導出的新增區段；不受舊bounded span末端限制 |
| 14D52..1549A | 1864 | 包含nested域後的連續可達聯集 |

共1968B／683條指令，三份physical code storage只配置一次。Shared tails與重複table entry不複製bytes；已有的12B7A..12B82／1549A..154A6 tails保持原storage。向外無link jumps與外部callee全部保留原控制引用及真實依賴，不假定return、callee ABI或整個邏輯函式extent。

13個exported FUNC helpers標記top-level case的captured entry fragments，在shared section內可有不同offset；其size只到該物理fragment末端，不是原作者C函式或該entry全部語意範圍。Nested targets以實際本地code labels參照。另有三個OBJECT carriers表示28／28／32B已證讀取聯集，三個address身份為NOTYPE、size0 views；這些有限視窗不證原完整資料物件型別／extent。

## 相對word的C／C++表示

88B RO有22個word，每項表示`target - table_base`。C11／C++17加RV32 inline assembly令每word有一筆ADD32(35)及一筆SUB32(39)，保留同址兩筆RELA。Assembler初值為0，link後的22個word逐byte等於原88B；不能把原encoded delta再次加減而重複編碼。

新verifier以list／Counter核每筆relocation及重複數，再計算`(initial + ADD(S+A) - SUB(S+A)) mod 2^32`，與原word比對。ADD必須指向真實captured code，SUB必須屬於自己的真table section；numeric witness不提供這些operands的實作。原source中的控制引用也以provider原位址加addend核對。

266筆新RELA＝216個直接控制引用（JAL84、BRANCH97、RVC_JUMP27、RVC_BRANCH8）＋3組正常AUIPC／own-LOW pairs（HI3／LO_I3）＋44筆relative32。實際本輪表式addend均為0；另行synthetic工具研究驗過雙addend及變更layout，該研究不代表原硬體相容性。

## 舊code的真section view

新case會回到既有12B7A tail。`__tsl9v4160_existing_code_12b7a`由partial-link script在舊`.text.tsl9v4160.direct_expansion_12b7a` section起點、KEEP之前建立，為global NOTYPE、size0、offset0；沒有新增storage或ABS實作。

其boundary綁定舊direct-expansion CFG SHA256 `7426eb0c195c7f855997df6b07348ba4d0e189cfc92c5a7c10bbdbead1d27265`，root12B24的真指令`12B7A:f240`，不是只憑偶數alignment或section flags。Fresh merged與linked witness均逐symbol檢查section、type、size與value，舊8B及全部其他配置保持原bytes。

## 最新整合與依賴

整合20700B code、547B RO，共21247B file-backed payload；226個非空allocations含225個file-backed sections及原35160B NOBITS RAM，27個RAM views不變；共1559筆RELA。Composite module providers為202個，其中183個來自前層，本輪新增19個（13FUNC／3OBJECT／3NOTYPE）；額外的舊code view另計1個，不能混成新函式。

Strict最終link仍拒絕92個UND／92個不同原位址：69個ordinary直接控制用途、22個目前僅materialized用途與ROM40000。增加的69個code義務由本輪實際分支揭露，沒有以未實作地址假裝閉合。1AAE8首次讀表的index生命週期仍未證，其他ROM參數／callback／資料extent也未因此解決。

W fresh receipt：`build/table-extension-1b1d208c38b248898a845717c0917c98/verification.json`，SHA256 `f00e6bfa2153423a262544d03642b7b290b87fe5328295d1b2f7b0d4e550f360`。C／C++ actual merged object同為 `6e588f4185a508d00c9eb3486b55182e78804f816bd30700fdfc6a45fa084981`；numeric witness同為 `a23925eaf2a09083f2d0bfa2a5ca4b1d5bd675bf2e7d5b2d28ecb6acc2b4b5d4`。witness只供原數字與原位bytes核對，不是韌體或缺失實作。

## 驗證與原機界限

Standalone每種語言實際測試16個負例，包括raw delta初值重複編碼、缺／改SUB、額外互相抵消的ADD／SUB、型別與ABS偽provider。額外同址pair實際compile/link後所有linked bytes仍相同，但因RELA Counter不符被拒。新整合verifier也有實際ELF的raw delta、SUB改ADD與舊code view改ABS負例，走同一檢查gate；測試metadata逐檔hash與內容回讀。

獨立review另核前層全部220個allocations、global／local views及1293筆semantic RELA multiset保留，不能只比較總數。交付資料在`../../analysis/v4160-table-cases-2026-10-20/`，目的地`destination-verification.json`另證fresh D編譯、舊檔保護、README備份及actual產物與審閱W一致。支援重做的入口與歷史取證路徑界限見REPLAY-NOTES。

原機MCU／PCB、BOOT／resident ROM、physical memory與stack／IRQ、完整必要功能及原BLE OTA接受條件仍未證。未網路、未執行／模擬RV32、未接觸硬體或刷寫；尚無可燒錄重建BIN，完整goal保持未完成。
