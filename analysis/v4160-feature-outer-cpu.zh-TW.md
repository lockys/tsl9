# v4.1.60 `0x14d2e` 七模式外層分派

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批在有限 CPU 中離線執行原 `0x829e` getter、`0x14d2e` 外層分派、mode 2–6 比對及返回；不執行 mode 1 分支內部或任何尾跳目標，不操作設備。

## mode 來自全域 byte

`0x829e` 只讀 `U8[0x2000bfb5]` 到 A0 並返回，其餘暫存器與記憶體保持。`0x14d2e` 建立 16-byte frame、保存 S0／RA，以 S0 保存 record 指標，再呼叫該 getter。

mode≤6 時使用原 `0x1a6b8` 的七項相對 word 跳表；每個 word 加上表基址，得到以下入口。表位址與數值直接取自已釘定的 APP，沒有合成另一張執行用跳表。

| mode | 入口 | 本批驗證到的行為 |
|---|---|---|
| 0 | `0x14d52` | A0=record，恢復 caller frame，尾跳 `0x10b60` |
| 1 | `0x14d5e` | 停在入口，frame 尚未恢復 |
| 2 | `0x153ba` | ID 比對，見下表 |
| 3 | `0x153da` | ID 比對，見下表 |
| 4 | `0x153fa` | ID 比對，見下表 |
| 5 | `0x1543a` | ID 比對，見下表 |
| 6 | `0x1547a` | ID 比對，見下表 |
| 7–255 | `0x1549a` | 不讀跳表，A0=0，恢復 caller frame，尾跳 `0x1074c` |

byte getter 不會產生大於 255 的 mode；本批不把額外 32-bit mode 當成正常 getter 的可達輸出。模式值只是數字，本批不替它們指定未證明的車型或功能名稱。

## mode 2–6 的 ID 尾跳映射

每條路徑恰讀一次 `U16[record]`，匹配時 A0=record，恢復 S0／RA／SP 後尾跳：

| mode | 十進位 ID → target |
|---|---|
| 2 | 169→`0x10870`；540→`0x108d8` |
| 3 | 169→`0x10870`；540→`0x10944` |
| 4 | 169→`0x10870`；393→`0x109c4`；1676→`0x10a00` |
| 5 | 890→`0x10ac6`；929→`0x10a16`；1002→`0x10b0a` |
| 6 | 169→`0x10870`；1176→`0x10936` |

未匹配則透過 `0x14da2` 恢復 caller 後返回。**A0 此時是跳表 cell 位址 `0x1a6b8+4*mode`，不是零或由此程式定義的成功碼。** 未匹配返回按 RA→S0 的順序讀回保存欄位；匹配尾跳與 mode 0／>6 路徑按 S0→RA 的順序讀回。

mode 1 入口的可觀察邊界為 A0=`0x1a6bc`、A4=`0x1a6b8`、A5=`0x14d5e`、S0=record、RA=`0x14d3a`、SP=`caller_SP-16`。此時不可聲稱 caller 狀態已恢復或分支功能完成。

所驗證 outer 路徑只做 frame 保存的兩項 stores，不寫 record、全域資料或 MMIO。A0／A4／A5 可變，S0／RA／SP 暫時用於 frame，其餘暫存器保持。mode 0、mode 1 與 >6 在本批停止點前均不讀 record，NULL record 的四組邊界探測分別以 mode=0／1／7／255 驗證；這不代表後續 target 可接受 NULL。

## 接回實際 consumer

完整串接使用既有固定 SDK copy **參考候選** 的 58-byte 原指令與合成 CSR／控制 word，並非已安裝 provider 的證明。consumer 在 slot 17 取得一筆非零 ID record，複製 snapshot、清除 queue ID；原 filter 使用兩個不符合條件的 table entries 返回零。原分類以 config bit 3 清零、`0x81aa` 指定正常返回 1，進入 `0x14d2e`。

未知 probe 保持明示的正常返回前提，刻意改寫 caller-saved 暫存器，保存 SP／S／GP 與記憶體。mode getter 與 outer 分派本身均執行 APP 原碼，沒有以 hook 指定 mode 或尾跳結果。

256 modes × 九個非零 ID，共 2304 組：

- 33 組未匹配返回到 `0x12d90`，繼續原掃描至 caller 返回，核對 SP／S0–S7 恢復。
- 2262 組停在尾跳 target 的第一條指令之前，核對 outer frame 已恢復、A0 和 link。
- 9 組停在 mode 1 入口，核對尚未恢復的 outer frame。

逐例核對精確資料 reads／stores、槽位清除後的完整 queue、snapshot 保持、CSR=0x88、copy 控制 word 恢復。直接全 ID 測試包含 ID=0，但 consumer 串接只使用非零 ID；沒有宣稱所有直接 fixture 都是 ingress 可達輸入。

## 重現與結果

```powershell
python analysis/test_v4160_feature_outer_cpu.py --standalone-only
python analysis/test_v4160_feature_outer_cpu.py
python -O analysis/test_v4160_feature_outer_cpu.py
```

獨立部分只需標準庫、原 APP 及既有有限 CPU。完整串接另外使用已發布的 consumer/filter/classification 測試模組和本機 carrier；`--carrier` 可指定路徑。串接前核對 carrier 長度、SHA-256、槽位與 body SHA-256，候選資料不另行上傳。

```text
PASS: 256 byte getters; 768 mode/ID probes; 327680 mode2-6/full-ID cases; 4 null-record boundaries; 2 mutations; mode1/tail providers NOT executed
PASS: 2304 detached-consumer/filter/classification/outer chains; 33 unmatched scan completions; 2262 tail boundaries; 9 mode1 boundaries; candidate-only copy binding
```

256 組 getter 核對 byte 寬度、精確地址和其他暫存器保持；768 組為每種 mode 的三個 ID 探測；327680 組為 mode 2–6 各自全部 65536 個 ID，逐例核對 endpoint、A0、frame、資料存取順序及僅有的兩項 stores。

兩個記憶體複本變異分別把 mode 2 跳表 entry 改成 mode 3，以及讓 getter 改讀相鄰 byte；均須被 endpoint oracle 抓出，不能以未知指令錯誤充當偵測。原 APP 不變，共用 CPU 未修改。

既有 `src/native/receive/feature_dispatch_outer.c` 已重建這段 C；本批增加原指令與 consumer 串接證據，沒有新增重建 bytes 或重算覆蓋率。仍需追查 mode 1 ID 樹、上述尾跳函式、其他 handlers 與未知 provider 綁定／保存合約。
