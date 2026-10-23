# 下一個 provider：僅主函式102 B

[English](next-provider-contract.en.md) · [完整契約／raw CFG](next-provider-contract.json) · [原182 B視窗](next-provider.json)

官方V4.1.60主函式為`[12A08,12A6E)`，102 B／35指令，SHA256 `334494853a765e550af99f0e8dd95523efaf7cbb86d392e0340a5d5f004940c9`。fresh r2、原BIN與原視窗的前35 rows一致，所有直接控制目標／rd／RA另由raw encoding核對。局部CFG35 nodes／38 edges；在opaque calls返回其encoded RA的語法模型下全35 rows可達，不證路徑實際可行。

**182 B視窗不是單一函式。** `12A64 RET`之後的`12A66..12A6E`仍是主函式cold path；接下來`[12A6E,12AA0)`50 B及`[12AA0,12ABE)`30 B是另兩entry。不能把全部182 B當12A08重建，也不能在第一個RET截掉cold path。

| 範圍（end exclusive） | B | i | 分析切點 |
|---|---:|---:|---|
| `12A08..12A16` | 14 | 6 | frame_status_and_branch |
| `12A16..12A20` | 10 | 3 | status_zero_ID_fallback |
| `12A20..12A28` | 8 | 3 | predicate_index0 |
| `12A28..12A2E` | 6 | 2 | tag_split |
| `12A2E..12A50` | 34 | 10 | record_metadata_and_resident_copy |
| `12A50..12A5E` | 14 | 4 | peripheral_call |
| `12A5E..12A66` | 8 | 4 | fresh_restore_return |
| `12A66..12A6E` | 8 | 3 | post_RET_tagged_call |

入口SP−48、SW S0@[SP+40]、SW RA@[SP+44]，再S0=A0。`12A10→81AA`／RA12A14讀status；其原始6 B確為`LBU A0,167(GP); RET`，自身只寫A0。status非零直接往predicate；status為零才LHU[S0]並要求ID=1。`12A22→821E`／RA12A26先設A0=0，僅已知回A0=0就退出；完整callee／ABI仍未知。不得因看過部分prefix或舊版本名稱就稱為免打擾。

predicate通過後fresh LBU[then-live S0+11]。非零到cold block，A0=then-live S0、`12A68→16B7C`／RA12A6C後跳restore。零tag路徑依序fresh LHU ID／LBU length、SH0@[SP+20]、**SW32 ID@[SP+12]**、SB length@[SP+22]。沒有初始化SP+16..19，不能推成全零struct。

`LUI A5,0x40`加C.LW76得fresh pointer word `0x4004C`；`12A4E C.JALR A5`／RA12A50前A0=then-live SP+23、A1=then-live S0+3、A2=讀得byte length。此處未證memcpy、指標有效或callee保留ABI。返回後重新組A0=`0x40006400`、A1=**post-call then-live SP+12**，`12A5A→18CA4`／RA12A5E；A2沒有重載，仍是resident residue。

sole restore依序fresh LW RA@[SP+44]、LW S0@[SP+40]、SP+48、RET。A0沒有統一status回傳；821E、resident、18CA4、16B7C之後的S0／SP／GP／memory均不得套普通C ABI保留假設。主函式無自身GP或CSR指令；81AA另有已知GP+167讀取。

本段沒有長度上限檢查。A2最初讀0..255，destination argument SP+23與saved S0/RA@[SP+40/44]的關係可做有明示snapshot／copy假設的離線區間診斷；未知resident並不證明實際copy、更不證overflow或硬體結果。診斷也可顯示各gate結果與已寫metadata／未寫bytes，不能自動補值、宣稱CAN／座椅／免打擾或送出成功。

最小C重建應限102 B，讓C表達ID/tag/metadata/argument算式，保留明示frame／then-live／call／cold-return ports。81AA可參考現有6 B C component；821E／18CA4／16B7C仍留真正unknown providers，resident保持動態邊界。沒有target／ISA／ESIL／MMIO／硬體／網路／compiler執行、BIN或Git操作；`firmware_ready=false`。
