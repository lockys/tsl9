# V4.1.60 Flash 暫存器與指令前綴

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

六個可讀 C11／C++17 函式已用固定 LLVM 18.0.2 RV32IMAC_Zicsr／ILP32 參數實際編譯，
並嚴格連結於原始入口。quarter／status／unlock／lock／erase／program 的大小
仍為 64／8／30／14／46／100 bytes，合計 262 bytes／99 指令。
component ELF SHA-256：
`575b2e1009437c77d71081fffeaa32988ff10b23c78decb01e9ad976c5e6c9c7`。

本輪五個葉函式共 198 bytes，與原始 ID2966 V4.1.60 BIN 完全相同，包括所有指令邊界、
暫存器、立即數、分支目標與兩個 ADD 的運算元順序。沒有填充、原始位元組借用、
物件修補、整函式組合語言或旗標搜尋；原始 BIN 僅用於驗證，不參與程式碼產生。

| 函式 | 入口 | bytes | 與原始相同 |
|---|---:|---:|---|
| quarter | 0x9C0A | 64 | 否：三個保存指令排列造成 6 bytes 差異 |
| status | 0x18E90 | 8 | 完全相同 |
| unlock | 0x18E98 | 30 | 完全相同 |
| lock | 0x18EB6 | 14 | 完全相同 |
| erase | 0x18EC4 | 46 | 完全相同 |
| program | 0x18EF2 | 100 | 完全相同 |

C 仍描述完整寫入演算法、fresh volatile 32-bit 存取、64 次正向逐字複製、未設上限的原生輪詢
及正常輸出。小型 native 原語只表達原始暫存器／事件站點：
解鎖金鑰高低部分的 A3／A4 相依關係、抹除時 A4 RMW／輪詢、
program 的 A5 首次 RMW、A3 mask 先於 A0 對齊、後續 A5 RMW／A4 輪詢。
兩個位址原語分別產生原始 `ADD A3,A1,A5`、`ADD A3,A0,A5`；
HOST 分支仍是相同的 uint32 加法。它們不讀取原始機器碼，也不包含原始 opcode。
wrapper 的既有 C 保存排列沒有改動；本輪不執行任何 ABI 排序後處理。

相對前輪完整映像 de159...68be1 的 Flash 元件，原有 62 個 Flash 差異縮減至
quarter 的 6 bytes；本輪僅產生 component ELF，沒有更新完整映像或產生 firmware BIN。
歷史三個受限診斷依序得到：第一版 erase exact、program 僅 ADD 交換；
加入 key2 低位相依橋後 unlock exact；最後兩個原始次序的 ADD 原語使 program 也 exact。
每一步使用相同編譯參數。

跨平台入口（Python 3.9+，已有本機編譯器；不會下載工具）：

```sh
python3 -B experiments/tsl9-v4160-flash-register-prefix/verify.py --project-root . --language both
python3 -B experiments/tsl9-v4160-flash-register-prefix/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B experiments/tsl9-v4160-flash-register-prefix/verify_native.py --project-root . --replay /path/to/native/c/verification.json
```

同目錄 `verify.sh`／`verify_native.sh` 接受相同參數，或使用 `PYTHON` 指定 Python。
兩個 runner 均支援新的 `--build-root`；原生可指定 `--clang`／`--linker`／`--objdump`。
`--firmware` 同時轉交 build 與 replay，只接受固定 SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的離線檔。
archive 使用其他位置的韌體參考時，replay 必須提供相同明確路徑。
replay 使用收據語言，若明確指定 c／cpp 必須一致；工具與 build override 僅供 fresh 編譯，
replay 會拒絕這些選項。alternate-location 參考的實際 C 編譯與 replay、錯誤預設／語言／
override 拒絕均已驗證。分析目錄在發布版為 `analysis/v4160-...`，工作目錄為 `apk-analysis/tsl9-v4160-...`。

主機每種語言通過 5 組／481 案例／247191 檢查，6 個實際編譯的語意負例均被拒絕。
每次正／負主機程式啟動前檢查 PE／ELF／thin Mach-O 是否符合目前 Python 自身標頭與程序寬度；
RISC-V ELF243、未知或不相符架構會在啟動前拒絕。macOS 要求 thin Mach-O Python，
目前拒絕 universal／fat Python。這輪實際主機執行僅 Windows；沒有宣稱 Linux／macOS／
POSIX shell 已執行。舊 guard／review 封存維持不變。

原生 checker 完整比對六物件與嚴格連結 ELF，涵蓋 raw disassembly 每個 byte、CFG／循環、
GPR、volatile i32 IR、無額外 ALLOC／writable／EH／UND／隱藏 helper、
五個 JAL 的來源與目標。五個葉函式要求原始位元組完全相同，不接受可交換 ADD 例外。
99 個逐指令 raw 反例及 3 個實際編譯的 native 約束反例均被拒絕。
6 份 MMD 逐條核對 target、primary source 與三檔案閉包；MMD 不包含編譯器 resource headers。
每種語言 57 個實際產物均以 hash 封存供唯讀 replay，工具／來源／checker 在建置前後保持一致。

重要限制：HOST unknown／HALT／TRANSFER／診斷輪詢上限只證明外部效果前綴，
不補做 cleanup，不把診斷上限當原生 timeout，也不聲稱實體 GPR 前綴。
五葉位元組 identity 是靜態事實；quarter 保存次序仍不同，整個 component 的完整指令前綴、
非同步／中斷／fault 等價、ROM 行為、晶片與板卡、Flash 容量、電源失敗、BLE／OTA、
實體可燒錄性仍未證明。沒有執行或模擬 RV32、操作硬體或連線網路。
此模型是部分可讀重建，並非整個韌體的原始碼還原。

發布只攜帶來源、分語言文件與選定 JSON 收據，不包含本機 build archives。
implementation/check.py 會明列缺少的 archives；`--require-local-builds` 要求實際產物可讀，
否則不把收據閱讀當成 fresh build 或實際產物重驗。後續完整映像整合與獨立 ABI 排序層須另案驗證。
