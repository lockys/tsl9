# 事件 callback 的獨立邊界審查

[English](readme.en.md) · [简体中文](readme.zh-CN.md)

目標為官方 ID2966 V4.1.60 的 8614..888C，共 632B。本套件分別保留原始呼叫／frame 靜態證據、具條件的 HOST 演算法測試，以及實際 C/C++ 原生元件的差距；沒有執行 RISC-V 韌體、CPU／ISA 模擬器或硬體。

## 原始邊界

`source.py` 直接驗證原 BIN 雜湊與 callback 雜湊，獨立解碼 15 個壓縮間接呼叫的 RA 寫入、11 個保存位置、11 個全新 frame 讀取及 5 個 PCREL 位址。886A 使用 A6 為目標，其餘使用 A5；每個呼叫的原始連結為該指令 PC+2。另有五個破壞原始指令欄位的反例。

原流程用 A1 的低 16 位元 bit15 做第一個判斷，保存的事件字與 XOR 回傳仍為完整 32 位元。優先序為 bit15、bit3、工作識別比對、bit0、bit1、bit2。bit0 路徑的 ROM 回覆必須恰等於 1，bit1 路徑則只測最低位元。差值採模 16 位元減法後的有號正值；容量則為 ROM 回覆減 3 後截成無號 16 位元。FFFE 連線值沒有在此函式被排除。

位址 40000 的 ROM 表槽名稱與 SDK 語意沒有被當成已確認事實。使用 live S2／S7／S3 的表讀取不代表未知 resident 一定保留這些值；GP、儲存指標及 frame 位置的來源相依性必須另外處理。

## HOST 證據與範圍

`independent_host.c` 使用合成位元組記憶體與明確回覆的 provider。C11 與 C++17 均實際通過 23 個案例、3,541 個檢查；每種語言另有三個來源變異實際編譯後被斷言拒絕。案例涵蓋完整事件字、優先序、非 B0 訊息 A4、live S2／S1 訊息轉送、兩種 gate 判斷、容量下溢、有號差值、fresh 計數遞減、複製後 GP／連線變更、fresh 16 位元加總、六參數 A6 呼叫、saved-frame 新位置與未知／停止／轉移前綴。

所有可執行測試皆先通過不可變的 HOST 機器格式檢查。這些測試只確認命名演算法效果與明示 provider 假設，不證明原生實體 GPR 前綴。`defined_argument_mask` 是明示演算法參數的子集合，不是全部暫存器殘值證明。`return_address` 是 saved-frame 內容的紀錄，不代表每個 opaque call 的即時架構 RA；正常 HOST 完成沒有執行或驗證還原後的跳返目標。變更合成 SP 的案例僅驗證後續讀取位址與內容。

## 原生差距

經實際量測的內聯元件為單一 FUNC658、241 條指令，仍比原 632B 多 26B。它沒有未解析提供者，保有 15 個寫 RA 的間接呼叫與 48B frame；C／C++ 元件位元組一致。儘管 frame 長度相同，原始 RA／S0 保存順序不同，原未使用的 SP+0 現保存 S10，15 個 resident 返回位址偏移亦不同。未知 resident 的實體 S 暫存器依賴、frame 別名及故障／中斷前綴均未被消除。

`native.py` 僅接受已實際量測的內聯 658B 形態，並保留先前 938／944B 加 90B helper 的診斷能力。它讀取真正 ELF／IR／完整反組譯，確認配置所有權、位元組覆蓋、volatile 寬度與間接呼叫，並拒絕兩個實際 ELF 反例。它的通過代表診斷自洽，沒有將 placement／完整 ABI 改成通過。

## 指令

預設封存檢查不讀原 BIN、不讀建置產物：

```sh
python -B ABI-review/check.py --project-root ROOT
```

新鮮 HOST C／C++ 編譯、三個實際編譯反例與唯讀產物重播：

```sh
python -B ABI-review/run-host.py --project-root ROOT --language both --build-root OWNED_BUILD
python -B ABI-review/run-host.py --project-root ROOT --replay HOST_VERIFICATION.json
```

僅檢查真正原生元件及唯讀重播，不要求 HOST 收據或原 BIN：

```sh
python -B ABI-review/review-native.py --project-root ROOT --folder NATIVE_MODE --receipt NEW_NATIVE.json
python -B ABI-review/review-native.py --project-root ROOT --replay NEW_NATIVE.json
```

原始來源、HOST 產物與真正原生診斷的合併檢查／唯讀重播：

```sh
python -B ABI-review/review.py --project-root ROOT --firmware FW --host-receipt HOST_VERIFICATION.json --native-folder NATIVE_MODE --receipt NEW.json
python -B ABI-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

封存只含來源與中繼資料；選定實際結果見 `summary.json`。目前完整映像仍保留上一里程碑，本 callback 沒有被採入。`original_full_ABI_admitted`、`placement_admitted` 與 `hardware_OTA_proved` 全為 false。
