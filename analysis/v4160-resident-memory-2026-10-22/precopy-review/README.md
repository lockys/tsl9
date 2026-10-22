# 複製前的 200004BC 完整比較 leaf

[English](readme.en.md)

**在既有兩個候選、正常返回與明確無 alias／無非同步干擾等前提下，這個 callee 不會改 S1、SP 或設定區 +52。** 它不是未知 nested ROM 呼叫：完整62B／19指令只有比較讀取與MMIO寫入。這可解除初始化前綴中這一站的局部保存疑慮，不能推定已安裝 resident、App實際可達性或後續 callback生命週期。

## 原始來源與完整範圍

| 候選 | 初始 word-copy 映射的 Flash來源 | 分析RAM範圍 |
|---|---|---|
| V1.40 / carrier | 4076C..407AA |200004BC..200004FA|
| V1.31 / carrier-dec2023 |4072C..4076A|200004BC..200004FA|

兩份完整62B內容相同，SHA256 `39eff00fe85a0bdea780df359a1f1d1356681a168097a60b7b805faac6303581`。**不是在第一個RET就截斷**：第一RET為200004DE，後面仍有比較迴圈與第二條回傳1路徑，最後RET為200004F8。next body不在本輪範圍。

source ledger保存兩個完整19-row operand表與映射；候選完整segment／原HEX雜湊、resident-entry映射與原114B初始化前綴重用已封存 allocator-callback/callback-review。顯式檔案模式另讀官方 ID2966，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，比對其原308B配置函式與已封存 App來源。沒有下載、codegen、compiler、HOST或target執行。

## 比較與返回值

1. 先READ32 MMIO4002420C至A5、WRITE32 zero、FENCE.I，之後才判斷A0與A2。零長度／null也有這些MMIO請求，不能當作pure memcmp。
2. A0==0或A2==0時，將先前讀到的A5寫回MMIO，A0=0並RET。這不是「空集合全部相等回傳1」。
3. 非零路徑先A4=A0+A2（32-bit數值），迴圈先A0+=1，再LBU A3,-1(A0)，以 BNE A3,A1 比較。**A1是完整32-bit值，沒有截低8位**；A2也沒有u16/u8截斷。
4. 任一不相等就跳到共同的寫回／回傳0路徑。只有全部指定byte相等，才從第二個寫回路徑A0=1並RET。若A1含非零高24bits，非空有效比較的第一個LBU必不相等；不是拿A1低byte比較。

兩個return的數值皆明確0／1，不是標準memcmp的正負結果。長度與地址沒有一般overflow／可讀範圍保護；本輪呼叫者的6-byte情形仍須有效位址與正常存取前提。

## 寫入範圍、register與呼叫邊界

本62B只有三個SW instruction：MMIO+20C寫零，以及兩個互斥return路徑的先前word寫回。沒有stack、heap、config或payload store。MMIO寫回是原碼請求，不能宣稱硬體副作用被完全還原。

原碼GPR目的集合僅 **A0／A3／A4／A5**。A1、A2、A6、A7、S1、其他S、GP、TP、SP、RA沒有明確寫入；沒有frame、nestedcall、opaque edge，所有directbranch均在這個完整leaf內。正常return時A4=40024000、A5=entry MMIO READ32結果；進迴圈時A3保留最後LBU值，null／零長度時A3保持entry值。RA只用作RET目標，bit0由JALR清除。

這些是固定原碼的局部write-set／CFG條件，沒有執行CPU狀態或宣稱任意fault／IRQ／code-as-data情境相等。

## 真正的 caller 參數與分支

兩版本的原114B BLE初始化前綴已實讀並逐列比對舊封存欄位。其entry+1C將傳入config指標放入S1；+1A設A2=6，+1E設A1=255，+22令A0=config+24，+28/+2C實際AUIPC/JALR數值目標為200004BC。

正常有效的caller比較因此是config+24..29的六個byte是否**全部**為FF。return1後caller設A4=1、A5=3，於entry+34 BEQ跳至entry+D2（前綴外的失敗出口）；return0則續行。這裡只固定其目標／當下register值，不以未審epilogue宣稱完整初始化返回契約。

續行NV guards只讀liveS1+8、+56、+60；若對應callback缺少亦跳entry+D2，A5已設6。通過或跳過NV條件才到entry+46設定S0=20003000並發出64B fill／copy。這段guard沒有S1／SP／config store；比較leaf本身也不寫它們。因此若入口config+52有某值，該站正常返回及local NV guards不會改它。

既有46B fill leaf的無S／SP寫入證據重用舊 memset-review封存，本輪另核對其實際候選body雜湊；既有58B copy leaf由來源鏈保留。於適當live S0/S1、數值與實體stack／code／MMIO無不利alias、正常memory/MMIO返回、無非同步改寫及正確映射／ISA等條件下，可以把**既有的config+52值**帶入後續copy。不能只憑本輪宣稱該值一定零、App版本gate一定通過，或copy後永久不變。更後面的初始化邏輯與callback不在此scope。

## 重跑與反例

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT \
  --firmware ID2966.bin --candidate-root EXISTING_WCH_REFERENCE
```

預設metadata_only=true、actual_candidate_leaf_bodies_read=0，核對封存來源與已保留operand，不讀候選。兩個參數同時提供才回報actual原FW=true、leaf bodies=2、caller prefixes=2、existing fill bodies rechecked=2。四個實際single-field byte反例／候選，共八個：null gate來源GPR、完整A1比較GPR、成功結果1、caller期待值255；全部被拒絕，不是合成ISA執行。

支援W `apk-analysis/tsl9-*`與交付`analysis/*`，不依賴歷史build；`capture.py`只create-only保存來源資料。已安裝身分、完整ABI、整段初始化continuation、原App可達性、callback當前值／生命週期及OTA仍未證明。沒有新BIN、網路、硬體或UID資料讀取／傳送。
