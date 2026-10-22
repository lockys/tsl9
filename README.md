# TSL9 逆向工程

[English](readme.en.md) · [简体中文](readme.zh-CN.md)

以 C/C++ 重建非凡 TSL9 韌體，研究藍牙 OTA 與原硬體相容性。

**免責聲明：本專案使用 Codex vibe coding 搭配 REA 進行實驗性重建，目前尚未成功逆向重建出已驗證可用的 TSL9 韌體。重建 BIN 未通過原硬體完整驗證；OTA 讀回成功不代表功能正常。**

## 開始使用

需要 Python 3.10+ 與 C11／C++17 編譯器。在專案根目錄執行離線模型測試：

```sh
python3 scripts/portable_verify.py --model runtime-loop --language both
```

Windows 使用 `py -3` 取代 `python3`；不連接或刷寫硬體。

[重建程式](src/) · [編譯實驗](experiments/) · [分析證據](analysis/) · [原廠 BIN](firmware-downloads/) · [APK／實驗映像](artifacts/)
