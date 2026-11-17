# v4.1.60 writer: offline C projection

The existing five bounded instruction projections for the writer at 0x18ca4 have been expressed as a single callback-based C candidate. This is not the firmware ABI, a formal source replacement, or additional original-image byte coverage.

The candidate was compiled as C11 and C++17 at /Od and /O2 and compared with the existing five decoded instruction projections on 11 synthetic bank, branch, wrap and alias cases. Output projections, ordered operations and synthetic byte memory were compared. The original decoded image was checked by SHA-256 0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667. Python normal and -O test runs passed. Builds emitted a missing vswhere.exe warning but succeeded.

Three compiled C/C++ negative controls demonstrate detection of status caching, a reordered branch read, and an omitted second port read. In a separate scripted read experiment, returning 0x20 on the second read leads the candidate to write 0x2d, versus 0x0d for the omitted-read mutant; the normal candidate was also compared to the decoded projections under the same script.

Status and changing reads are injected, unmapped writer bytes read as zero, and success is assumed. These results do not establish actual hardware behavior, fault handling, complete register equivalence, runtime reachability, provenance closure or a flashable image. The candidate and tests remain local pending publication review.