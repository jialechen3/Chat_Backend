

from util.database import chat_collection
from util.response import Response
from bson import ObjectId
def chat_delete(request, handler):

    res = Response()
    mes_id = request.path.split("/")[3]
    print("Message id:" + mes_id)
    mes = chat_collection.find_one({'id': mes_id})
    # get the user id inside the database
    current_id = request.cookies.get('session')

    if mes['author']!=current_id:
        res.set_status(403, 'Forbidden')
        res.text('fail, you are not the user')
    else:
        chat_collection.delete_one({"id": mes_id})
        res.set_status(200, 'ok')
        res.text('text delete success')

    res.headers({'Content-type': 'application/json'})
    handler.request.sendall(res.to_data())