import json

from util.database import chat_collection
from util.response import Response


def emoji_delete(request, handler):
    print('delete emoji route')
    res = Response()
    mes_id = request.path.split("/")[-1]
    emoji = json.loads(request.body.decode()).get('emoji')
    user_db = chat_collection.find_one({'id': mes_id})
    reaction = user_db['reactions']
    session_cookie = request.cookies['session']
    author = str(session_cookie)
    #if not reaction[emoji]:
        #chat_collection.update_one({'id': mes_id}, {'$unset': {f"reactions.{emoji}": ""}})
    user_found = False
    for key in reaction[emoji]:  # search the values in that emoji to see if the user is there
        if key == author:
            chat_collection.update_one({'id': mes_id}, {'$pull': {f"reactions.{emoji}": author}})
            user_found = True
            updated_db = chat_collection.find_one({'id': mes_id})
            updated_reaction = updated_db['reactions']
            if not updated_reaction[emoji]:
                chat_collection.update_one({'id': mes_id}, {'$unset': {f"reactions.{emoji}": ""}})
    print("block the remove")
    if not user_found:
        res.set_status(403, 'forbid')
        res.text('you dont have any reaction with this message')
        handler.request.sendall(res.to_data())
        return
    res.text('emoji deleted')
    handler.request.sendall(res.to_data())
