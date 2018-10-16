import json
import re

from Base.error import Error
from Base.response import Ret

import zlib
from urllib import request

from bs4 import BeautifulSoup


def abstract_grab(url, phone_agent=False):
    """
    抽象抓取
    :param url: 网页链接
    :param phone_agent: 是否模拟手机
    :return: 网页内容
    """
    req = request.Request(url)

    req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    req.add_header("Accept-Encoding", "gzip")
    req.add_header("Accept-Language", "zh-CN,zh;q=0.8")
    req.add_header("Cache-Control", "max-age=0")
    req.add_header("Connection", "keep-alive")
    if phone_agent:
        # 模拟手机User-Agent
        req.add_header("User-Agent",
                       "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) "
                       "AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1")
    else:
        req.add_header("User-Agent",
                       "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/56.0.2924.87 Safari/537.36")

    res = request.urlopen(req)
    gzipped = res.headers.get('Content-Encoding')  # 判断是否压缩
    compressed_data = res.read()
    res.close()
    if gzipped:
        content = zlib.decompress(compressed_data, 16+zlib.MAX_WBITS)  # 解压
    else:
        content = compressed_data
    content = content.decode("utf-8")

    return content


class NetEase:
    LYRIC_URL = 'https://music.163.com/api/song/media?id=%s'
    MUSIC_URL = 'http://music.163.com/song/media/outer/url?id=%s.mp3'
    COMMENT_URL = 'https://music.163.com/api/v1/resource/comments/R_SO_4_%s'

    @staticmethod
    def grab_music_info(url):
        if url.find('song/') == -1:
            return Ret(Error.ERROR_MUSIC_LINK, append_msg='，歌曲ID定位错误')
        sub_url = url[url.find('song/')+4:]
        while sub_url and not '9' >= sub_url[0] >= '0':
            sub_url = sub_url[1:]

        index = 0
        while len(sub_url) > index and '9' >= sub_url[index] >= '0':
            index += 1

        netease_id = sub_url[:index]
        if not netease_id:
            return Ret(Error.ERROR_MUSIC_LINK, append_msg='，歌曲ID获取错误')

        info_url = 'https://music.163.com/song?id=%s' % netease_id
        try:
            html = abstract_grab(info_url)
        except Exception as err:
            return Ret(Error.ERROR_GRAB_MUSIC, append_msg='，无法访问')

        try:
            soup = BeautifulSoup(html, 'html.parser')
            info = soup.find('a', class_='u-btni u-btni-share ')
            singer = info.get('data-res-author')
            name = info.get('data-res-name')
        except Exception as err:
            return Ret(Error.ERROR_GRAB_MUSIC, append_msg='，字段获取错误')

        try:
            cover_regex = '"images": \["(.*?)"'
            cover = re.search(cover_regex, html, flags=re.S).group(1)
        except Exception as err:
            return Ret(Error.ERROR_GRAB_MUSIC, append_msg='，字段获取错误')

        comment_url = NetEase.COMMENT_URL % netease_id

        try:
            data = abstract_grab(comment_url)
            total_comment = json.loads(data)['total']
        except Exception as err:
            return Ret(Error.ERROR_GRAB_MUSIC, append_msg='，评论获取错误')

        return Ret(dict(
            netease_id=netease_id,
            name=name,
            singer=singer,
            cover=cover,
            total_comment=total_comment,
        ))
