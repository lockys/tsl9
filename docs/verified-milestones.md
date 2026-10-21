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
