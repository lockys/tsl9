# ID2966：剩餘直接入口與191C6本體

重做：`python verify-extension.py --spec evidence/direct-closure-integration.json`。來源只用76800B的ID2966／伺服器標籤V4.1.60，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。它對使用者這顆硬體的完整適用性仍未證實。不帶--spec仍驗舊core-flow，不能當成最新整合。

## 新增的37個本體

依前一層actual ELF的direct-control RELA選取36個ordinary UND，全部經raw／r2 CFG盤點，得到2270B、36個連續物理片段。新1929A本體又有6個JAL指向原materialized身份191C6，於19382、1938A、1949A、194A0、195D6、195DC；六處都是真指令邊界，原bits與重定位均保留。

191C6另經raw／r2核對：191C6..19220共90B，無hole、舊配置或本輪重疊、unsupported、AUIPC、call、間接transfer或外出edge。故本輪補上此真實body，不把新發現的callee繼續留成任意數字。原address191c6仍是NOTYPE、size0、section-relative view，與captured_body_191c6的90B FUNC helper共用同一份storage。它原本於19BBA／19BBE被取址、19BC2存入stack、19BCC把stack指標傳給ROM slot40074的用途不被抹除；捕獲本體仍不能證明ROM或原始C ABI。

本輪合計2360B、37個物理code sections、37個FUNC labels加1個原NOTYPE view，共38個新exported providers。FUNC size只表示entry fragment，不是原作者完整邏輯函式extent或原型。所有新storage無holes、舊配置／本輪root重疊與decode／budget截斷；沒有假填空白或複製shared tails。呼叫後續可達性仍採有界caller inventory的continuation假設，不宣稱未知callee一定返回或保存暫存器。

新增102筆semantic RELA：JAL14、BRANCH30、RVC_JUMP10、RVC_BRANCH18，共72個直接控制引用；另15組正常AUIPC／own-LOW pairs，HI15、LO_I14、LO_S1。15個非零addend都指向真__ram OBJECT carrier的內部地址，沒有非零direct-control addend、自指AUIPC特例或舊code interior需求；舊generic verifier不變。

Standalone僅有兩個UND：既有真RAM carrier與既有實際232B的call16CC4。它們在composite中由原section-relative providers提供，沒有偽造ABS實作、新RAM配置或值。Component單獨的strict拒絕兩UND，與composite還缺的24個身份是不同範圍。

## 整合與尚未閉合的部分

新spec沿用凍結core-flow baseline及前五個module，再加direct-closure；前一層全部183個非空allocations、global／local views與1191筆semantic RELA須實際保留，不只比對總數。C11／C++17加RV32 inline assembly保留原指令與引用，尚未還原原作者的高階C型別及完整功能契約。

最新整合18732B code、459B RO，共19191B file-backed payload；220個非空allocations含219個file-backed sections與原35160B NOBITS RAM。27個RAM views不變；共1293筆RELA。Composite module providers為183個，其中145個來自前層，只有38個是本輪新增。

嚴格最終link仍拒絕24個UND／24個不同原位址。Actual ELF中只有ROM40000尚有未提供的直接控制引用；其餘23個身份目前只有materialized用途。這不證明全部程式或依賴已閉合：間接指標、表分派、未知ROM副作用及資料extent仍需取證。不能按address名稱猜成資料物件，也不能因call名稱清空就宣稱完整原始碼恢復。

W fresh receipt：`build/extension-21c482fa6a114710b2f38cb4d082fa10/verification.json`，SHA256 `f9ffe27c3a912b44695c093cf53bb1034db2850d02cb4f5ecea2cafd20f4e912`。C／C++ actual merged object皆為 `31c8aaffed8c0cbd0e5655edd8834b0786e5890f0b79d868e909c3881f375dd1`；numeric witness皆為 `d02d7c7be60543e6e1103bfef2aa4bfa8ac61decbbc8f8014274f927be05f0c3`。witness只綁原數字核對原位bytes，不提供缺失實作，不是可執行／可刷寫韌體。

## 取址身份與表的後續證據

本輪materialization-review另外研究前一層24個取址身份的實際consumer；其中191C6的新direct用途已由真body供應。1A680／1A6B8已證各28B、七項相對跳轉表的有限域，分別有6／7個不同原目標；guard、word、mod32目標計算與首指令均已核。但本輪native沒有配置這兩份RO視窗或補走它們的target bodies，不能把取證結果當成已實作。相對entry的target-minus-base語意、目標instruction boundary與單次物理storage均須在後續捕獲時保留。

1AAE8仍只有正常reset清零與已知mod7 writer寫0..6的條件式證據。首次讀表早於mod7；ROM／alias等副作用未閉合，生命週期不變量仍未證。原檔尾端僅280B，不能猜填保守1024B讀域所缺的744B，也不能借其他版本資料。

## 驗證與原機界限

Standalone audit實際拒絕六種負例：刪直接relocation、LOW addend偏移、額外零byte配置、缺callee偽ABS-FUNC、captured FUNC只改為SHN_ABS，以及原191C6 view只改NOTYPE為FUNC。Fixture路徑／hash／symbol與聲稱的byte差異逐項重開實檔核對；這些negative只證明所列檢查有效，不能證明原機相容。

來源、獨立審閱與交付收據位於 `../../analysis/v4160-direct-closure-2026-10-20/`。目的地destination-verification.json另證明fresh D編譯、舊檔hash保護、README備份及實際產物與已審W版本一致；歷史W取證路徑與目的地重播入口分開看待。

實體MCU／PCB、BOOT／resident ROM、physical memory與stack／IRQ、完整必要功能及原BLE OTA驗收條件仍未證。未網路、未執行／模擬RV32、未接觸硬體或刷寫；尚無可燒錄重建BIN，完整goal仍未達成。
