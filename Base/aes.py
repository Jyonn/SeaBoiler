import base64

from Crypto import Random
from Crypto.Cipher import AES

# from SeaBoiler.settings import SECRET_KEY
from Base.common import deprint
from Base.error import Error
from Base.response import Ret

SECRET_KEY = '38296423894673825637265'


def aes_encrypt(data):
    try:
        key = SECRET_KEY[:16]
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        encrypted_data = iv + cipher.encrypt(data)
        encrypted_data = base64.b64encode(encrypted_data).decode()
    except Exception as err:
        deprint(str(err))
        return Ret(Error.AES_ENCRYPT_ERROR)
    return Ret(encrypted_data)


def aes_decrypt(encrypted_data):
    try:
        encrypted_data = base64.b64decode(encrypted_data)
        key = SECRET_KEY[:16]
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]
        cipher = AES.new(key, AES.MODE_CFB, iv)
        data = cipher.decrypt(encrypted_data).decode()
    except Exception as err:
        deprint(str(err))
        return Ret(Error.AES_DECRYPT_ERROR)
    return Ret(data)
