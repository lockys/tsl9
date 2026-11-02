/* Bounded reconstruction of the normal-entry command classification at
 * 0x14062..0x140ba. Does not call the target or implement other commands. */
#ifdef __cplusplus
extern "C" {
#endif
int tsl9_ota_dispatch_14056(unsigned char command)
{
    switch (command) {
    case 0x45: case 0x52: case 0x53: case 0x55: case 0x57:
        return 1;
    default:
        return 0;
    }
}
#ifdef __cplusplus
}
#endif
