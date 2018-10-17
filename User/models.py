from django.db import models
from django.utils.crypto import get_random_string

from Base.common import deprint
from Base.error import Error
from Base.response import Ret
from Base.validator import field_validator


class User(models.Model):
    L = {
        'openid': 64,
        'avatar': 512,
        'nickname': 64,
        'str_id': 6,
    }

    openid = models.CharField(
        max_length=L['openid'],
    )

    avatar = models.CharField(
        max_length=L['avatar'],
        default=None,
        null=True,
        blank=True,
    )

    nickname = models.CharField(
        max_length=L['nickname'],
        default=None,
        null=True,
        blank=True,
    )

    str_id = models.CharField(
        max_length=L['str_id'],
        default=None,
        unique=True,
    )

    FIELD_LIST = ['openid', 'avatar', 'nickname']

    @classmethod
    def get_unique_str_id(cls):
        while True:
            str_id = get_random_string(length=cls.L['res_str_id'])
            ret = cls.get_user_by_str_id(str_id)
            if ret.error == Error.NOT_FOUND_USER:
                return str_id
            deprint('generate res_str_id: %s, conflict.' % str_id)

    @classmethod
    def _validate(cls, dict_):
        """验证传入参数是否合法"""
        return field_validator(dict_, cls)

    @classmethod
    def create(cls, openid):
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        ret = cls.get_user_by_openid(openid)
        if ret.error is Error.OK:
            return ret

        try:
            o_user = cls(
                openid=openid,
                str_id=cls.get_unique_str_id(),
            )
            o_user.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_USER)

        return Ret(o_user)

    @classmethod
    def get_user_by_openid(cls, openid):
        try:
            o_user = cls.objects.get(openid=openid)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        return Ret(o_user)

    @classmethod
    def get_user_by_str_id(cls, str_id):
        try:
            o_user = cls.objects.get(str_id=str_id)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        return Ret(o_user)

    def update(self, avatar, nickname):
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        self.avatar = avatar
        self.nickname = nickname
        self.save()
        return Ret()

    def to_dict(self):
        return dict(
            str_id=self.str_id,
            nickname=self.nickname,
            avatar=self.avatar,
        )
