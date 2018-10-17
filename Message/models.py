from django.db import models

from Base.common import deprint
from Base.error import Error
from Base.response import Ret
from Base.validator import field_validator


class Message(models.Model):
    L = {
        'msg': 512,
    }

    TYPE_RECOMMEND_ACCEPT = 0
    TYPE_RECOMMEND_REFUSE = 1
    TYPE_PUSH_DAILY_FAIL = 2
    TYPE_TABLE = (
        (TYPE_RECOMMEND_ACCEPT, '恭喜！你推荐的《%s》已被采纳，将作为%s的日推歌曲。'),
        (TYPE_RECOMMEND_REFUSE, '对不起，你推荐的《%s》没有被采纳，原因为：%s。'),
        (TYPE_PUSH_DAILY_FAIL, '你审核通过的歌曲《%s》因为系统原因无法加入日推，请联系管理员，谢谢。')
    )

    msg = models.CharField(
        max_length=L['msg'],
    )

    re_music = models.ForeignKey(
        'Music.Music',
        on_delete=models.CASCADE,
    )

    to_user = models.ForeignKey(
        'User.User',
        on_delete=models.CASCADE,
    )

    mtype = models.IntegerField(
        choices=TYPE_TABLE,
        default=None,
    )

    has_read = models.BooleanField(
        default=False,
    )

    FIELD_LIST = ['msg', 'mtype']

    @classmethod
    def _validate(cls, dict_):
        return field_validator(dict_, cls)

    @classmethod
    def create(cls, msg, re_music, to_user, mtype):
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        try:
            o_msg = cls(
                msg=msg,
                re_music=re_music,
                to_user=to_user,
                mtype=mtype,
                has_read=False,
            )
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_MESSAGE)
        return Ret(o_msg)

    def read_msg(self):
        self.has_read = True
        self.save()

    def to_dict(self):
        return dict(
            id=self.pk,
            msg=self.msg,
            has_read=self.has_read,
            music=self.re_music.to_dict(),
        )

    @classmethod
    def get_list_by_user(cls, user_id, only_unread=True, start=0, count=10):
        if count > 10 or count <= 0:
            count = 10

        messages = cls.objects.filter(to_user__str_id=user_id)
        if only_unread:
            messages = messages.filter(has_read=False)

        total = messages.count()

        is_over = total <= count
        if total < count:
            count = total
        messages = messages[:count]

        message_list = []
        for o_msg in messages:
            message_list.append(o_msg.to_dict())

        next_start = start if total == 0 else message_list[-1]['id']

        return dict(
            consider_list=message_list,
            is_over=is_over,
            next_start=next_start
        )

    @classmethod
    def get_msg_by_id(cls, msg_id):
        try:
            o_msg = cls.objects.get(pk=msg_id)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_MESSAGE)
        return Ret(o_msg)