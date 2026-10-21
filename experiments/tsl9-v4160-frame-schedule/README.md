# TSL9 明確的 ABI 堆疊保存順序處理

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

本工具只處理新編譯 C/C++ ET_REL 中兩個函式的自動堆疊保存順序。演算法仍由 C/C++ 編譯；最後的物件是「編譯器輸出加上明確的 ABI 保存順序處理」。不能宣稱 Clang 單獨產生了最後的保存次序，也不能將相同機器碼視為原硬體可燒錄的證據。

## 為何需要分開處理

目前編譯器在 prologepilog 階段插入的保存順序，與 ID2966 V4.1.60 中兩個函式不同。正常返回後的暫存器值可能相同，但部分保存完成時的堆疊狀態不同；不能以主機測試或正常返回等價取代此差異。

| 函式 | 編譯器保存順序 | 明確要求的保存順序 |
| --- | --- | --- |
| IRQ，原址 `0x9A42` | RA@12、S0@8、S1@4、S2@0 | S2@0、RA@12、S0@8、S1@4 |
| quarter，原址 `0x9C0A` | RA@28、S0@24、S1@20 | S0@24、S1@20、RA@28 |

數字為相對本函式新 SP 的 byte offset。`frame-policy.json` 記錄暫存器、槽位與順序，沒有原始機器碼模板。工具從實際輸入中取出既有的兩位元組 C.SWSP 指令，僅重新排列這些指令，不產生新 opcode、不增加長度、不讀原始 BIN 作為生成輸入，也不使用填補或原檔回退。

## 生成與唯讀重驗

```sh
python3 -B experiments/tsl9-v4160-frame-schedule/schedule.py \
  --project-root /absolute/project \
  --input /absolute/project/build/compiler-integrated.o \
  --output /absolute/project/build/source-integrated.o \
  --receipt /absolute/project/build/frame-scheduling.json

python3 -B experiments/tsl9-v4160-frame-schedule/replay.py \
  --project-root /absolute/project \
  --receipt /absolute/project/build/frame-scheduling.json
```

也提供同名 `.sh` 入口及 `PYTHON` 環境變數。所有路徑須位於指定專案內；輸入、輸出與收據必須是三個不同路徑，輸出與收據只允許新建。預設處理 `irq quarter`，獨立編譯單元可明確指定 `--functions irq` 或 `--functions quarter`。Python 3.10 以上；ELF 解析器使用專案內固定 SHA256 的既有實作。

## 邊界與證據

- 僅接受 RV32 RVC soft-float ET_REL、唯一的公開函式與唯一的指定可執行區段，精確核對函式長度、frame 大小、原保存順序與互不重疊的槽位。
- 排除保存區間內的具名或 mapping symbol、重定位位置與重定位目的；排除重疊儲存、相關 unwind/frame/build-id metadata。重新套用亦會拒絕。
- 輸出保持長度、區段 metadata、符號與全部 RELA 相同。收據記錄實際輸入／輸出雜湊、工具與規則身分、既有指令及變更 offset；唯讀重驗會讀取兩份實際物件重新推導全部內容。
- 本工具單獨只能證明受限的物件轉換。輸入確實由 C/C++ 來源產生，仍須整合流程的實際編譯命令、依賴檔與來源身分證據；檔名不是來源證明。
- 沒有重定位的計算式／編碼式內部進入點、原機 ROM、未知中斷觀察、實體故障與 BLE OTA 相容性仍未證明。工具不執行或模擬目標，也不接觸 BLE、UART、CAN 或實體 Flash。

Windows 的實際 Python／LLVM 驗證不代表 Linux、macOS、POSIX shell 或 CI 已通過。新的收據與整合結果須依各自實際執行環境判定。

`verify.py --input-c C.o --input-cpp CPP.o --build-root NEW_DIR` 對兩份實際物件執行生成及唯讀重驗，並以每語言七個實際收據／輸出篡改案例驗證拒絕行為。這項檢查使用指定的既有編譯物件，沒有重新編譯 C/C++；完整映像流程才會另外建立全新的編譯鏈。
