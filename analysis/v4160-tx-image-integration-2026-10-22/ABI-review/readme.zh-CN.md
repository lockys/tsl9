# TX 完整映像独立审查

[繁體中文](README.md) · [English](readme.en.md)

本套件检查真实完整映像的 691 个分配区域、LOAD、重定位、边界调用、实际排序层和 76,800B 导出内容。TX 采用真实 FUNC8／FUNC270／FUNC2，93 个字节差异均在 TX 内；不要求整张 BIN 与原文件相同，也不伪造 FUNC280 或 ABS 程序提供者。

30 个记录的边界引用包含区域外 29 个及已重建 page-reply 的 1 个调用，不代表完整调用枚举。8,258 笔非 TX 重定位仅允许九个 TX 入口目标如实从 FUNC280 改为 FUNC8。实际反例检查错误角色、重定位、调用链接、指令、LOAD 和导出字节。

默认 `python -B ABI-review/check.py --project-root ROOT` 只验证来源及封存元数据，不读取原 BIN、不重播实际构建。真实检查与只读重播：

```sh
python -B ABI-review/review.py --project-root ROOT --firmware FW --folder MODE --receipt NEW.json
python -B ABI-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

构建来源和完整编译链另由独立 source-review 检查。本套件不分发编译产物。静态产物通过不证明未知 ROM、所有异步／故障前缀、硬件兼容、BOOT 接受或蓝牙烧录；`original_full_ABI_admitted` 与 `hardware_OTA_proved` 均保持 false。完整说明请参阅繁体中文或英文文档。
