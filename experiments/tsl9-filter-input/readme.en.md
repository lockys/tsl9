# 完整160B filter-input與258B native leaf

本目錄只做離線編譯、連結及資料核對。選用來源為 `src/filter_input.v2.c`、`src/filter_leaf.v2.c`；C11與C++17原位完整418B（139筆原始instruction）均與ID2966 V4.1.60原廠相同。compiled ELF兩語言相同，SHA256 `b4672228dedbba6199f12427ffeeeac6e712e67e81faac140ba1345b8d65a725`。

強入口為 `tsl9_channel_external_128fe`，其JAL綁到真實 `tsl9_filter_program_18ba2` provider。26個STT_FUNC是架構區域，**不是26個原廠或普通C ABI函式**。兩個原廠範圍為 `[128FE,1299E)`160B/60i、`[18BA2,18CA4)`258B/79i；leaf ret後可達cold blocks到18CA2均保留。C owns loads/stores/unsigned operations in the free bank; physical frame/S-register/SP/control ports are explicit. 沒有opcode-byte carrier、原廠bytes provider或global ABS provider。

`build/input-v2/{c,cpp}/measurement.json`保留完整命令、原始stdout/stderr logs、來源與物件hash；`build/leaf-v2/{c,cpp}/measurement.json`是獨立leaf的實際編譯證據。input.o仍有一個真正UND leaf symbol，最終由該語言的leaf.o強定義解析。原位linked graph零UND、26 strong FUNC、12個typed control relocations（input3+leaf9），不代表resident已閉合。

## 保留的原始語義與未知

128FE使用176B frame：RA172/S0 168/S1 164/S2 160/S3 156/S4 152；112B workspace在SP+32。incoming A0/A1先進S1/S0，1291E呼叫`[40048]`（expectedRA12920）；之後的cap用當下S0、source用當下S1、destination用當下SP+32。1293A呼叫`[4004C]`（expectedRA1293C）；之後才由當下SP重新決定workspace並初始化14輪狀態。沒有把入口長度或原本workspace當作跨resident不變量。

每輪4×u16左移5後截成u16，descriptor20B包含bank0..13/mode1/scale0/FIFO0/active1；JAL後branch使用實體當下S1/S2。leaf自身完整無S/SP寫入及callee，所以無fault/IRQ且正常返回時14輪局部可閉合；opaque transfer/stack/MMIO/lifetime/installed ROM仍未知。finish按當下SP逐一還原，A0殘值是descriptor指標，不是成功布林。

18BA2的讀寫結構與本機固定WCH CAN_FilterInit核心相符：CAN1 base40006400、FCTLR/FWR/FSCFGR/FMCFGR/FAFIFOR及bank FR1/FR2；SDK可選D6/D8 errata分支未出現在本body。支持內建CAN filter編程語義，不宣稱精確board/chip或實車結果。五條外接resident/helper依賴與16CC4的完整獨立報告已回傳主代理；16CC4及SPI helpers不是本實作的providers。

兩個opaque resident port 40048/4004C的身份、ABI、S-register/SP與記憶體效果均未證。沒有普通C ABI、普遍形式語意等價、完整啟動/IRQ、硬體/OTA或可執行韌體主張。未執行target、HOST模型、ISA模擬、網路或任何硬體操作；未產BIN，也未修改src/manifest/既有checker。

## 版本與失敗保留

- leaf-v1的C trial可編譯連結，但raw不等：base materialization破壞跨region A0，cold-block shift順序不同；外層builder還把local STT_FILE誤認ABS provider而中止，未完成C++。source、raw compiler/link logs、ELF與`build-leaf.v1.py`皆保留。見 `failed-trials.json`。
- leaf-v2在C operands/order加入明確約束並通過全部258B；C logic維持可讀。input-v1只是未編譯的初始命名來源；input-v2以主線canonical strong名稱完成首個編譯試作。
- 初版spec文件的leaf argv切片漏最後一個`-ffixed-x31`，實際compiler命令與ELF無變。修正metadata前副本保留為 `spec.metadata-v1.json`、`verification.metadata-v1.json`；最新spec包含全部實際flags。見 `metadata-correction.json`。

## 固定工具與重跑

使用USERPROFILE下現有Android NDK27.1.12297006 LLVM，builder先查既有tool/stdint/原廠BIN的SHA，不下載依賴。input使用既有queue-consumer/record A0..A5 fixed bank；leaf使用既有transport A0..A6。所有其他register包含RA/SP都ffixed。leaf builder與input builder均只允許新建trial目錄，既有trial不覆寫。

從repo根目錄執行（只編譯/讀物件，**不執行產物**）：

```powershell
python -B experiments/tsl9-filter-input/build-leaf.py --source src/filter_leaf.v2.c --trial fresh-leaf-check
python -B experiments/tsl9-filter-input/build-input.py --source src/filter_input.v2.c --trial fresh-input-check
python -B experiments/tsl9-filter-input/verify.py
```

input builder有意固定引用已測量的 `build/leaf-v2/{c,cpp}/leaf.o`，先查該物件及來源hash；fresh leaf trial只另證leaf的可重現性。全新本機尚無leaf-v2時，第一步需以`--trial leaf-v2`建立該選用物件。verification是現有input-v2的唯讀replay，另查actual ELF symbol/type/owner/range、typed relocations及原位全bytes；它沒有重跑compiler，也沒有結構負例集合或普遍語意證明。

## 可核對輸入

| 路徑 | SHA256 |
| --- | --- |
| `src/filter_input.v2.c` | `f8e5ae4b05abd72b2a5ec60c441effd06c5490b272c862ef435d2b2c3a37b547` |
| `src/filter_leaf.v2.c` | `bb2735ae1cb35abb4d80989625aa696bb006d0abe7e30d0c7e87ed8de7fc4ab6` |
| `build-input.py` | `30e431a2f80c6f3543a9d52797ad7403c4bf6bb62aa7bdae60de410dd5237ef3` |
| `build-leaf.py` | `0cb3d61e89e1f2de88859022f2d0727cf4ed000f474e1c1e544788f7fc784f90` |
| `verify.py` | `c0fc5a07ccfa83b9da2a0b96bce0295dca53312ee68b5a14f0abc0727ff5fda8` |
| `spec.json` | `d4b38a417d3c486ca1daa4929d3b993629ecff4e481a766737e6aa45f814ccd6` |
| `verification.json` | `238a3eb2942ba8395fba08685564a76260d99d8d1af297e92f3accf548771b11` |
| `original-listing.json` | `d14fc2d98a573842ce355065e8c9214de7b8bb82118a134a14436e7992215672` |
