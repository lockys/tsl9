# 来源自有 ABI frame 排序：独立对象审查

冻结版工具通过六次实际对象转换、两次完整链接见证、21 个对象防护反例及三种写入前路径别名拒绝。涵盖 C／C++ 合并对象、独立 IRQ main.o 与 Flash quarter.o。[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

工具只排列新编译对象中已有的 C.SWSP 指令：IRQ 八字节、wrapper 六字节；其他字节、section metadata、symbol、RELA 不变。不使用原始 BIN 生成内容，不含 opcode 模板、填充或整函数汇编。交付流程明确是 C／C++ 编译器加来源自有 ABI scheduling，不能宣称编译器单独生成最终顺序。

实际链接后，两函数144B／64B与原始机器码相同，691配置、15 LOAD及20个已知进入点合约保留。这是对先前全映像对象的排序步骤验证，不代表本轮五个新 leaf 已合并成新全映像。全部21个反例与三种路径别名均被拒绝；详细证据与限制见繁体中文或英文文件。

```sh
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/frame-pass-review/check_seal.py --project-root .
```

只读重验不执行 linker、不写文件；原始三次写入 API 路径拒绝结果作为绑定证据保留。prefix 形状不能认证 C／C++ 来源，也未排除未知计算式内部进入点。完整使用须绑定来源、编译命令、工具／policy、pre-object与配置。完整异步／非返回行为、ROM、硬件与 OTA 成功仍未证明。本轮没有目标执行、ISA模拟、实体 I/O、网络或新固件 BIN。
