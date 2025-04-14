import json
import uuid

from util.database import zoom_collection
from util.response import Response


def videocall(request, handler):
    generated_id = str(uuid.uuid4())
    body = request.body.decode()
    room_name = json.loads(body).get("name")
    zoom_collection.insert_one({"id": generated_id, "name": room_name})
    res = Response()
    res.json({"id": generated_id})
    handler.request.sendall(res.to_data())