import hashlib
import os
import uuid

from util.database import user_collection
from util.response import Response

from util.multipart import parse_multipart


def avatar_upload(request, handler):
    res = Response()

    parsed = parse_multipart(request)

    ######################Find the uploaded file##########################
    avatar_part = None
    for part in parsed.parts:
        if part.name == "avatar":
            avatar_part = part
            break

    if not avatar_part:
        res.set_status(400, 'bad request')
        handler.request.sendall(res.to_data())
        return

    #######################Save the uploaded file############################
    img_dir = "public/imgs/profile"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    avatar_id = str(uuid.uuid4())
    mime_type = avatar_part.headers['Content-Type']

    _type = mime_type.split('/')[1]
    #if _type != 'jpeg' or 'jpg' or 'gif' or 'png':
        #res.set_status(400, 'bad request')
        #handler.request.sendall(res.to_data())
    filename = f"{avatar_id}.{_type}"
    filepath = os.path.join(img_dir, filename)

    # write content to file
    with open(filepath, "wb") as f:
        f.write(avatar_part.content)

    #####################Update the user's profile########################

    auth_cookie = request.cookies.get("auth_token")

    if not auth_cookie:
        res.set_status(400, "No auth cookie")
        res.text("No auth cookie")
        handler.request.sendall(res.to_data())
        return

    hashed_token = hashlib.sha256(auth_cookie.encode()).hexdigest()
    user = user_collection.find_one({'auth_token': hashed_token})
    if not user:
        res.set_status(400, "Invalid auth token")
        res.text("Invalid auth token")
        handler.request.sendall(res.to_data())
        return

    user_collection.update_one({'auth_token': hashed_token}, {'$set': {'imageURL': f"{img_dir}/{filename}"}})


    res.set_status(200, 'ok')
    handler.request.sendall(res.to_data())