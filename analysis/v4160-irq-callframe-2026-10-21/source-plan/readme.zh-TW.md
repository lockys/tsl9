# 可呼叫 C 重建的原始 callframe 契約

原始初始化器 `0x9A42..0x9AD2` 精確為 **144 bytes、46 指令**；四個 helper 各 30 bytes／12 指令。本審查以 runtime `0ee64183...` 及 source seal `4d6745033aae496576b9db2fb7467396fbfda5067713cf1451a34b949b414283` 核對全部 264 bytes／94 指令；重用封存 decoder，另解碼 JAL 和 compressed frame operands，保存完整指令邊界，未執行 ISA 或編譯重建程式。

`0x9A42` 使 SP 減16，frame base 為 **進入時 SP−16**，不能假定絕對 RAM 位址。依序保存 S2@0（`0x9A44`）、RA@12（`0x9A46`）、S0@8（`0x9A48`）、S1@4（`0x9A4A`），全部早於 `0x9A50` CSR800 clear88。`0x9AC2` set88 後，`0x9AC6/8/A/C` 重新從記憶體載入 RA@12、S0@8、S1@4、S2@0；`0x9ACE` SP 加16；`0x9AD0` RET。

重新載入具有實際語意：原始程式回復記憶體中的 word，不能當成抽象保存值。若 stack word 被外部改變，返回值也可能改變；相同入場值的推論需假設 stack 未遭修改。此處未證明 frame 對齊、非同步中斷或外部 stack 行為。CSR set 也不是還原先前儲存的 CSR。

| call 位址 | 四-byte JAL 目標 | 返回續行 | A0 mask | A1 | 新讀取位址 |
|---|---|---|---|---|---|
| `0x9A5E` | `0x19142` | `0x9A62` | `0x02020006` | 1 | `0x4002101C` |
| `0x9A6A` | `0x19124` | `0x9A6E` | `0x101D` | 1 | `0x40021018` |
| `0x9A74` | `0x1917E` | `0x9A78` | `0x02020006` | 1 | `0x40021010` |
| `0x9A7E` | `0x1917E` | `0x9A82` | `0x02020006` | 0 | `0x40021010` |
| `0x9A88` | `0x19160` | `0x9A8C` | `0x101D` | 1 | `0x4002100C` |
| `0x9A92` | `0x19160` | `0x9A96` | `0x101D` | 0 | `0x4002100C` |

全部實際編碼 rd=RA，signed JAL 位移在範圍內且為偶數。RV32C 不要求四-byte 對齊。目標皆是 helper 起點，link 皆為 main 指令邊界；不能用不設定 link 的 J x0 取代 helper call。

長期常數角色為 S2=88（`0x9A4C` 至兩次 CSR）；S1=`0x02020000`（`0x9A54`，在 `0x9A58/6E/78` 加6）；S0=`0x1000`（`0x9A62`，在 `0x9A64/82/8E` 加29）。原始 helper bytes 只寫 A0/A4/A5，保留完整 A1、三個 S 暫存器、A2/A3/SP/RA，不另開 frame，透過實際 link 返回。六次 RMW 必須各自新讀取；連續啟用／停用也不能重用舊 word。

最後 helper 的 A0 是新 READ32(`0x4002100C`) AND `0xFFFFEFE2`；後續六次寫入及 CSR 不寫 A0/A1。一般返回 A1=0、A4=128、A5=`0xE000E000`；main／helper 不寫 A2/A3；S0/S1/S2/RA 由 frame 新載入。既有 caller 證據顯示 A3 會往 `0x131E0` 未知 callback 傳遞，是否使用仍未知，必須保留。已知 `0x9258` call 的 link 是 `0x925C`，但函式應依實際入場 link 返回，不能寫死。

## 下一版 C 的具體限制

六次呼叫需使用原址、bytes 相同的 **out-of-line** helper；一般 helper API 保留 A1 完整位元。普通 C ABI 允許 A2/A3 等 caller-saved 暫存器被改，僅靠型別無法保留原始契約。若開放 S0/S1/S2 作常數快取，必須檢查實際儲存／重載、所有目的暫存器、真正 prologue／epilogue 及 outlined 函式。不能將不同 frame slot 當成逐點等價。

一般 RV32 C call pseudo 在停用 relaxation 時可能是 **8-byte AUIPC/JALR** 加 CALL relocation；六次會比原始四-byte calls 多24 bytes。此處未證明新版 call 寬度。任何限定 direct-JAL primitive 或 linker relaxation，都需另查參數、clobber、RA、六次位移及邊界；不能為通過大小限制而開啟全面 relaxation 或弱化 section assertion。本設計不構成修改 compiler profile 的授權。

候選必須查實際 C/C++ object／連結機器碼、helper identity、六次 call 順序／目標／link、聲稱的 16-byte frame、CSR順序、新 RMW、尾端寬度、最終 A0/A1/A4/A5 及所有必要保留值。不同但符合普通 ABI 的 frame 不等於原始 stack 效果。大小必須重新量測，使用 call 不代表必然放得進144、完成配置或具備非同步 IRQ 等價。

十一個指定 raw 變異（frame 大小／slot、call rd／目標、mask、CSR來源、返回暫存器、末次 flag、尾端寬度）實際在記憶體中修改並被 source gate 拒絕；不是 compiled mutants。ledger 保存完整 raw rows、geometry、輸入雜湊及限制。未修改 model／舊證據，沒有編譯、ISA 執行、網路、硬體或新 BIN。
