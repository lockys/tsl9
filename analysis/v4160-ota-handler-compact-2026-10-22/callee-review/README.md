# UID callee：App 已確認與 resident 候選條件

[English](readme.en.md)

本審查只讀官方 ID2966 的 `92BA..9334`（56B builder＋66B comparator、48條指令），以及兩份既有公開SDK候選的 slot4004C 所指58B leaf。未編譯或執行HOST，沒有執行／模擬RV32、接觸硬體、下載或連網，也沒有讀取／傳送真實晶片UID。

`contracts.json` 區分三層證據：**App原始位元組已確認、兩候選局部實作有條件成立、原機installed identity與transitive ABI仍未知**。這不能授權縮減目前的full8呼叫bridge。

## 已確認 App

92F2先比較完整A1是否等於14，不符直接A0=1／RET，沒有frame。此路徑仍保留A1..A4/A6/A7及S/GP/SP的入口值；不讀某值不代表可以破壞其返回時的preservation。

長度相符才配置32B frame、保存S0與RA、將A0=目前SP，透過9302 **C.JAL** 到92BA（RA9304）。builder配置16B frame並依原順序保存S1/S0/S2/RA。92C2先讀取第一個slot目標，時點甚至早於後面的S0/S2/RA保存，不能任意重排其fault／alias prefix。

| 邊界 | 直接原碼要求 |
|---|---|
| 92D6第一次copy | A0=entry目的、A1=1FFFF7EC、A2=8、A5=READ32(4004C)；A3/A4/A6/A7仍是ambient。JALR link92D8。 |
| 92F0第二次copy | 92D8先以post-call liveS0+7E8形成A1；92DE另以liveS1+4C新讀target到T1；A0=liveS2+8、A2=6。S0/RA/S1/S2各自從liveSP fresh讀回，SP+=16，再JR T1。A3..A7為第一callee留下的值，A5不是第二target。 |
| 9308比較迴圈 | builder返回後index=0、A3=14；先LBU liveS0+index的輸入byte，再LBU currentSP+index的建構byte。首個不等回1，全14相等回0；不是標準memcmp符號語義，也沒有valid-length下的NULL guard。 |
| 9324返回 | fresh讀currentSP+28的RA、+24的S0，SP+=32，再JR RA；任意opaque SP/frame修改不能被稱為無條件恢復。 |

App並未自行讀A6/A7，也沒有直接GP存取；但builder進入不明resident，且fast path本身有ambient preservation。**不能只靠這122B的局部read-set，就丟掉額外參數／暫存器約束。** 第二slot必須保持fresh load；alias、resident寫入或其他變化可能使它不同於第一個。

## 兩候選的有限結論

既有封存的startup mapping分別將V1.40 flash405E2、V1.31 flash405A2對應到RAM20000332。兩份捕獲slot4004C都存20000332，映射後的 `[20000332,2000036C)` 共58B／18條指令完全相同：SHA256 `558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36`。每份來源都重新讀取；同一段位元組僅需一份欄位解碼。沒有把後續word-copy函式納入，也沒有擴大ROM分析。

此leaf先LW 4002420C到A4、SW0、FENCE.I，**之後**才檢查destination／source是否NULL與length是否0。正常／early return都先將保存的A4寫回MMIO。正長度copy為forward逐byte，LBU來源在SB目的之前，index於store之前增加；沒有memmove或wrap／fault保護。

這58B本體只需A0/A1/A2及控制link RA，沒有nested call、S/GP/SP/RA或A7的明示寫入。A0/A1/A2不變，因此A0正常返回仍是destination，**不是布林成功碼**。A3/A4/A5/A6可能改變。此段不需要Xwchc解碼；仍必須假設正確candidate已安裝、RAM映射／指令可見性／標準指令、MMIO與所有memory/return成功，且沒有非同步干擾。這些條件不等於已測量TSL9原機resident。

## 重跑與停止範圍

```sh
# 只檢查封存／pin metadata，不讀官方BIN或外部候選body
python3 -B check.py --project-root ROOT

# 實際讀官方App與兩候選來源，重解48+18列及6個單欄位operand反例
python3 -B check.py --project-root ROOT --firmware OFFICIAL_BIN \
  --candidate-root EXISTING_WCH_REFERENCE

# 可再加：--original-object ACTUAL_PREVIOUS_APP_CARRIER.o
```

預設 `metadata_only=true`、`actual_original_firmware_read=false`、`actual_candidate_source_bodies_read=0`。明確傳firmware才實際讀App與兩候選，回報上述旗標true／2；不需要W歷史build，除非自己要求額外object回讀。checker同時辨識 `apk-analysis/tsl9-` 與交付版 `analysis/` 的既有證據位置。

6個小型raw反例分別改UID14、builder link、第二slot live base、尾部length6、候選MMIO restore來源及copy來源byte目的暫存器；只做欄位解碼與比較。`app-llvm.txt`是實際LLVM靜態視圖，`candidate-static-display.json`只保留r2的位址／bytes／opcode，沒有使用或執行ESIL。證據只到這兩個候選leaf，`installed_resident_identity_proved=false`、`dropping_ambient_args_authorized=false`、`transitive_original_ABI_proved=false`。
