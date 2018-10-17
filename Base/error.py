""" 180226 Adel Liu

错误表，在编码时不断添加
自动生成eid
"""


class E:
    _error_id = 0

    def __init__(self, msg):
        self.eid = E._error_id
        self.msg = msg
        E._error_id += 1


class Error:
    OK = E("没有错误")
    ERROR_NOT_FOUND = E("不存在的错误")
    REQUIRE_PARAM = E("缺少参数")
    REQUIRE_JSON = E("需要JSON数据")
    REQUIRE_LOGIN = E("需要登录")
    STRANGE = E("未知错误")
    REQUIRE_BASE64 = E("参数需要base64编码")
    ERROR_PARAM_FORMAT = E("错误的参数格式")
    ERROR_METHOD = E("错误的HTTP请求方法")
    ERROR_VALIDATION_FUNC = E("错误的参数验证函数")
    REQUIRE_ROOT = E("需要管理员登录")
    ERROR_TUPLE_FORMAT = E("属性元组格式错误")
    ERROR_PROCESS_FUNC = E("参数预处理函数错误")

    AES_ENCRYPT_ERROR = E("AES加密失败")
    AES_DECRYPT_ERROR = E("AES解密失败")

    JWT_EXPIRED = E("身份认证过期")
    ERROR_JWT_FORMAT = E("身份认证错误，请登录")
    JWT_PARAM_INCOMPLETE = E("身份认证缺少参数，请登录")

    NOT_FOUND_CONFIG = E("不存在的配置")

    ERROR_MUSIC_LINK = E("错误的歌曲分享链接")
    ERROR_GRAB_MUSIC = E("爬取数据错误")

    ERROR_CREATE_MUSIC = E("创建歌曲错误")
    NOT_FOUND_MUSIC = E("不存在的歌曲")

    ERROR_CREATE_USER = E("创建用户错误")
    NOT_FOUND_USER = E("不存在的用户")

    ERROR_JSCODE = E("错误的微信code")
    DECRYPT_ERROR = E("无法解密加密数据")
    ILLEGAL_BUFFER = E("错误的缓冲区")
    VALIDATE_APPID_ERROR = E("应用ID验证失败")
    VALIDATE_SIGNATURE_ERROR = E("签名验证失败")
    ERROR_APP_ID = E("不匹配的小程序ID")

    COMMENT_TOO_MUCH = E("只能推荐评论数小于999的小众歌曲")

    @classmethod
    def get_error_dict(cls):
        error_dict = dict()
        for k in cls.__dict__:
            if k[0] != '_':
                e = getattr(cls, k)
                if isinstance(e, E):
                    error_dict[k] = dict(eid=e.eid, msg=e.msg)
        return error_dict
