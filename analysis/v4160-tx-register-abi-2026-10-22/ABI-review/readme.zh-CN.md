# TX 寄存器 ABI 独立审查

[繁體中文](readme.zh-TW.md) | [English](readme.en.md)

本轮区分行为兼容与字节相同。普通 C/C++ 的两个 cold-success 提示产生 278 bytes／95 条指令，恢复两次 ROM gate 的 RA：`0x8A90`、`0x8AB6`。这一步仍有先建 frame、延迟恢复和原范围末端 2 bytes 未覆盖的问题。

后续实测的窄入口使用标准 BLTU mnemonic 和一条 `R_RISCV_BRANCH` relocation，连接真正的 typed C 返回 leaf，组成 entry8＋body270＋leaf2＝280 bytes。入口位于 `0x8A56`，自然落入 `0x8A5E` 的 C body；超长分支指向 `0x8B6C` 的编译 RET。entry FUNC 的真实大小是 8，280 是共享 allocation 的总长，不伪造 compiler FUNC280。

新的 source-owned frame 排序层仅处理 body 的 `[2,12)`、`[208,270)` 两个窗口。它重排五个实际编译 C.SWSP，并移动五个已有 C.LWSP，让 RA/S1/S2/S3 在 descriptor SH 前恢复、S0 在两个 SH 后／ROM pointer load 前恢复，SP increment 保留在 task LBU 后。其他指令 word 顺序、长度及全部 ELF metadata 不变。没有 whole-function asm、原始字节回填、padding、新 opcode encoder 或旧 pass 修改。

原 frame 读取时序不能靠普通 ABI 假设抹去：frame 与 descriptor 可以别名。具体静态反例见繁中／英文说明。前缀独立 word store 的交换、相同 ADD/MUL 的来源交换，以及经过证明的内部 CFG 重排不必要求原始字节相同；不同逻辑角色仍需逐项核对。

`loop.py` 实读原始96及新 linked ELF，核对原 BLTU true 跳向 payload 与候选 BGEU false 落入 payload 的关系、相同低16 counter／live S0、八条 payload 指令、backedge 和 checksum finish。只允许 ADD A6 来源互换。它不运行循环或 ISA 状态。

每种语言有 14 项实际 ELF guard 变异、3 项 linked entry 变异、9 项 loop 指令变异均被拒绝；另有三个实际 CLI 路径 alias 拒绝。已验证范围是独立静态子集。未知 ROM、异步行为、code-as-data、任意 computed interior entry、完整映像外部入口／private role 整合及硬件／OTA 均未声称通过。

默认只检查封存源文件、中间资料及依赖源码 hash，不读取固件或 build：

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/check.py --project-root .
```

显式重验新编译产物：

```sh
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/formal/ordered/c --receipt /absolute/new-review.json
python3 -B apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --replay /absolute/new-review.json
```

实际模式从该 producer receipt 的 `pre_folder` 取得 provider，也可用 `--providers` 显式指定。新 receipt 为 create-only；`--replay` 只读。默认 stdout 为 `actual_build_artifact_replay:false`，实际模式为 true；两者均保留 `original_full_ABI_admitted:false`、`whole_image_integrated:false`。`review.sh` 无参数运行默认模式，其他参数转交实际模式；`PYTHON` 可指定 Python。
