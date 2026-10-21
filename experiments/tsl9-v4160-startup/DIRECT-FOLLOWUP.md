# ID2966：後續入口與253項有限分派

本輪僅依76800B的ID2966／server V4.1.60 image，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。C11與C++17透過RV32 inline assembly保留實際指令及符號引用；未恢復原作者高階程式、完整函式邊界或C ABI。伺服器版本標籤不是實體TSL9硬體相容證據。

## 實際捕獲範圍

原49個直接UND入口的reachable union為3616B；扣除舊AD48 storage112B，新增3504B／50個code fragments。共享90B只配置一次，未訪問holes不補零。另追查D810、954E、95BC與FE08，共300B／4個必要fragment；各原地址身份保留NOTYPE,size0，另有captured_body FUNC helper，不把helper extent稱為原完整函式。

15630先將索引限制為u8，15634／15638以unsigned guard保留0..252。1563C／15640取1A6F4表址，scale4／LW／add-base後於1564E分派。253項共1012B，174個不同目標；續查必要case新增3408B／2個fragments，原1578C..15798的12B與49入口共用一次。該表範圍為[1A6F4,1AAE8)，不解決下一張1AAE8表的索引生命週期或缺失744B。

每個relative word由初值0及同址一筆ADD32、一筆SUB32表示；253項原位結果逐字相符。不能以原delta作初值後再次加減，也不能以抵消pair掩蓋額外RELA。四個有限literal carriers為19EA8／19EB8／19EC8各16B、1AB50為8B，共56B；其範圍只代表已證consumer reads，不代表原完整資料物件。

## 重用與配置限制

舊`.text.tsl9v4160.direct_successors_ad48`保留112B、flagsAX及真GLOBAL FUNC `__tsl9v4160_call_ad48`，size112。SHA256 `87727e2593048c5727caca62e73faf5af795ca163ae95be9cd882d8ebbbb5832`。其26筆RELA完整保留，不在新module重發。原ADD2的raw `9dbf`是C.J→AD48，以真重定位引用舊provider；先前可能fallthrough的假說已被原指令否證。

另有真1578A→1578C fallthrough（raw `6dd5`），必須保持原VA相鄰。原有固定配置契約亦保留，不能宣稱整個程式可任意搬移。FD6A新增的是舊54B程式區段內的NOTYPE0 view，以原CFG指令邊界`8d47`為證，不新增storage，也不以ABS冒充實作；原12B7A view不變。

AB02、137C0、D810、954E、95BC、FE08六個地址身份保持NOTYPE0；其body helpers分開命名。五個RO地址views同樣保持NOTYPE0，OBJECT carriers另行命名。新module不配置RAM，也不宣稱提供runtime pointer值。

## 編譯與實際產物

新增7212B code＋1068B RO＝8280B，共61個physical sections（56code／5RO）；69個新globals＝53FUNC＋5OBJECT＋11NOTYPE。新增1129筆RELA＝473control＋150正常PCREL（75pairs）＋506relative32（253pairs）。

整合49562B code＋2688B RO＝52250B file payload，453個非空allocations（452file-backed及原35160B NOBITS RAM），5765筆RELA。434個module providers，另計兩個existing-code views；528個relative32 expressions。原27個RAM views保留。

ROOT receipt：`build/table-extension-fbd62902b4e24698974e11070d800cfb/verification.json`，SHA256 `6dbec284574b0cc03d3ec089e9220c4f5b96a5ce49e385f1a2cc2674594e3f25`。C11／C++17 merged object相同，SHA256 `5d6b36e2c1ea29d3749b8e556f3f582ff8fff26499c5124ced31c0d8ab475524`；numeric witness SHA256 `1843d86caef9a8d632cd7f2201ae90d33a021c7bedac6242e32394125ee8b867`。Witness僅核對數字與原bytes，不是缺失實作或韌體。

Standalone final receipt：`native/build/01d15821c2d6452c836791c55dd30dea/verification.json`，SHA256 `d82dbd01bfc88d3c9ba586bf826a5c727c3daeeadf00b18d362c6d7391138bc4`，每語言27個actual negative fixtures均被拒。反例涵蓋控制與own-LOW引用、relative初值／運算元／RELA multiplicity、NOTYPE身份變更、ABS假provider、未證零填及FD6A view型別突變。嚴格standalone連結拒絕148UND；整合後仍拒絕145真UND，按actual RELA用途為82 direct-only、60 materialized-only、兩個mixed（1552A／EDF2）及ROM1。不能將符號數當作功能完成率。

目前captured raw instructions共有177個indirect calls、54個non-return indirect tails及368個RA returns。這些是靜態site數，不是已知callee實作或實際執行次數；有限域證明另計，不將所有間接轉移視為已閉合。

獨立審查檢查舊392配置、全部global／local identities及4636筆舊semantic RELA，並重新掃描目前已知direct及有限computed入邊。最終結果見目的地`../../analysis/v4160-direct-followup-2026-10-20/integration-review/review.json`及`destination-verification.json`，後者另記fresh D編譯、hash readback與舊檔保護。

## 仍需完成的目標

新捕獲內尚有9506 incoming callback、137E6 ROM40048、13926／139E8 ROM4004C、1733C ROM40050五個未知間接site；其他既有runtime／IRQ義務也未解除。253項有限域不能證任意callback入口或未知ROM writer安全。

1AAE8的首次索引、alias、完整extent仍未證；缺744B不補零、不借其他版本。使用者目前無法讀晶片印字，MCU／PCB、BOOT／ROM ABI、實體記憶體／stack／IRQ、必要功能完整性及原藍牙OTA封裝／接受條件均須進一步證據。

本輪純離線，不執行或模擬RV32，不連硬體，不刷寫；`target_ready`、`native_bin`與`ota_verified`保持false，完整goal未完成。
