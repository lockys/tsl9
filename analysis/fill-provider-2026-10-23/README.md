# 填值提供者與標記傳送鏈

[English](readme.en.md) · [C/C++來源](../../src/native/receive/fill_provider.c) · [填值細節](../../experiments/tsl9-fill-provider/README.md) · [三區段連結](../../experiments/tsl9-tagged-native-chain/README.md)

已重建`0x8520`的168B／55指令，保留反向byte stores、word stores、computed跳轉與RA／T0殘值，沒有以libc替換。第一版LLVM對調兩指令；第二版只增加順序約束，來源與量測都保留。

五份真正C來源已實際編譯並連結：**三個原PC區段合計740B／260指令／58強FUNC，全部程式碼符合原BIN，直接符號與重定位均解析**。31組computed案例僅有16個唯一目的位址。ELF的59,218B可執行LOAD含未驗證缺口；740B只是已證明的code投影。

`src/` 目前63個C/H、37個原生單元、74組C/C++比較、148物件；舊72組結果與433產物雜湊不變。填值每語言94項、整合每語言264項負向檢查及獨立唯讀重播通過。

仍未知`[0x4004C]`新讀的resident目標與契約；0UND不代表執行環境已閉合。**尚未證明完整映像、實體硬體、IRQ與OTA相容性，未產出可刷寫BIN。** 既有1162B整合保持原樣。

[摘要](summary.json)／[獨立審閱](independent-review.json)／[公開收據對應](publication-provenance.json)。四份可攜原始收據完整保留，一份公開檔僅匿名化路徑；原始收據與未選用版本保留本機，不改寫Git歷史。
