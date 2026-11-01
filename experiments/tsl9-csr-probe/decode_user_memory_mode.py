"""Decode a USER[7:5] value from WCH V2.5 table 32-4; never reads hardware."""
def decode(mode):
    if type(mode) is not int or not 0 <= mode <= 7:
        raise ValueError("mode must be an integer in 0..7")
    if mode < 2:
        return {"code_kib": 128, "ram_kib": 64}
    if mode < 4:
        return {"code_kib": 144, "ram_kib": 48}
    return {"code_kib": 160, "ram_kib": 32}

def reset_extent_comparison(mode):
    """Compare observed reset endpoints with a hypothetical contiguous RAM window."""
    top = 0x20000000 + decode(mode)["ram_kib"] * 1024
    ends = (0x2000C94C, 0x2000C958)
    return {"ram_end_exclusive": top,
            "reset_end_range": ends,
            "overflow_bytes_range": tuple(max(0, end - top) for end in ends)}
