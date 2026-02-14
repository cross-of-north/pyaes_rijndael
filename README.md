Some [pyaes](https://github.com/ricmoo/pyaes)-based AES implementation testing helpers:
- Support for the customized key generation schedule.
- Pure Python emulation of the AES-NI instructions (VAESDEC, VAESDECLAST, VPBLENDVB, VPSHUFB).
- Rijndael-256 decoding flow implementation reproducing the AES-NI flow from the [Intel® white paper](https://www.intel.com/content/dam/doc/white-paper/advanced-encryption-standard-new-instructions-set-paper.pdf) (Fig.30 "Using the AES instructions to compute a 256-bit block size RINJDAEL<sub>sic!</sub> round"):
```assembly

; initialization
    ...
    vmovdqa xmm0, <blend_mask>
    vmovdqa xmm1, <shuffle_mask>
    ...
    vmovdqa xmm2, xmmword ptr [<keys+keys_offset>]
    vmovdqa xmm3, xmmword ptr [<keys+keys_offset>+10h]
    vpxor   xmm2, xmm2, xmmword ptr [<data+data_offset>]
    vpxor   xmm3, xmm3, xmmword ptr [<data+data_offset>+10h]
    ...

;loop
        ...
        vpblendvb xmm4, xmm2, xmm3, xmm0
        vpblendvb xmm3, xmm3, xmm2, xmm0
        vpshufb xmm2, xmm4, xmm1
        vaesdec xmm2, xmm2, xmmword ptr [<keys+keys_offset>-10h]
        vpshufb xmm3, xmm3, xmm1
        vaesdec xmm3, xmm3, xmmword ptr [<keys+keys_offset>]
        ...

; final round
    ...
    vpblendvb xmm4, xmm2, xmm3, xmm0
    vpblendvb xmm2, xmm3, xmm2, xmm0
    vpshufb xmm3, xmm4, xmm1
    vaesdeclast xmm3, xmm3, xmmword ptr [<keys+keys_offset>]
    vpshufb xmm2, xmm2, xmm1
    vaesdeclast xmm2, xmm2, xmmword ptr [<keys+keys_offset>+10h]
    ...
```