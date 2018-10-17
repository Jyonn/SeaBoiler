import requests

from Base.common import deprint
from Base.error import Error
from Base.response import Ret

import base64
import json
from Crypto.Cipher import AES

from Config.models import Config


class Weixin:
    APP_ID = Config.get_value_by_key('weixin-app-id', 'YOUR-APP-ID').body
    APP_SECRET = Config.get_value_by_key('weixin-app-secret', 'YOUR-APP-secret').body

    CODE2SESSION_URL = 'https://api.weixin.qq.com/sns/jscode2session' \
                       '?appid=' + APP_ID + \
                       '&secret=' + APP_SECRET + \
                       '&js_code=%s' \
                       '&grant_type=authorization_code'

    @staticmethod
    def code2session(code):
        url = Weixin.CODE2SESSION_URL % code

        data = requests.get(url).json()

        if 'openid' not in data:
            return Ret(Error.ERROR_JSCODE)
        return Ret(data)

    @classmethod
    def decrypt(cls, encrypted_data, iv, session_key):
        try:
            encrypted_data = base64.b64decode(encrypted_data)
            iv = base64.b64decode(iv)
            session_key = base64.b64decode(session_key)

            cipher = AES.new(session_key, AES.MODE_CBC, iv)

            decrypted = json.loads(cls._unpad(cipher.decrypt(encrypted_data)).decode())

            if decrypted['watermark']['appid'] != cls.APP_ID:
                # raise Exception('Invalid Buffer')
                return Ret(Error.ERROR_APP_ID)
        except Exception as err:
            deprint(str(err))
            return Ret(Error.DECRYPT_ERROR)

        return Ret(decrypted)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
