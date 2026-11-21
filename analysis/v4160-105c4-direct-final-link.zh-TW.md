# v4.1.60：0x105c4 直接連結的最小驗證

延續 [輸入 addrsig 身分復核](v4160-105c4-input-addrsig-remap.zh-TW.md)。將 140 個基準輸入物件，或 141 個拆分並重新對應 leaf addrsig 的候選物件，直接交給 LLD 最終連結，不先做 `ld -r`，不注入 72 個別名。診斷連結只以 `0x105c4` 為根，使用 `--no-relax --gc-sections --no-undefined --fatal-warnings`，另以腳本明確要求目標符號存在。

一般 Python 與 `-O` 均通過：每次 C/C++ 各一組基準和候選，四路均在 `0x105c4` 重現原 BIN 的 12 bytes。各語言的基準與候選配置區段投影一致：C 為 `.target`；C++ 為 `.target`、`.eh_frame`。兩種語言拿掉 leaf 後均被腳本的 `missing 105c4 definition` 拒絕。僅指定入口並未讓首次缺 leaf 的對照報錯，因此保留明確的定義檢查。

此測試只證明最小直接連結可重現目標，不證實 addrsig 對 ICF 的影響，也不包括兩個真實呼叫點、整張配置、設備 ABI 或可刷性。聚合路徑的 `sh_link=0` 問題仍未解決。下一步以兩個真實呼叫點為根，獨立核對其重定位是否指向 `0x105c4`，並釐清因此保留的外部依賴。原 BIN 與正式來源未改；本次只發布報告。重跑：`experiments/v4160-aggregate-no-ident-next/verify.py --baseline <saved baseline> --objcopy <llvm-objcopy.exe>`。
