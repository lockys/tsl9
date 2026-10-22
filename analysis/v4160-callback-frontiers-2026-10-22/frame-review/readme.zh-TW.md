# Callback 最後一次 RA frame 覆寫的來源證明

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

結論是有條件的肯定：沿原始 callback 的正常返回路徑，最後 `0x198E6→0x188E2` 必定把新 ADC 暫存 RA 的同一個 word（callbackSP-4）覆寫成 `0x198EA`，而後直到原 callback 的 `0x1995A` RET 都沒有來源內的同址 stack store。因此在既有144 B 私有 stack、正常存取、無 alias／非同步修改／觀察等前提下，**整個 callback 正常出口的這一個 word**，原版與新 ADC 候選相同。

這不是新 ADC callee 返回 `0x1989A` 當下的相同，也不使較早暫存值可被外部觀察。前一輪候選在自己的16 B frame 把 RA=`0x1989A` 寫到新SP+12，即 callbackSP-4；該唯一新 stack store 的來源契約沿用已封存 ABI 審查，本輪沒有重編譯或執行它。

新 ledger 直接來自實際 ID2966 V4.1.60：callback `0x197F0..0x1995C` 為364 B／130列，reset-like `0x188E2..0x1892E` 為76 B／25列，固定 RCC leaf `0x19160..0x1917E` 為30 B／12列，共3段470 B／167列。另以舊 source checker 重讀14段完整相依閉包946 B／352列；新3段已包含在該總數，不能相加成不同來源的總覆蓋。整個原檔76800 B SHA256 是 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，不代表解碼整個檔案。

證明是靜態來源 CFG 與 stack 位址代數，沒有 CPU／暫存器執行模型。直接呼叫只使用已封閉的正常返回來源摘要，不從 PSABI 猜保存暫存器。從新 ADC 正常返回點 `0x1989A` 可到達68個 callback CFG 節點；移除 `0x198E6` 後，唯一正常 RET `0x1995A` 不再可達，故最後一次呼叫支配正常出口。這不把一個可能無限循環的路徑當作已返回。

最後的四 byte `JAL RA` 產生 link值 `0x198EA`。188E2 先令 SP減16，188E8 在任何分支或巢狀呼叫之前執行 `SW RA,12(SP)`；此前沒有寫 RA。兩個正常出口形式都被該 store 支配，並從相同 slot 重新讀 RA、還原 SP。巢狀19160不寫 SP／RA／S0，也不使用 stack，只有固定 `0x4002100C` 的讀改寫。RA 的這個保存 word 因而是 `callbackSP-16+12=callbackSP-4=entrySP-132`，位於既有 `entrySP-144..entrySP-1` 區間內。

188E2 正常返回之後沒有其他 callback 呼叫或 stack store。來源中後續 store 只使用固定 RCC／ADC base；正常存取及 disjoint 前提排除它們對這個 stack word 的別名。其餘 SP-relative 讀取在 callbackSP 的非負 offset，最後19958還原128 B外層 frame。callback19920會另行還原真正外層 caller 的 RA；`0x198EA` 是保存在私有 word 的內部 link值，不是宣稱 callback 最後要返回這個位址。

保留一個來源本身允許的反例邊界：poll 在 `0x198D6` 有回到 `0x198C6` 的 backedge，沒有編碼 timeout；如果每次狀態結果都是零，來源允許永遠不到198E6，也不正常返回。因此不能無條件宣稱每次 invocation 都一定覆寫或一定返回。MMIO／stack fault、非同步觀察及其他干擾同樣不在本次正常來源證明內。

實際 `--firmware` 模式拒絕六個 raw operand 反例：最後 CALL link暫存器、保存 slot offset、保存值來源、16 B frame 位移、128 B外層 SP還原量，以及只修改 poll branch target、跳到19906繞過覆寫但仍可到原 RA/SP epilogue的 CFG 反例。反例只在記憶體內修改來源 bytes並重新靜態解碼，不生成 opcode stub 或新 BIN，沒有指令步進。

```sh
python3 -B check.py --project-root /absolute/project/root
python3 -B check.py --project-root /absolute/project/root --firmware /absolute/original.bin
python3 -B check.py --project-root /absolute/project/root --firmware /absolute/original.bin --receipt /new/proof.json
python3 -B check.py --project-root /absolute/project/root --replay /existing/proof.json
```

預設僅讀封存 metadata，actual firmware與raw-controls旗標為false；明示原檔才重新驗整檔身份、實際範圍與反例。收據 create-only，replay只重讀。W `apk-analysis/tsl9-*` 與 D/P `analysis/*` lookup都支援，本輪未寫入 D/P或發布。

這個單字的最終相同，不能推成整個 RAM、整個原 callee ABI、fault／async／IRQ trace、晶片／ROM／BOOT、Flash/NV ownership或BLE OTA相容性已證實。沒有新 HOST、硬體、網路、native／MMIO／ISA／ESIL執行、link或BIN；不需新r2擷取，也不新增或修改舊decoder／ISA定義。POSIX sh wrapper提供相同 Python入口，既有 Git Bash 拒絕不重試，sh runtime保持未驗證。新文字LF、單EOF，default README與繁體中文完全相同。
