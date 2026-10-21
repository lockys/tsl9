# Verified milestones / 已驗證里程碑

Latest actual reset/entry/bridge/copy composition: C11/C++17 each17 groups/480,259
assertions; four compiled countercases rejected. This is synthetic host evidence.

最新實際reset／entry／bridge／copy整合：C11／C++17各17組／480,259項，拒絕四個
實際編譯反例；這是合成host證據。

## English

The resident-entry milestone reconstructs68B entry,114B initializer and48B RAM
seed. Source proof checks230B/66 instructions plus4B header and rejects35 raw
operand mutations. Parent C11/C++17 each pass5 groups/121,496 checks; independent
review each passes8 groups/149,883 checks. Composition links actual reset,entry,
bridge and reference-copy source over shared synthetic RAM/CSR state. RAM helper
identity is explicitly bound without executing its original instructions.

Actual main+tail stops at READ32 source6EB2C; main-only stops at6EAA4. Both preserve
the prefix without saved-RA reload,zeroing or MRET. A synthetic unknown-memory
fixture tests the suffix separately. MSTATUS preserves OR1888,RA is freshly
reloaded,and MRET observes current provider MEPC. Inner RI_LIMIT may become outer
reset HALT because the unchanged caller folds nonreturns; both states remain
reported. No native resident symbol or physical ABI is supplied.

The prior58B/18-instruction byte-copy retains MMIO save/clear/FENCE before guards,
live forward reads,increment-before-store and ordinary-only restore/RET. Parent
host suites pass5 groups/772 checks per language; actual BC/UID/copy/Flash
composition passes23 groups/34,613 assertions per language and rejects four
successfully compiled countercases. These are source/host results,not physical
Flash success or original firmware execution.

Source-level proofs are published under analysis/*/source/. Detailed local
independent/composition receipts also bind executable/log artifacts excluded from
this snapshot; historical replay may require the local archives. The publication
manifest verifies only actual shipped files. Milestones are committed/pushed
after precise staged-file and sensitive-data review. New docs are English plus
Traditional Chinese; old seals retain original bytes with companion notes.
Hardware,startup,installed ROM,memory,IRQ,physical Flash and BLE OTA remain unproved.

## 繁體中文

resident-entry里程碑重建68B入口、114B初始化與48B RAM seed；來源核對230B／66指令
及4B header，拒絕35個raw operand突變。父流程C11／C++17各通過5組／121,496項，
獨立審查各8組／149,883項。實際整合連結既有reset、新entry／bridge及reference-copy，
使用共享合成RAM／CSR；明確確認RAM helper身份，但不執行原始指令。

實際主段加tail在6EB2C的READ32停止，只有主段則在6EAA4停止；兩者都保留前綴，不提前
重讀RA、zero或MRET。合成未知記憶體fixture另驗後綴。MSTATUS保留OR1888，RA重新
讀取，MRET觀察provider當下MEPC。舊caller折疊部分nonreturn，內層RI_LIMIT可能成
外層reset HALT，兩層都分開報告。沒有提供原生resident symbol或實體ABI。

前輪58B／18指令byte-copy保留guard前MMIO保存／清零／FENCE、即時向前讀取、store前
遞增，以及只有正常路徑才restore／RET。父host suite每語言5組／772項，實際BC／UID／
copy／Flash整合每語言23組／34,613項，拒絕四個成功編譯的反例。這些是來源／host結果，
不是實體Flash成功或原韌體執行證據。

source-level proof位於analysis/*/source/。完整本機獨立／整合收據還綁執行檔與log，
暫存產物不放此快照，歷史重播可能需本機archive。publication manifest只核實際發佈
檔案。每個完成驗證的里程碑經精確staging與敏感資料審查後commit／push；新文件用
英文＋繁體中文，舊seal維持原bytes並旁附說明。硬體、啟動、原機ROM、記憶體、IRQ、
實體Flash及原藍牙OTA仍未證實。

## Runtime main, initialization and dispatcher: English

The newest model covers original ID2966 V4.1.60 main9008, initializer9250,
permanent loop8180 and dispatcher901A: 220 bytes/80 instructions. The portable
source proof rejects45 raw operand mutations. Parent C11 and C++17 each pass
6 groups/1,431 checks, with all seven model files, source proof, original firmware,
type dependency, compiler and actual executable pinned. Source/host effects do
not establish installed ROM, original ABI, hardware or OTA acceptance.

Calls require an explicit return route, including the initializer's tail call.
Loop callback slots are loaded afresh; live callee changes affect subsequent
numeric addresses/register values. Budget exhaustion leaves the frame in place,
never executing main9012 as cleanup. Dispatch mode is sampled before its argument;
one-shot fields clear before callback, and result masking uses live S0/S1 before
fresh frame restoration. Unknown bits never silently become zero. Detailed local
independent and actual RC/RI/ML composition seals remain in the delivery archive;
their host binaries are excluded from this repository snapshot.

Current actual RC/RI/ML composition passes21 groups/725,870 assertions per
language; independent model review passes7 groups/293 checks per language and
rejects six compiled behavioral countercases. Actual composition rejects six
successfully compiled countercases. Strict captured
resident segments admit no ML effects. The nested dispatcher experiment uses an
explicit synthetic resident-task policy; it does not identify the real scheduler.
The earlier composition attempt is retained as superseded; composition-v2 binds
the corrected full-known return-route rule and final parent receipts.

## Runtime主程式、初始化與派送：繁體中文

最新模型涵蓋原始ID2966 V4.1.60的main9008、initializer9250、永久loop8180及
dispatcher901A，共220B／80條指令。可攜來源證據拒絕45個raw operand突變；父流程
C11與C++17各通過6組／1,431項，核對七個模型檔案、來源證據、原韌體、型別依賴、
編譯器及實際執行檔雜湊。來源／host結果不代表原機ROM、ABI、硬體或OTA已獲證明。

每次callee均須明示返回路徑，包括初始化尾呼叫。loop即時重讀callback槽，callee改動
會影響後續數值位址與暫存器。觀察次數用盡時保留堆疊，不會把main9012當清理執行。
派送先取mode再取argument；單次欄位在callback前清除，結果在fresh frame還原前使用
當下S0／S1。未知位元不自動補零。完整本機獨立審查與實際RC／RI／ML整合seal保留
於交付archive，host執行檔不放此GitHub快照。

最新實際RC／RI／ML整合每語言通過21組／725,870項，六個成功編譯的反例均遭拒絕。
獨立模型審查每語言通過7組／293項，另外六個已編譯行為反例均遭拒絕。
嚴格使用擷取resident段時不允許任何ML效果；巢狀dispatcher實驗須明示合成resident-task
政策，不等於辨識真實排程器。較早整合保留為舊紀錄；composition-v2綁定修正後的完整
已知返回路徑規則及父流程最終收據。
