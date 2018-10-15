from django.views import View

from Base.Netease import NetEase
from Base.error import Error
from Base.response import error_response, response
from Base.validator import require_post
from Music.models import Music


class MusicView(View):
    # /api/music/
    @staticmethod
    @require_post(['url'])
    def post(request):
        url = request.d.url

        ret = NetEase.grab_music_info(url)
        if ret.error is not Error.OK:
            return error_response(ret)

        data = ret.body
        name = data['name']
        singer = data['singer']
        cover = data['cover']
        total_comment = data['total_comment']
        netease_id = data['netease_id']

        ret = Music.create(name, singer, cover, total_comment, netease_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_music = ret.body
        if not isinstance(o_music, Music):
            return error_response(Error.STRANGE)

        return response(body=o_music.to_dict())


class MusicListView(View):
    # cls.object.filter
    pass


# 1
# 31
# 61
# 获取歌曲
# GET /api/music/?count=10&start=-1 /// 61- 52, 51-42
# a = \
# {
#     'song_list': [
#         {
#             'name': '修炼爱情',
#
#         },
#         {}
#     ],
#     'next_id': 41,
# }
#
#
#
