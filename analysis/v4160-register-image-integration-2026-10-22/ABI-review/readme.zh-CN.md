# 原始寄存器顺序全映像：独立 ABI 审查

实际 C11／C++17 编译、明确 ABI 排序与链接产物通过独立静态审查。76,800 字节与原始固件零差异，SHA-256 为 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

此证据覆盖11个可读 C／C++函数、526字节；其余680个区段仍保留 carrier 来源，不代表整套应用已经解释或完整还原为高级 C。实际核对 pre／post 编译对象、14字节排序、691配置、15 LOAD、53绑定、11 JAL、10分支角色、20进入点及57命令关联；每种语言五个聚焦反例均拒绝。

本 seal 仅含来源、文件、回条与 metadata，不发布生成的对象、ELF、BIN、IR、相依档或 log。默认命令只检查来源／metadata，明确回报 `actual_build_replayed=false`：

```sh
python3 -B apk-analysis/tsl9-v4160-register-image-integration-2026-10-22/ABI-review/check_seal.py --project-root .
```

若需实际重验，先从来源新建 MODE_DIR，再使用 `review.py --project-root . --firmware ORIGINAL_BIN --folder MODE_DIR --receipt RESULT.json`，以及 `--replay RESULT.json`。缺少实际产物会停止，不能以 metadata 成功替代；新回条应保存于被忽略的 model/build 目录。

最终保存顺序由编译器加明确来源自有 ABI 排序产生，不能宣称编译器单独输出。原始 BIN 只供比较。硬件、ROM、更新封装、恢复能力、OTA与实际设备成功均未由静态字节相同证明。本轮没有网络、实体 I/O、目标执行或 ISA模拟。详细证据和限制见繁体中文／英文文件。
