# v4.1.60 settings writer: bounded offline observations

The local decoded image has SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. The existing source already represents the settings writer beginning at `0x13052`; this work does not add source coverage.

An experimental callback-based C projection and a bounded decoder were compared for C11 and C++17. In both normal Python and `python -O`, each language passed 420 synthetic cases and detected four compiled projection mutants. Tests cover selected live stack pointer and saved-return-address aliases; callbacks are synthetic and represent an assumed arrival at a specified continuation, not execution of the actual providers. Failed callbacks and memory event logs are model contracts, not hardware traps or complete provider traces.

This evidence does not establish real ABI, actual flash writes, complete CPU execution, firmware reachability, or a flashable image. The C projection and its tests have not been published with this report.