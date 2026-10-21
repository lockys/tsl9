# 十二函式映像：獨立來源與建置追溯

[English](readme.en.md)

本輪檢查完整的離線 ID2966 V4.1.60 payload：其中12個 native 函式、共650 bytes 由可讀來源提供，其餘仍保留原始 carrier。這不代表已完整還原韌體原始碼，也不是通用 C ABI。native 來源仍受其暫存器、不透明呼叫及常駐 provider 條件限制。原始指令與 HOST 證據不變，本輪新增編譯／整合證據，不重跑未變動的 HOST 測試。

## 來源與處理鏈的邊界

`source-inputs.py` 獨立核對79份 native 專案檔：恰好是先前76份，加上 `page_reply.c`、`page_reply.h`、`reply_io.h`。native 依賴不包含 HOST adapter。檢查器從精確的 quoted assembly owner 範圍，獨立重建5份過濾 carrier：移除先前11個 typed owner；將 reply 儲存區換成原始零長度 AX boundary，保留 GLOBAL NOTYPE size0 及 local size0 入口角色，避免原始124 bytes 機器碼與新 C FUNC124 同時殘留。

來源／編譯處理鏈有兩個不同的順序調整階段：

1. 編譯34個 raw TU、9個 typed TU，另輸出9份對應 LLVM IR。reply 仍是只有一個配置區段的獨立 object；以限定的 reply ABI pass 處理 `reply.o`，只重新排列 compiler 已產生的指令，輸出 `reply-ordered.o`。
2. 先將其他8個 typed object 與已調整的 reply 合併，再透過 `canonical53.ld` 和 raw carrier 合併；最後才對完整 `pre-frame-integrated.o` 執行原有 IRQ／quarter 保存字順序調整，輸出 `source-integrated.o`。

boundary script 先放原始零長度 reply owner，再放真正 native reply input section。原公開符號維持 NOTYPE0；C 函式在同一入口提供另一個 GLOBAL FUNC124。原本私有空配置分支角色由實際編譯的本地控制流取代。原始 `9DF4` 的 `693b` 是 **RV32 C.JAL**，rd=x1、target9B8E、link9DF6；依據補充更正 seal `89992f1f7d8f98595b5e151d34479ef0876162d697087c8e562d72036472a34c`，不能只看 RVC_JUMP 重定位名稱就判斷為無連結跳轉。9BF8 的釋放呼叫仍是另一個不寫 link 的 T1 尾端轉移。

compiler body、typed-provider body、最終調整後 body 是不同的身分。manifest 中含 `native_object_sha256` 的欄位代表**函式 body bytes**，不是整份 ELF object；實際完整 object 雜湊另外放在 artifact pins。最終 payload 可以與原始 bytes 相同，中間 ELF metadata 仍可能合理不同；必須依角色規則核對，不能宣稱所有 object 逐位元組相同。

## 獨立實體建置追溯檢查

`provenance.py` 從已固定的8組 provider 及獨立 reply 來源重建精確 profile，再依順序核對61筆命令：59筆 compiler／query／link／export，加上2筆明確 Python `-B` 階段。每筆都核對來源、語言、ISA／ABI、旗標、強制 adapter、輸出角色、日誌及結束碼。產生流程不接受 BIN、舊 object 或將完整合併 object 交給 reply ordering；原始韌體只供參照／比較。

43個實際 object TU 均產生 `-MD` 依賴，包含 compiler resource header。實際專案依賴為74份既存輸入，加上14份產生輸入（5份 filter、9份 adapter），另有1份實際 Clang resource header。每份規則都綁定自己的 object target、第一個 primary source 及強制 adapter。專案外路徑必須位於實際 compiler resource directory，且符合 resource-relative header 雜湊；並核對查詢命令／日誌／工具，以及 header 前後身分。這是本次43筆編譯的實際 header 依賴，不是整個 toolchain 的檔案清單。

逐一讀取每個實際 raw carrier object，確認沒有 selected 機器碼 fallback。實際空 reply section 只能有精確的原始 NOTYPE／local 角色。這些來源檢查與另一份 ABI／LOAD／image 審查及製作者 replay 分開；不以製作者 `passed` 布林值替代獨立來源核對。

13個有限控制在記憶體內修改實際紀錄資料：10個命令／來源／profile／順序案例，加上3個 Make rule 的 target／primary／adapter 案例，包含將 raw reply.o 放入 typed merge、將完整 object 交給 reply ordering、顛倒必要階段順序、改編譯 HOST 來源、插入隱藏 response file，以及把 `-MD` 換成 `-MMD`。全部必須被拒絕。這些是**紀錄／規則控制，不是新編譯的語意 mutant**。本輪不重跑未變動的製作者87案例或獨立90案例 HOST 測試。

## 證據與執行限制

`selected-receipts.json` 保存最終選定收據的身分與實際結果。最終 C、C++ 收據（`23f9ac76…27d71`、`1904e97f…b0c18`）各固定223份 artifact 及41個製作者控制（30個 ELF／RELA／image、4個依賴、6個順序處理收據、1個命令先後順序）。兩者均通過本次獨立61命令／43 TU 追溯與13個有限控制、另一份 ABI／LOAD／image gate，以及製作者唯讀 replay。43份實際依賴規則中，有14份觀察到同一份 resource header。`results-c.json`、`results-cpp.json` 保留這些實體讀回報告。發布 seal 不包含產生的 build artifact。預設檢查目前來源、已封存參照及選定 metadata，明確回報沒有重新讀取實體 build 封存。指定實體收據時才讀取真正的編譯產物、依賴、object、IR及日誌，並呼叫製作者的唯讀 replay；不啟動目標程式或 compiler 命令。

預期76800 bytes 的離線 payload SHA256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。strict link 仍須因唯一缺少的 ROM provider 失敗；第二次連結僅提供明示的 ROM 數值位址 witness0x40000，沒有 ROM bytes 或常駐實作。完整裝置記憶體、已安裝 BOOT／ROM 身分、任意中斷／故障等價、硬體行為及 OTA 接受條件仍未確認。本輪沒有新增使用者功能，也不宣稱已可刷寫；沒有執行 RV32、ISA 模擬、BLE 流量或廠商請求。

## 可攜入口

由工作區根目錄執行；發布版改用 `analysis/v4160-reply-image-integration-2026-10-22`：

```sh
python3 -B apk-analysis/tsl9-v4160-reply-image-integration-2026-10-22/source-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

shell wrapper 接受相同參數，需要時設定 `PYTHON`。加上 `--receipt PATH/verification.json` 才檢查實際的目前 C 或 C++ build。預設 metadata 模式不需要封存的 Windows compiler／resource 目錄；實體封存 replay 則需要保留紀錄中的工具、header及實際產物，不能用來源檢查替代。
