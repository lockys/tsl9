# Reuse audit companion — English

The immutable `reuse/README.md` was sealed before the bilingual-document request.
This companion adds Traditional Chinese without changing its original bytes or
seal. Its English original remains the detailed audit. Reuse the exact reset
handoff18730→40000 and shared memory/CSR provider, not an IRQ restore or numeric
address witness. The candidate sets its own GP/SP, saves and freshly restores RA,
and reaches MRET only through the established route. Actual native objects still
have one SHN_UNDEF resident entry; SHN_ABS40000 is only address evidence. Source
proof and host tests do not establish physical ROM, CSR, RAM, IRQ or OTA success.

# 重用審查旁附說明 — 繁體中文

`reuse/README.md` 在使用者提出雙語文件要求前已封存；本旁附文件補上繁中說明，不改
原 bytes 或 seal。英文原件保留完整細節與來源位置。

既有可讀 reset 模型已有合適接點：18730的 `RC_HANDOFF`，target40000。即使 backend
正常承認，`rc_reset` 仍以 TRANSFER 結束，不虛構18734 fallthrough。應重用此邊界與
數值記憶體／effect-provider 介面，不能重寫原 reset、套 IRQ restore，或用只有位址的
witness 去解析真正 resident symbol。

原 ID2966 的138B startup 已獨立核對：GP20004000、SP20010000、1AB60的128B初始化、
BSS終點2000C958；BC0寫31、804寫3、MSTATUS是 SET／OR1888，不能 overwrite；
MTVEC寫803B、clock18720→1874A，之後1872C才將MEPC寫9008。18730是 JAL x0，
不寫RA，也不是普通C呼叫返回。`initial_gp/sp` 只描述前綴，不能當作clock後即時寄存器。

候選V1.31的40000先到6DE7E，自行設定GP／SP；6DEBA呼叫初始化6DE0C，RA為6DEBE。
初始化SP減16、在SP+12保存RA，兩次呼叫已複製的word helper，再於6DE72重新讀RA、
SP加16、tail jump到RAM20000022的zero helper。只有最後返回路徑確認為6DEBE時，
才可能走到MRET；保存RA變動或未知時，不能直接替換成常數。此entry／init／seed沒有
MEPC或MSTATUS寫入，MRET仍依賴共享provider當下的CSR狀態與未證實的實體語義。

最新實際C與C++ merged objects各有691個配置section、8280筆RELA，以及唯一真正
GLOBAL UND `__tsl9v4160_rom_entry`：NOTYPE、size0、value0、SHN_UNDEF。數值witness
把同名symbol設成SHN_ABS／value40000，只證位址，不是resident實作；本審查讀實際ELF
metadata與既有strict拒絕收據，沒有重跑連結。原始image byte fidelity不能解除這項義務。

新的V1.31必須明確選用，不能沿用整個V1.30 RC／RK／GB profile。共享known-mask記憶體
與CSR bank，保留MSTATUS的OR及未知bits；MRET前可能的外部mutation不能被舊snapshot
掩蓋。RAM seed程式須在套用其資料語義前確認身份，不能推定instruction coherence，
也不能增加來源沒有的FENCE.I。IRQ模型的MRET終止邊界可參考，但其128B frame與CSR804
操作不能套在這個resident入口。

wordcopy包含末址：第二段請求140B，但tail只捕獲136B，缺6EB2C..6EB30。稍後zero會
覆寫目的2EF8，也不能證明之前的source讀取成功。嚴格captured provider必須停止；
只有明確的合成provider可供應成功但未知的結果，不能補原檔。bridge可保留內層
RI_LIMIT，但凍結的外層reset會將RC_OBSERVATION_LIMIT折成HALT；兩層狀態應分開報告。

`reuse/check-reuse.py --check` 會核來源operands、實際C／C++ ELF身份、目前source hash
與十個記憶體內反例；這些是host byte／metadata檢查，不是原程式執行。仍未知的項目
包括實機resident、vendor CSR／ISA／MRET、RAM／stack、低位RAM所有權、程式可見性、
clock成功、IRQ交錯與原C／callback／IRQ ABI。`OTA_ready=false`。
