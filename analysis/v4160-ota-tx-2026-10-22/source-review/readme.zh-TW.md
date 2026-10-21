# 原始8A56傳輸建構：指令與契約

[English](readme.en.md)

本份只核對官方 ID2966 V4.1.60 的 `0x8A56..0x8B6E`：**280 bytes、96條指令**。`raw.py` 將 RV32I/M/C 的單條指令欄位當作資料拆解，逐一比對96組明列操作數及順序，沒有 CPU state、指令解譯器、ESIL或執行介面。40個有限錯誤操作數案例均由指令契約拒絕，不是只比對完整映像雜湊。`contracts.json` 記錄含 PC 的完整順序契約，`source-proof.json` 保留實測結果。

原始 payload SHA256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；本段為 `3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b`，file offset=VA−0x8000。精簡 LLVM 資料核對全部指令邊界與原始 bytes，mnemonic 不作獨立 decoder 的輸入。來源為完整 section 反組譯，避免只查公開 symbol 時在下一個 private label 截斷。

## 輸入、條件與不透明呼叫

入口使用完整32位元 A0=context、A1=command、A2=數值 payload 位址、A3=unsigned length。`8A56/5A` 在變更 SP 或記憶體之前拒絕 length>1039；此時 A0 保持入口值、A5=1039。因此 A0 不是統一布林／狀態回傳值。

進入後配置32 bytes堆疊、保存 S0/S1/S2/S3/RA，並保存輸入長度／位址／context／command。先後從當下 GP+0x96、GP+0x9A 讀取 unsigned16，再與完整32位元 context 比較並排除0xFFFE。第一個候選使用入口 context；第二個使用當下 S2，先前不透明呼叫可能已改變它。

`8A8E`、`8AB4` 分別透過重新讀取的0x4013C之32位元 slot 呼叫，設定 A1=當下 GP+0x80。只接受回傳 A0==1，以選出緩衝區 lane。它們是**不透明、與1比較的 gate**，不能據此確認為配置器、權限 API 或特定 BLE API。第二次呼叫的 A2/A3：第一次未被呼叫時仍為入口值，否則是第一次留下的值。`8AB8` 在第二次呼叫後將 A2 設成1，即使接下來失敗亦然；第一次成功則於8ACC設 A2=0。

GP／S／SP 都保持即時相依，沒有第二次呼叫後的長度檢查。被呼叫函式保留這些暫存器，可以是特定 native profile 的前提，並非本份已證實的常駐行為。任何不確定或不返回的 gate／記憶體操作，都不能補造後續效果。

## 記憶體順序與加總校驗

對 lane0/1 定義 `B=u32(0x2000B18C+1062*lane)`、`P=u32(B+6)`，N 為 gate 後、加6與還原之前的當下 S0。base 是 AUIPC／ADDI 的靜態位址配對事實，並有 RAM 符號重定位佐證。stride 指令是 MUL，不是 REMU。magic 經 LUI／XORI 形成完整32位元0x00007F55；改成 ADDI 即使最後 SH 的低16位元相同，指令／暫存器契約仍不同。

| PC | 依序效果 |
| --- | --- |
|8AEC|WRITE16(P,0x7F55)，小端 bytes55 7F|
|8AF0|WRITE8(P+4,low8(N))|
|8AFA|WRITE8(P+3,low8(N>>8))|
|8B00|WRITE8(P+2,low8(當下 command))|
|8B56/62|逐 byte 重新 READ8(source+counter)，再 WRITE8(P+5+counter,byte)|
|8B16|WRITE8(P+5+N,checksum)|
|8B32/36|WRITE16(B+2,low16(N+6))，再 WRITE16(B+4,0)|

checksum 是 command、長度低／高部分及每個重新讀取的 payload byte 加總後取低8位元，不含 magic，**不是多項式 CRC**。這是本機記憶體格式，沒有實體 wire capture。B+0..1 沒有由本段初始化；最後寫零是 B+4 的 SH16，不是 SW32，不會蓋掉 B+6 的 magic。

迴圈將 `low16(完整32位元counter)` 與完整32位元 N 比較，但來源／目的位址使用完整 counter。每次都先讀來源 byte、再寫對應 byte，可能產生向前重疊回饋，不能直接假設整段快照或一般 memcpy 等價。若 N 穩定且<=65535、記憶體操作完成，迴圈會執行 N 次；入口<=1039只在不透明呼叫前成立。若呼叫後 N>65535，通常無法遇到終止條件；HOST 可以用明示 budget 回報有限／未知前綴，不能補造 native guard、clamp或成功返回。

## 返回、尾端轉移與暫存器

失敗區8ABE..8ACA重新讀回 RA/S0/S1/S2/S3 及還原 SP。沒有 gate 被呼叫時 A0 是入口 context；第一次返回後第二個 lane 不合資格時保留第一次結果；第二次失敗時保留第二次結果。caller-saved 殘留值亦依路徑而異，第二次呼叫後的 A2 即使失敗仍為1。

成功路徑在最後 metadata 寫入**之前**重新讀回 RA/S1/S2/S3，設定 A1=1，計算 A2=當下 GP+0x94+4*lane；於8B40才重新讀回 S0，接著讀0x40050之32位元尾端目標、從 A2 的 byte0 讀 unsigned A0、增加當下 SP，於8B50以 **JR T1、不寫 link** 轉移。此處不是讀 GP+0x9A 的16位元 handle。A3=0x2000B18C、A4=checksum、A5=0x40000；非空迴圈後 A6=P+N−1，零長度則保留不透明殘留值。A7本段未直接寫入，但不能宣稱跨不透明呼叫仍保留。後續是否返回及結果，屬於尾端目標的行為。

堆疊資料會重新讀取，不是快取。先前 payload／metadata 寫入或不透明呼叫，可能透過別名改到稍後的保存字；不能以普通 C ABI 假設替代原始讀回／寫入交錯順序。本段沒有直接 allocator／copy／release 呼叫，但無法確認不透明函式內部是否做這些工作。

## 符號、參照及重查

原始 AX／PROGBITS owner 對齊2，公開 `__tsl9v4160_call_8a56` 是 FUNC280。有11筆 owned 重定位：10個本地目標（包含 PCREL low）及1個外部 RAM PCREL high。9個已記錄外部參照都指向 offset0，包含重建 page-reply 的9BE0 JAL。獨立解碼原始指令後，為**8個寫 link 的呼叫、1個不寫 link 的尾端跳轉**，不能只靠重定位名稱判斷。此 carrier 沒有已記錄的外部 interior 參照；計算、編碼或常駐程式的參照仍未知。

選定證據保留原始 carrier 與目前十二函式 carrier 的實體角色／body讀回。預設重查使用已固定 manifest、相關 raw carrier directives 及原始 bytes，不需要這些封存 object；指定 `--object` 才重新讀取實際 carrier 的相關符號／重定位／body，並另行回報實體讀回數量。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/source-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

發布版改用 `analysis/v4160-ota-tx-2026-10-22`；shell wrapper 接受相同參數，可用 `PYTHON` 指定 runtime。實際封存存在時才加上可重複的 `--object ORIGINAL.o`／`--object CURRENT.o`。預設明確回報本次實體 carrier 讀回為0，歷史選定讀回為2；發布不包含產生的 object。C/C++行為、native 長度適配、實體中斷／故障前綴、常駐 ABI、硬體／BLE及OTA相容性，都需要另外證據，本 seal 不予宣稱。
