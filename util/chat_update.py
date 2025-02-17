import html
import json

import bson
from bson import Binary, Code

from util.database import chat_collection
from util.response import Response
from bson import ObjectId
from bson.json_util import loads


def chat_update(request, handler):
    res = Response()

    user_id = request.path.split("/")[3]

    mes = chat_collection.find_one({'id': user_id}) #get the user id inside the database

    current_id = request.cookies.get('session')

    if mes['author']!=current_id:
        res.set_status(403, 'Forbidden')
        res.text('fail, you are not the user')
    else:
        cont = json.loads(request.body.decode())
        print(cont)
        real_content = cont.get('content')
        #real_content = html.escape(real_content)
        print('after strip the content is:', cont)
        chat_collection.update_one({'id': user_id}, {'$set': {'content': real_content, 'updated': True}})
        res.set_status(200, 'ok')
        res.text('text update success')


    #res.text(request.body.decode())

    res.headers({'Content-type': 'application/json'})
    handler.request.sendall(res.to_data())




