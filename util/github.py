import hashlib
import os
import uuid

from dotenv import dotenv_values, load_dotenv

from util.database import user_collection
from util.response import Response

load_dotenv()

import requests
#1, redirect the user to github user 302
#2. github sends the user back to our server and with a code
#3. your server with then exchange the code for an access token(save it to the databse)
#4. save the user iwth the access token and get their information from the github api
def authgithub(request, handler):
    res = Response()
    CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
    redirect_url = os.environ.get("REDIRECT_URI")
    github_url = "https://github.com/login/oauth/authorize"

    url = f"{github_url}?"
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_url,
        "scope": "user:email,repo",
    }
    for key, value in params.items():
        url += f"{key}={value}&"
    url = url.rstrip("&")
    res.set_status(302, "Found")
    res.headers({"location": url})
    #config = dotenv_values(".env")

    #scope: repo
    #params =
    #requests.get("string", params=params)
    handler.request.sendall(res.to_data())


def authcallback(request, handler):
    res = Response()

    body = request.path

    code = body.split('=')[-1]

    if not code:
        res.set_status(400, "no user")
        handler.request.sendall(res.to_data())
        return

    redirect_ult = "https://github.com/login/oauth/access_token"
    params = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": code,
        "redirect_uri": os.environ.get("REDIRECT_URI")
    }

    response = requests.post(redirect_ult, data=params, headers={"Accept": "application/json"})
    if response.status_code != 200:
        res.status(400, 'invalid token')
        handler.request.sendall(res.to_data())
        return

    data = response.json()
    access_token = response.json().get("access_token")
    if not access_token:
        res.set_status(400, 'no token')
        handler.request.sendall(res.to_data())
        return

    user_url = "https://api.github.com/user"

    response = requests.get(user_url, headers={"Authorization": f"Bearer {access_token}"})
    if response.status_code != 200:
        res.status(400, 'no user')
        handler.request.sendall(res.to_data())
        return

    user = response.json()
    username = user.get("login")
    #email = user.get("email")

    userid = str(uuid.uuid4())
    if not user_collection.find_one({"username": username}):
        user_collection.insert_one({
            "userid": userid,
            "username": username,
            "access_token": access_token,
            "auth_token": '',
            "two-factor": ''
        })
    else:
        user_collection.update_one({'username': username}, {'$set': {"access_token": access_token}})
    auth_token = str(uuid.uuid4())
    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
    cookie_str = auth_token + ";Max-Age=3600;HttpOnly"
    user_collection.update_one({'username': username}, {'$set': {"auth_token": hashed_token}})
    res.cookies({"auth_token": cookie_str})
    res.set_status(302, 'redirect')
    res.text('github logged in')
    res.headers({"location": "/"})

    handler.request.sendall(res.to_data())
