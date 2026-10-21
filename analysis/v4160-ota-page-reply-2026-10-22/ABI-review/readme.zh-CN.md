# OTA 页面回复：独立 ABI 静态审查

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

本范围检查 ID2966 V4.1.60 的 `0x9B8E..0x9C0A`（124 bytes、50 条指令），以及实际由 C/C++ 编译生成的物件。原始证据位于已封存的 `../source-review/`。最终实际产物为 `experiments/tsl9-v4160-ota-page-reply/build/formal-native-final/{c,cpp}`，两种语言排程后的连结内容均与原始124 bytes一致，尚未整合完整映像。

实际编译器产物保留所有调用、分支和末端跳转位置，标头写入、完整 32 位索引公式与 TX 参数顺序符合原始指令。剩余差异是 `[+0x02,+0x16)` 和 `[+0x58,+0x60)` 两个窗口的顺序，共 28 bytes。每个窗口的指令字清单相同；编译器本身还没有输出完整原始顺序。

`native.py --project-root ROOT --folder ACTUAL_COMPONENT_FOLDER --report NEW_REPORT.json` 检查实际 ELF、50 条原始指令字段和 LLVM IR。可额外提供 `--scheduled SCHEDULED_OBJECT`，要求只有上述窗口改变，其他 ELF bytes、符号和重定位保持一致，最终顺序符合原始证据。每种语言必须拒绝 7 个实际机器码变异与 4 个 IR 变异。

完整实际检查为 `review.py --project-root ROOT --folder ACTUAL_COMPONENT_FOLDER --receipt NEW_REPORT.json`；唯读重播为 `--project-root ROOT --replay NEW_REPORT.json`。还会验证排程收据、语言配方、固定连结入口、TX目标与RA，并拒绝3个实际连结ELF变异。TX的ABS符号只是数值见证，没有驻留实现。`verify.py`／`verify.sh` 预设只检查封存来源和中继资料，不重播未发布的实际产物。封存不含 `.o`、`.elf` 或 `build/`。中继资料保存每种语言18个ELF、5个路径、3个收据排程变异结果。

释放是恢复后经 T1 的尾端跳转，不创建新 RA。空配置结果使用独立返回路径，没有统一状态值。三参数 `musttail` 只是原始寄存器接口；A1/A2 转发 TX 返回后的值，不能证明驻留释放函数的 C 签名。未知驻留 SP／保存寄存器行为、计算式入口、ROM、硬件与 OTA 相容性仍未验证。显式排程是来源 ABI 顺序恢复，不是任意输入下可交换的证明。本范围没有执行目标 CPU、模拟器、网络或实体 I/O。
