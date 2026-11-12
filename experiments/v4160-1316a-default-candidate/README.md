# 0x1316a 有限事件候選（非正式、非目標執行）

固定 decoded APP：`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，基址 0x8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。窗口 `[0x1316a,0x131c2)` 88 bytes，SHA-256 `0eee723b584b06b7f4addfd45403bbfd17b9f0b09cb29aadaedfbf9f346a5514`。

以索引中的 `C:\Users\locky\Tools\radare2\bin\r2.exe` 唯讀反組譯：`r2 -q -n -a riscv -b 32 -m 0x8000 -c "e asm.bytes=true; pd 40 @ 0x1316a" <decoded.bin>`。關鍵實際 bytes：`13172 bc44` slot 讀；`13188 8297` jalr；`1318e 2311f400` sh；`13194 2302f400` sb；`1319c 2314f400` sh；`131a4 8843` gp+84 間接讀；`131a6 fc44` 第二 slot 讀；`131b4 8297` jalr；`131be 6ff0bff7` 尾跳 0x13138。模型順序保留讀與寫、各呼叫與尾跳；jalr 清除目標低 bit，RV32 加法回捲。第一呼叫可修改後續讀的記憶體，第二呼叫也可修改外部狀態；非正常返回時不產生後續事件。事件 callback 承載未建模副作用，不將未知 callee 等同 memset/memcpy。

## 適用限制

假設兩次被呼叫者若返回，遵循必要 ABI：保留 s0、s1、gp、sp 及堆疊保存區，正常返回原續點；無非同步中斷、例外、故障、重入或併發。gp 為入口傳入且保持；不假設其數值或指標內容。所有訪存可成功、對齊，callback 依事件順序忠實提供共享記憶體的即時讀寫及 callee 副作用，含別名；其他訪存和副作用不在此模型範圍。stack 保存/還原事件未列出，假設其記憶體不與任何觀測位置或 callee 可改寫區別名，且呼叫者所需 stack 有效。呼叫事件只指定 a0-a2 和目標；其他寄存器、callee 結果及 ABI 影響未知；尾跳時所有參數暫存器及其他未建模寄存器未知，不推定第二 callee 的返回值。尾跳目標內部不建模。不可將本模型視為硬體、完整 ABI、可達性或二進位等價證明。

`test_model.py` 僅執行獨立 Python 抽象模型，不執行 C，也不測試 C 實作等價性；其 store 僅記錄事件，不更新 Python 的 words 映射，因此不測試 store 與後續讀取的記憶體別名。固定整個映像、窗口及 C blob 的 SHA-256，附帶 pin 損壞、非返回、事件順序和尾跳負面檢查；這些不能證明模型符合機器碼。執行：`python test_model.py` 與 `python -O test_model.py`。未編譯，未執行或模擬目標。
