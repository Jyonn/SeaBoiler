import datetime

from django.db import models

from Base.common import deprint
from Base.error import Error
from Base.response import Ret
from Base.validator import field_validator
from Config.models import Config


class Music(models.Model):
    L = {
        'name': 255,
        'singer': 100,
        'cover': 1024,
    }

    STATUS_CONSIDER = 0
    STATUS_ACCEPTED = 1
    STATUS_REFUSED = 2
    STATUS_TABLE = (
        (STATUS_CONSIDER, 'under consider'),
        (STATUS_ACCEPTED, 'accepted'),
        (STATUS_REFUSED, 'refused'),
    )

    name = models.CharField(
        verbose_name='歌曲名',
        max_length=L['name'],
    )

    singer = models.CharField(
        verbose_name='歌手',
        max_length=L['singer'],
    )

    cover = models.CharField(
        verbose_name='封面',
        max_length=L['cover'],
    )

    total_comment = models.IntegerField(
        verbose_name='评论总数',
        default=0,
    )

    netease_id = models.IntegerField(
        verbose_name='网易云歌曲ID',
        default=0,
    )

    re_user = models.ForeignKey(
        'User.User',
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
        related_name='recommend_user',
    )

    create_time = models.FloatField(
        default=0,
    )

    status = models.IntegerField(
        choices=STATUS_TABLE,
        default=STATUS_CONSIDER,
    )

    last_update_time = models.FloatField(
        default=0,
    )
    updated_total_comment = models.IntegerField(
        default=0,
    )

    consider_user = models.ForeignKey(
        'User.User',
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name='consider_user',
    )

    FIELD_LIST = [
        'name', 'singer', 'cover', 'total_comment', 'netease_id', 'create_time',
        'status', 'last_update_time', 'updated_total_comment',
    ]

    @classmethod
    def _validate(cls, dict_):
        return field_validator(dict_, cls)

    @classmethod
    def create(cls, name, singer, cover, total_comment, netease_id, o_user):
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        ret = cls.get_music_by_netease_id(netease_id)
        if ret.error is Error.OK:
            return ret

        crt_time = datetime.datetime.now().timestamp()

        try:
            o_music = cls(
                name=name,
                singer=singer,
                cover=cover,
                total_comment=total_comment,
                netease_id=netease_id,
                re_user=o_user,
                create_time=crt_time,
                status=cls.STATUS_CONSIDER,
                last_update_time=crt_time,
                updated_total_comment=total_comment,
            )
            o_music.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_MUSIC)

        return Ret(o_music)

    def update_comment(self, total_comment):
        crt_time = datetime.datetime.now().timestamp()
        self.updated_total_comment = total_comment
        self.last_update_time = crt_time
        self.save()

    def update_status(self, status, consider_user):
        if self.status != self.STATUS_CONSIDER:
            return Ret(Error.ALREADY_CONSIDERED)
        self.status = self.STATUS_ACCEPTED if status else self.STATUS_REFUSED
        self.consider_user = consider_user
        self.save()
        return Ret()

    @classmethod
    def get_music_by_netease_id(cls, netease_id):
        try:
            o_music = cls.objects.get(netease_id=netease_id)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_MUSIC)
        return Ret(o_music)

    @classmethod
    def get_consider_list(cls, start, count=10):
        if count > 10 or count <= 0:
            count = 10

        considers = cls.objects.filter(status=cls.STATUS_CONSIDER, pk__gt=start)
        total = considers.count()

        is_over = total <= count
        if total < count:
            count = total
        considers = considers[:count]

        consider_list = []
        for o_music in considers:
            consider_list.append(o_music.to_dict())

        next_start = start if total == 0 else consider_list[-1]['id']

        return dict(
            consider_list=consider_list,
            is_over=is_over,
            next_start=next_start
        )

    @classmethod
    def get_list_by_user(cls, user_id):
        return cls.objects.filter(re_user__str_id=user_id)

    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            singer=self.singer,
            cover=self.cover,
            total_comment=self.total_comment,
            create_time=self.create_time,
            netease_id=self.netease_id,
            updated_total_comment=self.updated_total_comment,
            last_update_time=self.last_update_time,
            status=self.status,
            owner=self.re_user.to_dict() if self.re_user else None
        )


class DailyRecommend(models.Model):
    dat_e = models.DateField(
        default=None,
        unique=True,
    )

    re_music = models.ForeignKey(
        Music,
        on_delete=models.SET_DEFAULT,
        default=None,
    )

    @classmethod
    def get_dr_by_date(cls, date_):
        try:
            o_dr = cls.objects.get(dat_e=date_)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_DAILYRECOMMEND)
        return Ret(o_dr)

    @classmethod
    def push(cls, o_music):
        pushing_date_str = Config.get_value_by_key('next-recommend-date', '2018-10-17').body
        pushing_date = datetime.datetime.strptime(pushing_date_str, '%Y-%m-%d').date()

        try:
            o_dr = cls(
                dat_e=pushing_date,
                re_music=o_music,
            )
            o_dr.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_DAILYRECOMMEND)

        next_date = pushing_date + datetime.timedelta(days=1)
        next_date_str = next_date.strftime('%Y-%m-%d')

        Config.update_value('next-recommend-date', next_date_str)

        return Ret(o_dr)

    def get_readable_date(self):
        return '%s年%s月%s日' % (self.dat_e.year, self.dat_e.month, self.dat_e.day)

    @classmethod
    def get_daily_music_list(cls, end_date=None, count=10):
        if count > 10 or count <= 0:
            count = 10

        crt_date = datetime.datetime.now().date()

        if end_date:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        if not end_date or end_date > crt_date:
            end_date = crt_date

        first_date_str = Config.get_value_by_key('first-date', '2018-10-17').body
        first_date = datetime.datetime.strptime(first_date_str, '%Y-%m-%d').date()

        daily_music_list = []
        is_over = False
        for _ in range(count):
            if end_date < first_date:
                break
            ret = cls.get_dr_by_date(end_date)
            if ret.error is Error.OK:
                o_dr = ret.body
                daily_music_list.append(o_dr.to_dict())
            end_date -= datetime.timedelta(days=1)

        if end_date < first_date:
            is_over = True

        return Ret(dict(
            daily_music_list=daily_music_list,
            next_date=end_date.strftime('%Y-%m-%d'),
            is_over=is_over,
        ))

    def to_dict(self):
        return dict(
            date=self.dat_e.strftime('%Y-%m-%d'),
            music=self.re_music.to_dict(),
        )
