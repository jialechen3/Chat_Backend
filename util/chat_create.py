import html
import json
import os
import uuid
import requests

from util.database import chat_collection
from util.response import Response


def chat_create(request, handler):
    res = Response()
    #since: Request (JSON): {"content": string}
    data = json.loads(request.body.decode('utf-8'))
    #get the content from the dict
    content = data.get('content')

    #html escape
    content = html.escape(content)
    session_cookie = 'empty'
    message_id = str(uuid.uuid4())

    #generate path for profile img
    public_dir = "public/imgs"
    img_dir = "public/imgs/profile"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)



    #end generating path



    for cookie in request.cookies:
        if cookie.startswith('session'):   #if there is a session cookie
            session_cookie = request.cookies['session']
            author = str(session_cookie)
            cookie_str = author + "; Expires=Wed, 21 Oct 2025 07:28:00 GMT; Secure"
            #I am finding the nickname for this author id
            name = chat_collection.find_one({"author": session_cookie})
            update_nickname = name['nickname']
            #end nickname


            res.cookies({"session": cookie_str})
            chat_collection.insert_one({
                "author": session_cookie,
                "id": message_id,
                "content": content,
                "updated": False,
                "reactions": {},
                "nickname": update_nickname,
                "imageURL": f"public/imgs/profile/avatar_{author}.svg"
            })

    if session_cookie == 'empty':
        session_cookie = uuid.uuid4()
        author = str(session_cookie)
        cookie_str = author + "; Expires=Wed, 21 Oct 2025 07:28:00 GMT; Secure"
        res.cookies({"session": cookie_str})

        #adding profile img
        # adding img
        url = f'https://api.dicebear.com/9.x/fun-emoji/svg?seed={author}'
        response = requests.get(url)
        filename = f"avatar_{author}.svg"  # filename unique
        filepath = os.path.join(img_dir, filename)
        # write content to file
        with open(filepath, "wb") as f:
            f.write(response.content)

        # end adding image


        chat_collection.insert_one({
            "author": author,
            "id": message_id,
            "content": content,
            "updated": False,
            "reactions": {},
            "nickname": "",
            "imageURL": f"public/imgs/profile/avatar_{author}.svg"
        })

    # Send response
    res.set_status(200, 'OK')

    res.bytes(b'message sent')
    res.headers({'Content-Type': 'application/json'})
    handler.request.sendall(res.to_data())
    print("A create length:" + res.heads['Content-Length'])