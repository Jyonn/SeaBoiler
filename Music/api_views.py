import datetime

from django.views import View

from Base.Netease import NetEase
from Base.error import Error
from Base.response import error_response, response
from Base.user_validator import require_login, require_consider
from Base.validator import require_post, require_get, require_put
from Music.models import Music


class MusicView(View):
    @staticmethod
    @require_get([('user_id', None, None)])
    @require_login
    def get(request):
        """ GET /api/music/list?user_id

        获取用户推荐的音乐列表
        如果user_id为空，则返回自己的数据
        """
        user_id = request.d.user_id

        o_user = request.user
        if user_id:
            musics = Music.get_list_by_user(user_id)
        else:
            musics = Music.get_list_by_user(o_user.str_id)

        music_list = []
        for o_music in musics:
            music_list.append(o_music.to_dict())

        return response(music_list)

    @staticmethod
    @require_post(['url'])
    @require_login
    def post(request):
        """ POST /api/music/recommend

        用户推荐歌曲
        """
        url = request.d.url

        o_user = request.user

        ret = NetEase.grab_music_info(url)

        if ret.error is not Error.OK:
            return error_response(ret)

        data = ret.body
        name = data['name']
        singer = data['singer']
        cover = data['cover']
        total_comment = data['total_comment']
        netease_id = data['netease_id']

        if total_comment > 999:
            return error_response(Error.COMMENT_TOO_MUCH)

        ret = Music.create(name, singer, cover, total_comment, netease_id, o_user)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_music = ret.body
        if not isinstance(o_music, Music):
            return error_response(Error.STRANGE)

        return response(o_music.to_dict())

    @staticmethod
    @require_put()
    def put(request):
        """ GET /api/music/update

        更新歌曲总评论数
        """
        crt_time = datetime.datetime.now().timestamp()
        for o_music in Music.objects.all():
            if crt_time - o_music.last_update_time < 60 * 60 * 12:
                continue
            ret = NetEase.get_comment(o_music.netease_id)
            if ret.error is Error.OK:
                total_comment = ret.body
                o_music.update(total_comment)
        return response()


# class MusicListView(View):
#     # /api/music/list
#     @staticmethod
#     @require_get([{
#         'value': 'end',
#         'default': True,
#         'default_value': -1,
#         'process': int,
#     }, {
#         'value': 'count',
#         'default': True,
#         'default_value': 10,
#         'process': int,
#     }])
#     def get(request):
#         end = request.d.end
#         count = request.d.count
#
#         ret = Music.get_music_list(end, count)
#         if ret.error is not Error.OK:
#             return error_response(ret)
#
#         return response(ret.body)

class ConsiderView(View):
    @staticmethod
    @require_get([{
        'value': 'start',
        'process': int,
    }, {
        'value': 'count',
        'process': int,
    }])
    @require_consider
    def get(request):
        start = request.d.start
        count = request.d.count

        return response(Music.get_consider_list(start, count))
