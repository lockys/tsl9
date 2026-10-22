# 原 18F56 六位元組 helper 的局部 footprint

[English](readme.en.md)

**原函式18F56不會在正常靜態路徑上改寫 SP、S0 或 callback欄位 SP+68..71。** 它是完整50B／14指令的葉函式，沒有 nested／opaque call。這解除設定區分析中對這個特定 callee 的過度寬泛未知；不會把更早的 resident 呼叫、App設定初值或整體生命週期一併證明。

## 實際範圍與原始 byte

官方 ID2966 SHA256：`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，分析base8000。

| 區段 | 長度／指令 | SHA256 |
|---|---|---|
| helper18F56..18F88 |50B／14|`5ea71cc5060b528919272111556388a084fe65e49474efa62683825e4df2eedf`|
| caller19AAC..19AEE |66B／24|`747ccb507745f07b46289b7fb200480c46f79ff63e399ce44e72042ac4ca421c`|

初次實讀的既有 linked ELF SHA256為`6ab2e06720dc9f9ea4fa531836605fed6d3b8832a7dfa008d76bd9bd0a54f7b2`。其 `.text.tsl9v4160.direct_expansion_18f56` 是AX／PROGBITS、address18F56、size50、align2；真正 GLOBAL FUNC `__tsl9v4160_call_18f56` 同址／size50，原 BIN相應50B與 section完全相同。本輪不要求任何其他全image已被重建／驗證。

## helper 真正做的事

1. 18F56固定 A4=1FFFF000，18F5A READ32[A4+7E8]至A5。
2. 18F62／66／70／74依序 WRITE8 A0+0／1／2／3，值為第一個 word的低8／8..15／16..23／24..31 bits。
3. 18F78才 freshly READ32[A4+7EC]至A5；18F7C／82 WRITE8 A0+4／5，值為第二個word的低兩個byte。不是把所有來源預先快照後一次寫出。
4. 18F86 JALR rd0,RA,0，目標bit0清除；沒有寫RA。

完整函式只有 A3／A4／A5 被原碼寫入；A0、A1、A2、A6、A7、RA、SP、GP、TP與所有S暫存器沒有明確寫入。正常完成後 A3=第一個READ32值>>16，A4=1FFFF000，A5=第二個READ32值>>8。沒有 frame、內部分支、nested call或間接 provider。

這裡確認的是數值來源位址與位元組擷取，沒有讀取實體硬體的MAC／UID值，也不單憑函式名稱宣稱來源一定是IEEE MAC。若目的地或其他記憶體別名影響稍後來源讀取，必須保持上述先後順序。

## 呼叫者至 BLE init 的局部範圍

19AAC設A0=currentSP+8；19AB4是 JAL rd1→18F56，link=19AB8。helper沒有SP寫入，19AB8..19AEC亦沒有SP／S／GP寫入；其間沒有另一個opaque call。

19AB8設A4=SP+16，19ABA設indexA5=0，19ABC設limitA3=6。每次從SP+8+index LBU A2，先index+=1、A4+=1，再在19ACA SB A2,23(A4)，19ACE BNE index,6回到19ABE。因此六次目的地為 `SP+16+(i+1)+23`，即 **SP+40..45／config+24..29**；helper自身的六次目的地是SP+8..13。

本66B caller範圍另有19AAE SH SP+48..49與19AB2 SW SP+64..67，亦在原始欄位中完整列出。沒有任何其他store；上述三組明確 byte footprint皆不包含 **SP+68..71／config+52**。這是由已核對的常數、步幅與loop bound做的閉式整數推導，不是CPU狀態執行或ISA模擬。

19AD2..19AE0仍可能因原設定欄位不符合條件而進入self-loop，不能宣稱一定到達init。若分支通過，19AE2..19AEC用新的數值40000基底讀slotA4並以A0=SP+16呼叫；這個呼叫之後的效果不在此局部證明內。

## 條件與剩餘未知

局部論證以前述原碼／正常存取及返回、code不被data alias改寫、無非同步GPR／記憶體干擾為前提；數值地址不重疊也不量測實體RAM是否有鏡像或特殊硬體副作用。異常、fault、IRQ、任意code-as-data／實體alias仍不在完整ABI證明內。

本輪因此可以排除「這個leaf會呼叫未知ROM而改SP／S0或任意寫SP68」的籠統疑慮；**不能證明整個App配置實際為零、先前slot40048等呼叫的效果、已安裝resident或callback後續生命週期**。這些需要各自的來源證據，不能靠本函式名稱補足。

## 重跑

```sh
# Metadata／已封存依賴，不讀原BIN或ELF
python3 -B check.py --project-root ROOT

# 實讀兩個原碼區段並重跑四個byte operand反例
python3 -B check.py --project-root ROOT --firmware ID2966.bin

# 另核對實際helper section／symbol／50B，並非whole ELF來源重播
python3 -B check.py --project-root ROOT --firmware ID2966.bin --image-elf IMAGE.elf
```

預設 `metadata_only=true`、`actual_original_firmware_read=false`、`actual_helper_ELF_view_read=false`。顯式FW回報原碼實讀true；只有提供ELF才回報ELF view true。四個真實single-field byte反例分別改第六byte目的地、RET的來源GPR、caller SP+8偏移及copy目的地偏移，均被拒絕。資料與checker支援工作區 `apk-analysis/tsl9-*` 和交付 `analysis/*`；沒有歷史build硬依賴、compiler／HOST執行、target／ESIL／ISA執行模擬、硬體、網路或新BIN。
