import hashlib
import html
import json
import os
import uuid
import requests
import bson.json_util

from util.database import chat_collection, user_collection
from util.github import handler_command, repos, star, createissue
from util.response import Response


def chat_create(request, handler):
    res = Response()
    #since: Request (JSON): {"content": string}
    data = json.loads(request.body.decode('utf-8'))
    #get the content from the dict
    content = data.get('content')

    #html escape
    content = html.escape(content)
    session_cookie = 'empty'
    message_id = str(uuid.uuid4())

    #generate path for profile img
    public_dir = "public/imgs"
    img_dir = "public/imgs/profile"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    #end generating path
    logged = False
    for cookie in request.cookies:
        if cookie.startswith('auth_token'):
            logged = True

    ############################################Github Api Command#################################################
    if content[0] == '/':
        if not logged:
            print("Test2: not logged")
            res.set_status(400, 'forbidden')
            res.text('you are not logged in')
            handler.request.sendall(res.to_data())
            return

        auth_token = request.cookies.get('auth_token')
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
        user = user_collection.find_one({"auth_token": hashed_token})
        if not 'access_token' in user:
            res.set_status(400, 'forbidden')
            res.text('you are not github user')
            handler.request.sendall(res.to_data())
            return
        else:
            access_token = user['access_token']
            parts = content.split(" ", 1)
            command = parts[0]  #("/repos")
            args = parts[1:]  #(["user"])

            if not handler_command(command, args, user['access_token']):
                res.set_status(400, 'forbidden')
                print(args)
                res.text('wrong command')
                handler.request.sendall(res.to_data())
                return
            else:
                if command == "/star":
                    if star(command, args, user['access_token']) == 204:
                        link = f"https://github.com/{args[0]}"
                        content = f"Starred: <a href='{link}' target='_blank'>repo:{args[0]}</a>"
                    elif star(command, args, user['access_token']) == 304:
                        link = f"https://github.com/{args[0]}"
                        content = f"Already Starred: <a href='{link}' target='_blank'>repo:{args[0]}</a>"
                    else:
                        res.set_status(400, 'forbidden')
                        res.text('no repo')
                        handler.request.sendall(res.to_data())
                        return
                elif command == "/repos":
                    content = ("<br>The repo for this user:<br>" + handler_command(command, args, user['access_token']))
                elif command == "/createissue":
                    arg = args[0].split(' ', 1)
                    if createissue(command, arg, user['access_token']) == 201:
                        repo = arg[0]
                        print("repo: ", repo)
                        url = f"https://github.com/{repo}"
                        content = f"Issue created: <a href='{url}' target='_blank'>repo:{arg[0]}</a>"
                        print(content)
                    else:
                        res.set_status(400, 'forbidden')
                        res.text('no repo for issue create')
                        handler.request.sendall(res.to_data())
                        return
    ############################################END GITHUB#########################################################


    #####################################if there is a session cookie######################################
    for cookie in request.cookies:
        if cookie.startswith('session'):
            session_cookie = request.cookies['session']
            author = str(session_cookie)
            cookie_str = author + "; Expires=Wed, 21 Oct 2025 07:28:00 GMT; Secure; Path=/"

            #I am finding the nickname for this author id
            #end nickname

            res.cookies({"session": cookie_str})
            if not logged:
                name = chat_collection.find_one({"author": session_cookie})
                update_nickname = name['nickname']
                chat_collection.insert_one({
                    "author": session_cookie,
                    "id": message_id,
                    "content": content,
                    "updated": False,
                    "reactions": {},
                    "nickname": update_nickname,
                    "imageURL": f"public/imgs/profile/avatar_{author}.svg"
                })
            else:
                auth_token = request.cookies['auth_token']
                hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
                user = user_collection.find_one({"auth_token": hashed_token})
                update_nickname = ''
                name = chat_collection.find_one({"author": user['username']})
                if name:
                    update_nickname = name['nickname']
                chat_collection.insert_one({
                    "author": user['username'],
                    "id": message_id,
                    "content": content,
                    "updated": False,
                    "reactions": {},
                    "nickname": update_nickname,
                    "imageURL": f"public/imgs/profile/avatar_{author}.svg"
                })
    ##########################################################################################


    ##########################################################################################
    ####################''''''''No session cookie''''''''''####################################
    ###########################################################################################
    if session_cookie == 'empty':
        session_cookie = uuid.uuid4()
        author = str(session_cookie)


        #######################################################################################
        #adding profile img
        #adding img
        url = f'https://api.dicebear.com/9.x/fun-emoji/svg?seed={author}'
        response = requests.get(url)
        filename = f"avatar_{author}.svg"  # filename unique
        filepath = os.path.join(img_dir, filename)
        # write content to file
        with open(filepath, "wb") as f:
            f.write(response.content)
        #end adding image
        ########################################################################################


        ####################################################################
        #if user logged in
        if logged:
            auth_token = request.cookies['auth_token']
            hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
            user = user_collection.find_one({"auth_token": hashed_token})
            chat_collection.insert_one({
                "author": user['username'],
                "id": message_id,
                "content": content,
                "updated": False,
                "reactions": {},
                "nickname": "",
                "imageURL": f"public/imgs/profile/avatar_{author}.svg"
            })
        ######################################################################

        if not logged:
            cookie_str = author + "; Expires=Wed, 29 Oct 2025 07:28:00 GMT; HttpOnly; Secure; Path=/"
            res.cookies({"session": cookie_str})
            chat_collection.insert_one({
                "author": author,
                "id": message_id,
                "content": content,
                "updated": False,
                "reactions": {},
                "nickname": "",
                "imageURL": f"public/imgs/profile/avatar_{author}.svg"
            })




    # Send response
    res.set_status(200, 'OK')

    res.bytes(b'message sent')
    res.headers({'Content-Type': 'application/json'})
    handler.request.sendall(res.to_data())


def chat_delete(request, handler):

    res = Response()
    mes_id = request.path.split("/")[3]
    #print("Message id:" + mes_id)
    mes = chat_collection.find_one({'id': mes_id})
    # get the user id inside the database
    current_id = request.cookies.get('session')
    logged = False

    for cookie in request.cookies:
        if cookie.startswith('auth_token'):
            logged = True

    if logged:
        auth_token = request.cookies.get('auth_token')
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
        user = user_collection.find_one({'auth_token': hashed_token})
        if mes['author'] != user['username']:
            res.set_status(403, 'Forbidden')
            res.text('fail, you are not the user')
        else:
            chat_collection.delete_one({'id': mes_id})
            res.set_status(200, 'ok')
            res.text('text update success')
    else:
        if mes['author'] != current_id:
            res.set_status(403, 'Forbidden')
            res.text('fail, you are not the user')
        else:
            chat_collection.delete_one({"id": mes_id})
            res.set_status(200, 'ok')
            res.text('text delete success')

    res.headers({'Content-type': 'application/json'})
    handler.request.sendall(res.to_data())





def chat_get(request, handler):

    res = Response()
    mes = chat_collection.find() #get all messages inside the database

    message = bson.json_util.dumps({"messages": mes})

    res.set_status(200, 'OK')

    res.text(message)
    res.headers({'Content-Type': 'application/json'})

    handler.request.sendall(res.to_data())



def chat_update(request, handler):
    res = Response()

    mes_id = request.path.split("/")[3]

    mes = chat_collection.find_one({'id': mes_id}) #get the mes id inside the database

    logged = False

    for cookie in request.cookies:
        if cookie.startswith('auth_token'):
            logged = True



    current_id = request.cookies.get('session')

    if logged:
        auth_token = request.cookies.get('auth_token')
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
        user = user_collection.find_one({'auth_token': hashed_token})
        if mes['author']!=user['username']:
            res.set_status(403, 'Forbidden')
            res.text('fail, you are not the user')
        else:
            cont = json.loads(request.body.decode())
            real_content = cont.get('content')
            real_content = html.escape(real_content)
            chat_collection.update_one({'id': mes_id}, {'$set': {'content': real_content, 'updated': True}})
            res.set_status(200, 'ok')
            res.text('text update success')

    else:
        if mes['author']!=current_id:
            res.set_status(403, 'Forbidden')
            res.text('fail, you are not the user')
        else:
            cont = json.loads(request.body.decode())
            real_content = cont.get('content')
            real_content = html.escape(real_content)
            chat_collection.update_one({'id': mes_id}, {'$set': {'content': real_content, 'updated': True}})
            res.set_status(200, 'ok')
            res.text('text update success')


    #res.text(request.body.decode())

    res.headers({'Content-type': 'application/json'})
    handler.request.sendall(res.to_data())









