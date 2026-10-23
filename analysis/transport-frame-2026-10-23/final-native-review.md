# v6 獨立 source／native review

[原始契約](original-contract.md) · [完整 machine／artifact 證據](final-native-review.json)

對 frozen `transport_frame.v6.c`（SHA256 `6908f14f0fc37e6491cdcd043a909059117eee04a0e15cf0013fda2950a119e8`）及既有 C／C++ probe-v6 各兩份實際 ELF 做離線唯讀檢查。範圍內通過；未發現新的 operand／then-live source mismatch。此紀錄沒有重跑編譯或正式 checker。

- 原始範圍280 B／96 instructions，13 regions長度／順序／owner全對；native和partial各13 genuine FUNC，無額外ALLOC、UND或global ABS。
- 九筆真實 pending RELA：8×R_RISCV_BRANCH(16)、1×R_RISCV_RVC_JUMP(45)，addend與encoded immediate均0，target皆為正確genuine FUNC。其餘246 B逐byte原樣；含control opcode／register／condition共有2133固定bits相符。
- C／CPP native ELF均 `e722e2ce3361c930be307507328e1305280e5cc06c4f854fa84b6882b07d6984`；partial均 `8c9c84504250b95495d9a82bb8ce1c58d3e333c0801a46fe1174a792a3cd20de`。
- 兩組 `b7070400 83a7c713` 各自推導word-address `0x4013C`；tail `b7070400 03a30705`推導`0x40050`。v1錯誤已在原始契約保留；本次只review v6。
- 兩個 C.JALR A5保留link；原位續接為8A90／8AB6。tail是C.JR T1、rd0，並保留interleaved restores／metadata stores。
- S0/S1/S3與SP／GP在原始使用位置依physical ports取then-live值；不把入口長度當post-call限制。A1維持full32 index，只有比較值縮成u16。
- 只有cold copy的8B5A寫A6；8B62使用A6作store address。選定路徑copy零次時，後續body不額外寫A6。這不假設先前opaque admission保留A6。

既有9份source/tool/header inputs、20份mode artifacts、每語言5recipes與2筆MD dependencies均核對實際hash／flags／path／size；compile／IR／link diagnostic logs為空。flags只准X10..X16 allocation，其餘GPR保留。兩語IR各13functions、4volatile loads、6volatile stores；physical S-register memory ports另依實際指令檢查。這些是有限IR anchors，沒有宣稱完整SSA驗證。

**尚未閉合：**partial仍是VA0的ET_REL，九個machine branch displacements未解析，全280 B機器碼並非原樣。AUIPC計算只在正確原位有預期base。動態admission／tail provider即使沒有UND symbols仍未知；1039只在call前檢查，post-call長度、alias／fault／IRQ、resident ABI、協定／座椅／免打擾、實體傳送與刷寫均未驗證。未執行target／ISA／ESIL／MMIO／硬體／網路；`firmware_ready=false`。
