import hashlib
import json
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
        "auth_token": ''
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
    user_collection.update_one({'username': username}, {'$set': {"auth_token": hashed_token}})
    res.cookies({"auth_token": cookie_str})

    ################################################################################################################
    #######if there is a session cookie, change all the message author name remove session cookie#########################################
    for cookie in request.cookies:
        if cookie.startswith('session'):
            session_cookie = request.cookies['session']
            author = str(session_cookie)
            chat = chat_collection.update_many({"author": author}, {"$set": {"author": username}})
            cookie_str = '0;max-age=0;HttpOnly;Secure'
            res.cookies({"session": cookie_str})

    res.set_status(200, 'OK')
    res.text('user logged in')
    handler.request.sendall(res.to_data())

def logout(request, handler):
    res = Response()
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


    #if 'session' in request.cookies:
     #   session_cookie = request.cookies.get('session')
     #   cookie_str = '0;max-age=0;HttpOnly;Secure'
     #   res.cookies({"session": cookie_str})

    cookie_str = '0;max-age=0;HttpOnly;Secure'
    res.cookies({'auth_token': cookie_str})


    user_collection.update_one({'auth_token': hashed_token}, {'$set': {'auth_token': None}})

    res.set_status(302, 'Found')
    res.headers({"location": "/"})
    res.text("User logged out")
    handler.request.sendall(res.to_data())

def get_me(request, handler):
    res = Response()

    logged = False
    auth_token = ''
    for cookie in request.cookies:
        if cookie.startswith('auth_token'):
            auth_token = request.cookies.get('auth_token')
            logged = True
    if auth_token=='':
        res.set_status(400, "Invalid auth token")
        res.json('')
        handler.request.sendall(res.to_data())
        return
    if not logged:
        res.set_status(401, "Unauthorized")
        res.json('')
        handler.request.sendall(res.to_data())
        return
    else:
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
        user = user_collection.find_one({"auth_token": hashed_token})
        user_profile = {
            "username": user["username"],
            "id": user["userid"]
        }
        res.json(user_profile)
        handler.request.sendall(res.to_data())

def search_user(request, handler):
    res = Response()
    body = request.body.decode('utf-8')
    query = ''
    username = ''
    if '?' in request.path:
        query = request.path.split('?')[-1]
        if query:
            for pair in query.split('&'):
                key, value = pair.split('=', 1)
                if key == 'user':
                    username = value
    if username == '':
        res.set_status(200, "OK")
        res.json({})
        handler.request.sendall(res.to_data())
        return

    user = user_collection.find({"username": {"$regex": username}})
    users =  []
    if user:
        for user in user:
            users.append({"id": user["userid"], "username": user["username"]})

    res.json({"users": users})
    handler.request.sendall(res.to_data())



def update_profile(request, handler):
    strl = extract_credentials(request)
    username = strl[0]
    password = strl[1]
    result = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    res = Response()
    if len(password) == 0:
        auth_cookie = request.cookies.get("auth_token")
        hashed_token = hashlib.sha256(auth_cookie.encode()).hexdigest()
        user = user_collection.find_one({'auth_token': hashed_token})
        chat = chat_collection.update_many({"author": user['username']}, {"$set": {"author": username}})
        user_collection.update_one({'auth_token': hashed_token}, {'$set': {"username": username}})
        res.text('user updated')
        handler.request.sendall(res.to_data())

    if not validate_password(password):
        res.set_status(400, 'invalid password')
        res.text('set a stronger password!')
        handler.request.sendall(res.to_data())
        return

    auth_cookie = request.cookies.get("auth_token")
    hashed_token = hashlib.sha256(auth_cookie.encode()).hexdigest()
    user = user_collection.find_one({'auth_token': hashed_token})
    if not auth_cookie:
        res.status(400, "no auth cookie")
        res.text('no auth cookie')
        handler.request.sendall(res.to_data())
        return
    if not user:
        res.status(400, "no auth_token")
        res.text('no auth_token')
        handler.request.sendall(res.to_data())
        return

    hashed_token = hashlib.sha256(auth_cookie.encode()).hexdigest()

    chat = chat_collection.update_many({"author": user['username']}, {"$set": {"author": username}})
    user_collection.update_one({'auth_token': hashed_token}, {'$set': {"password": result, "username": username}})





    res.text('user updated')
    handler.request.sendall(res.to_data())