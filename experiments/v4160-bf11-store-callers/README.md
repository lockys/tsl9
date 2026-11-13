# V4.1.60：BD46 位址與兩個局部 store 序列

此工具純 Python 標準函式庫、離線、無其他專案 parser。只讀指定 BIN，單次 `read(76801)`，要求長度恰為 76800 bytes、SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；以 base `0x8000` 換算檔案偏移。雜湊只釘住內容，不證明來源。出錯時非零退出，stderr 為 JSON 錯誤，不輸出成功結果。

## 範圍與條件

假設這是 little-endian RV32，且指定的 `0xbd46`、`0xef5c`、`0xf034` 為自然指令邊界，局部解碼得：

| PC | bytes | 解碼 |
|---|---|---|
| bd46 | `17050020` | `auipc a0,0x20000`：以本指令 PC 加 `0x20000000` |
| bd4a | `1305b51c` | `addi a0,a0,459`：算得 `0x2000bf11` |
| bd4e | `8280` | `c.jr ra` |
| ef5c | `efc0bfde` | `jal ra,0xbd46`（位移 -12822） |
| ef60 | `23000500` | `sb zero,0(a0)` |
| f034 | `efc03fd1` | `jal ra,0xbd46`（位移 -13038） |
| f038 | `8547` | `c.li a5,1` |
| f03a | `2300f500` | `sb a5,0(a0)` |

**僅條件式結果**：若各指定地址確實按此指令邊界執行、BD46 正常返回、`a0` 到各 store 前未被改動、成功取得該記憶體的寫入權限，且無例外或干擾，則 EF5C 局部序列對 `0x2000bf11` 寫入 byte 0；F034 局部序列寫入 byte 1。此為兩條 local instruction sequence，不是完整控制流或所有 writer；不證實入口可達、實際 runtime 效果、記憶體 owner 或 ABI。未解碼 EEE0 入口，不對其作宣稱；亦未核對 F016 路徑，不能由此推論其未知外呼、正常返回或堆疊條件。

解碼器只接受本例所需的 AUIPC、ADDI、JAL、SB、C.JR、C.LI，拒絕不支援的編碼與位址加法溢位；不模擬處理器、韌體或硬體。語意檢查先於視窗的精確 bytes 比對；測試直接以合成未 pin bytes 呼叫解碼及視窗檢查，不依賴 SHA 拒絕來掩蓋語意弱點。

## 執行與實測

從 repository root 執行（`-B` 防止產生 bytecode 檔）：

```text
python -B experiments/v4160-bf11-store-callers/test_verify.py
python -B -O experiments/v4160-bf11-store-callers/test_verify.py
python -B experiments/v4160-bf11-store-callers/verify.py firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
python -B -O experiments/v4160-bf11-store-callers/verify.py firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

本機兩種模式的測試皆通過，包含空測試集 runner 必須失敗；固定 BIN 兩種模式皆直接驗證成功，結果如下：

```json
{
  "passed": true,
  "size": 76800,
  "sha256": "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667",
  "base": "0x8000",
  "bd46_address": "00x2000bf11",
  "callers": [
    {"pc":"0xef5c","jal_displacement":-12822,"jal_target":"0xbd46","store_pc":"0xef60","store_value":0},
    {"pc":"0xf034","jal_displacement":-13038,"jal_target":"0xbd46","store_pc":"0xf03a","store_value":1}
  ]
}
```
