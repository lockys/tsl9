# TSL9 reverse engineering

[繁體中文](README.md) · [简体中文](readme.zh-CN.md)

Study Feifan TSL9 firmware and Bluetooth OTA, rebuilding its features and native execution layer in C/C++ for the original hardware.

**No rebuilt BIN has passed full flashability validation.** Successful transfer and readback do not prove correct execution after restart or hardware compatibility.

## Getting started

Requires Python3.10+. Model tests also require C11/C++17 compilers. From the repository root:

```sh
python3 scripts/portable_verify.py --list
python3 scripts/portable_verify.py --model runtime-loop --language both
```

On Windows, replace `python3` with `py -3`. These are offline model checks; they neither connect to nor flash hardware.

## Contents

- [src/](src/): curated C/C++ reconstruction.
- [experiments/](experiments/) · [analysis/](analysis/): build instructions, evidence and limitations.
- [firmware-downloads/](firmware-downloads/): official BINs; [artifacts/](artifacts/): APK and experimental images.
