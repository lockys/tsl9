# TSL9 离线 C/C++ 重建

[繁體中文](README.md) | [English](readme.en.md)

本项目保存原始 APK、22 份不同的更新器 BIN、可读 C/C++ 行为模型及静态来源证据。完整目标仍是生成与原硬件及 BLE 更新器兼容的重建 BIN，并在逆向过程中评估值得新增的功能，将提案与已实现功能分别列出。**目前尚无经验证可刷写的重建 BIN。**

## 跨平台验证

最新完整映像已纳入 OTA 页面回复：12 个可读 IRQ／Flash／OTA 函数共 650 bytes，完整 76,800-byte BIN 与官方 ID2966 V4.1.60 相同。C、C++ 各新编译 43 个单元，61 个命令含两次明确 ABI 排序；全部单元记录完整标头依赖。其余 679 个区段仍使用原始承载，这是部分源码重建，**不是原硬件或 BLE OTA 验证**。参见[新版整合](analysis/v4160-reply-image-integration-2026-10-22/README.md)与[离线映像](artifacts/offline-images/ID2966-V4.1.60-reply-integrated/README.md)。

需要 Python 3.10 以上、C11／C++17 编译器及 POSIX shell。Linux 可用 GCC 或 Clang；macOS 可用 Clang；Windows 可用 Git Bash 加 Visual Studio C++ Build Tools。新的跨平台入口不需要 PowerShell 或 CMake。

```sh
sh ./verify.sh --list
sh ./verify.sh --model runtime-loop --language both
sh ./verify.sh --model system-clock-query --language both
```

`sh ./verify.sh` 执行目前全部已登记的跨平台模型；也可直接执行 `python scripts/portable_verify.py`。`CC`／`CXX` 可指定单个编译器可执行文件；shell 入口可用 `PYTHON` 指定 Python 可执行文件。路径根据项目位置解析，不依赖调用者的工作目录；产物写入新的忽略目录。

第一批跨平台项目为 runtime-loop、system-clock-query、resident-entry 及 resident-copy。每项核对确切原始文件、封存的 raw 来源证据、程序依赖与 C/C++ 主机行为；验证记录包含实际编译器及可执行文件哈希。原始固件只作为数据读取，不执行或模拟。

仓库另有 116 个历史 PowerShell 脚本；其中 RV32、ELF、集成与下载检查须逐项移植，主机测试通过不能代替这些检查。历史封存文件保留原始字节，移植清单会标明确切范围。跨平台 CI、本地测试与实体硬件证据分别报告。

## 内容

专题文档目前分别提供繁体中文和英文；下表中的中文说明链接到繁体中文版本。

| 内容 | 位置 |
| --- | --- |
| 原始 APK 1.2.7 | [APK](artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk) |
| 22 份原始解码 BIN | [固件封存](firmware-downloads/legacy-options-2026-10-20/BINs/) |
| 新时钟计算模型 | [繁体中文说明](experiments/tsl9-v4160-system-clock-query/readme.zh-TW.md) |
| 可读的原生中断初始化 | [繁体中文说明](experiments/tsl9-v4160-interrupt-init/readme.zh-TW.md) |
| 可读的原生时钟与派生字段 | [繁体中文说明](experiments/tsl9-v4160-native-clock/readme.zh-TW.md) |
| 时钟正常返回寄存器契约 | [繁体中文说明](experiments/tsl9-v4160-clock-registers/readme.zh-TW.md) |
| 启动数据复制、BSS 清零与输出寄存器 | [繁体中文说明](experiments/tsl9-v4160-reset-memory/readme.zh-TW.md) |
| 中断初始化正常寄存器契约 | [繁体中文说明](experiments/tsl9-v4160-interrupt-registers/readme.zh-TW.md) |
| 原址机器码一致的 RCC helper 与新版 IRQ 核心 | [繁体中文说明](experiments/tsl9-v4160-irq-native/readme.zh-TW.md) |
| 可放回原区段的 144-byte IRQ 调用框架 | [繁体中文说明](experiments/tsl9-v4160-irq-callframe/readme.zh-TW.md) |
| IRQ 可读来源与完整原始布局整合 | [繁体中文说明](analysis/v4160-irq-image-integration-2026-10-21/readme.zh-TW.md) |
| 六个可读 Flash 函数与原址组件 | [繁体中文说明](analysis/v4160-flash-native-2026-10-22/README.md) |
| 自然生成 100-byte program 与原始进入顺序 | [繁体中文说明](analysis/v4160-flash-entry-order-2026-10-22/README.md) |
| 十一个 IRQ／Flash 函数整合的完整离线映像（尚未验证可刷写） | [繁体中文说明](analysis/v4160-flash-image-integration-2026-10-22/README.md) |
| 五个 Flash 叶函数的寄存器与指令前缀一致 | [繁体中文说明](experiments/tsl9-v4160-flash-register-prefix/README.md) |
| 明确的 ABI 堆栈保存顺序处理与只读复验 | [繁体中文说明](experiments/tsl9-v4160-frame-schedule/README.md) |
| 十一个可读函数与官方 bytes 相同的完整离线映像 | [繁体中文说明](analysis/v4160-register-image-integration-2026-10-22/README.md) |
| 新功能候选与既有功能证据 | [繁体中文提案](analysis/v4160-irq-callframe-2026-10-21/feature-candidates/readme.zh-TW.md) |
| Runtime 主程序／初始化／循环／分发 | [说明](experiments/tsl9-v4160-runtime-loop/readme.zh-TW.md) |
| resident 候选入口与 byte-copy | [入口](experiments/tsl9-resident-entry-reference/readme.zh-TW.md)／[copy](experiments/tsl9-resident-copy-reference/readme.zh-TW.md) |
| 发布文件身份 | [Manifest](publication-manifest.json) |

WCH CH32V20x 已列入硬件假说，CH32V208 是其中值得比较的子系列。寄存器布局与程序相似仍不能确定 TSL9 的确切型号、电路板、原机 ROM、引脚或中断 ABI。resident 候选采集数据仍有缺失；合成条件下的延续不能补全缺失的原始字节。

原有 76,800-byte 来源一致的离线映像仍为 **NOT-FLASH-VALIDATED**。测试不访问 BLE、UART、CAN 或实体 Flash。每个完成验证的里程碑 commit／push。`README.md` 默认显示繁体中文；英文与简体中文分别放在 `readme.en.md` 与 `readme.zh-CN.md`，`readme.zh-TW.md` 保留独立的繁体中文版本。各语言分开维护，历史封存文档保留原始内容。发布时排除真实设备标识、凭证、私有请求／响应日志及临时编译产物。
