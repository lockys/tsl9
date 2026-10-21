# TX 暫存器 ABI：必要條件與可接受的編譯差異

[English](readme.en.md) | [简体中文](readme.zh-CN.md)

本輪從原始 `0x8A56..0x8B6E` 的 280 bytes 與實際 C/C++ 物件，區分功能／ABI 條件與單純編譯排版。目標是相容行為；**不是所有不同 bytes 都必須改回原樣**。未知 ROM 與記憶體別名仍不允許直接宣稱硬體相容或放進既有完整映像。

目前已實際驗證窄 entry、真正返回的 typed C leaf 與新編譯 C body 合計 280 bytes；再以明示的 source-owned frame 排序層恢復 save／fresh restore 邊界。原始與候選 loop 的有限 CFG 對應也已核對。這些是分層的靜態成果，不是完整硬體／OTA 驗證。

## 哪些差異可以接受

- ADD、MUL 在相同位置、寬度與目的暫存器下，交換兩個同值來源的順序，仍是同一個 unsigned 32 位運算。不同位置還須證明資料依賴與觀測邊界一致。
- BEQ／BNE 的兩側可對調，但目標、條件與對應控制角色須另外核對。不能把外型相同的 sentinel 比較當成 gate 回傳值比較。
- 純內部條件反轉、區塊移動可以成立，但要對實際 CFG、返回 continuation、已知入口與 relocation 用途逐項核對。
- PCREL anchor 可移動，條件是實際 HI/LO 配對仍將同一個 RAM 符號地址放入 A3，使用時序與已知角色沒有遺失。舊 anchor `+0x80` 並非一律必須保留的位置。
- frame 的五個獨立 word save 若全部正常完成，來源暫存器尚未變動，且不主張 fault／中斷前綴等價，順序不同不一定改變第一個 ROM 呼叫看到的完成狀態。不能延伸成任意記憶體讀寫都可交換。

`predicates.py` 的 commutative shape 清單只是語法候選；它明確不證明不同 PC 的輸入值或邏輯角色相同。

## 仍然必要的具體條件

原始 unsigned `A3 > 1039` 路徑不配置 frame、不碰記憶體，保留 entry A0／RA／SP，A5 為 1039。第一個 ROM gate 的 RA 為 `0x8A90`，第二個為 `0x8AB6`。ROM 的實際行為未知，不能只依一般 C ABI 假設它忽略 RA、T1 或其他殘值。

第二個 gate 的 A2/A3 是第一個 opaque gate 留下的值；第二個 gate 返回後，即使判斷失敗，也先將 A2 設為 1。failure A0 隨路徑而異，不存在已證明的共同狀態碼。

成功路徑先 fresh-read RA/S1/S2/S3，才寫 descriptor；S0 則在 ROM tail pointer 讀取之前 fresh-read。這裡不能假設 stack 與 descriptor 不相交。例如 live SP `0x2000B170`、lane0 descriptor B `0x2000B18C` 時，saved RA 的 `SP+28` 就是 B。若 saved RA 為 `0x12340003`、N=1，先讀 RA 的原程式不受後續 `SH16(B+2,7)` 影響；延遲讀取卻會得到 `0x00070003`。這是來源工作者提供的位址區間與 byte 代數反例，不是 CPU 執行或已確認的實際 stack 位置。

copy 必須保持 live S0／S1、低16 counter 判斷、完整32 counter 地址與逐 byte read-before-write。tail 必須保持 task LBU、fresh ROM `+0x50` target、參數／殘值與 JR T1 不產生新 RA 的效果。

## 一般 C 的可行性與目前界線

簡化 C 範例確實能在 frame 前產生 guard；原函式移除 guard 的 memory clobber 或啟用 shrink-wrap 後仍未改變。因此 memory clobber 不是已證明的充分原因，也未證明一般 C 不可能做到。

實際 source-only split 診斷產生 18-byte entry 與 272-byte valid body。entry 的 oversized RET 不碰 frame，成立；有效路徑透過 compiler-owned AUIPC/JR T1 尾跳，無新 RA。但總共 290 bytes，超出原範圍；T1 在第一個 opaque gate 前多了一次寫入，且 body 的 late restore 問題仍在。這個診斷只證明一個前綴可用一般 C 達成。

canonical C/C++ 加入兩個 cold-success 分支提示後，實際產生 278 bytes／95 條指令。兩次 gate 的 RA 已恢復為 `0x8A90`／`0x8AB6`；這是一般 C 拓樸調整的實際進展。它仍先配置 frame，成功路徑仍延後還原，若放在原入口則尚少 2 bytes 的來源所有權證據。數值上放得下不代表可直接替換。

窄 entry 的第一個 assembler 實測曾將 external BLTU 擴成 BGEU+JAL，總共 284 bytes，未被接受。後續以標準 `bltu a5,a3,0` 與一筆 `R_RISCV_BRANCH` relocation 指向真 typed RET，實際得到 entry8／body270／leaf2：`0x8A56` 自然落入 `0x8A5E` 的 C body，超長分支到 `0x8B6C` 的編譯 RET。entry 的真 FUNC 大小是 8；280 是三段共用 allocation 的大小，不強造 280-byte compiler FUNC。這個入口沒有引進額外 T1 跳轉。

## 明示的窄 frame 排序層

新 pass 只處理新編譯 valid body 的兩個窗口：`[2,12)` 的五個 C.SWSP 與 `[208,270)` 的 success tail。prefix 重排成 S0/S1/S2/S3/RA；tail 只移動五個既有 C.LWSP，將 RA/S1/S2/S3 放到 descriptor SH 前，S0 放到兩個 SH 後／ROM pointer load 前，SP increment 保留在 task LBU 後。其餘指令 word 的順序、總長與全部 ELF metadata 不變。沒有讀取原始韌體來產生 words。

`tail.py` 獨立讀取 pre/post 物件，核對兩個窗口、全部外部 bytes、字詞 inventory 與 fresh-read 位置。`controls.py` 對每種語言做 14 項實際 ELF 變異拒絕測試，包含 storage alias、symbol/relocation/branch/call-return 進入窗口、錯誤暫存器／slot／寬度及重複套用。另有三個實際 CLI 路徑 alias 拒絕測試。這是 compiler 加明示 ABI 排序層，不宣稱 compiler 本身產生了最終順序。

## Loop 的有限對應

`loop.py` 讀取原始 96 條指令與實際 ordered linked ELF。原 BLTU 的 true 邊跳到 out-of-line payload；候選 BGEU 的 false 邊落入 payload。兩者使用相同低16 counter 與 live S0，比較後的八條 payload 指令逐 semantic fields 對應，僅 ADD A6 的來源順序互換；backedge 都回相同 counter header。checksum finish 及零次迴圈不寫 A6 也符合。每種語言的九個實際 linked 指令 byte 變異均被拒絕。

此對應以前後邏輯邊界的 A1/A4/A5/S0/S1 與逐次記憶體回應相同為前提。它沒有執行迴圈或 ISA 狀態；也不含非同步干擾、把不同 instruction bytes 當 payload 讀取、未知 computed interior entry 或任意 ROM 行為。既有完整映像的九個外部入口與 private role 尚需另外整合核對。

尚未採用的診斷不會取代已封存的元件或完整映像。沒有 full-function asm、原始 bytes 回填、padding、擴張舊 scheduler 或新 opcode encoder。

## 靜態檢查

預設僅檢查封存來源／中繼資料與相依來源 hash，不讀韌體或 build：

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/check.py --project-root .
```

完整的實際元件子集重驗由 `review.py` 串接 entry、兩個 frame 窗口、loop CFG 及既有 14 項 guard controls。它從新 producer receipt 的 `pre_folder` 讀取 provider，亦可用 `--providers` 指定。新收據採 create-only，重驗採唯讀：

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/formal/ordered/c --receipt /absolute/new-review.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --replay /absolute/new-review.json
```

預設 stdout 的 `actual_build_artifact_replay` 為 false，實際模式為 true；兩者均保留 `original_full_ABI_admitted:false`、`whole_image_integrated:false`。`review.sh` 無參數執行預設模式，其他參數轉交實際模式，可用 `PYTHON` 指定 Python。

個別來源與診斷工具仍可明確呼叫：

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/predicates.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/prior-native/c --receipt /absolute/new-predicates.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/split.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/split/c --receipt /absolute/new-split.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/candidate.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/candidate/c --receipt /absolute/new-candidate.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/loop.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --elf /absolute/ordered/COMPONENT-ONLY-NOT-FIRMWARE.elf --receipt /absolute/new-loop.json
```

收據採 create-only。`predicates.py` 的四項測試是已解碼運算元關係的拒絕檢查；`split.py` 的四項測試則確實修改新編譯 entry bytes，核對條件、RET link、T1 與 tail link；`candidate.py` 沿用已封存的七項實際運算元變異檢查，再另外要求兩次 gate 的實際 RA 符合原始來源。以上均不執行或模擬 RISC-V。已記錄的外部入口與內部角色證據有範圍限制，不宣稱排除了任意 computed reference。
