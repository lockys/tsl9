# TSL9 逆向工程

[English](readme.en.md) · [简体中文](readme.zh-CN.md)

研究非凡 TSL9 的韌體與藍牙 OTA，以 C/C++ 重建功能及原機執行層，目標是產出可用於原硬體的韌體。

**目前尚無完整驗證可刷寫的重建 BIN。** OTA 傳輸與讀回成功，不代表重啟後功能及硬體相容性已通過驗證。

## 開始使用

需要 Python 3.10+；執行模型測試另需 C11／C++17 編譯器。在專案根目錄執行：

```sh
python3 scripts/portable_verify.py --list
python3 scripts/portable_verify.py --model runtime-loop --language both
```

Windows 可將 `python3` 換成 `py -3`。以上為離線模型驗證，不會連接或刷寫硬體。

## 專案內容

- [src/](src/)：目前整理的 C/C++ 重建程式。
- [experiments/](experiments/) · [analysis/](analysis/)：編譯方式、分析證據與限制。
- [firmware-downloads/](firmware-downloads/)：原廠 BIN；[artifacts/](artifacts/)：APK 與實驗映像。
