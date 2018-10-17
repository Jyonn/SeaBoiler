from django.views import View

from Base.aes import aes_encrypt
from Base.error import Error
from Base.jtoken import jwt_e
from Base.response import error_response, response
from Base.user_validator import require_login
from Base.validator import require_get, require_put
from Base.weixin import Weixin
from User.models import User


def get_token_info(o_user, session_key):
    encrypt_session_key = aes_encrypt(session_key).body
    ret = jwt_e(dict(openid=o_user.openid, session_key=encrypt_session_key))
    if ret.error is not Error.OK:
        return ret
    token, dict_ = ret.body
    # dict_['token'] = token
    return token


class CodeView(View):
    @staticmethod
    @require_get(['code'])
    def get(request):
        code = request.d.code

        ret = Weixin.code2session(code)
        if ret.error is not Error.OK:
            return error_response(ret)

        openid = ret.body['openid']
        session_key = ret.body['session_key']

        ret = User.create(openid)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_user = ret.body

        return response(get_token_info(o_user, session_key))


class UserView(View):
    @staticmethod
    @require_put(['encrypted_data', 'iv'])
    @require_login
    def put(request):
        encrypted_data = request.d.encrypted_data
        iv = request.d.iv

        session_key = request.session_key

        ret = Weixin.decrypt(encrypted_data, iv, session_key)
        if ret.error is not Error.OK:
            return error_response(ret)

        data = ret.body

        o_user = request.user
        avatar = data['avatarUrl']
        nickname = data['nickName']
        ret = o_user.update(avatar, nickname)
        if ret.error is not Error.OK:
            return error_response(ret)

        return response(o_user.to_dict())
