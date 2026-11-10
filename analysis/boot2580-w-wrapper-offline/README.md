# ID2580 BOOT W 成功回覆：下游封裝靜態追蹤

僅針對保存的 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin`，12,288 bytes，SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`；PC 使用 base `0x1000` 的分析座標，並非實測位址。上游成功條件與 `(context, 0x57, 0, 0)` 請見 [W 回覆](../boot2580-w-reply-offline/README.md)。這是靜態推導，沒有執行目標 ISA、連設備、發送或刷寫。

## 條件式結果

`0x1848` 接收 `(a0=context, a1=command, a2=data, a3=length)`。長度須不大於 1039，context 須等於 `lhu 126(gp)`，該值不能是 `0xfffe`；透過 `READ32(0x4013c)` 的 provider 呼叫須返回恰好 1，才進入封裝。否則直接返回；provider 實際語意及副作用未知。W 的零資料路徑進入封裝後，**若 RAM 寫入正常且沒有並行改寫**，靜態推導出六個連續 buffer bytes：

```
55 7f 57 00 00 57
```

依序為固定兩 bytes、命令、長度高 byte、長度低 byte、低 8 bits 加總（命令＋兩個長度 byte＋payload）。此路徑 payload 為空，所以這個封裝 buffer **不加 page 或 nonce**。這不排除 provider、下游或其他狀態加欄位；不能稱為已觀察到的線上封包。

## 原始指令錨點

以下 mnemonic 引自既有 radare2 保存結果 [`source-map.json`](../boot2580-uid-helper-2026-10-21/identity-link/source-map.json) 的 native span `0x1848`；本次重新讀原始影像並固定整段 `[0x1848,0x192c)` 的 228 bytes，SHA-256 `e9e1e949d9ddde3636ccb3cbf144c7dfdff67c243aa7754fc24a59d4c832d5dd`。這不是新的獨立反組譯或執行。

| PC / bytes | 推導 |
|---|---|
| `1848 1307f040`, `184c 637fd708` | 長度 unsigned <= 1039 才往 `18ea`；否則 `1850` return |
| `18ea 03d7e107`, `18ee 631ea702`, `18f2 c167`, `18f4 f917`, `18f6 630af702` | current context 比對及 `0xfffe` 排除 |
| `18fe 83a7c713`, `1916 8297`, `1918 8547`, `191a e30cf5f2` | 讀 `0x4013c` 間接呼叫；返回值等於 1 才跳 `1852` |
| `1852 e177`, `1854 93c757f5`, `185c 2319f784` | 計算 halfword `0x7f55`、little-endian 存入 `0x200090aa` |
| `1868 23849784`, `1874 230fb782`, `187e a309f782` | command 存 `0x200090ac`，低長度存 `0x200090ae`，高長度存 `0x200090ad` |
| `1878 a695`, `188a ae97`, `188c 93f7f70f`, `189c 63ec8502`, `18d4..18e8` | 初始化 checksum，逐 byte 複製並加總；length 0 時不讀 data |
| `18a0 33078600`, `18a4 a305f700`, `18a8 1904` | 在 `0x200090af+length` 存 checksum；總長 length+6 |
| `18aa..18b6`, `18c6 03a30705`, `18ca 03c5c107`, `18ce 8545`, `18d2 0283` | 總長存 `0x200090a6`、零存 `0x200090a8`；尾跳 `READ32(0x40050)`，a0=`lbu 124(gp)`、a1=1；其效果未知 |

`0x200090aa` 是指令形成的數值 RAM 座標；最終間接 provider 如何取用該 buffer、是否再封裝或傳送均未證明。上游條件和 provider 返回值均非觀測事實，尤其不能推論 Flash 已持久化或成功收到 ACK。

## 重播與反例

`python -B analysis/boot2580-w-wrapper-offline/check.py` 驗證完整影像 hash、整段精確 bytes、23 個繞過全檔 hash 的單 byte 突變，以及由人工解讀導出的空／非空 buffer 和長度、context、sentinel、provider 回傳正負例。模型測試不是 ISA 執行或獨立語意證明。分析不代表真機安裝此 BOOT、BLE 流量、BOOT 配對、硬體寫入或傳輸成功。
