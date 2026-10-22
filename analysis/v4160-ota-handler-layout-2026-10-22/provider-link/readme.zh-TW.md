# 真實 providers 的部分連結

[English](readme.en.md)

只使用已存在並由原receipt artifact map驗證的兩個objects，實際執行一次標準 `ld.lld --no-relax -r`。沒有重編C/C++或HOST。C／C++兩組各測得：

| 項目 | 原carrier | compact native | 新ET_REL |
|---|---:|---:|---:|
| 非空 allocated sections | 691 | 1 | 692 |
| RELA | 8261 | 20 | 8281 |
| 真UND | ROMentry 1 | 9 | ROMentry 1 |

九個native UND全綁至原carrier的真實allocated providers，保留其section-relative value／size／info／visibility。剩餘 `__tsl9v4160_rom_entry` 仍真UND，沒有ABS／defsym／stub／undefined-ignore或假大小provider。

原raw handler530B（`__tsl9v4160_ota_code_9c4a`，原NOTYPE0角色）與新truthful FUNC568（`tsl9_ota_handler_native_9c4a`）同時存在。原caller仍指向原handler；沒有entry reroute。所有原allocated bytes、NOBITS角色、type/flags/alignment/size保留，native568 bytes不變；完整RELA語義等於兩input聯集，只將九個UND投影到真provider角色。

這是provider closure，不是功能fullimage。`-r`保留8281 relocation records，**不宣稱已套用或range-check JAL**；本次native instruction bytes仍與輸入相同。沒有 final ELF／BIN／placement／installed ABI或OTA證明，也沒執行RISC-V。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/provider-link/link.py \
  --project-root . \
  --base-object PATH/c/source-integrated.o --base-receipt PATH/c/verification.json \
  --native-object OTHER/c/ota_handler.o --native-receipt OTHER/c/verification.json \
  --ld /path/to/llvm/bin/ld.lld --build-root NEW-OWNED-DIR
```

mode從兩個input receipts取得且必須一致。目前接受的base object為既有V4.1.60 TX-integrated C/CPP精確hash，native為封存compact568精確hash；不是任意object linker。`--ld`必須是封存Windows NDK linker身份（Windows檔名ld.lld.exe），未測其他平台binary。Python／shell metadata介面可攜，不代表任意LLVM版本／Linux/macOS native linker已通過。

預設產物是此scope/build內新UUID目錄；`--build-root`也必須位於該build且不存在。輸出 `PROVIDER-CLOSURE-ONLY.o`、log、verification.json。stdout回receipt/hash/mode、九bindings及剩餘UND。Inputs和receipts可用明示路徑提供，不依賴隱藏W路徑；輸入objects／receipt／linker／runner／parser在前後核對hash。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/provider-link/link.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/provider-link/check.py --project-root .
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/provider-link/check.py --project-root . --receipt PATH/verification.json
```

發布版case位於analysis/v4160-ota-handler-layout-2026-10-22。check預設只驗seal／來源依賴／兩份selected metadata，actual flags false，不需要W archives。明示--receipt才重讀actual objects、input receipts、output、command/log與完整artifact集合；replay不啟動linker。source-only發布排除opaque objects及build archives，保留metadata；不把缺archive的檢查稱作actualreplay。
