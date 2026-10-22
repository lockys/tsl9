# Callback 暫存器與 live GP：獨立來源審查

[English](readme.en.md)

這份審查重用已封存的632B／217指令原始證據，但重新讀官方 ID2966 BIN 並逐一解碼所有 rd／rs1／rs2。它不以文字中沒有 `s10` 或 `s11` 作證明，也不重跑舊26個 raw controls 或未改變的 HOST 行為矩陣。新的控制只針對這次的暫存器、SP0 與 GP 限制。

| 離線產物 | Bytes／指令 | S10 ports | S11 ports | GP reads | direct frame words |
|---|---|---:|---:|---:|---:|
| 官方原始 callback | 632／217 | 0 | 0 | 6 | 22 |
| 前輪 inline native | 658／241 | 6 | 0 | 16 | 24 |
| 只增加 fixed26／27 | 656／240 | 0 | 0 | 16 | 22 |
| 同旗標、live GP bridge | 624／223 | 0 | 0 | 6 | 22 |
| 明示 word-order pass 後 | 624／223 | 0 | 0 | 6 | 22 |

原函式自己的所有明確 register operands 都不使用 x26／S10、x27／S11。這不表示未知 ROM 不能改變它們，也不證明 callee 保存它們。原函式不負責儲存／還原這兩個值；其後真正流向 caller 的值仍取決於 opaque callee。

原 frame是48B，11次SW使用 slots+4..+44，依序保存 S0、RA、S1..S9；共同 epilogue從 liveSP重新讀 RA、S0..S9，最後 liveSP+=48，JR fresh RA。原始指令沒有直接 SP+0 word access，但其他指標別名、ROM或非同步行為能否存取那個實體 word仍未知，不能把它視為可自由使用的空間。

前輪658B產物的六個 S10 ports 已由實際 byte欄位與 LLVM operands交叉核對：SW S10,SP0；ADDI S10,S1,-1；兩次AND以S10為mask；一次ADD讀S10；LW S10,SP0。它以S10承載0xFFFF相關運算並額外覆寫／讀取SP0。`baseline-658.json` 與 `baseline-fixed656.json` 保存當時實際檔案指紋及欄位，不會在預設驗證時偷偷讀取 W 的歷史 archive。

增加的旗標嚴格只有 `-ffixed-x26 -ffixed-x27`，接在已封存的原 profile之後。保留兩者可避免修掉S10後把暫存器壓力轉移到同樣未出現在原指令的S11。旗標文字本身不構成證明；必須檢查全部機器欄位、11組 save/readback、沒有 replacement spill，以及實際來源與編譯命令。

GP在原函式只有六個明確讀取點：`868E` LBU+94、`8698` LBU+98、`86A8` GP+94的地址運算、`86CC` GP+80、複製後的 `87C0` GP+80，以及 `87FC` 取得liveGP供下一個LHU+2A使用。原函式自己不寫GP；未知ROM是否保存GP仍未證實。

新的來源改動可機械核對：六個 `s->gp` 改成 `CB_GP(h)`，移除 native entry snapshot與 native call後的 snapshot原始碼位置，加入窄 fixed-x3 empty volatile asm讀取 port。HOST macro仍指向同一個 `h->values.gp`，而固定的 local alias `s` 原本就指向 `h->values`；控制流程、算術、寬度及HOST API沒有改動。這是來源等價理由，不是假造一次新的HOST執行。

實際624B C／C++元件包含六個直接 GP ports、沒有GP寫入，IR也確實是六個固定x3、帶memory clobber的empty outputs。兩次GP+80分別進入正確的後續opaque call，postcopy GP讀發生在copy call與新target load之後。最後原LHU被Clang降成LH再SH，低16-bit寫入仍可對應，但暫時GPR的sign extension不同，所以不能宣稱完整physical prefix相等。

各 native component都是真實單一FUNC及完整allocation，沒有拿原BIN作codegen、沒有補成假FUNC632。正式產物另以明示 pass重排既有save words，恢復11個保存項目的相對順序；原始SLLI等其他prefix位置沒有因此變成逐指令相同。這一步不是pure Clang輸出，八個recipes包含五個原始native步驟與三個ordering／link／disassembly步驟。實際call RA offset集合仍不等原始。624B的數值fit不授權配置原區域剩餘8B；未知ROM的S/SP行為、fullABI、非同步行為、尾端／interior ownership、完整映像及OTA均未在此admit。

預設命令只重新驗證官方BIN的來源限制、當前來源的機械改動與封存metadata，明示沒有actual native replay。指定新formal receipt才驗實際pre／ordered ELF、IR、八個recipes、`.d` closure、已知工具與來源pins；不需要舊build archive。來源四個有針對性的raw controls與每語言五個實際native欄位controls均檢查S10、S11、GP寫入、SP0及freshGP限制，沒有新增廣泛測試矩陣。

```sh
python3 -B check-review.py --project-root /project --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python3 -B check-review.py --project-root /project --firmware /absolute/ID-2966-V4.1.60-decoded.bin --receipt /absolute/new-native/ordered/c/verification.json
```

所有操作都是靜態檔案檢查；沒有執行／模擬RV32、連網、裝置I/O或燒錄。
