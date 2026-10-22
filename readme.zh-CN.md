# TSL9 离线 C/C++ 重建

[繁體中文](README.md) | [English](readme.en.md)

本项目保存原始 APK、22 份不同的更新器 BIN、可读 C/C++ 行为模型及静态来源证据。完整目标仍是生成与原硬件及 BLE 更新器兼容的重建 BIN，并在逆向过程中评估值得新增的功能，将提案与已实现功能分别列出。**目前尚无经验证可刷写的重建 BIN。**

## 配置 callback 字段来源与 556-byte C/C++ 实验

两份候选 BLE 初始化的实际64-byte copy，已追到配置 callback word 来自设置结构 `staCB`（+52）；两份 header 经真实 RV32 C 编译核对字段。原 App 的 SNV 设置数值为 `0x08077C00`，不代表其他 Flash 可用。两个有依据的 C 生命周期调整将 OTA 组件缩为 **556 bytes／188 指令／48-byte frame**，移除一对 S8 保存；独立回复对象位于 SP+10/11，仍比原 SP+12/13 低2 bytes，**指针 ABI 尚未通过，不替换现有568组件或完整 BIN**。 [代码、实物证据与限制](analysis/v4160-allocator-callback-2026-10-22/README.md)

## OTA 原 caller 已接上真实 C/C++，新增完整实验映像

新的 C11／C++17 同 TU 强别名接上原 caller；实际 `0x14094` 的 JAL 已指向 `0x1AC00`，返回地址仍为 `0x14098`。两种语言生成相同 **77,824-byte** 实验 BIN；继承的76,800 bytes中仅该指令的三个bytes改变，原530-byte handler保留，尾端新增568-byte C与456-byte非执行FF页尾数据。SHA-256：`3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`。

**这不是已经验证可刷写的 BIN。** 部分链接仍保留真实 ROM UND；完整 ELF 只沿用原始 `0x18730` 指令已指向的 `0x40000` 数值见证，不提供 ROM 实现或实机身份。新增区域的 Flash／NV 所有权、callee／堆栈 ABI、实体 BOOT 与 OTA 接受／恢复仍待证明。两份候选配置路径会把 ambient A2 传到另一个未知 callback，不能宣称回复地址不被观察。 [代码与证据](analysis/v4160-ota-source-wiring-2026-10-22/README.md) | [实验映像](artifacts/offline-images/ID2966-V4.1.60-ota-source-wired/README.md)

以下里程碑中的“未整合／没有新 BIN”描述仅适用于该历史范围。

## OTA 的九个 provider 已完成真实部分链接

现有 568-byte C／C++ 组件通过真实 provider 对象完成 `ld.lld -r`，九个外部引用均解析到已分配区段，只剩原有 ROM 入口未解析。**原 caller 尚未改向新 C，没有 final ELF 或新 BIN。** 同时确认回复指针会逃逸到配置 slot 的 A2；候选 BOOT 的 Runtime 页上限为95，数值余量不代表可用 Flash。 [链接工具、原始证据与配置限制](./analysis/v4160-ota-handler-layout-2026-10-22/README.md)

## OTA 原生组件缩减至 568 bytes

通过分离回复数组的生命周期和共用三个 C 回复出口，将组件从 776 bytes／285 指令／112-byte 栈帧缩减至 **568 bytes／193 指令／48-byte 栈帧**，保留八个寄存器调用桥接与各命令效果。仍超出原 530-byte 范围 38 bytes，**尚未链接、没有新增 BIN；完整 TX 映像不变**。前轮分析 README 的“四个展开 quarter callsite”已另附更正，实际对象只有一个循环调用点。 [代码、独立核对与限制](./analysis/v4160-ota-handler-compact-2026-10-22/README.md)

## OTA 命令已重建为共享 C/C++

新增 U／S／W／R／E 命令的可读 C11／C++17，保留 UID、长度、页码、实时模式、四次 quarter 写入与逐 word 读回的先后顺序。两种语言各通过本组和独立 HOST 测试；实际原生对象均为 **776 bytes／285 指令／112-byte 栈帧**，比原 530-byte 范围多 246 bytes，九个外部引用仍为真正的 UND。**尚未链接或纳入 BIN；原有完整 TX 映像保持不变。** W 写入 BOOT 别名，不代表已证明 Runtime 自更新。 [代码、证据与缺口](./analysis/v4160-ota-handler-2026-10-22/README.md)

## callback 原生组件缩减至 624 bytes

新的 C11／C++17 组件均为 624 bytes／223 条指令：明确保留 S10／S11，将六个 GP 使用位置改为读取当前实体 GP，并通过明确步骤交换两个已有保存指令。48-byte 栈帧、十一组保存／恢复、十五个间接调用已由独立审查核对；本轮未重跑 HOST。原始剩余 8 bytes 含有可执行指令，完整入口、调用返回 ABI、尾区所有权及原位配置尚未证实。**组件尚未集成，没有新增 BIN；原有完整 TX 映像保持不变。** [证据与限制](./analysis/v4160-callback-registers-2026-10-22/README.md)

后续静态调用边界核对确认：GP+42 的半字在新旧调用前均已覆盖，没有这里的 A4 漏传；两份官方 ROM 候选的 `+0x13C` 小函数对仅按一般方式保存／返回 RA，不读取 caller S4／S7。这缩小了部分限制，但不证明实际 ROM 身份或其余 callee。候选 slot 对应 CCC 配置读取与通知发送；读取可返回 0..255，仍须区分原始 `==1` 与 `&1` gate。 [调用边界与候选条件](./analysis/v4160-callback-call-frontiers-2026-10-22/README.md)

## 先前事件 callback 的可读重建与原生差距

`0x8614..0x888C` 的 632-byte callback 已重建为可读 C/C++，涵盖事件优先级、两组 context／connection、分段长度、重试与后续事件。原生明确内联诊断由 1,034 bytes 降到单函数 658 bytes，取得 48-byte 栈帧／十五个间接调用；仍超出 26 bytes，且额外 S10 保存、保存顺序、返回地址与未知 ROM 契约仍待确认。**此 callback 尚未纳入完整 BIN，没有新增可刷写映像。** [分析与限制](analysis/v4160-event-callback-2026-10-22/README.md)

## TX 源码已纳入完整实验 BIN

正式 C11／C++17 各新编译 46 个单元，生成相同的 76,800-byte 实验 BIN；十三个原始函数范围共 930 bytes，由十五个真实 FUNC 角色承接，678 个其余区段保留原始承载。与官方 ID2966 的 93 个差异全部位于 TX，其余 byte 相同。SHA-256：`28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。**新 BIN 尚未验证可刷写。** [完整整合](analysis/v4160-tx-image-integration-2026-10-22/README.md) | [实验映像](artifacts/offline-images/ID2966-V4.1.60-tx-integrated/README.md)

## 跨平台验证

OTA 发送入口 `0x8A56` 已取得实际 280-byte 原生组件：8-byte 窄汇编入口、270-byte 可读 C/C++ 主体及 2-byte 返回函数。超长输入可直接返回、不碰栈，两次 ROM 调用的返回地址吻合。寄存器保存／恢复时序以新的独立排序步骤核对；**此组件已纳入上述新版映像，仍未经原硬件或 BLE OTA 验证**。参见[入口与调用框架分析](analysis/v4160-tx-register-abi-2026-10-22/README.md)、[原始发送契约](analysis/v4160-ota-tx-2026-10-22/README.md)及[新功能提案](analysis/v4160-ota-tx-2026-10-22/continuation-plan/README.md)。

先前完整映像已纳入 OTA 页面回复：12 个可读 IRQ／Flash／OTA 函数共 650 bytes，完整 76,800-byte BIN 与官方 ID2966 V4.1.60 相同。C、C++ 各新编译 43 个单元，61 个命令含两次明确 ABI 排序；全部单元记录完整标头依赖。其余 679 个区段仍使用原始承载，这是部分源码重建，**不是原硬件或 BLE OTA 验证**。参见[新版整合](analysis/v4160-reply-image-integration-2026-10-22/README.md)与[离线映像](artifacts/offline-images/ID2966-V4.1.60-reply-integrated/README.md)。

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
