import json

from util.database import chat_collection
from util.response import Response


def emoji_create(request, handler):
    res = Response()
    mes_id = request.path.split("/")[-1]
    emoji = json.loads(request.body.decode()).get('emoji')
    user_db = chat_collection.find_one({'id': mes_id})
    reaction = user_db['reactions']
    session_cookie = request.cookies['session']
    author = str(session_cookie)

    # if emoji in reaction:

    if emoji in reaction:#if the emoji exist in the dict
        user_found = False
        for key in reaction[emoji]:#search the values in that emoji to see if the user is there
            if key == author:
                user_found = True
                res.set_status(403, 'forbid')
                res.text('you already have this reaction')
                handler.request.sendall(res.to_data())
                return

        if not user_found:
            rea_str = reaction[emoji]
            rea_str.append(author)
            chat_collection.update_one({'id': mes_id}, {'$set': {f"reactions.{emoji}": rea_str}})

    else:
        chat_collection.update_one({'id': mes_id}, {'$set': {f"reactions.{emoji}": [author]}})

    res.text('emoji added')
    handler.request.sendall(res.to_data())