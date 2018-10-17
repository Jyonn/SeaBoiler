from Base.aes import aes_decrypt
from Base.common import deprint
from Base.error import Error
from Base.response import Ret
from Base.validator import decorator_generator


def require_login_func(request):
    """需要登录

    并根据传入的token获取user
    """
    jwt_str = request.META.get('HTTP_TOKEN')
    if jwt_str is None:
        return Ret(Error.REQUIRE_LOGIN)
    from Base.jtoken import jwt_d

    ret = jwt_d(jwt_str)
    if ret.error is not Error.OK:
        return ret
    dict_ = ret.body

    user_id = dict_.get("user_id")
    if not user_id:
        deprint('Base-validator-require_login_func-dict.get(user_id)')
        return Ret(Error.STRANGE)

    session_key = dict_.get("session_key")
    if not session_key:
        deprint('Base-validator-require_login_func-dict.get(session_key)')
        return Ret(Error.STRANGE)
    ret = aes_decrypt(session_key)
    if ret.error is not Error.OK:
        return ret
    session_key = ret.body

    from User.models import User
    ret = User.get_user_by_str_id(user_id)
    if ret.error is not Error.OK:
        return ret
    o_user = ret.body
    if not isinstance(o_user, User):
        return Ret(Error.STRANGE)

    request.user = o_user
    request.session_key = session_key

    return Ret()


def maybe_login_func(request):
    """decorator, maybe require login"""
    require_login_func(request)
    return Ret()


require_login = decorator_generator(require_login_func)
maybe_login = decorator_generator(maybe_login_func)
