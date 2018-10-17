from django.views import View

from Base.error import Error
from Base.response import error_response, response
from Base.user_validator import require_login
from Base.validator import require_get, require_put
from Message.models import Message
from User.models import User


class MessageView(View):
    @staticmethod
    @require_get([{
        'value': 'only_unread',
        'process': bool,
    }, {
        'value': 'start',
        'process': int,
    }, {
        'value': 'count',
        'process': int,
    }])
    @require_login
    def get(request):
        """ GET /api/message/

        获取已读/所有消息
        """
        only_unread = request.d.only_unread
        start = request.d.start
        count = request.d.count

        o_user = request.user
        if not isinstance(o_user, User):
            return error_response(Error.STRANGE)

        return response(Message.get_list_by_user(o_user.str_id, only_unread, start, count))

    @staticmethod
    @require_put(['msg_id'])
    @require_login
    def put(request):
        msg_id = request.d.msg_id
        o_user = request.user

        ret = Message.get_msg_by_id(msg_id)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_msg = ret.body
        if not isinstance(o_msg, Message):
            return error_response(Error.STRANGE)

        if o_msg.to_user != o_user:
            return error_response(Error.MESSAGE_NOT_BELONG)
        o_msg.read_msg()

        return response()
