# Conditional build gate

The full candidate build first verifies two section-backed symbols and three conditional data aliases. Under those assumptions, the strict link still lacks `tsl9_boot_resident_40000`; only the diagnostic link uses a numeric address witness, and its image is compared with the independently assembled candidate.

An isolated test rebuilds the C and C++ images from 197 source and build files, and a negative control verifies that a failed link check produces no candidate BIN. Of the 3,128 carrier bytes, 432 are compiled from source and the rest remain opaque.

This test does not execute the device or prove resident ROM, data indices, RAM ownership, or flashing safety.
