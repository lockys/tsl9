# Conditional resident memory leaves

[English](readme.en.md)

這是兩份已保存 SDK candidate RAM leaf 的可讀 C11／C++17 演算法重建。位址是條件式來源身份，不代表已安裝的 resident provider，也沒有執行或模擬原始 RV32 指令。

| candidate leaf | 原始範圍 | 正常結果 |
| --- | --- | --- |
| compare-byte | 200004BC，62B／19 指令 | 非 null 且非零長度、所有 byte 等於完整 32-bit expected 才回 1，否則回 0 |
| fill | 2000039C，46B／14 指令 | 正常填完回 u32(destination+count)，null／零長度回原 destination |
| forward copy | 20000332，58B／18 指令 | 回原 destination；source／destination null 或零長度不複製 |

三者都先 READ32(4002420C) 保存、WRITE32 同址為 0、FENCE.I，然後才測 null／count；正常及 early return 都 WRITE32 恢復原保存值。不是 libc memset／memcpy／memcmp：compare 不把 expected 截成 byte；fill 只在 store 時截低 8 位；copy 每次 fresh READ8 後才 WRITE8，forward overlap 會回饋，所有位址加法為 u32 回繞。原指令本身沒有提供一般 invalid-memory／fault cleanup 保證。

共享 C 使用明確 read8／write8／read32／write32／fence_i 五種數值位址 port。HOST provider 是合成記憶體，CONTINUE 表示該次完整值／effect 已知；HALT／TRANSFER／UNKNOWN 使演算法停止並保留已發生 prefix，不假造最後 restore 或正常回傳。diagnostic budget 只在 HOST port，沒有加入 native loop timeout。typed context 的 flow 與 counter bookkeeping 不是原始實體暫存器證明。

## 實測範圍

自有 HOST C／C++ 各 27 cases、219 checks，另各三個實際編譯 semantic mutants 被拒絕：expected 截 byte、反向 source 讀取、以 0 取代 saved MMIO restore。測試包括短路／fresh read、MMIO/data alias、overlap、跨 0xFFFFFFFF、null／zero、停止 prefix。

Native 只編譯 ET_REL／IR／MD／完整靜態 disassembly。C／C++ 的 compare146B、fill138B、copy160B，另有真 local begin86B；合計 530B／218 指令、13 RELA、五個真 IO UND。這是帶 context／flow 結果的 typed port ABI（含 sret 與 frame），不是原始無 frame leaf 的 drop-in。host_io.c 僅編入 authored HOST tests，不是實際 MMIO／FENCE.I provider。沒有 link／BIN、numeric provider、尺寸偽裝、opcode 產碼或硬體操作。

## 使用

```sh
sh experiments/tsl9-resident-memory-leaves/verify.sh --project-root "$PWD" --language both
python3 CASE/implementation/probe.py --project-root ROOT --tool-dir LLVM --language both
python3 experiments/tsl9-resident-memory-leaves/verify_host.py --project-root ROOT --replay HOST_MODE/verification.json
python3 CASE/implementation/probe.py --project-root ROOT --replay NATIVE_MODE/verification.json
```

兩個 fresh CLI 都可指定 `--build-root NEW`，必須為 model/build 內全新路徑；省略時為 UUID，輸出各為 `{c,cpp}/verification.json`。CASE 是發布的 analysis/v4160-resident-memory-2026-10-22，或工作副本 apk-analysis/tsl9-v4160-resident-memory-2026-10-22。check.py 預設只有來源／metadata；明示 `--host-receipt`／`--native-receipt` 才讀實際 archives，可重複提供。缺檔即失敗，replay 不重新編譯。

Python／POSIX sh 入口可攜，HOST 每次 executable launch 都使用既有 immutable 本機 machine guard（mutants 也相同）。本輪 native 實測工具是 pinned Windows NDK LLVM；不宣稱 Linux／macOS native 工具已准入。未複製完整 vendor ROM，來源 candidate proof 與兩份已保留 references 的實讀由獨立 scope 提供。installed identity、原始完整 ABI、provider readiness、physical／OTA 全部未證明。
