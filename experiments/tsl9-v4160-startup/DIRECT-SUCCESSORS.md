# ID2966：66個直接入口、必要分派與有限常數讀取

最新入口：`python verify-table-extension.py --spec evidence/direct-successors-integration.json`。新spec須明示；不給spec仍是舊table-cases階段。原generic、verifier、舊spec、sealed scopes及先前C/C++均保留。

來源僅用76800B的ID2966／server V4.1.60，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。標籤不證使用者實體TSL9對應硬體。C11／C++17搭配RV32 inline assembly保留已證指令與引用；不是恢復原作者C/C++、prototype或完整ABI。

## 真入口與共享配置

上一輪actual ELF的169筆incoming direct RELA導出66個非ROM入口。每一個都經raw／r2 CFG核對，合併為5800B／1941條指令，67個物理code fragments，與舊315配置無重疊。沒有unsupported、decode mismatch、硬截邊界或linear 4K cutoff。

`D53C`與`E220`為split roots，兩者共享`E220..E246`的38B，只配置一次。`D53C`原bounded domain以外的`EBAA`是真控制義務；`E220`的graph已捕獲`EBAA..EBAC`兩個原bytes，不猜RET或重配storage。未走訪區段不依span整段複製或補零。root-local holes與全域未捕獲bytes分開記錄，不能相加充當payload。

66個FUNC helpers只表示實際entry fragments，其size不是原完整邏輯函式範圍。必要case targets採真本地指令labels，不另宣稱原作者函式。

## 五張有限相對表與必要分支

| JR site | unsigned guard | table base | index | bytes |
|---|---|---|---|---:|
| E244 | E222 | 1A13C | 0..4 | 20 |
| E27E | E26A | 1A150 | 0..29 | 120 |
| E826 | E812 | 1A1C8 | 0..82 | 332 |
| E974 | E960 | 1A314 | 0..9 | 40 |
| EA6C | EA58 | 1A33C | 0..60 | 244 |

E220先以unsigned guard限制原incoming a2；其餘表有原byte normalization與guard，再scale4／LW／add-base／JR。從E244五項續走，遇四個nested finite domains後逐一證域、續所有目標，共189words／756B、72個不同目標。

必要case union為`E246..EBAA`（末端不含），2404B／772條指令，真contiguous捕獲；沒有受初始4K或五個top-level entries截斷，也沒有填補未訪問bytes。新增case沒有未解間接轉移；64個direct callsites引用38個不同callee，其中16個已有真provider、22個仍未提供，逐一保留真引用與義務。

五張表的每個word由初值0與同址一筆ADD32(35)、一筆SUB32(39)表示。核對`(initial + target + target_addend - base - base_addend) mod 2^32`須等於原word，保完整RELA multiset及multiplicity；不能複製raw delta再加減一次。ADD指向真captured code，SUB屬於自己的真table section。

這是固定image、已證consumer path的有限域，不證任意進入block或硬體異常狀態安全。獨立整合review另掃目前admitted raw／actual ELF的已知direct及finite computed入邊；未分析全image或任意callback入口時，不能聲稱全域不存在bypass。

## 四個literal讀取視窗

| address identity | index計算 | index domain | bytes |
|---|---|---|---:|
| 1A4E4 | `((LBU_u8+16)&255)>>4` | 0..15 | 16 |
| 1A518 | `(LBU_u8+1) REM 15`，dividend為1..256 | 0..14 | 15 |
| 1A528 | 同一已證index | 0..14 | 15 |
| 1A538 | 同一已證index | 0..14 | 15 |

四份合61B，以原始literal bytes初始化，與relative表的零初值分開。兩種RO都必須在link後等於原image。表間空隙不配置；OBJECT carriers僅表示有限讀取聯集，原address identities為NOTYPE、size0 views，沒有推定原完整物件型別／extent。

49個前層materialized-only UND共有65組實際HI／own-LOW引用，consumer ledger在本輪materialized-review。`D7A4`／`D7B0`／`D7BC`／`D7C8`只經`D8E2`／`D90E`傳往`9124`，不能憑間距擅給12B資料或猜callee讀取長度。其餘資料與callback仍明列未知。

## 新元件與整合實際結果

新增8204B code＋817B RO（756relative＋61literal）＝9021B，77個配置（68code＋9RO）。84個defined globals＝66FUNC＋9OBJECT＋9NOTYPE。1462筆新增RELA＝780direct control＋304正常PCREL（152 pairs）＋378relative（189 pairs）。107個HI sites使用既有真RAM carrier，沒有新RAM或RAM view；原27個views不變。

整合42350B code＋1620B RO＝43970B file payload，392個非空allocations（391file-backed＋原35160B NOBITS RAM）、4636筆RELA、365個module providers，額外舊12B7A code view1個；275個relative32 expressions＝舊86＋新189。舊315配置、全部global／local symbol identities及3174筆semantic RELA須完整保留。舊五個原位fallthrough adjacency contracts仍保留，不能因此宣稱whole program任意可搬移。

Fresh ROOT receipt：`build/table-extension-7698075fa486487aae0a3d0803f3e3e5/verification.json`，SHA256 `55ce65555d340f7d82b766c4ee2bc962f909fe7f26416b36d788faef5169d546`。C11／C++17 actual merged objects同為 `4f3c17ada935b9a5f9b7a843dc545814d57ef603c5d8a4035e8b4adf7775b017`；原位numeric witnesses同為 `d476e6920cec4007e1b1b88bb9e0a369af81c7cc0836edca5a58e00e99b6c161`。後者只核原數字／bytes，不是缺失provider實作或韌體。

Standalone final receipt：`native/build/32e5d12054384140a97f78fc340342b4/verification.json`，SHA256 `f8292f63d8ca4f33c2d382dd46512cdb742c65f0d8d818ce4b81307082c3636a`，strict拒絕102個UND／102個不同VA。初稿104 UND的舊receipt保留為superseded，不能取代final。

每語言23個actual ELF反例均被拒，涵蓋控制／PCREL變更、relative初值／SUB／addend、同址數值抵消仍多出RELA、九個NOTYPE view型別變更、captured／missing callee的ABS偽provider、未證零填及兩個mixed UND的type-only突變。metadata及fixture實檔逐一回讀，不能只看測試名稱。

整合strict仍拒絕116個UND／116個不同VA，依actual用途為47 direct-only、66 materialized-only、2 mixed與ROM1。`AB02`、`137C0`分別以單一NOTYPE UND身份保留direct及PCREL雙用途，沒有以數字地址或函式型別假閉合。總數雖與前層同為116，原66入口已捕獲，新依賴由真分支揭露；不能把UND數字當成功能完成率。

目的地另做fresh編譯、actual產物與已審W比較、舊檔hash保護及README備份，結果看`../../analysis/v4160-direct-successors-2026-10-20/destination-verification.json`。取證scope搬移限制見REPLAY-NOTES。

## 完整目標仍未完成

本輪保留七處新的unknown indirect：六處取用未知ROM slot4004C callee，107D6調用incoming a3 callback；caller參數或呼叫外觀不能證實際ABI。其他原有runtime pointer／ROM／IRQ義務同樣未解。

1AAE8首次index全生命週期、alias／ROM writer及資料完整extent仍未證；原image尾端不足744B不補零、不借其他版本。MCU／PCB目前不可讀，BOOT／resident ROM、physical memory／stack／IRQ、完整必要功能及原BLE OTA封裝／接受條件都需要實際證據。

本輪離線，不執行或模擬RV32、不連硬體、不刷寫；`target_ready`、`native_bin`、`ota_verified`保持false。尚無可燒錄重建BIN，完整goal保持未完成。
