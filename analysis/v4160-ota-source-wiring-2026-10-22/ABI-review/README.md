# 真實C來源入口接線的獨立檢查

[English](readme.en.md)

這份審查驗證實際來源、ELF及實驗BIN的接線，沒有宣稱韌體可燒錄。新入口是與既有568B共享C核心同一翻譯單元內產生的strong FUNC alias，並非ABS地址或假函式。

標準objcopy只在基底副本把舊`__tsl9v4160_ota_code_9c4a`由GLOBAL NOTYPE改成WEAK NOTYPE。全部691配置區、8261RELA與其他符號保持；原9C4A的530B程式仍在原位。Partial link合併真C與明確非執行FF資料，形成693配置區、8281RELA，九個callee／callback符號均綁向真實配置區。只有ROM入口仍為真正UND。

最終數值地址見證將真C置於1AC00，兩個真FUNC568符號指向同一配置區／程式；實際14094的JAL為rd1→1AC00，RA仍是14098。所有原始配置位址與內容保持，只有該caller的四byte指令字可改。新77824B實驗BIN由原76800B、568B實際linkedC與456B非執行FF填充組成，全部section bytes與flat image逐byte相等；新增填充不是可執行NOP或借用原始程式。

另外逐項檢查完整RELA合併、20個新C重定位的opcode／rd／target／HI20／LO12、全部普通符號及metadata角色。兩個新attributes mapping轉為非provider ABS、兩個新SECTION角色均由真物件推導；excluded addrsig為舊58B加新4B，最終丟棄。既有link規則丟棄comment與SECTION metadata，保留FILE／程式mapping／ISA attributes；這些差異被明列。

來源證據包含全11個真實compile／IR／objcopy／partial／strict link／address witness／extract指令、MD的四個project檔及真實stdint資源、工具和來源hash、單一C定義與真alias IR、193指令及完整8-register opaque橋。演算法與HOST核心沒有改變，不重跑HOST。

實讀官方ID2966：18730原始`6f70120d`是rd0→40000，來源reset186AA+134的唯一ROM relocation仍是真UND。沒有ROM提供者時，strict link應失敗且不產ELF。最終`ADDRESS-WITNESS-ONLY`僅將該符號設為ABS40000，以核對數值地址；它不包含實機ROM，也不是provider closure證明。

九個實際ELF反例針對假ABS alias、未weak、遺失C配置、caller不寫RA、錯目標、錯callback HI20、改動其他原始byte、可執行填充及假ROM provider；必須由預期語義檢查拒絕。反例只寫本scope的build目錄，不修改producer檔案。

```sh
python -B ABI-review/check.py --project-root ROOT
python -B ABI-review/review.py --project-root ROOT --folder MODE --firmware FW --receipt NEW.json --controls
python -B ABI-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

預設`check.py`只讀來源與封存metadata，明示不讀generated image或FW。`review.py`必須明確提供真實folder和官方FW，收據create-only且位於producer folder外；replay只讀既有實物，不重新建立反例或編譯。`--prototype`僅診斷早期物件，不是正式選定收據。Shell wrapper可用`PYTHON`指定Python。

這只證明記錄中的caller已接到C來源。未知computed入口可能仍進舊530B；並未證明所有執行路徑已改用C。Physical S/SP／暫存器、reply指標逃逸、opaque ROM、IRQ／fault／非同步、實際Flash/NV所有權、installed BOOT、CRC／簽章／復原與OTA契約仍未准入。相同RA只是其中一個已核對投影。1AC00是數值layout選擇，不能據此宣稱存在空閒21頁。

封存只含來源及結果metadata，generated build／物件／ELF／BIN不包含在內。正式結果與來源pin見`selected.json`及`reference-pins.json`。
