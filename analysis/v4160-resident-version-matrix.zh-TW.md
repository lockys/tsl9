# v4.1.60：三個 resident 參考版本的 gate 對照

重跑 `analysis/resident-version-gate-static/verify.py`：一般 Python 及 `-O` 各拒絕 15 組 APP 指令／literal 變造及 6 組候選變造。原 APP 在 `0x19a04` 呼叫 `[0x4003c]` 的比較器，以 `[0x40034]` 的值作版本字串指標，比較長度為 21，回傳非零才繼續。APP 的 `CH32V20x_BLE_LIB_V1.3` 後方 NUL 不參與比較。

加入[已核對原始 Intel HEX 的 V1.30](v130-resident-sparse-copy-coverage.zh-TW.md)，對三份雜湊固定的主段重查 marker、slot 及原始比較器 bytes。結果：V1.30（字串位址 `0x6e524`）及 V1.31（`0x6e6a0`）的前 21 bytes 都相等，不能藉此區分。V1.40（`0x6e890`）在第 21 byte 即不等；若指標及內容維持參考值、比較器已正確安裝且依已分析的相等契約完成，V1.40 會被這個 gate 拒絕。

三份 `0x4003c` 均指向 `0x20000442`。依各自初始化映射，V1.30／V1.31 比較器來源 `0x406b2`，V1.40 來源 `0x406f2`；三份 72-byte body 完全相同，SHA-256 `a9dbd2b47ccefe55ab45f0b4e5a073d7aeb00f42dbe503191a75b6b66efff3aa`。相同 body 與前綴結果並不證明實機 ROM 身分、可成功執行或已到達 gate。無設備操作，無原 BIN 或正式來源變更。

後續：找 APP 在 gate 之後實際引用的 resident slots，按用途與候選實作差異排序，而不是以版本後綴猜測部署版本。
