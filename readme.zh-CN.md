# TSL9 逆向工程

[繁體中文](README.md) · [English](readme.en.md)

**TSL9 = 非凡司令官**。

以 C/C++ 重建非凡 TSL9 固件，研究蓝牙 OTA 与原硬件兼容性。

[`legacy-options-2026-10-20`](firmware-downloads/legacy-options-2026-10-20/) 收录从官方更新服务提取的固件。

**免责声明：本项目使用 Codex vibe coding 搭配 REA 进行实验性重建，目前尚未成功逆向重建出已验证可用的 TSL9 固件。重建 BIN 未通过原硬件完整验证；OTA 读回成功不代表功能正常。**

**已验证重建覆盖率：95.67%**（73,478／76,800 bytes；代码 69,412B＋数据 4,066B）。仅计入 C/C++ 重建后逐 byte 通过原地址比对的部分；不是功能完成率或可刷入比例。[验证依据](experiments/tsl9-sequence-pattern-integration/summary.json)

最新整合：[新增序列比对数据48B已纳入 SRC 与原地址对照](experiments/tsl9-sequence-pattern-integration/README.md)，实机执行与硬件兼容性仍未证明。

ROM候选：[C/C++](experiments/tsl9-resident-completion-status-gates/README.md) · [序列数据](experiments/tsl9-sequence-pattern-data/README.md) · [中断合约](experiments/tsl9-trap-profile-contract/README.md) · [RAM配置合约](experiments/tsl9-resident-task-layout-contract/README.md)，实机兼容性未确认。

## 开始使用

需要 Python 3.10+ 与 C11／C++17 编译器。在项目根目录运行离线模型测试：

```sh
python3 scripts/portable_verify.py --model runtime-loop --language both
```

Windows 使用 `py -3` 替代 `python3`；不连接或刷写硬件。

[重建代码](src/) · [编译实验](experiments/) · [分析证据](analysis/) · [原厂 BIN](firmware-downloads/) · [APK／实验映像](artifacts/)
