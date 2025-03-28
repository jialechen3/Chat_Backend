import os

import ffmpeg
import requests

from util.database import video_collection
from util.response import Response

##########Question to ask: why file not found? What is to be send after getting the vtt file, the data of the response?
def _transcribe(request, handler):

    res = Response()
    #api url: https://transcription-api.nico.engineer/
    redirect_ult = "https://github.com/login/oauth/access_token"
    API_TOKEN = os.environ.get("YOUTUBE_CLONE_API")
    API_URL = "https://transcription-api.nico.engineer/transcribe"
    video_id = request.path.split("/")[3]
    video = video_collection.find_one({"id": video_id})
    if not video:
        res.set_status(404, 'not found')
        handler.request.sendall(res.to_data())

    file_path = video["video_path"]

    #####creating path for audio
    audio_dir = "public/audios"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    output_path = os.path.join(audio_dir, f"{video_id}.mp3")
    print(file_path)
    ffmpeg.input(file_path).output(output_path).run()


    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    with open(output_path, "rb") as f:
        files = {"file": ("audio.mp3", f, "audio/mpeg")}
        response1 = requests.post(API_URL, headers=headers, files=files)

    data = response1.json()
    unique_id = data.get("unique_id")
    print("Transcription Request ID:", unique_id)
    response = requests.get(f"https://transcription-api.nico.engineer/transcriptions/{unique_id}", headers=headers)
    if response.status_code != 200:
        res.set_status(400, 'invalid token')
        handler.request.sendall(res.to_data())
        return
    video_collection.update_one({'id': video_id}, {'$set': {'transcription_id': unique_id}})
    res.set_status(200, 'ok')
    res.text('transcription success')
    handler.request.sendall(res.to_data())