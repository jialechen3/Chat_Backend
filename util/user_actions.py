import hashlib
import uuid

import bcrypt
import bson

from util.auth import extract_credentials
from util.auth import validate_password
from util.database import chat_collection, user_collection
from util.response import Response


def register(request, handler):
    strl = extract_credentials(request)
    username = strl[0]
    password = strl[1]
    print('see password'+password)
    res= Response()
    if not validate_password(password):
        res.set_status(400, 'invalid password')
        res.text('set a stronger password!')
        handler.request.sendall(res.to_data())
        return


    if user_collection.find_one({"username": username}):
        res.set_status(400, "user already exists")
        res.text("username already exists")
        handler.request.sendall(res.to_data())
        return

    result = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    userid = str(uuid.uuid4())
    user_collection.insert_one({
        "userid": userid,
        "username": username,
        "password": result,
        "user_token": ''
    })
    res.text('account created')
    handler.request.sendall(res.to_data())

def login(request, handler):
    strl = extract_credentials(request)
    res = Response()
    username = strl[0]
    password = strl[1]
    user = user_collection.find_one({"username":username})

    if not user:
        res.set_status(400, "user not exist")
        res.text("username does not exist")
        handler.request.sendall(res.to_data())
        return

    if not bcrypt.checkpw(password.encode(), user["password"]):
        res.set_status(400, "Wrong password")
        res.text("Incorrect password")
        handler.request.sendall(res.to_data())
        return

    auth_token = str(uuid.uuid4())
    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
    cookie_str = auth_token + "; max-age=3600; HttpOnly; Secure"
    user_collection.update_one({'username': username}, {'$set': {"user_token": hashed_token}})
    res.cookies({"auth_token": cookie_str})

    ################################################################################################################
    #######if there is a session cookie, change all the message author name#########################################
    for cookie in request.cookies:
        if cookie.startswith('session'):
            session_cookie = request.cookies['session']
            author = str(session_cookie)
            chat = chat_collection.update_many({"author": author}, {"$set": {"author": username}})


    res.set_status(200, 'OK')
    res.text('user logged in')
    handler.request.sendall(res.to_data())

def logout(request, handler):
    res = Response()
    auth_cookie = request.cookies.get('auth_token')
    for cookie in request.cookies:
        if cookie.startswith('session'):
            print('logout cookie')
            cookie = request.cookies.get('session')
            session_cookie = cookie + "; max-age=0; HttpOnly; Secure"
            res.cookies({"session": session_cookie})
    #auth_cookie = cookie.split(';')[0]
    cookie_str = auth_cookie + "; max-age=0; HttpOnly; Secure"
    res.cookies(({"auth_token": cookie_str}))



    res.set_status(302, 'Found')
    res.text("user logged out")
    handler.request.sendall(res.to_data())


