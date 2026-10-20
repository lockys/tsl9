/* Section-relative views into the existing 35160B RAM carrier.
 * No additional storage or assumed field values. */
SECTIONS {
  .bss.tsl9v4160.ram 0 : {
    KEEP(*(.bss.tsl9v4160.ram))
    __tsl9v4160_data_2000bebc = __tsl9v4160_ram + 0x7ebc;
    __tsl9v4160_data_2000bec0 = __tsl9v4160_ram + 0x7ec0;
    __tsl9v4160_data_2000bec1 = __tsl9v4160_ram + 0x7ec1;
    __tsl9v4160_data_2000bec2 = __tsl9v4160_ram + 0x7ec2;
    __tsl9v4160_data_2000bec4 = __tsl9v4160_ram + 0x7ec4;
    __tsl9v4160_data_2000bec8 = __tsl9v4160_ram + 0x7ec8;
    __tsl9v4160_data_2000becc = __tsl9v4160_ram + 0x7ecc;
  }
}
