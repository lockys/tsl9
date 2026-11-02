# Command dispatcher branch

The 56 bytes at `0x14288..0x142C0` compile from C/C++ architectural instructions, with four branch relocations in each object. Linked at the original address, they match the original image byte for byte. The fragment contains two indirect calls through resident slots and depends on the original dispatcher frame and unverified installed slot contracts; it is not independently callable.

An isolated 199-file build reproduces both 76,800-byte candidates and passes the failure control. Of the 3,128-byte carrier, 548 bytes are compiled from source and 2,580 remain opaque original bytes; installed ROM, RAM, complete behavior and flashing compatibility are unverified.
