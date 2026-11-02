# Command dispatcher continuation

The 88 bytes at `0x14230..0x14288` compile from C/C++ architectural instructions; each object has 10 relocations. Linked at the original address, they match the original image byte for byte. The full conditional link checks executable section backing for call targets `0x81AA` and `0x9124`.

The fragment requires the original dispatcher frame and is not independently callable. An isolated 199-file build reproduces both 76,800-byte candidates and passes the failure control. Of the 3,128-byte carrier, 548 bytes are compiled from source and 2,580 remain opaque original bytes; installed ROM, RAM, complete behavior and flashing compatibility are unverified.
