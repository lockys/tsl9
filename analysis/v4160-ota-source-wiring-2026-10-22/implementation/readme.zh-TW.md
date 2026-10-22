# Source-wired 數值地址 witness producer

[English](readme.en.md)

正式入口是單一 `verify_image.py`，支援fresh與read-only replay。它fresh編譯同TU strong alias的實際C568及非執行FF456資料，僅弱化既有carrier副本的原入口，再partial link與原layout＋extension link。完整算法／八暫存器bridge直接include封存compact來源，實際raw object kernel hash仍b486c6...63af。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/verify_image.py \
  --project-root . --tool-dir /path/to/llvm/bin \
  --base-object BASE/source-integrated.o --base-receipt BASE/verification.json \
  --base-witness BASE/ADDRESS-WITNESS-ONLY.elf \
  --base-image BASE/NOT-FLASH-VALIDATED-tx-integrated.bin \
  --build-root experiments/tsl9-v4160-ota-source-wiring/build/NEW-C
```

一次一語言，mode由base receipt推導且固定原flags；沒有--mode／--language／--firmware。CPP傳它自己的base artifacts。四個base inputs以既有receipt artifact map與精確hash驗證；historical NUMERIC-ROM-WITNESS-ONLY.ld由receipt同folder取得並驗證。不要猜D/P的formal目錄，使用實際先前UUID archive。預設新UUID build，明示build-root也必須是model/build內不存在的目錄。

實測兩語言相同BIN：77,824B，SHA3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee。原caller14094的JAL ef60d036確實到新C1AC00，RA14098。原691alloc／8261RELA全部保留，只變原公開入口的binding/preemption與caller relocation；新partial693alloc／8281RELA，9真allocated providers，唯一ROMentry真UND。原530B raw body仍在原section；不是假FUNC568借舊大小或ABS alias。

**ROM_provider=false。** strict link實際nonzero，錯誤只有缺ROM且沒有STRICT-MISSING-ROM.elf。另一路只逐byte複用歷史ROM=40000數值script，明確輸出ADDRESS-WITNESS-ONLY.elf與NOT-FLASH-VALIDATED BIN；不提供ROM code，不提升installed-ROM／完整ABI／Flash-NV free／OTA admission。原reset tail和舊ROM boundary未改。

正式每語言11exact chronological recipes、20actual artifacts。Source/tool/input before-after pins、實際MD4project＋stdint.h、193指令raw與linked完整bytecoverage、13個full8 asm bridges、20個native relocations、所有一般及metadata symbol來源、17LOAD permissions／bytes／RAM35160 NOBITS及全部77824export ownership可唯讀重驗。舊75頁只在14094 caller word內3bytes不同；新一頁真C568＋nonexec FF456，沒有codegen byte borrow／BIN fallback／未擁有的輸出holes。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/verify_image.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/check.py --project-root .
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/check.py --project-root . --receipt C/verification.json --receipt CPP/verification.json
```

發布路徑為analysis/v4160-ota-source-wiring-2026-10-22。check預設source/seal/metadata-only，actual flags false；明示receipt才讀actual inputs/outputs/logs和工具，replay不啟動compiler/linker。results.json列兩份正式receipt metadata與兩份first prototype metadata；prototype.py只為歷史診斷，正式replay使用verification.json。Opaque objects/build archives不發布，不能把缺archive的metadata檢查稱為actualreplay。原historical layout CRLF bytes完整保留為舊input，所有新source/docs/JSON均LF。

獨立ABI審查兩語言actual artifacts及每語言9個真ELF反例通過；allocator-review保留unknown slot70可觀察ambient/pointer的條件，不構成刪減橋或ABI放行。沒有重跑未變更HOST/base compiler。沒有RISC-V執行／ISA模擬／網路／硬體／Flash寫入或UID/VIN存取。
