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
    video_path = f"{file_path}"
    #####creating path for audio
    audio_dir = "public/audios"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    #check for duration
    print("probe path:", video_path)



    probe = ffmpeg.probe(video_path)
    print(probe['format']['duration'])
    output_path = f"{audio_dir}/{video_id}.mp3"
    print('input:',video_path)
    print('output:',output_path)
    video = ffmpeg.input(video_path)
    video = ffmpeg.output(video, output_path, format='mp3')
    ffmpeg.run(video)


    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    file = open(output_path, "rb")  # Open the file in binary read mode
    files = {"file": file}

    print(files)
    response1 = requests.post(API_URL, headers=headers, files=files)

    data = response1.json()
    print(data)
    print(response1.status_code)
    unique_id = data.get("unique_id")
    print("Transcription Request ID:", unique_id)
    response = requests.get(f"https://transcription-api.nico.engineer/transcriptions/{unique_id}", headers=headers)
    print(response.status_code)
    print(response.json())
    if response.status_code != 200:
        print("Transcription request failed")
        res.set_status(400, 'invalid token')
        handler.request.sendall(res.to_data())
        return

    #there will be a s3 url in res and then make another get request
    video_collection.update_one({'id': video_id}, {'$set': {'transcription_id': unique_id}})
    res.set_status(200, 'ok')
    res.text('transcription success')
    handler.request.sendall(res.to_data())