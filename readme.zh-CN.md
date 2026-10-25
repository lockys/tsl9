# TSL9 逆向工程

[繁體中文](README.md) · [English](readme.en.md)

**TSL9 = 非凡司令官**。

以 C/C++ 重建非凡 TSL9 固件，研究蓝牙 OTA 与原硬件兼容性。

[`legacy-options-2026-10-20`](firmware-downloads/legacy-options-2026-10-20/) 收录从官方更新服务提取的固件。

**免责声明：本项目使用 Codex vibe coding 搭配 REA 进行实验性重建，目前尚未成功逆向重建出已验证可用的 TSL9 固件。重建 BIN 未通过原硬件完整验证；OTA 读回成功不代表功能正常。**

**已验证重建覆盖率：63.90%**（49,074／76,800 bytes；代码 46,486B＋数据 2,588B）。仅计入 C/C++ 重建后逐 byte 通过原地址比对的部分；不是功能完成率或可刷入比例。[验证依据](analysis/notification-support-2026-10-25/summary.json)

## 开始使用

需要 Python 3.10+ 与 C11／C++17 编译器。在项目根目录运行离线模型测试：

```sh
python3 scripts/portable_verify.py --model runtime-loop --language both
```

Windows 使用 `py -3` 替代 `python3`；不连接或刷写硬件。

[重建代码](src/) · [编译实验](experiments/) · [分析证据](analysis/) · [原厂 BIN](firmware-downloads/) · [APK／实验映像](artifacts/)
