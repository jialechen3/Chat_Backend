import hashlib
import json
import os
import uuid
from cgitb import handler
from datetime import datetime

import ffmpeg
import requests

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
    if not os.path.exists("public/imgs/thumbnails"):
        os.makedirs("public/imgs/thumbnails")

    video_id = str(uuid.uuid4())
    mime_type = check_type

    _type = mime_type.split('/')[1]

    filename = f"{video_id}.{_type}"
    filepath = f'{video_dir}/{filename}'

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


    ########make the thumbnail###########
    probe = ffmpeg.probe(filepath)

    frames, thumbnail = extract_frames(filepath)

    video_collection.insert_one({
        "author_id": user['userid'],
        "title": title.decode(),
        "description": description.decode(),
        'video_path': filepath,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'id': video_id,
        'transcription_id': '',
        'thumbnails': frames,
        'thumbnailURL': thumbnail
    })

    ###########Make the transcription############
    duration = float(probe['format']['duration'])

    if duration <= 60:
        _transcribe(video_id)




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
            "id": video["id"],
            'transcription_id': video["transcription_id"],
            'thumbnails': video["thumbnails"],
            'thumbnailURL': video["thumbnailURL"]
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
        "created_at": video["created_at"],
        "id": video["id"],
        'transcription_id': video["transcription_id"],
        'thumbnails': video["thumbnails"],
        'thumbnailURL': video["thumbnailURL"]
    }
    res.json({'video': video_data})
    res.set_status(200, 'ok')

    handler.request.sendall(res.to_data())










##########Question to ask: why file not found? What is to be send after getting the vtt file, the data of the response?
def _transcribe(id):

    res = Response()
    #api url: https://transcription-api.nico.engineer/
    redirect_ult = "https://github.com/login/oauth/access_token"
    API_TOKEN = os.environ.get("YOUTUBE_CLONE_API")
    API_URL = "https://transcription-api.nico.engineer/transcribe"
    video_id = id
    video = video_collection.find_one({"id": video_id})
    if not video:
        return False

    file_path = video["video_path"]
    video_path = f"{file_path}"
    #####creating path for audio
    audio_dir = "public/audios"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    #check for duration



    probe = ffmpeg.probe(video_path)
    duration = float(probe['format']['duration'])
    if duration > 60:
        return False
    output_path = f"{audio_dir}/{video_id}.mp3"

    audio_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "audio"]

    if not audio_streams:
        print("no audio streams")
        return False

    video = ffmpeg.input(video_path)
    video = ffmpeg.output(video, output_path, format='mp3')
    ffmpeg.run(video)
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    file = open(output_path, "rb")  # Open the file in binary read mode
    files = {"file": file}

    response1 = requests.post(API_URL, headers=headers, files=files)

    data = response1.json()

    unique_id = data.get("unique_id")
    video_collection.update_one({'id': video_id}, {'$set': {'transcription_id': unique_id}})


    return True






def endpoint_transcription(request, handler):
    res = Response()
    API_TOKEN = os.environ.get("YOUTUBE_CLONE_API")
    myid = request.path.split("/")[3]
    video = video_collection.find_one({'id': myid})
    transcription_id = video["transcription_id"]
    header = {'Authorization': f'Bearer {API_TOKEN}'}
    response = requests.get(f"https://transcription-api.nico.engineer/transcriptions/{transcription_id}", headers=header)

    if response.status_code != 200:
        res.set_status(400, 'transcription not exist')
        handler.request.sendall(res.to_data())
        return

    response = requests.get(response.json().get("s3_url"))
    res.bytes(response.content)


    res.set_status(200, 'success')
    handler.request.sendall(res.to_data())


def extract_frames(filepath, num_frames=5, output_dir="public/imgs/thumbnails"):
    thumbnail_path = ''
    # Get video duration
    probe = ffmpeg.probe(filepath)
    duration = float(probe['format']['duration'])

    # Calculate frame positions (0%, 25%, 50%, 75%, 100%)
    positions = [0, duration * 0.25, duration * 0.5, duration * 0.75, max(0.0, (duration - 1.0))]

    path_array = []
    for i, pos in enumerate(positions):
        frame_id = str(uuid.uuid4())
        frame_path = f"{output_dir}/{frame_id}.jpg"

        # Extract frame
        (
            ffmpeg.input(filepath, ss=pos)
            .output(frame_path, vframes=1, update=1)
            .run(overwrite_output=True)
        )
        path_array.append(frame_path)

        # First frame becomes thumbnail
        if i == 0:
            thumbnail_path = frame_path

    return path_array, thumbnail_path

def set_thumbnail(request, handler):
    res = Response()
    print('in the function')
    video_id = request.path.split("/")[3]
    body = request.body.decode()
    url = json.loads(body).get("thumbnailURL")

    print(url)
    video_collection.update_one({'id': video_id}, {'$set': {'thumbnailURL': url}})
    res.json({'message': 'change thumbnail success'})
    handler.request.sendall(res.to_data())


