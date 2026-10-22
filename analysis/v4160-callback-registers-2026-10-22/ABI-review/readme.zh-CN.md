# Callback 暂存器与 GP 精修独立审查

[繁體中文](README.md) · [English](readme.en.md)

本轮仅新增固定 S10/S11 的两项旗标。656B诊断保留；六处实际使用点读取当前GP后得到624B/223指令。没有重跑未变的 HOST 演算法，也没有执行目标CPU或模拟器。

实际代码没有 S10/S11 操作或SP0 spill替代，保留48B frame、11个保存／恢复、15个写RA的间接调用。新排序层只移动两个既有保存指令；除4个字节外，整个对象与链接ELF均不变。所有raw字段与独立LLVM文字一致，五个native及四个排序反例均拒绝。

默认 `check.py` 仅查来源和元数据；实际 `review.py` 检查 raw compiler 产物，`review-ordered.py` 检查 compiler→排序→链接并支持只读 `--replay`。完整指令见繁中或英文文档。

624B只表示数值尺寸可容纳。原区间最后8B仍没有来源提供者；完整entry prefix、返回位址、未知ROM及硬件ABI未证明，没有加入完整映像。whole632／fullABI／placement／hardwareOTA 保持false。
