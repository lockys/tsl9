# 回覆物件與保存槽的獨立審查

[English](readme.en.md)

原530B與已交付568B的共同七個保存位置其實相同：RA44、S040、S136、S232、S328、S424、S520。原保存順序為S0、S2、RA、S1、S3、S4、S5；568B則為RA、S0、S1、S2、S3、S4、S5，另加S6@16、S7@12、S8@8。兩者都減SP48，保存次序及額外寫入仍不同。

原回覆是liveSP+12/+13。568B真實獨立volatile兩byte物件在SP+6/+7；最終新候選556B／188指令保留48B frame，移除S8保存／恢復對，物件在SP+10/+11，未借用保存區。它仍保存S7@12，因此不能直接將指標強制改到SP+12。

若共同入口SP為E、frame大小為F、回覆offset為R，原指標為E−36，數值匹配條件是R−F=−36。568B為−42，556B為−38。這個條件不要求所有候選都使用48B frame或字面SP12；例如較大frame可能以其他R形成同一地址，但保存槽、物件生命週期、對齊與callee契約仍需實證。

即使數值相同也不充分：假設savedS7為A1B2C3D4，在SP12/13寫05/01，該word就成A1B20105。正常epilogue若照原slot讀回，會損毀caller的S7。這只是little-endian storage overlap代數，沒有執行指令。若要借用保存區，必須有另一個真實不重疊的備份與所有適用出口復原證據；不能把spill bytes冒充獨立回覆物件。

原14094呼叫前A3取liveS2、A2取liveS0、A0取liveS1、A1保留command。返回14098後caller立即從其192B frame恢復RA/S0/S1/S2/S3再RET，沒有本地A0判斷，也不恢復S7。因此不能以「眼前caller沒讀S7」認定它已dead。

UID comparator在length!=14時直接回1、不建frame；有效路徑有自己的32B frame和16B builder frame。已確認的App本地程式並不直接把handler回覆指標當UID資料。它仍經過opaque ROM及fresh stack reads；不能假定未知callee保存S/SP/GP，或不窺視caller frame。原9D96在UID前用S1=1寫回覆，9DA6則用post-UID liveS1寫active；原生普通C的寄存器配置不自動重建這些physical契約。

候選唯一來源差異是quarter call之後`buffer=OH_QUARTER_OFFSET(buffer)`：HOST為uint32 identity，native為空的read/write寄存器asm。header、全部8-register opaque橋、memory clobber、provider效果順序不變。沒有第三個profile或HOST重跑。淨減12B與一對保存槽是實際codegen結果，並未修復numeric pointer契約或准入完整ABI。

本審查唯讀核對D/P C/C++四個既有568B物件與最終C/C++556B候選、原169個handler operands、24B caller及122B UID來源。兩個actual ELF反例拒絕強制SP12覆寫savedS7及錯誤S7恢復槽。560B第一個假設只是未改善frame的歷史證據，不列為當前來源。

```sh
python -B frame-review/check.py --project-root ROOT
python -B frame-review/review.py --project-root ROOT --firmware FW --folder MODE --receipt NEW.json --controls
python -B frame-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

預設只查封存metadata與source delta，不讀FW/generated物件。Actual模式要求明確FW、folder與create-only收據；replay唯讀、不重建反例。沒有link、新BIN、目標CPU/ISA執行或硬體測試。新556B沒有整合進既有來源接線BIN。完整frame lifetime、physical S/SP/GP/RA、未知callback、alias、IRQ/fault及OTA相容性均未證明。
