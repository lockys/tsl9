# Command dispatcher fragment

The 90 bytes at `0x141D6..0x14230` compile from architectural instructions and an external relocation as both C and C++ objects. Each contains 14 relocations; linked at the original address, the fragment matches the original image byte for byte. The full conditional link also checks that the `0x13BA6` call target has executable section backing.

The fragment depends on the original dispatcher frame and is not independently callable. An isolated test uses 196 source and build files; both 76,800-byte candidates match the earlier image and the failure control passes. Of the 3,128-byte carrier, 344 bytes compile from source and 2,784 remain original carrier bytes.

Installed ROM, RAM, complete behavior, and flashing compatibility remain unverified.
