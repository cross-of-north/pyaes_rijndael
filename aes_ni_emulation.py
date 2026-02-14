import pyaes

def words_to_bytes(words4):
    return b''.join(w.to_bytes(4, "big") for w in words4)

def bytes_to_words(b16):
    return [int.from_bytes(b16[i:i+4], "big") for i in range(0, 16, 4)]

def vpblendvb(a, b, mask):
    return bytes(b[i] if mask[i] & 0x80 else a[i] for i in range(16))

def vpshufb(data, mask):
    return bytes(data[mask[i] & 0x0F] for i in range(16))

def vaesdec(state, rk):

    (s1, s2, s3) = [3, 2, 1]
    a = [0, 0, 0, 0]
    t = bytes_to_words(state)
    _Kd = bytes_to_words(rk)
    for i in range(0, 4):
        a[i] = (pyaes.AES.T5[(t[ i          ] >> 24) & 0xFF] ^
                pyaes.AES.T6[(t[(i + s1) % 4] >> 16) & 0xFF] ^
                pyaes.AES.T7[(t[(i + s2) % 4] >>  8) & 0xFF] ^
                pyaes.AES.T8[ t[(i + s3) % 4]        & 0xFF] ^
                _Kd[i])

    return words_to_bytes(a)

def vaesdeclast(state, rk):

    (s1, s2, s3) = [3, 2, 1]
    a = [0, 0, 0, 0]
    t = bytes_to_words(state)
    _Kd = bytes_to_words(rk)
    result = [ ]
    for i in range(0, 4):
        tt = _Kd[i]
        result.append((pyaes.AES.Si[(t[ i          ] >> 24) & 0xFF] ^ (tt >> 24)) & 0xFF)
        result.append((pyaes.AES.Si[(t[(i + s1) % 4] >> 16) & 0xFF] ^ (tt >> 16)) & 0xFF)
        result.append((pyaes.AES.Si[(t[(i + s2) % 4] >>  8) & 0xFF] ^ (tt >>  8)) & 0xFF)
        result.append((pyaes.AES.Si[ t[(i + s3) % 4]        & 0xFF] ^  tt       ) & 0xFF)

    return bytes(result)
