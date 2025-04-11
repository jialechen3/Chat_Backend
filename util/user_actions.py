import bcrypt

import os
import uuid
import html
import hashlib
import pyotp

from util.multipart import parse_multipart
from util.auth import extract_credentials
from util.auth import validate_password
from util.database import chat_collection, user_collection



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
        "auth_token": '',
        "two-factor": '',
        "imageURL": ''
    })
    res.text('account created')
    handler.request.sendall(res.to_data())

def login(request, handler):
    strl = extract_credentials(request)
    res = Response()
    username = strl[0]
    password = strl[1]
    code = None
    if len(strl) == 3:
        code = strl[2]
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
    cookie_str = auth_token + ";Max-Age=3600;HttpOnly"
    user_collection.update_one({'username': username}, {'$set': {"auth_token": hashed_token}})
    res.cookies({"auth_token": cookie_str})

    #############################Check for Two Factor####################################################################
    if user["two-factor"] != '':
        if not code:
            res.set_status(401, "Two-factor authentication")
            handler.request.sendall(res.to_data())
            return


        totp = pyotp.TOTP(user["two-factor"])
        if not totp.verify(code):
            res.set_status(400, "Invalid")
            res.text(json.dumps({"Invalid code"}))
            handler.request.sendall(res.to_data())
            return

    ################################################################################################################
    #######if there is a session cookie, change all the message author name remove session cookie#########################################
    for cookie in request.cookies:
        if cookie.startswith('session'):
            session_cookie = request.cookies['session']
            author = str(session_cookie)
            chat = chat_collection.update_many({"author": author}, {"$set": {"author": username}})
            cookie_str = 'no;Max-Age=0;HttpOnly'
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

    cookie_str = 'no;Max-Age=0;HttpOnly'
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
    print("TEST type:", _type)
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


def nickname(request,handler):
    res = Response()
    name = json.loads(request.body.decode()).get('nickname')
    escaped_name = html.escape(name)
    session_cookie = request.cookies['session']
    author = str(session_cookie)
    chat = chat_collection.update_many({"author": author},{"$set": {"nickname": escaped_name}})
    res.text('set nickname success')
    handler.request.sendall(res.to_data())


def generateTwoFac(request, handler):
    secret = pyotp.random_base32()


    res =Response()
    data = {"secret": secret}
    res.json(data)

    #######################Data base thing update two factor check####################################################
    auth_token = request.cookies.get('auth_token')
    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
    user = user_collection.find_one({"auth_token": hashed_token})
    user_collection.update_one({'auth_token': hashed_token}, {'$set': {"two-factor": secret}})
    ##################################################################################################################

    handler.request.sendall(res.to_data())



from util.database import chat_collection
from util.response import Response


def emoji_create(request, handler):
    res = Response()
    mes_id = request.path.split("/")[-1]
    emoji = json.loads(request.body.decode()).get('emoji')
    user_db = chat_collection.find_one({'id': mes_id})
    reaction = user_db['reactions']
    session_cookie = request.cookies['session']
    author = str(session_cookie)

    # if emoji in reaction:

    if emoji in reaction:#if the emoji exist in the dict
        user_found = False
        for key in reaction[emoji]:#search the values in that emoji to see if the user is there
            if key == author:
                user_found = True
                res.set_status(403, 'forbid')
                res.text('you already have this reaction')
                handler.request.sendall(res.to_data())
                return

        if not user_found:
            rea_str = reaction[emoji]
            rea_str.append(author)
            chat_collection.update_one({'id': mes_id}, {'$set': {f"reactions.{emoji}": rea_str}})

    else:
        chat_collection.update_one({'id': mes_id}, {'$set': {f"reactions.{emoji}": [author]}})

    res.text('emoji added')
    handler.request.sendall(res.to_data())


import json



def emoji_delete(request, handler):
    res = Response()
    mes_id = request.path.split("/")[-1]
    emoji = json.loads(request.body.decode()).get('emoji')
    user_db = chat_collection.find_one({'id': mes_id})
    reaction = user_db['reactions']
    session_cookie = request.cookies['session']
    author = str(session_cookie)

    user_found = False
    for key in reaction[emoji]:
        if key == author:
            chat_collection.update_one({'id': mes_id}, {'$pull': {f"reactions.{emoji}": author}})
            user_found = True
            updated_db = chat_collection.find_one({'id': mes_id})
            updated_reaction = updated_db['reactions']
            if not updated_reaction[emoji]:
                chat_collection.update_one({'id': mes_id}, {'$unset': {f"reactions.{emoji}": ""}})
    if not user_found:
        res.set_status(403, 'forbid')
        res.text('you dont have any reaction with this message')
        handler.request.sendall(res.to_data())
        return
    res.text('emoji deleted')
    handler.request.sendall(res.to_data())
