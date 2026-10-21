# ID2966：71個直接入口、可達片段與局部分派閉包

重做：`python verify-extension.py --spec evidence/direct-expansion-integration.json`。來源只用ID2966／伺服器標籤V4.1.60，76800B，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。C11／C++17加RV32 inline assembly保存原指令及語意引用；不是完整原始C型別或ABI的還原。

## 本輪新增的範圍

以前一frontier階段的71個 `call_*` UND入口為根，全部納入有限CFG；另核原名為opaque地址的引用用途，但不憑名字猜物件型別。本輪新增4932B可達code、73個物理片段、71個entry-fragment FUNC labels及311筆重定位。68份既有入口盤點為起點，另對18F56／19106／19B56三入口重新作raw bits與r2核對；8520再加入獨立證明的局部計算分派邊與62B指令。

這71個是前一階段的入口清單，**不是整份韌體的全部函式**。FUNC的st_size僅涵蓋entry所在的實際片段，不表示已證原始邏輯函式完整extent、原型或外部callee實作。所有cold片段只配置一次，沒有用整段span或補零隱藏未走訪bytes。

| 特殊入口 | 實際捕獲 | 明示界限 |
|---|---|---|
| 8520 | 8520..85C8，共168B／55指令 | 其中855A..8598的62B由有限分派證明可達；沒有猜填hole |
| 12B24 | entry12B24..12B58的52B；cold12B7A..12B82的8B | 中間34B不配置；FUNC size只取52B |
| 14D2E | entry14D2E..14D52的36B；cold1549A..154A6的12B | 中間1864B不配置；FUNC size只取36B |

另外68個入口各有一個連續物理片段；連續不等於對外依賴已閉合。有外出直接分支的15個root保留其目標身份與真正UND或實際既有provider，沒有把外出edge當作已知return。

## 8520的兩個有限計算跳轉

原bits建立t1=15。抵達854A的三條本地incoming路徑分別有unsigned<=15或AND15的限制，因此a2域為0..15。8550的AUIPC立即數為0，8556的JR目標為 `855A+4*(15-a2)`，16個合法指令入口；a2=0直接落到8596的RET。

另一條路徑先有a5=destination&15且a5!=0，所以a5為1..15。85AE的AUIPC同樣只取得原PC，85B6的JALR目標為 `8556+4*a5`，15個SB入口。62B區段內只有15個4B的 `SB a1,offset(a4)`（offset14降到0）及2B的RET。在此local-call context，RA=85BA；SB串不改a1/a4/t0/t1/a5/ra，RET返回85BA後才以t0恢復舊RA。第一個JR不設新link，不能把兩種RET context混為一談。

這是固定image、由8520 entry進入的局部raw-field／bitvector域證明；不是CPU執行、任意外部entry、interrupt ABI或destination安全性的證明。數值操作符合byte-fill helper模式，但沒有宣告原libc原型、可寫記憶體範圍或MMIO相容性。獨立checker拒絕5個raw mutation及9個越界domain反例。

兩個AUIPC各保留self-anchor HI20，沒有虛構LOW companion；它們與64組正常AUIPC／own-LOW pairs分開核對。311筆新RELA＝181個直接控制引用＋128筆正常pair引用＋2筆self-HI。36筆非零addend只引用既有真RAM carrier的interior offset；carrier仍是單一35160B OBJECT／NOBITS，十個既有NOTYPE0 RAM views維持其原身份，沒有新增RAM值或配置。

## 整合與仍未解的部分

本輪composite spec仍用凍結core-flow建置基線，帶入原callback、readonly、frontier三個未修改module及新direct-expansion module。舊generic verifier及舊spec不變；不帶 `--spec` 仍只驗舊core-flow。獨立審查另對前一frontier實際物件的全部storage、global／local views與587筆semantic RELA multiset作保留比較。

目前整合12000B code、459B RO、898筆RELA、136個allocations；27個RAM views及原35160B NOBITS保持。composite modules有95個exported providers，其中24個來自前一層，不重複計為本輪新增。C/C++靜態編譯與原位逐byte核對不等於原機可執行。

嚴格最終連結仍拒絕69個UND／69個不同數值位址：44個call名稱的直接entry身份、21個尚無直接code用途的opaque身份、三個保留address名稱而兼有直接code用途的身份、ROM40000。三個mixed用途地址為13346／17666／197B8；13346在本輪先取址後被直接控制引用，178EA→17666與19BA8→197B8也有直接控制證據。它們本輪尚無body provider；不能按 `address_*` 前綴一律稱為pure opaque，也不能只憑取址替其他地址宣告callback ABI。ROM40000另有直接控制用途，因來源／ABI未知而單列；ordinary code body候選為47個，若含ROM則48個UND身份出現在direct-control RELA中。

已捕獲code共有138個間接callsite與34個非RET間接tail/jump site；其中8520的兩個local target domains已有限證明，其餘目標域未全部閉合。原先記錄的exact runtime pointer value仍未觀察；已知有限domain與已知單一實際runtime值是不同結論。

1AAE8的首次table read在mod7／寫回之前；從該local u8讀取只能得0..255域，保守需要1024B，而現有image從1AAE8到末尾僅280B。因此不以「後續有mod7」猜成7筆表、不填尾段，也不借其他版本bytes。這是尚未證明的讀取閉包，不證明實際硬體一定越界。

來源、negative fixtures、獨立dispatch／address審查與交付收據位於 `../../analysis/v4160-direct-expansion-2026-10-20/`。其中 `destination-verification.json` 確認目的地fresh編譯、舊檔保留，以及actual merged／numeric-witness與已獨立審閱W產物的SHA一致。

數值witness只為核對地址與bytes；未提供缺失程式／資料，不可執行或燒錄。實體晶片／PCB、BOOT／resident ROM、記憶體／stack／IRQ契約、完整功能及原BLE OTA相容性均未達成驗證。沒有執行／模擬RV32、網路請求、接觸硬體或刷寫；未產出可燒錄的重建BIN，原完整goal仍未完成。
