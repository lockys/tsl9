# Callback 暫存器設定與 GP 精修的獨立審查

[English](readme.en.md) · [简体中文](readme.zh-CN.md)

本輪只使用一組新增設定 `-ffixed-x26 -ffixed-x27`，沒有旗標搜尋或重跑未變更的 HOST 演算法。已封存的 658B 基準、固定 S10／S11 的 656B 診斷及最終 fresh-GP 624B 元件分別保留；沒有覆寫舊證據。

獨立結果如下：

- 656B 有 240 條指令，S10／S11 在所有實際 rd／rs1／rs2 欄位均沒有出現。原先額外保存於 SP+0 的 S10 已移除；沒有用新的直接或衍生 SP 存取代替它。
- 新來源在六個原有使用位置讀取當下 GP，移除入口與各 opaque call 後的 GP 快照。最終624B 有223條指令、六個真實 GP 使用位置、沒有 GP 寫入；不再有16個 `MV reg,GP`。
- 六個位置分別是兩個工作位元組 LBU、GP 加 lane×4 後的連線 LHU、兩個 gate 的 A1＝GP+128、gate 後 GP+42 的半字讀取。實際後者為 LH，沒有被誤報成原指令 LHU 的物理暫存器等價。
- 新元件保持48B frame；11個保存與11個全新讀取的實際 register／slot 對應為 RA44、S0 40、S1 36、S2 32、S3 28、S4 24、S5 20、S6 16、S7 12、S8 8、S9 4，寬度均32。SP+0 沒有存取，沒有額外堆疊 spill 替代。這是已解碼語法與靜態位址來源的證據，不是任意硬體別名不存在的證明。
- 15個實際 opaque JALR 保持寫 RA（14個A5、1個A6）；IR 保留八個 raw argument read/write 綁定與原 caller-clobber。這些綁定不代表原始全部 scratch GPR 殘值皆相同。
- 所有223條 raw 指令欄位與獨立 LLVM 文字解讀一致。真實 ET_REL／ELF 都只有一個 GLOBAL FUNC624、沒有未解析提供者、額外配置、隱藏 helper 或 padding。五項編譯／IR／link／反組譯 recipe 與實際 MD 來源閉包另行核對。

`baselines.json` 是驗證用欄位／雜湊紀錄，不是程式產生輸入。一般檢查不需要歷史 Windows `.o` 或 ELF；`prepare-baselines.py` 僅供來源歷程稽核。

## 兩個既有保存指令的明示排序層

新函式範圍內的排序層僅交換編譯後624B函式 offset+2／+4 的兩個既有 C.SWSP。獨立審查確認只變更4個檔案位元組，其他 ELF 位元組、sections、symbols、RELAs 全部相同；再以正常 linker 連結後，完整 ELF 也只差這4個指令位元組。

這使 S0@40、RA@44 的相對保存順序符合原始 memory-store projection。原始函式先有4B的 SLLI A5 再開始保存；因此本層沒有還原完整 entry prefix，也沒有還原 resident 返回位址或所有實體 GPR。沒有已知直接跳入／call-return frontier 指向被交換的兩個字，未知計算跳入仍未排除。

五個 raw native 反例拒絕 reserved S10、SP0 spill、失去 RA 的 opaque call、gate 使用 cached S1 替代 GP、虛構 FUNC632。四個實際排序反例拒絕錯誤 slot、內部 mapping symbol、非空 REL section、額外非視窗位元組變更。兩種語言均完成實際產物檢查。

## 指令與證據層級

預設只驗證來源與封存中繼資料，不讀原 BIN、不讀編譯產物：

```sh
python -B ABI-review/check.py --project-root ROOT
```

實際 raw compiler 產物審查及唯讀重播：

```sh
python -B ABI-review/review.py --project-root ROOT --folder PRE_MODE --receipt RAW.json
python -B ABI-review/review.py --project-root ROOT --replay RAW.json
```

實際 compiler→排序→連結的完整審查與唯讀重播：

```sh
python -B ABI-review/review-ordered.py --project-root ROOT --pre PRE_MODE --folder ORDERED_MODE --receipt NEW.json
python -B ABI-review/review-ordered.py --project-root ROOT --replay NEW.json
```

`review.sh` 無參數走中繼資料檢查，其餘參數轉交 ordered review；`PYTHON` 可指定直譯器。收據應放在 producer 的 MODE 資料夾之外。預設明示 actual flags=false；實際模式明示真正讀取產物。封存只含來源與中繼資料，沒有編譯物件或 BIN。

## 尚未成立的主張

624≤632 只是數值尺寸容納，原區間最後8B仍沒有來源提供者，`whole632_storage_covered=false`。沒有將8B補為 padding、借用原 BIN、虛構 FUNC632 或採入完整映像。未知 resident 的實體 S／GP／SP 契約、scratch 殘值、改變的15個 RA offsets、所有 fault／interrupt 前綴、BOOT／OTA與硬體仍未獲證實。原 full ABI、placement、硬體／OTA flags 持續為 false。
