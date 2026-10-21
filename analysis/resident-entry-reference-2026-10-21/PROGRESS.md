# Resident entry milestone — English

Final actual reset/entry/bridge/copy composition passes17 groups/480,259 assertions
in each language and rejects four actually compiled countercases. Parent read-only
replay checks the source/dependency/host-executable seals before delivery.

最終實際reset／entry／bridge／copy整合每語言通過17組／480,259項，拒絕四個實際編譯
反例；交付前由父流程唯讀重播source／相依檔／host執行檔seal。

Previous goal turn: **progress**. The reference byte-copy C/C++, actual UID/BOOT/
Flash composition and destination readback were delivered. This turn implements
the candidate resident's entry68B, initializer114B and RAM seed48B in readable
C/C++, plus the exact bridge from the unchanged Runtime reset. It does not define
the native resident symbol or change strict native-link requirements.

Raw source proof covers230B/66 instructions plus4B/1 header jump, with35 raw
mutation rejections. Parent C11/C++17 each pass5 groups/121,496 checks; receipts
pin9 model files and11 original/dependency files. Source data providers stay
explicit. The host binding callback must attest the then-installed RAM helper;
it is not an original data read. The word helper's pointer increments precede its
store, while seed increments follow its store. The saved RA is freshly reloaded
before SP restoration and the tail zero helper. MRET observes live provider CSR
state and terminates transfer, never an invented C return.

With main+tail captured bytes, the strict path stops at second-copy read35,
source6EB2C..6EB30, pending destination20002EF8. It has34 second stores, no frame
reload, zero suffix or MRET. Main-only stops at6EAA4 instead. Synthetic full/unknown
memory fixtures exercise suffix behavior without filling the original file or
proving the real read faults/succeeds. The existing reset's outer flow can fold
an inner RI_LIMIT into HALT; both layers and their prefixes remain explicit.

## Original objective audit / 原始完整目標稽核

| Requirement / 要求 | Current evidence / 目前證據 | State / 狀態 |
| --- | --- | --- |
| Necessary C/C++ features / 必要功能 | Existing features, transport, UID, BOOT, copy and new entry data effects / 既有功能與本輪入口資料效果 | Partial / 部分 |
| Original execution layer / 原機執行層 | Source-bound startup/IRQ/entry contracts; one true native resident UND / 有來源契約，真正resident入口仍UND | Partial / 部分 |
| Exact installed hardware/ROM / 實機硬體與ROM | Conditional WCH references, no exact physical identity / 只有候選，沒有確切實機身份 | Unproven / 未證實 |
| Startup/memory/IRQ compatibility / 啟動記憶體中斷相容 | Explicit providers, missing read and ABI obligations retained / 保留provider、缺讀與ABI義務 | Unproven / 未證實 |
| Actual Flash/update behavior / 實體Flash與更新 | Source and synthetic composition only / 只有來源與合成整合 | Unproven / 未證實 |
| Complete new installable BIN / 完整可安裝新BIN | Existing source-identical offline image; no new native resident implementation / 既有原位址離線映像，沒有新原生resident | Not achieved / 未達成 |
| Original BLE OTA acceptance/run / 原藍牙OTA接受與執行 | No physical acceptance/boot/behavior evidence / 沒有實機接受啟動或行為證據 | Not achieved / 未達成 |

GitHub synchronization now follows **each verified milestone**, as requested;
new narrative documents are English plus Traditional Chinese. Historical seals
remain immutable, with bilingual companions where needed. Publication requires
exact staged-file review and excludes real identifiers, credentials, private
request/response logs, temporary builds and unrelated files. Current host results
never authorize vendor probing, target execution or hardware I/O.

# Resident 入口里程碑 — 繁體中文

上一個目標回合分類為**有進展**：已交付byte-copy C/C++、實際UID／BOOT／Flash合成整合
及目的地讀回。本輪新增候選resident的68B入口、114B初始化、48B RAM seed可讀C/C++，
並從既有Runtime reset建立精確bridge；沒有定義原生resident symbol，也未降低strict
native-link條件。

來源核對230B／66指令，加4B／1條header jump，拒絕35個raw突變。父流程C11與C++17
各通過5組／121,496項檢查，收據綁9個模型檔與11個來源／相依檔。資料provider必須明確
提供；host binding需確認當下RAM helper身份，但不是原指令額外資料讀取。word helper
先遞增指標再store，seed則store後才遞增；保存RA會重新讀取，再恢復SP與tail zero。
MRET依provider當下CSR狀態觀察並終止為transfer，不虛構C return。

實際主段加tail時，嚴格captured流程在第二段copy第35次讀取6EB2C..6EB30停止，pending
目的為20002EF8；僅完成34個第二段store，沒有frame reload、zero後綴或MRET。只有主段
時更早在6EAA4停止。合成完整／未知記憶體fixture可驗後綴，但不補原檔，也不能宣稱實體
讀取必定fault或成功。既有reset外層可能將內層RI_LIMIT折成HALT，需同時保留兩層前綴。

依使用者指定，GitHub在**每個完成驗證的里程碑**commit／push；新敘述文件使用英文＋
繁體中文。歷史seal不改，必要時新增雙語旁附文件。發佈前審查精確staging，排除真實裝置
識別資料、憑證、私有請求／回應、暫存編譯與無關檔案。host結果不構成廠商探測、目標
執行或硬體I/O授權。現有76800B離線image維持SHA
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，
仍為NOT-FLASH-VALIDATED；完整原硬體／啟動／ROM／記憶體／IRQ／OTA目標尚未達成。
