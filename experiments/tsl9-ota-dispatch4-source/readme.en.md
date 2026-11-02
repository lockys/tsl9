# Command dispatcher check continuation

The 60 bytes at `0x142C0..0x142FC` compile from architectural instructions in C/C++, with one direct call and three branch relocations; linked at the original address, they match the earlier image byte for byte. This fragment depends on the original dispatcher frame, the `0x92F2` function and an unverified resident release slot. It is not independently callable or complete functionality.

An isolated 199-file build reproduces both 76,800-byte candidates and passes the failure control. Of the 3,128-byte carrier, 548 bytes are compiled from source and 2,580 remain opaque original bytes; installed ROM, RAM, complete behavior and flashing compatibility are unverified.
