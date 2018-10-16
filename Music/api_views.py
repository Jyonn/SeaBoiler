from django.views import View

from Base.Netease import NetEase
from Base.error import Error
from Base.response import error_response, response
from Base.validator import require_post, require_get
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
    # /api/music/list
    @staticmethod
    @require_get([{
        'value': 'end',
        'default': True,
        'default_value': -1,
        'process': int,
    }, {
        'value': 'count',
        'default': True,
        'default_value': 10,
        'process': int,
    }])
    def get(request):
        end = request.d.end
        count = request.d.count

        ret = Music.get_music_list(end, count)
        if ret.error is not Error.OK:
            return error_response(ret)

        return response(body=ret.body)
