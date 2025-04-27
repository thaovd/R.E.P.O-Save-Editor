from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from Crypto.Hash import HMAC, SHA1
import gzip
import os

def encrypt_es3(data, password, should_gzip=False):
    if should_gzip:
        data = gzip.compress(data)

    iv = os.urandom(16)

    key = PBKDF2(password, iv, dkLen=16, count=100, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))

    return iv + encrypted_data