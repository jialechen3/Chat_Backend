import json
import uuid

import bson.json_util
from bson import Binary, Code
from bson.json_util import dumps

from util.database import chat_collection
from util.response import Response


def chat_get(request, handler):

    res = Response()
    mes = chat_collection.find() #get all messages inside the database

    message = bson.json_util.dumps({"messages": mes})

    res.set_status(200, 'OK')

    res.text(message)
    #res.headers({'Content-Type': 'application/json'})
    handler.request.sendall(res.to_data())







