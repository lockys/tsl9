# 原始暫存器順序全映像：獨立 ABI 審查

實際 C11／C++17 編譯、明示 ABI 排序及連結產物通過獨立靜態審查。輸出 **76,800 位元組，與原版零差異**，SHA-256：`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。[English](readme.en.md) · [简体中文](readme.zh-CN.md)

這是 11 個可讀 C／C++ 函式共 526 位元組的來源整合證據；其他 680 個區段仍使用保留的 carrier 來源。輸出相同不代表整份應用程式已被解釋或完整還原為高階 C。

## 實際證據

- 分別讀取 compiler-integrated.o、source-integrated.o、frame-scheduling.json、連結 ELF 及實際 BIN；以凍結 policy 重算 pure plan，只允許編譯器既有 C.SWSP 的 14 位元組排列。其餘位元組、section、symbol、RELA 完全不變。
- Pre-object 的 11 個函式符合已封存 compiler 邊界；post-object 連結後，11 個原位址函式逐位元組等同原版。包含 IRQ／wrapper 的原始保存順序，以及五個 Flash leaf 與 program 的所有原始指令邊界。
- 691 配置、15 LOAD 的範圍／權限、680 個外部內容、8,259 外部 RELA、8,270 總 RELA、53 相對綁定、11 個 JAL／RA 返回位置、10 個私有分支角色及 20 個實際 caller 的寬度／目的／RA 均核對。
- 690 個 file-backed 配置完整覆蓋全部輸出，沒有洞、額外配置或補洞；BIN 同時等於 ELF scatter 與原始韌體。
- 每種語言核對 57 個實際命令／log／輸出關聯與全部 producer artifact 雜湊，包含 42 個 object 編譯及八個 typed IR 命令。嚴格缺 ROM 連結仍失敗；`0x40000` 只作數值見證。
- 每種語言另有五個聚焦反例：誤用未排序物件、假稱 compiler 單獨輸出、實際 JAL→tail、BIN 一位元組錯誤、export 來源改為非連結 ELF，全部拒絕。沒有重跑先前完整 frame／native 反例矩陣；詳細來源及 `.d` 閉包另由來源審查負責。

回條保留原生編譯與明示排序的兩階段身分，**不宣稱 compiler 單獨輸出最終保存順序**。原始 BIN 只供驗證；轉換讀取 compiler 物件，export 讀取實際連結 ELF。尚未執行目標、模擬 ISA、操作硬體或燒錄。

## 預設只驗證來源與 metadata

本 seal 只包含來源、文件、回條及 metadata；**不包含 generated build 物件、ELF、BIN、IR、相依檔或 log**。以下預設命令不讀取、重建或重驗實際建置產物，明確回報 `actual_build_replayed=false`：

```sh
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/check_seal.py --project-root .
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/review.py --project-root .
```

封存回條證明當時實際執行的審查；metadata 通過不代表使用者本機重新編譯或重驗了那些產物。

## 選擇性實際產物審查

先用生產端工具從來源產生新 C 或 C++ MODE_DIR，再明確要求：

```sh
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/review.py --project-root . --firmware ORIGINAL_BIN --folder MODE_DIR --receipt models-build-independent.json
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/review.py --project-root . --firmware ORIGINAL_BIN --replay models-build-independent.json
```

將新回條存於 model/build 等忽略目錄。`--report` 是 `--receipt` 的別名；`--replay` 可搭配 `--folder` 明確指定相同產物目錄。實際產物不存在時會停止，不能退回 metadata 假稱實際通過。Windows 可用 `python -X utf8 -B`；POSIX 包裝 `review.sh` 僅靜態檢查，未在本輪執行 WSL／Git Bash。

位元組相同是靜態來源／ABI 整合結論。實體晶片／板型、ROM 內容、更新包裝與燒錄相容性、復原能力、外部裝置狀態及硬體／OTA 成功仍未由此驗證；未知計算式進入點的缺席也未獨立證明。沒有網路、實體 I/O、目標 ISA 執行或模擬。
