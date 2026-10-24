# 原廠啟動C/C++實驗

[English](readme.en.md) · [分析結果](../../analysis/original-startup-2026-10-24/README.md)

選用來源：[boot_original.v1.c](src/boot_original.v1.c)，原樣整理至 [src/native/startup/boot_original.c](../../src/native/startup/boot_original.c)。原廠bytes、工具及來源雜湊固定於 [spec-v1.json](spec-v1.json)；[integration-v1.json](integration-v1.json)另固定真實初始化資料與objcopy，不更動先前trial證據。

[build-v1.py](build-v1.py)只編譯與檢查原生物件。[integrate-v1.py](integrate-v1.py)從真實C資料物件取出128B section，再以 [joined-v1.ld](joined-v1.ld)做unresolved部分連結。沒有配置假定的RAM／stack或偽造provider。

使用本機已安裝、雜湊符合規格的LLVM，並保留本次完整build目錄時，可唯讀重播：

~~~sh
python3 experiments/tsl9-original-startup/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-startup/build/trial-v1
python3 experiments/tsl9-original-startup/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-startup/build/component-v1
~~~

LLVM_BIN由執行者設定為實際LLVM bin目錄；Windows可使用已安裝的python。正式trial/build僅接受新的輸出目錄，避免覆蓋證據。原始收據依賴本機保留的完整產物；公開可攜式證據不能替代缺少的編譯產物或用來聲稱跨機重播成功。

來源比對收據為本機build/curated-source/original-startup-20261024-v1/verification.json：79檔、53單位、106組比對／212物件。前104組及625筆產物保持一致。當前manifest由精確的78檔父清單只新增一檔／一單位；[parent-manifest-v1.py](parent-manifest-v1.py)重建並核對父清單原始bytes。

本實驗不執行韌體、模擬ISA或產生BIN。完整原機啟動／ROM／向量／記憶體／OTA相容性尚未通過。
