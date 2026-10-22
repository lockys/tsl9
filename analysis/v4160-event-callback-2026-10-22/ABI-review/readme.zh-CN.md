# 事件 callback 独立审查

[繁體中文](README.md) · [English](readme.en.md)

本套件分开原始632B callback 的呼叫／frame 证据、条件化 HOST 效果测试及实际原生元件诊断。HOST 使用合成内存、明确 provider 和本机格式保护；没有执行固件、CPU 模拟器或硬件。保存的 return_address 不是每个 opaque call 的实时架构 RA，正常完成也没有执行恢复后的返回目标。

实际内联元件658B仍超出原区间26B。虽然 frame 为48B、15个间接调用仍写RA，保存顺序、额外 S10 保存及返回位址仍不同。完整原 ABI、placement 和硬件／OTA 仍为 false；没有加入完整映像。

默认 `python -B ABI-review/check.py --project-root ROOT` 只验证来源／元数据。真实 HOST 测试使用 `run-host.py`；真实来源／HOST／native 合并验证使用 `review.py`，详细参数见繁体中文或英文说明。封存不含编译产物。
