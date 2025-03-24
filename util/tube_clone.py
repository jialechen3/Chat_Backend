import hashlib
import os
import uuid
from datetime import datetime

from util.database import user_collection, video_collection
from util.multipart import parse_multipart
from util.response import Response


def video_upload(request, handler):
    res = Response()
    parts = parse_multipart(request)
    title = ''
    description = ''
    check_type = ''
    video_part = None
    for part in parts.parts:
        if part.name == "title":
            title = part.content
        elif part.name == "description":
            description = part.content
        elif part.headers['Content-Type']:
            check_type = part.headers['Content-Type']
            video_part = part
            break

    video_dir = "public/videos"
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    video_id = str(uuid.uuid4())
    mime_type = check_type

    _type = mime_type.split('/')[1]

    filename = f"{video_id}.{_type}"
    filepath = os.path.join(video_dir, filename)

    # write content to file
    with open(filepath, "wb") as f:
        f.write(video_part.content)

    #####################Update the video data base########################

    auth_cookie = request.cookies.get("auth_token")

    if not auth_cookie:
        res.set_status(400, "No auth cookie")
        res.text("No auth cookie")
        handler.request.sendall(res.to_data())
        return

    auth_token = request.cookies['auth_token']
    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
    user = user_collection.find_one({"auth_token": hashed_token})
    video_collection.insert_one({
        "author_id": user['userid'],
        "title": title.decode(),
        "description": description.decode(),
        'video_path': f"{video_dir}/{filename}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'id': video_id
    })

    data = {'id': video_id}
    res.json(data)
    res.set_status(200, 'ok')
    handler.request.sendall(res.to_data())

def video_get_all(request, handler):
    res = Response()
    videos = video_collection.find()
    video_list = []
    for video in videos:
        video_list.append({
            "author_id": video["author_id"],
            "title": video["title"],
            "description": video["description"],
            "video_path": video["video_path"],
            "created_at": video["created_at"],
            "id": video["id"]
        })
    res.json({'videos': video_list})
    res.set_status(200, 'ok')
    handler.request.sendall(res.to_data())

def video_get_one(request, handler):

    res = Response()
    video_id = request.path.split("/")[3]

    video = video_collection.find_one({"id": video_id})
    video_data = {
        "author_id": video["author_id"],
        "title": video["title"],
        "description": video["description"],
        "video_path": video["video_path"],
        "created_at": video["created_at"] if isinstance(video["created_at"], str) else video["created_at"].strftime(
            '%Y-%m-%d %H:%M:%S'),
        "id": video["id"]
    }
    res.json({'video': video_data})
    res.set_status(200, 'ok')

    handler.request.sendall(res.to_data())


