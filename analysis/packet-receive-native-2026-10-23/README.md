# Packet receive：A1 存活性修正，尚未通過重建

[English](readme.en.md)

目標是官方 ID2966 V4.1.60 `[0x16A7C,0x16B0A)`，142B／52 指令。本輪建立[可讀 C／架構埠候選](../../experiments/tsl9-packet-receive/src/packet_receive.c)，沒有修改編譯旗標，也沒有把失敗候選納入 `src/`。

| | v1 | v2 | 官方 |
| --- | --- | --- | --- |
| bytes／指令 | 156／59 | 154／58 | 142／52 |
| SPI call offsets | 36／48／54 | 34／46／52 | 34／46／52 |
| ring call offset | 140 | 138 | 126 |
| 第一個非呼叫差異（合併 offset） | +22 | +40 | — |

v1 沒有在 C／asm 契約中宣告 incoming A1 必須存活至 `SW A1,12(SP)`，編譯器因此把 A1 當暫存，先寫入常數 1，保存的位址參數已錯。v2 明示 A1 匯入並餵給保存埠，且以既有 A4 值進行通道比較；前 34 bytes 現與原碼完全相同，IR 也保留正確 A1 資料流。這是實際 ABI 修正，沒有宣稱整個函式等價。

仍有四類差異：`MV A0,A1` 提早於 S0／S2 初始化；還原段被複製；DLC 計算使用 A0 暫存，改變拒絕分支的原始 residue；ID 組合時 `MV A3,S1` 與移位順序互換。v2 仍有四個 genuine JAL relocation／兩個 UND provider，沒有假 ABS provider；尚未部分連結進 352B 管線。未解析 JAL 的零位移令 raw 首差在 +35；排除呼叫視窗後的首差是投影 +36、合併 +40，兩者不能混稱。

[summary.json](summary.json)及[兩份收據副本](receipts/)記錄精確雜湊、旗標與差異。公開副本只替換實體路徑，原始收據／ELF／IR／MD／日誌留在本機；可逆映射後完整 JSON 相同。原有 producer 路徑變數保留，新匿名化欄位使用 `LOCAL_PROJECT_ROOT`、`LOCAL_LLVM_BIN`、`LOCAL_CLANG_RESOURCE`、`LOCAL_STDINT_HEADER`。v1 是歷史快照，主要來源已改為 v2，不能宣稱它目前可直接重播。

下一步先保留 LW A1 → S0／S2 初始化 → MV A0,A1 的原順序，再處理拒絕分支的 A0 與共用還原段。不得以尺寸吻合取代完整契約。沒有 target／ISA／MMIO／硬體執行、網路 API 或 BIN 產生。
