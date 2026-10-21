# 四份保存 BOOT 的 W／S 回應差異

PASS：有限原opcode／source定位顯示 **ID2815會請求完整1026B W page echo**；ID2349、2492、2580的已查成功路徑仍請求empty W。這是實質資訊增益，能解釋原APK也許對應另一種BOOT回應形狀。沒有證明任一選項適用這顆硬體，也不建議選用或刷入任何一份。

四檔都來自先前已保存的catalog選項，檔名tag同為V1.0.00、長度12288B、數值分析base1000；相同tag與大小不是同product／board／binary證明。

| catalog ID | SHA256 | 已查W成功request |
|---|---|---|
| 2349 | `8aa3d7eeeeea1a05bd41917ef5c1e6404af670e296e04b72aa322e5634c91f4e` | n0／ptr0；`22D8/22DA`設定，`2352→2AE4` |
| 2492 | `2889084225f808f799e10aa65c6fe31e01a832eed0a1ae149c681088c8e38423` | n0／ptr0；同一組原PC |
| 2580 | `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb` | n0／ptr0；`2294/2296`設定，`230E→2AA0`；即先前保存BOOT |
| 2815 | `7d42d74eadcb675e2ae74836f4847f6f3ff334c9cfb269c72812578c7d40deaa` | n1026／ptr=aligned source-2；`23A0→29A0` |

ID2815在四次program返回、word readback全部相等後，`2310`將index高位準備到s5，`2314` SB高byte到s2-2，`2318` SB低byte到s2-1；`231C` a3=1026、`2320` a2=s2-2、`2324` command W，經`2328→238C`與epilog走`23A0→29A0`。其後29A0按nonnull pointer／nonzero length分流到既有sender。這裡echo的是live aligned source那1024B，加上新寫的BE16頁碼，與V4.1.60 Runtime的9B8E allocate／Flash-copy echo流程不同，不得共用實作細節。source RAM、overlap、saved registers、sender與實際發送仍有未知。

原APK固定接受一byte0或完整PageSize且Verify相等；因此2815的**request shape**可以符合完整頁分支，條件是實際transmitter保留該長度與bytes且內容相符。這不是已觀察到的ACK或更新完成。三份empty成功request則仍保留主protocol-review中的條件不匹配；本輪四個成功slice未見一byte0 W request，不宣稱全image不存在其他response路徑。

四份已查W都要求active、n1026，數值目的base08008000與unsigned start limit17F00給page0..95。所有數值只是原指令下的地址模型，不是物理Flash map保證。

四份S slice均以`uint8(n-1)`傳入length14 helper，檢mode1；成功後從stack還原原payload與原n給response helper，失敗清active並將原payload byte0改255。**沒有**V4.1.60 Runtime那種新建兩byte`[mode,1]` capability回應。因此原APK在普通15B S echo下不會因該式啟用額外Read，但2815本身的W fullpage echo可走W Verify分支。沒有比較或產生任何真UID值。

`review.json`逐份保留原bytes hash、W/S/helper的r2 rows、源PC、長度／index／目的地址常數與靜態control target。這是限定slice的比較，不是完整function／transport／resident／硬體閉合。沒有重跑75頁封裝、下載、選包、執行或模擬韌體、GATT發送、硬體或Flash操作。

重播只讀四份已保存BIN及封存主proof，僅寫本scope review.json：

```powershell
& 'C:/Users/locky/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -X utf8 -B apk-analysis/tsl9-v4160-ota-route-2026-10-21/boot-variants/review-variants.py
```

本輪新增的是「存在不同BOOT回應形狀」的證據；仍缺catalog product對應、原機installed BOOT身份、底層傳輸／ROM／Flash行為與硬體適用性。沒有可刷包、替代建議或OTA-ready結論。seal／一次readonly readback後停止寫入。
