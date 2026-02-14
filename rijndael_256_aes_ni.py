import pyaes
from aes_ni_emulation import words_to_bytes, vpblendvb, vpshufb, vaesdec, vaesdeclast

XMM_BLEND = bytes.fromhex("80808000808000008080000080000000")[::-1] # reverse
XMM_SHUFFLE = bytes.fromhex("0B0A0D0C07060908030205040F0E0100")[::-1] # reverse

def decrypt_aes(params, data, blocks):

    rounds = params["rounds"]
    schedule = params["schedule"]
    key_index = params["key_index"]
    stride = params["stride"]

    out = bytearray()
    rdx = 0

    for _ in range(blocks):

        A = data[rdx:rdx+16]
        B = data[rdx+16:rdx+32]

        rkA = words_to_bytes(schedule[key_index+1])
        rkB = words_to_bytes(schedule[key_index])

        A = bytes(a^b for a,b in zip(A, rkA))
        B = bytes(a^b for a,b in zip(B, rkB))

        rk_ptr = key_index + 2

        def prepare_round():
            nonlocal A, B, rkA, rkB, rk_ptr
            tmp = vpblendvb(A, B, XMM_BLEND)
            B  = vpblendvb(B, A, XMM_BLEND)

            A = vpshufb(tmp, XMM_SHUFFLE)
            B = vpshufb(B, XMM_SHUFFLE)

            rkA = words_to_bytes(schedule[rk_ptr+1])
            rkB = words_to_bytes(schedule[rk_ptr])

        for _ in range(rounds-1):

            prepare_round()

            A = vaesdec(A, rkA)
            B = vaesdec(B, rkB)

            rk_ptr += 2

        prepare_round()

        A = vaesdeclast(A, rkA)
        B = vaesdeclast(B, rkB)

        out.extend(A)
        out.extend(B)

        rdx += stride

    return bytes(out)

def decrypt_rijndael_256(key, ciphertext):

    aes = pyaes.AESModeOfOperationECB(key, cypher_key_length=32, rounds=29, skip_inversion=1)

    decrypted = decrypt_aes(
        {
            "rounds": 14,
            "key_index": 0,
            "stride": 32,
            "schedule": aes._aes._Kd
        },
        ciphertext, len(ciphertext) // 32)

    return decrypted
