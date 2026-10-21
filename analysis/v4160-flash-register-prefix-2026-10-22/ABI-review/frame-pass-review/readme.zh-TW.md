# 來源自有 ABI frame 排序：獨立物件審查

凍結版排序工具通過本審查：**六次實際物件轉換、兩次完整連結見證、21 個實際物件防護反例及三種路徑別名拒絕**。C／C++ 的合併物件、獨立 IRQ main.o 與 Flash quarter.o 均涵蓋。[English](readme.en.md) · [简体中文](readme.zh-CN.md)

排序工具 SHA-256：`dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d`；policy：`2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d`。Native ABI 的原始 backend 診斷另封存在上一層，不由本 bundle 修改。

轉換只依宣告順序排列**新編譯物件中既有的 C.SWSP 指令**：IRQ 八個位元組、wrapper 六個位元組。全部其他物件位元組、section metadata、symbol 與 RELA 不變。沒有原始 BIN 作為轉換輸入、opcode 樣板、補洞或整函式 assembly。最終管線明確標為「C／C++ compiler + 來源自有 ABI scheduling」，不能說編譯器單獨產生該順序。

實際兩次連結後，IRQ144B／wrapper64B 整段等同原始機器碼；691 配置、15 LOAD、53 綁定、8,259 外部 RELA 及 20 個已知實際進入點的寬度／目的／RA 合約保留。這些見證使用先前已驗證的全映像 compiler 物件，以隔離排序步驟；不是本輪五個新 leaf 與排序器合併後的新全映像驗證。原始韌體只供事後比較，未生成 BIN。

21 個反例涵蓋錯誤 GPR／slot／64 位移／重疊槽位／寬度／frame、LOCAL 或非預設可見性 FUNC、大小、內部 symbol、RELA site／target、unwind、儲存別名、重複區段名稱、ELF 種類／program header／浮點旗標、空／重複選擇及重複套用，全部拒絕。input=output、input=receipt、output=receipt 皆在寫入前拒絕，來源未變。先前發現的函式 binding、路徑及區段名稱防護缺口已修正並重驗。

```sh
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/frame-pass-review/check_seal.py --project-root .
```

或 `sh .../review.sh --project-root . --replay .../report.json`。只讀重驗解析封存的 pre／post 物件、實際連結見證與回條，重做 pure plan、metadata／呼叫及 21 個位元組反例；不執行 linker 或寫入檔案。原本三次 API 路徑拒絕結果綁定於回條，重驗不重新呼叫寫入 API。`audit.py --report PATH` 則是另外的歷史 profile 生產器，會產生六組物件與兩個靜態 ELF；需要原有 compiler 產物與 linker。沒有執行 WSL／Git Bash；Shell 包裝僅靜態檢查。

工具的 prefix 形狀本身不能證明 C／C++ 出處，也未解碼任意物件中所有已解析分支。完整使用必須綁定來源、42TU 編譯命令、工具／policy、pre-object 及原始配置；本證據保留已核對的實際 pre-object 副本及其 compiler 回條雜湊。實際 IRQ／wrapper 內只有既知 JAL／RET，沒有直接分支回到保存區間。未知計算式內部進入點仍未排除；完整非返回／非同步、ROM、硬體及 OTA 成功均不由此證明。

本 seal 僅納入選定 report 的產物與列名成員；先前 preliminary／final-candidate 回條及其他未選定 build 目錄均排除。沒有目標執行、ISA 模擬、實體 I/O、網路或新韌體 BIN。
