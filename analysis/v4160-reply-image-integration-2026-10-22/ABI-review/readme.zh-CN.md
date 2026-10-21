# 十二函数完整映像：独立ABI审查

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

本范围核对12个可读C/C++函数，共650 bytes；其余区段仍保留原始字节载体，没有宣称还原全部源码。实际验证包含691个配置区段、679个保留区段、8257笔外部加12笔内部JAL重定位、53个相对绑定、21个入口和11个分支消除。9DF4的693b是写入RA9DF6的C.JAL；原公开NOTYPE/size0与local entry0保留，新FUNC124独立存在。

回覆物件28 bytes与合并后14 bytes分别经过明确ABI排程，不能称作编译器单独产生最终顺序。排除型`.llvm_addrsig`必须只追加实际原生回复物件的一个索引，旧56 bytes不变，最终ELF中消失。

实际BIN必须等于所有690个文件区段的ELF散布结果及原始76800 bytes。所有LOAD的内存范围和权限都须符合区段所有权。6个实际ELF／BIN字节变异控制必须拒绝。

`check.py --project-root ROOT`与`check.sh`预设只验证封存来源／中继资料，不读原始固件或建置产物。实际模式为`review.py --project-root ROOT --firmware FW --folder MODE --receipt NEW.json`；唯读重播使用`--replay NEW.json`并保留root和firmware参数。封存不包含`.o`、`.elf`、BIN或build目录。最终实际结果见`summary.json`与`receipts/`。

本审查没有执行或模拟目标CPU、联网、操作硬件或产生固件BIN。未知计算入口、ROM、硬件、芯片型号、中断时序及蓝牙烧录相容性仍未验证。
