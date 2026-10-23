# 821E record predicate：原始契約

[English](next-821e-contract.en.md) · [15 rows／完整CFG](next-821e-contract.json)

官方ID2966 V4.1.60主範圍為`[821E,8248)`，42 B／15指令，SHA256 `4af30f18b196e304a5b6d30bb167ee2a02c567c4ffcf4e36bb4f72e6204bcdcd`。fresh r2與原BIN逐byte相符；local CFG為15 nodes／16 edges，唯一RET8246，全部rows語法可達。本函式沒有call、frame、CSR或RET後cold block。

180 B視窗`[821E,82D2)`並非單一函式：依序為821E..8248（42 B／15i）、8248..828C（68 B／26i）、828C..829E（18 B／5i）、829E..82A8（10 B／3i）、82A8..82D2（42 B／16i）。8248的call/tail與cold returns、82A8的directional resident-tail都不屬於821E。前方820C..821E clear及後方82D2 filter是不同已知邊界。

原式依序是：LW[GP+84]得pointer，LBU[pointer+4]得config；A5=0，A4=config&8。bit3非零就回0。否則A4=2、再次A5=0，使用unsigned full32 index>2判斷；超界回0。通過後fresh GP+192+index，再LBU **+1**，因此state位置是**GP+193+index**。SLTIU byte,3轉成0/1，MV A0=A5後RET。

輸出residue也屬契約：config-bit路徑A4=8；其他路徑A4=2；所有正常返回A5=A0=0/1。自身只寫A0/A4/A5，沒有memory store，不改GP/SP/RA/S-registers。這是15條raw指令的效果，不是普通C ABI假設。GP數值、pointer有效性與IRQ/fault等仍未知。

**config pointer與byte讀取先於index guard。** 不能因index>2就省掉這兩次讀取；也不能先把index縮成byte。state是unsigned byte<3，不能用signed char比較或誤用GP+192。12A22 caller設A0=0，所以正常路徑index gate已滿足；bit3clear後讀GP+193。此leaf的own code不改caller的S0/SP，但沒有因此證明其他callee保留。

可讀C可以承擔volatile reads、bit mask、unsigned條件與0/1結果；fresh GP／固定A0/A4/A5 ports保留實體register與incidental residue。後續實測需保留兩個LI A5,0、read order、late GP sample與15typed rows，並證明無額外frame/call/UND。此契約沒有編譯或宣稱native完成。

只能稱為config/state eligibility predicate；不能由舊版本或相似algebra直接命名為座椅／免打擾／CAN功能。離線診斷需分開顯示config、index、state的known/unknown，不能把讀取失敗當disabled。未執行target／ISA／ESIL／硬體／網路／compiler／Git；`firmware_ready=false`。
