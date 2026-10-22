OUTPUT_ARCH(riscv)
SECTIONS
{
  .packet 0 : ALIGN(2)
  {
    KEEP(*(.text.tsl9_receive_buffer_entry_16a7c))
    KEEP(*(.text.tsl9_packet_receive_body))
    KEEP(*(.text.tsl9_packet_receive_finish_16afe))
  }
}
