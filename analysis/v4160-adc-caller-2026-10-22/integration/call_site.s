.section .text.tsl9_adc_call_site,"ax",@progbits
.option push
.option norelax
.option norvc
.globl __tsl9_adc_call_site
__tsl9_adc_call_site:
    jal ra, tsl9_adc_config_1892e
.option pop
