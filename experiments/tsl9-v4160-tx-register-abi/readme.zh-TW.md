# TSL9 TX：原始入口與 frame 讀寫時序

[English](readme.en.md)

這個離線元件把原始 `0x8A56..0x8B6E` 的 280 bytes 拆成真實的 8-byte 入口、270-byte 具型別 C11／C++17 valid body 與 2-byte C return leaf。實際編譯、標準重定位及連結均已完成；沒有輸出 BIN，也沒有取代現有十二函式完整映像。

入口只使用 `LI A5,1039` 與 unsigned `BLTU A5,A3`。分支透過標準 `R_RISCV_BRANCH` 指向真正編譯出的 returning C leaf；有效長度直接 fall through 到 C body。超長路徑不寫 SP、RA、A0 或 stack，leaf 位於原始 `0x8B6C`。不使用整函式 assembly、原始碼位元組模板、padding、自製 branch encoder 或偽造 noreturn／unreachable。

共用 C 演算法只增加兩個 identity-preserving branch layout hints，使兩個 ROM gate 的實際返回位址恢復 `0x8A90`／`0x8AB6`，RAM HI／LO anchor 恢復 offset `0x80`。HOST macro 是 identity，原有 HOST 邏輯未改，因此這一輪沒有重跑舊 HOST suite。

LLVM 本身仍會用不同的 save／restore 順序。正式流程包含明示的 `postpass/schedule.py`：只重排新 C 編譯產物中五個現有 `C.SWSP` words，以及五個現有 `C.LWSP` words。它把 S0／S1／S2／S3／RA 的保存順序，以及 descriptor SH 前的 RA／S1／S2／S3 還原、SH 後且 ROM slot 讀取前的 S0 還原，排回原始相對時序。其他 instruction word 順序、ELF metadata、位元組長度與重定位不變。這是 C／C++ 加窄入口與已驗證排程層，不能稱為純編譯器輸出，也不主張與排程前產物在 alias／fault 情境等價。

```sh
sh experiments/tsl9-v4160-tx-register-abi/verify.sh --tool-dir /path/to/audited/llvm/bin --language both
python -B experiments/tsl9-v4160-tx-register-abi/verify.py --project-root . --replay /path/to/ordered/c/verification.json
```

可使用 `PYTHON=/path/to/python`；預設使用新的 UUID build 目錄，也可指定尚不存在的 `--build-root`，必須在本 model 的 `build/` 內。`--firmware` 可指定相同固定雜湊的原始證據檔，只供驗證，絕不作為程式碼產生輸入。重播不執行 compiler 或目標，也拒絕建置用的 tool-dir／language／build-root 參數。

每個語言都 fresh compile 三個來源：raw assembly 入口（無預處理／include）、C body 與 C leaf，並保留兩份 LLVM IR。實際 `-MD` closure 是 body 三個 project inputs、leaf 一個 input，以及一個真正的 Clang resource `include/stdint.h`。工具使用已核對的 LLVM NDK Windows binaries；Python／shell 介面可攜，但其他作業系統的 compiler binaries 尚未驗證。

`pre/{c,cpp}` 保留 compiler 原始產物。`ordered/{c,cpp}` 保留明示 pass 收據、排程後 body、可重用的 ET_REL composite 與 `COMPONENT-ONLY-NOT-FIRMWARE.elf`。ET_REL 恰有 280-byte AX allocation、真實相對 FUNC 範圍 `0/8/278` 與大小 `8/270/2`、三個標準重定位及唯一未解 SRAM 符號。缺少 RAM provider 的 strict link 必須失敗；將真 leaf 放到範圍外的實際 linker 負控制也必須失敗。數字 `0x2000B18C` 只供位址見證，沒有建立 SRAM 或 ROM 實作。

獨立靜態證據涵蓋入口／leaf、兩個 gate 的 RA、frame 保存／還原前緣、完整 280 bytes／96 指令覆蓋，以及原始 BLTU 與新 BGEU 的互補迴圈、低 16 位 counter 對 live S0、即時 byte 複製、回邊與 checksum finish。完整原始 ABI、所有私人 symbol／computed target、逐指令 interrupt／fault 行為、完整映像及實體硬體相容性仍未通過。public entry 的真 FUNC size 是 8；未偽稱它已有原始 whole-FUNC280 metadata 角色。

歷史診斷保留於本機：啟用 shrink wrapping、移除純 guard 的 memory clobber、拆 restore region 都未改變原單函式的 frame hoist；普通 C dispatcher 雖有無 frame 的入口，但總長 290 bytes。首次 raw adapter 的外部分支被 assembler 放寬為 12 bytes，形成 284-byte rejected candidate。TEMP 失敗則已用普通檔案能力測試定位為繼承的 sandbox TEMP 配置問題，改為本次 build 專屬 TMP／TEMP，使用同一 compiler，未改權限或繞過審批。
