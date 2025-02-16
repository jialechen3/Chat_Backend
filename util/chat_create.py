import html
import json
import uuid

from util.database import chat_collection
from util.response import Response


def chat_create(request, handler):
    res = Response()
    #since: Request (JSON): {"content": string}
    data = json.loads(request.body.decode('utf-8'))
    #get the content from the dict
    content = data.get('content')
    if not content:
        res.set_status(400, 'Bad Request')
        res.text('No Content')
        handler.request.sendall(res.to_data())
        return

    #html escape
    content = html.escape(content)
    session_cookie = 'empty'
    author = ''
    message_id = str(uuid.uuid4())
    for cookie in request.cookies:
        if cookie.startswith('session'):
            session_cookie = request.cookies['session']
            chat_collection.insert_one({
                "author": session_cookie,
                "id": message_id,
                "content": data.get("content"),
                "updated": False
            })

    if session_cookie == 'empty':
        session_cookie = uuid.uuid4()
        author = str(session_cookie)
        cookie_str = author + "; Expires=Wed, 21 Oct 2025 07:28:00 GMT; HttpOnly; Secure"
        res.cookies({"session": cookie_str})
        chat_collection.insert_one({
            "author": author,
            "id": message_id,
            "content": data.get("content"),
            "updated": False
        })


    # Send response
    res.set_status(200, 'OK')

    res.text('message sent')
    res.headers({'Content-type': 'application/json'})
    handler.request.sendall(res.to_data())
    print("A create length:" + res.heads['Content-Length'])