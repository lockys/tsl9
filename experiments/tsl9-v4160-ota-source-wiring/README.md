# OTA handler 真實 source wiring 實驗

[English](readme.en.md)

新TU直接include封存compact來源，並以同TU的真實strong compiler alias，讓原公開入口 `__tsl9v4160_ota_code_9c4a` 對應到實際FUNC568。只在既有carrier的副本使用標準llvm-objcopy弱化原NOTYPE0入口，再讓原caller的symbolic relocation由strong C定義接手。

實際C11/C++17均得到77,824B的**NOT-FLASH-VALIDATED數值地址witness**，SHA `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`。0x14094的真JAL已指向0x1AC00，RA仍0x14098。原76,800B僅caller word內3個bytes改變；原530B body仍保留於0x9C4A，已證明的known ingress改走新C，不推論所有computed entries。

追加的1,024B是實際編譯568B C body加456B明示非執行FF資料，組成數值上的下一頁至0x1B000。FF是page packaging，不是缺失code的補洞。每個export byte皆有實際ELF section及LOAD覆蓋，沒有從舊BIN複製fallback。相同frame48、完整八暫存器bridge與kernel568身份只證明這個編譯來源，不構成完整原始ABI。

**ROM_provider=false。** 沒有ABS ROM的partial ET_REL仍只有真UND `__tsl9v4160_rom_entry`；strict final link真的因缺ROM失敗且無輸出。另一條明示numeric witness只複用歷史 `ROM = 0x40000` 邊界，與原reset tail數值相符，並未提供ROM body／installed ROM。不得據此宣稱可燒錄／可OTA。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/verify_image.py \
  --project-root . --tool-dir /path/to/llvm/bin \
  --base-object BASE/source-integrated.o --base-receipt BASE/verification.json \
  --base-witness BASE/ADDRESS-WITNESS-ONLY.elf \
  --base-image BASE/NOT-FLASH-VALIDATED-tx-integrated.bin
```

一次一語言，mode由base receipt取得；C與CPP各執行一次。fresh預設model/build內新UUID，或指定尚不存在的`--build-root NEW`。既有base object／witness／image以真實receipt和固定身份核對，不重編base或未變更HOST。原BIN／baseline image只做驗證，不能作產碼模板。

```sh
sh experiments/tsl9-v4160-ota-source-wiring/verify.sh --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/check.py --project-root .
```

發布版case路徑為analysis/v4160-ota-source-wiring-2026-10-22。Python／shell入口可攜，實際工具身份為本機Windows NDK；沒有宣稱Linux/macOS native實跑。replay只讀actual inputs／sources／artifacts，不啟動工具；預設check只核對source／seal／metadata，actual flags false。build archives和opaque objects不發布。

仍未證明installed ROM/BOOT、0x1AC00的Flash/NV free ownership、pointer/frame/S/GP/RA/async完整ABI或OTA相容性。既有原raw carriers仍佔主要部分。本實驗是實際source entry wiring進展，不是完成整份可讀韌體或硬體驗證。
