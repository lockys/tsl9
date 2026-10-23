# 傳輸封裝重建證據

[English](readme.en.md) · [C 實作與驗證](../../experiments/tsl9-transport-frame/README.md) · [原始指令契約](original-contract.md) · [獨立 native 審核](final-native-review.md)

已重建 `8A56..8B6E` 的 280B／96 指令，保留 post-RET copy loop、兩次 admission 與最後的 no-link tail。C／C++ 正式檢查、獨立原始位元核對、唯讀 replay 與 strict 拒絕均通過；這些是離線證據，並非原機相容性驗證。

已將這份真實 C 物件接入[既有 dispatch 元件](../../experiments/tsl9-transport-dispatch-component/README.md)：806B／280 指令／32 FUNC。filter 的 `C.JAL 8A56` 現在綁定真實定義；仍有5個strong UND與41筆pending RELA。這是符號層級的綁定，機器跳轉立即數與原位配置尚未完成；亦未合併為整機韌體。

重要更正：上一輪 `analysis/queue-filter-2026-10-23/next-transport.md`、英文版與 `summary.json` 的描述將 admission cell 誤寫為 `0x40013C`。原始兩組 `LUI 0x40; LW +316` 實際都是 **`0x4013C`**。舊收據／封存檔不改寫；本輪 raw operand 推導、v6 來源、正式負例與更正歷程採用正確位址。早期 v1／v2 候選有同樣錯誤，從未被提升為目前來源。

| 證據 | 已確認 | 尚未確認 |
| --- | --- | --- |
| guard／admission | 初始 unsigned 1039 guard；fresh `[4013C]`，RA 回到8A90／8AB6 | post-call S0 是否有界、provider 身分與完整 ABI |
| header／copy | nominal table2000B18C、stride1062、7F55、命令／長度／逐 byte checksum；完整32-bit index | 原位 table、RAM ownership、任意 opaque 效果下是否終止 |
| finish | 先還原 RA／S1..S3，後寫 metadata；S0 最後還原，SP+32後 `JR T1` | fresh `[40050]` 的實際作用、硬體介面與傳送是否成功 |

可新增的診斷功能（尚未實作）：離線 frame 長度／checksum 檢查；將 admission、資料封裝、tail 呼叫與實際硬體送出分開呈現；依版本標示 GP／table 佈局。這段尚不能對應座椅或免打擾功能。

原始收據保留本機。公開版本若只替換路徑，會明示原始 SHA256、path-only derivative 與 inverse JSON equality；不將衍生版宣稱為原始收據的 byte-exact replay。

八份分析稿另有末尾換行整理與一項文件參照SHA更新，逐byte可逆檢查及本機原件備份記錄於[publication-provenance.json](publication-provenance.json)；未變動任何機器碼或正式檢查輸入。

下一個直接 provider 為 `12A08`。[初始182B視窗](next-provider.json)實際包含三個入口；[獨立界定](next-provider-contract.md)只將102B／35指令的 `12A08..12A6E` 納入下一個C重建目標，保留RET後的cold path。它會檢查status／ID／tag，再分派至其他provider；硬體介面身分仍待證明。
