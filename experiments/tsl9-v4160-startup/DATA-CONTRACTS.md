# 有界唯讀資料與原機 ROM 契約

本階段使用 ID2966 / V4.1.60，原始 76800-byte Runtime 的 SHA-256 為
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。
伺服器版本標籤不能證明 TSL9 實體硬體適用性。

## 兩條有原始指令證據的讀取路徑

在 `C94E..CC54` 家族內，`CB32` 是共用的 byte read。`CB14` 分支前，
packet byte4 的高位與中位已分離，column 由 `(packet4+1)&15` 限定。

| 原始基址 | 路徑條件 | 首次讀取 offsets | 位元組數 |
| --- | --- | --- | --- |
| `19ED8` | `CB14` highbits 等於零；row 是 `(packet5&15)+(middlebits?10:0)` | `0..415` | 416 |
| `1A018` | `CB14` highbits 不等於零；row 是 `(packet4>>6)+(middlebits?3:0)` | `16..111` | 96 |

兩者實際讀取位址聯集是 `[19ED8,1A088)`，共 432 bytes。
此範圍與前階段全部 598 個 allocated sections 零重疊；新增一個 RO carrier，
`19ED8` 與 `1A018` 各保留為 GLOBAL NOTYPE / size0，後者在同 carrier 內 offset320。
carrier 的 OBJECT432 表示已保存的聯集，不宣稱原程式的 C 陣列邊界。

證據包含完整 774-byte 家族 CFG、兩條分支各自的 dominator、原始 bits、
兩語言 actual ELF 的全部 6672 RELA、534 relative targets、兩項 self-PC 分派及
已捕獲程式的直接／線性入邊。已知外部入口是 `150EA→C94E`。
仍不宣稱未知 ROM 或任意動態指標無法跳入中段。

## 保留的三項首次讀取缺口

| 基址 | 首次可能讀取域 | 來源可見 bytes | 缺少 bytes |
| --- | --- | --- | --- |
| `1A078` | 4096 bytes | 2952 | 1144 |
| `1AAE8` | 1024 bytes | 280 | 744 |
| `1AB48` | 512 bytes | 184 | 328 |

`CF7C` 的 AND7 寫入 a3；`CF3E` 用於位址的仍是未遮罩 a4。
讀取之後的 REM3／REM7、其他路徑的 AND3 都不能縮小首次 fresh-u8 讀域。
`1A078` 前 16 bytes 雖落在本次 carrier 內，完整依賴仍不滿足，canonical 繼續 UND。
不補零、不引用其他版本、不把數值 ABS 當成實作。

## Resident 介面仍須證明

16 個 opaque 參數／record 地址共 17 組 HI/own-LOW 引用已按原始 caller 整理。
保存的候選 SDK header 是 V1.40，function table base 為 `40034`；
`40080` 是候選 process-event 註冊介面，`400A4` 是候選 BLE 初始化介面。
原 Runtime 的版本字串是 `V1.3`；候選 576-byte table 與其他 saved-byte fragments
不能代替原機 resident code、table、低 RAM 初始化內容及 callback/register ABI。
本階段不以候選 ABI 將這 16 個地址改標為 FUNC 或提供 stub。

## 重播與完成邊界

在本資料夾明示執行 `python verify-data-anchor-extension.py --spec evidence/data-contracts-integration.json`。
D 交付目錄可使用預設 firmware 路徑；W 工作副本另加
`--firmware ../../exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`。
從其他工作目錄執行時，`--spec` 與 `--firmware` 應提供對應的絕對路徑。
原 generic、舊 specs 與原始程式／資料均保留。C11/C++17 編譯、partial link 與
`ADDRESS-WITNESS-ONLY.elf` 都是靜態產物；strict link 必須對剩餘真 UND 失敗。
ROOT fresh verification 已通過：55908B code、3676B RO、59584B file-backed payload，
599 個非空配置、6672 RELA、626 個 module providers、2 個 code views、1 個獨立 data anchor、
534 個 relative32 expressions；原 27 個 RAM views 與 35160B NOBITS 保留。
C11／C++17 產物一致，strict 拒絕 23 個真 UND。
ROOT receipt 位於 `build/data-anchor-extension-96064cc66aec4f5e9fc950f985ed0530/verification.json`，
SHA-256 `fac5f7b420cf6666539a9c460affa20e48f7d01131634f4e4ac69331607db40b`。
Native 模組拒絕 37 個實際負例：C16、C++15、共用 raw/domain6；初始 `.set` 繼承錯誤 OBJECT
身分的實際 C 產物另有保留，不宣稱該初始寫法的 C++ 版本也經測試。
獨立審查與 D 交付結果另以本輪 review／destination receipt 為準。

原機晶片、resident ROM、啟動與 IRQ ABI、實體記憶體／stack、BLE OTA 接受性仍未驗證。
沒有執行或模擬 Runtime，沒有硬體 I/O、刷寫、額外廠商網路呼叫，也沒有可宣稱可燒錄的重建 BIN。
