# Callback 呼叫邊界：GP 半字資料不是漏傳參數

[English](readme.en.md)

這份補充只回答新的 def/use/kill 問題。十五站的目標來源、A0..A7 明示設定與 opaque 殘值，仍以已封存的 `v4160-event-callback-2026-10-22/source-review/contracts.json` 中 `opaque_calls`、`additional_raw_argument_obligations`、`all_calls` 為準；沒有重製另一張參數表，也沒有修改舊證據。檢查器同時辨識工作目錄的 `apk-analysis/tsl9-` 與交付目錄的 `analysis/` case 路徑。

新檢查從官方 ID2966 的實際檔案（base `0x8000`、SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）重讀十五個 JALR 的 rd、rs1、寬度與 RA，並核對這個短控制流窗口。沒有重跑舊 217 指令／26 反例矩陣。

| 原始位址 | 原始欄位及用途 |
|---|---|
| `0x87C8..0x87CA` | A0 與 1 後，非零分支進入 `0x87FC`；A3/A4/A6/A7 沒有被覆寫。 |
| `0x87FC` | A5 = live GP，供下一筆載入定址。 |
| `0x8800` | **LHU A5,[A5+0x2A]**；目的暫存器是 x15，並非 A4。 |
| `0x8804..0x8806` | A2=0，A1=live S1。 |
| `0x8808` | SH A5,[live S1+0]，只消費資料的低 16 位。 |
| `0x880C` | **LW A5,[live S7+0xD4]**，覆寫先前資料值，建立呼叫目標。 |
| `0x8810..0x8812` | A0=live S5；JALR RA,A5，原始 link=`0x8814`。 |
| `0x8814` | A0 非零時轉入 `0x87CC` 的 release 路徑。 |

因此 GP+0x2A 的資料在 `0x8812` 已 dead。將它補入 C 的 `a[4]` 反而會改寫原碼保留的 post-`0x87C6` A4 殘值。**這一站沒有發現需要修補的 C 參數漏傳。** 目前 C 已使用獨立的 `v` 完成 SH，再載入 `target`；native call port 將 target 放入 A5。

選用 `--component` 時會讀取先前封存審查過的實際 624B ELF，不執行它。C／C++ 的實際位元組相同：`0x120A` 的 LH A0,[GP+0x2A] → `0x120E` 的 SH；`0x121A` 又以 connection 角色覆寫 A0，`0x1220` 才呼叫 A5。兩者的半字 SH 資料在共同 GP、描述欄位地址與相同記憶體回覆前提下相等；候選的符號延伸暫存值也已 dead-at-call。這不表示中間 GPR、fault、interrupt 或非同步觀察點相同。

尚有兩個具體橋接條件：

- 原碼 `0x880C` 讀 **live S7+0xD4**；候選 `0x1212` 重新建立 `S8=0x40000`，再於 `0x1216` 讀固定基址的 slot。必須證明先前 opaque ROM 保存原始 S7，或實作並驗證真正的 physical-S7 port／register ownership，不能靠 C 欄位或常數重建推定等價。
- 原碼 RA=`0x8814`；候選 component RA=`0x1222`。若僅將 base `0x1000` 平移至 `0x8614`，候選 RA 會是 `0x8836`。需要實際 source/layout 變換保留 callee 可見 link，或取得 ROM 不觀察 RA 的證據。這裡未產碼、填補尾區或宣告完整 ABI。

```sh
python3 -B check-review.py --project-root ROOT --firmware OFFICIAL_BIN
python3 -B check-review.py --project-root ROOT --firmware OFFICIAL_BIN \
  --component ACTUAL_ORDERED/COMPONENT-ONLY-NOT-FIRMWARE.elf
```

預設 `actual_candidate_artifact_read=false`，只表示實際原始來源與封存的模型 source 身分核對；明確提供 ELF 才是 `true`，不需要歷史 W build 路徑。此選項針對目前已審查的 624B 身分，不接受任意未審查候選。三個可解碼 operand 反例分別改 LHU 的 rd、SH 的 rs2、目標 LW 的 slot offset；由局部語義欄位檢查拒絕，非僅靠檔案 hash。未重跑 HOST、未編譯新模型、未執行／模擬 RV32、未連網或操作硬體。
