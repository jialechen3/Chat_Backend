import html
import json

from util.database import chat_collection
from util.response import Response


def nickname(request,handler):
    res = Response()
    name = json.loads(request.body.decode()).get('nickname')
    escaped_name = html.escape(name)
    session_cookie = request.cookies['session']
    author = str(session_cookie)
    chat = chat_collection.update_many({"author": author},{"$set": {"nickname": escaped_name}})
    res.text('set nickname success')
    handler.request.sendall(res.to_data())
    #question to ask: if the user doesn't have a cookie(first time to the page) and a data field,
    # are they able to set the nickname?


