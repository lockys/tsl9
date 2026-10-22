# TSL9 逆向工程

[繁體中文](README.md) · [English](readme.en.md)

研究非凡 TSL9 的固件与蓝牙 OTA，以 C/C++ 重建功能及原机执行层，目标是生成可用于原硬件的固件。

**目前尚无通过完整刷写验证的重建 BIN。** OTA 传输与读回成功，不代表重启后的功能及硬件兼容性已通过验证。

## 开始使用

需要 Python3.10+；运行模型测试另需 C11／C++17 编译器。在项目根目录运行：

```sh
python3 scripts/portable_verify.py --list
python3 scripts/portable_verify.py --model runtime-loop --language both
```

Windows 可将 `python3` 换成 `py -3`。以上为离线模型验证，不会连接或刷写硬件。

## 项目内容

- [src/](src/)：目前整理的 C/C++ 重建代码。
- [experiments/](experiments/) · [analysis/](analysis/)：编译方式、分析证据与限制。
- [firmware-downloads/](firmware-downloads/)：原厂 BIN；[artifacts/](artifacts/)：APK 与实验映像。
