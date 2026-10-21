# Resident entry reference — English

This C11/C++17 project reconstructs fixed data/effect flows of the retained
Dec2023 V1.31 candidate: 40000 jump, entry68B/18 instructions, initializer114B/32,
and seed48B/16. It is not a CPU interpreter, physical ROM implementation or native
link substitute. `RI_DEC2023_133D3705` is an explicit reference choice, not hardware
detection. The unknown profile stops before effects. No original/rebuilt target
code, device I/O or network operation runs.

Entry establishes numeric GP20004000/SP20010000 and copies twelve live source
words40280..402B0 to RAM20000010..20000040. Each seed store returns before source
and destination advance. The copied18B word helper and30B zero helper are not
automatically treated as executable: a separate host `bind` callback must attest
the then-installed code identity. This premise is not an extra original data
read; absent/rejected binding preserves the prefix and stops. Register data is
preserved across primitive callbacks; synthetic memory may change.

Initializer saves RA6DEBE at SP2000FFF0+12, stores three global pointers, then
copies2957 words402B0→RAM40 (last2E70 inclusive) and35 words6EAA4→RAM2E70 (last2EF8
inclusive). The word helper reads a5, increments a1/a0, then stores through the
previous destination. Failed stores therefore retain advanced pointers. Source
and destination are live numeric addresses with unsigned32-bit arithmetic.

**Captured bytes do not prove completion.** With the actual main segment plus
136-byte tail, the35th second-copy READ32 requests6EB2C..6EB30, which is absent.
A strict captured-memory provider stops before that read returns:34 second words,
no pending store, no RA reload, no zeroing and no MRET. A main-segment-only provider
must stop earlier at6EAA4. An explicitly synthetic full/unknown-memory provider can
exercise the remaining flow; it cannot fill the original artifact or prove a real
Flash fault/read value. The ordinary suffix freshly reloads saved RA, restores
SP, tail-jumps to the zero helper, stores456 zero words and returns to6DEBE only
when that route is established. Wrong/unknown saved RA does not become MRET.

`RI_MRET` observes a fresh provider-declared transfer target (such as shared MEPC).
It does not add a CSR_READ instruction or presume physical CSR semantics. Even a
normal provider acknowledgement ends as TRANSFER; no original fallthrough or C
return is invented. HALT/TRANSFER/budget stops preserve all prior effects. New
activation is explicit and never native-PC resumption or automatic cleanup.

`ri_reset_handoff` accepts only the unchanged Runtime reset's RC_HANDOFF at18730
to40000. It does not reuse initial_gp/sp diagnostics as post-clock live state;
one shared synthetic memory/CSR provider carries MEPC/MSTATUS. The bridge maps
RI_LIMIT to RC_OBSERVATION_LIMIT, but the frozen outer reset folds that into
RC_HALT/RC_PROVIDER_UNKNOWN; the inner RI_LIMIT and exact prefix remain available.
No native `__tsl9v4160_rom_entry` symbol is defined and strict native linking is
still unresolved. The older V1.30 profile and IRQ-frame restore are not substitutes.

Run `./verify.ps1` and `./verify.ps1 -Cpp`. These pin original inputs/model sources,
replay the portable raw checker, and compile/run only own synthetic host tests
with MSVC `/W4 /WX`. Historical sealed evidence remains immutable. All new
narrative documentation is English plus Traditional Chinese; older sealed files
retain their original bytes and may have bilingual companion notes.

# Resident 入口參考重建 — 繁體中文

本 C11／C++17 工程重建已封存 Dec2023 V1.31 候選的固定資料／效果流程：40000 跳轉、
68B／18 指令入口、114B／32 指令初始化及 48B／16 指令 seed。這不是 CPU 模擬器、
實體 ROM 實作或原生連結替代品。`RI_DEC2023_133D3705` 是明確選用參考版本，不能辨識
硬體；未知 profile 會在任何效果前停止。沒有執行原始／重建目標程式、硬體 I/O 或網路。

入口建立數值 GP20004000／SP20010000，將40280..402B0 的十二個即時 source word
複製至 RAM20000010..20000040。seed 每次 store 正常返回後才遞增來源及目的指標。
搬入的18B word helper／30B zero helper 不會自動視為已安裝可執行程式；獨立 host
`bind` callback 必須確認當下 RAM 程式身份。這是模型的前提檢查，不是原指令額外的資料
讀取。未提供／拒絕 binding 會保留前綴後停止；primitive callback 保留模型暫存器，
共享合成記憶體則可以改變。

初始化先在 SP2000FFF0+12 保存 RA6DEBE，寫三個全域指標，再複製2957 words：
402B0→RAM40，包含末址2E70；接著複製35 words：6EAA4→RAM2E70，包含末址2EF8。
word helper 先讀 a5，再遞增 a1／a0，最後寫入先前的目的位址，因此 store 中止時，
已遞增的指標不會被復原。來源／目的都是即時數值位址，保留32-bit 無號運算。

**封存 bytes 不能證明初始化完成。** 實際主段加136B尾段仍缺第二次 copy 第35次
READ32 所需的6EB2C..6EB30。嚴格 captured-memory provider 會在該讀取返回前停止：
第二段僅完成34 words，不能先寫 pending word、重讀 RA、清零或 MRET。只有主段時，
更應在6EAA4第一次讀取就停止。明確標示的合成完整／未知記憶體 provider 可驗證後續
流程，但不會補入原檔，也不能證明實體 Flash 會 fault 或回傳特定值。正常後綴會重新
讀保存的 RA、恢復 SP、tail jump 到 zero helper、寫456個零 word；只有確認返回
6DEBE 才可能進入 MRET。錯誤或未知的保存 RA 不會被當作正常 MRET。

`RI_MRET` 觀察 provider 當下宣告的轉移目的地，例如共享 MEPC；沒有增加 CSR_READ
指令或假定實體 CSR 行為。即使 provider 正常承認，模型也以 TRANSFER 結束，不虛構
原流程 fallthrough 或 C return。HALT／TRANSFER／預算停止保留先前效果；明確的新
activation 不是原 PC 續跑，也不會自動清理。

`ri_reset_handoff` 只接受既有 Runtime reset 在18730跳至40000的 RC_HANDOFF，
不把 initial_gp／sp 診斷值當作 clock 後的即時暫存器；MEPC／MSTATUS 由同一共享合成
記憶體／CSR provider 承接。bridge 把 RI_LIMIT 轉成 RC_OBSERVATION_LIMIT，但既有
外層 reset 會折成 RC_HALT／RC_PROVIDER_UNKNOWN；內層 RI_LIMIT 與精確前綴仍保留。
本工程沒有定義原生 `__tsl9v4160_rom_entry`，嚴格原生連結仍未解析。舊 V1.30
profile 與 IRQ-frame restore 不能直接代替這段入口。

使用 `./verify.ps1` 與 `./verify.ps1 -Cpp`，核對來源／相依檔、重播 raw checker，
以 MSVC `/W4 /WX` 僅編譯執行自有合成 host 測試。歷史封存證據維持原 bytes；
新敘述文件採英文＋繁體中文，舊封存文件可由旁附雙語說明補充。實體硬體、原機 ROM、
記憶體／中斷 ABI 及原藍牙 OTA 仍未證實，`OTA_ready=false`，沒有新增可燒錄 BIN。
