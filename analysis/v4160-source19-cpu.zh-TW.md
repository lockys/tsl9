# v4.1.60：19-byte TX 來源的分段組裝、重設與保存條件

2026-11-26。接續 [provider 候選映射](v4160-provider-binding-ledger.zh-TW.md) 與 [TX 建構入口](v4160-tx13346-prefix-cpu.zh-TW.md)，本批追查 `D1A8` 返回的 `0x2000bf48`，沿原 APP 的 `D1B2` 三段組裝與 `D272` 清除入口，補上資料來源及必要保存條件。

輸入仍為 76800-byte decoded APP，基址 `8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。使用既有有限 RV32IMC 解譯器與合成 RAM，所有未知 provider 均在入口停止。下文的 copy／fill 寫入及正常返回均為明示前提；未執行 provider 本體、設備、CSR 或實際傳輸，亦不讀真實 ROM／RAM。

既有 `src/native/receive/record_field_transitions.c` 已保存這些原位址區段。本批增加原指令驗證及資料流說明，未修改既有 C、共享 CPU、原 BIN 或封存，也未增加 C 覆蓋率。

## 從實際 mode 1 ID 分派進入

原 `14D2E` 外層讀取 mode；mode 1 進入 ID 樹，讀 row 的 unsigned halfword ID。ID=1029 時，`15026..1502E` 恢復外層 S0、RA、SP，以原 row 指標尾跳 `D1B2`。

24 組案例從真正外層入口開始，使用 stage={0,1,2,255}、sub={16,17,18}、ready={0,1}，先驗證既有 ID 樹到尾跳，再接本次原 handler。這不是已安裝系統必然收到該記錄或完整 RX 至此的可達性證明。

令 B=`2000bf48`、S=`GP+236`；GP 使用原 reset 計算值 `20004000`，故 S=`200040ec`。以下 offset 及 sub 值均為十進位。

| 入口狀態 | 原 APP 判斷及動作 |
|---|---|
| B[0] 非零 | 不讀 S 或 row[3]，設 A0=1，尾跳 `12AD0`；該下游本體未展開。 |
| B[0]=0，S=0，row[3]=16 | 先寫 S=1，向 `[4004c]` 尾跳，請求 `(B+1,row+8,3)`。 |
| B[0]=0，S=1，row[3]=17 | 先寫 S=2，恢復本機 frame 後尾跳，請求 `(B+4,row+4,7)`。 |
| B[0]=0，S=2，row[3]=18 | 先寫 S=3，呼叫 `[4004c]`，請求 `(B+11,row+4,7)`；正常返回後才寫 B[0]。 |
| B[0]=0，其餘 stage/sub | 寫 S=0 後返回；不清除 B 的舊分段資料。S 不屬 0、1、2 時不讀 row[3]。 |

完整 256×256 stage/sub-byte 矩陣核對每一步資料存取順序、frame、參數與所有映射記憶體的寫入範圍。另 4080 組非零 ready 案例覆蓋全部 255 個非零 byte，確認短路行為。

handler 自身不讀 row 的長度 byte。測試保留合法 12-byte 合成 row，並使用長度 0 等值確認這個局部事實；不據此推定上游接收入口沒有長度檢查。

## 第三段的完成旗標有保存前提

前兩段在服務入口已恢復 caller frame，RA 為原 caller 返回位址；沒有本機 copy 後續段。第三段不同：服務入口 RA=`D250`、SP=入口 SP−16、live S0=1；原 caller S0 與 RA 已存入 frame。

`D250` 的原指令先把 **low8(live S0)** 寫到 B[0]，再恢復 saved RA、S0、SP 返回。正常路徑不檢查服務返回 A0，A0 原樣留給 caller。因此需要服務正常返回、保存 live S0=1、GP/SP 及 saved frame，才能得到 B[0]=1；不能只因參考 SDK ABI 或完成旗標而宣稱未知 installed provider 遵守此合約。

8 組 S0 探針使用 0、1、2、255、256、257、80000001、FFFFFFFF；marker 隨其低 byte 改變，saved caller S0 仍由 frame 恢復。另在第三段服務入口停住時，S 已是 3，而 B[0] 尚為 0。

測試也明示讓服務「完全不寫目的範圍，只正常返回且保存上述內容」。三段仍能走到 B[0]=1，證明完成旗標本身不足以證明資料寫入成功。這是對 APP 返回流程的條件性反例，並非聲稱實際服務會如此行為。

## 17-byte 分段資料與未重寫的最後一 byte

在每次服務只寫指定目的範圍的前提下，三段結果為：

| B 內偏移 | 來源／動作 |
|---|---|
| 0 | 第三段正常返回後，由原 APP 寫 live S0 的低 byte。 |
| 1..3 | 第一筆 row[8..10]，3 bytes。 |
| 4..10 | 第二筆 row[4..10]，7 bytes。 |
| 11..17 | 第三筆 row[4..10]，7 bytes。 |
| 18 | 此三段與完成 store 均不重寫，保留原值。 |

2048 組完整三段 fixture 為 256 種來源模式 × copy 有／無目的寫入 × 先行 fill 有／無 × 第三段 reply={0,FFFFFFFF}。各次重新載入不同的合成 slot target，核對新 target、完整 19 bytes 與兩側 canary；未把第一筆 row 當作之後兩筆來源。

最後接原 `133A6..133B4` caller 片段與真正 `D1A8` getter：以早先 TX prefix 已建立的 S0=40000、當前 SP 為明示入口上下文，確認請求 `(SP+60,B,19)`，RA=`133B4`。getter 與 caller 片段本身沒有讀這 19 bytes；本次在 copy 入口停止，並未重新執行完整 TX、transport 或 provider。

以上不能把偏移 18 命名為字串終止符，也不能把 17 bytes 命名為 VIN 或其他實體識別資料。

## 清除入口與 reset 的差異

`D272` 只讀 `[40048]`，尾跳參數 `(B,0,19)`；自身沒有清零 store，也沒有重設 S。768 組案例覆蓋全部 stage 與 ready={0,1,255}，確認原入口委派前的存取與保存行為。

若三段完成後 S=3，並另明示 fill 成功令 B 的 19 bytes 全為零，下一筆即使 row[3]=16，也先因 S=3 走重設 S=0 的返回路徑；再試一筆才進第一段。這個結果以 fill 不額外修改 S 的前提為限。

原 reset 的 `186AA..186B2` GP pair 可靜態算得 GP=20004000。本批另從原 `186DE` 清零迴圈入口，以該 GP 和完整可寫合成 span 執行，核對 8758 個 zero-word stores，精確覆蓋半開區間 `[20004080,2000c958)`，包含 B 的 19 bytes 及 S；兩側 word canary 保持原值。在 `186F8` 停止，未進 CSR 初始化。

這證明指定原 reset 迴圈在明示入口狀態、存取成功的前提下會清零兩者，不是完整啟動已完成或實機仍保留此值的證明。若以已完成 reset 為前提、且其後只有上表範圍的寫入，偏移 18 才可推得仍為零；本次沒有建立全 APP writer census。

## 重現

[test_v4160_source19_cpu.py](test_v4160_source19_cpu.py) 使用既有 `test_v4160_mode1_dispatch_cpu.py`、`test_v4160_feature_outer_cpu.py`、`test_v4160_zero_id_queue_cpu.py` 與原 APP，只需標準庫，不需要本地 SDK carrier 或網路。一般與 `-O` 模式相同，檢查使用 `check()`。

```text
python analysis/test_v4160_source19_cpu.py
python -O analysis/test_v4160_source19_cpu.py

PASS: original reset loop 8758 zero-word stores; 19-byte source and stage inside BSS; CSR boundary not entered
PASS: 65536 stage/sub-byte cases; 4080 nonzero-ready short-circuits
PASS: 2048 conditional three-fragment/TX-source chains; 24 real mode1 tails; 768 clear boundaries; 8 S0 contract probes
PASS: exact events/frame/memory; untouched byte18; 5 specified mutations; providers/hardware NOT executed
```

5 個原 BIN 記憶體副本 mutation 分別改第一段 count、第二段 destination、完成 marker offset、clear count、TX source count。均繞過 baseline 全檔 hash 的預檢，直接重跑指定路徑，由指定參數／存取檢查拒絕；不把解碼或 unmapped 錯誤當作偵測。

原區段 SHA-256，右界不含：

| 範圍 | SHA-256 |
|---|---|
| D1B2..D272 | `02af7bc6cee33d1d65a90b91166e2907366841edb48264cc6e7cb86be46fb84f` |
| D272..D288 | `170d96f02a7d7a07a74fd3be5cdfcf71749b4493dbc7b724d8ca2e210cadae61` |
| 133A6..133B4 | `b4876139bdf470ba3922890d33ba984619429e3aaf13a928dbf4d8c25c86dead` |
| 186DE..186F8 | `53e8753086d6a33d612f27e3f21393ac8c64e9603498c443023275973c3fa5a0` |

仍需追查 ready 非零後的 `12AD0`、其他可能寫入者與實際 provider 綁定／保存及目的寫入合約。另一個 TX 來源 `08077b00` 不在 APP 映射內；本批沒有取得其真實資料，也沒有執行 flash 寫入流程。
