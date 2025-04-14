import base64
import hashlib
import json
import uuid
from datetime import datetime, timezone
from util.database import drawing_collection, user_collection, dm_collection, zoom_collection
from util.response import Response



def compute_accept(websocket):
    specific_key = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    to_compute = websocket + specific_key
    hashed = hashlib.sha1(to_compute.encode()).digest()
    accept_key = base64.b64encode(hashed).decode()
    return accept_key

class WebFrame:
    def __init__(self, fin_bit, opcode, payload_length, payload, frame_length):
        self.fin_bit = fin_bit
        self.opcode = opcode
        self.payload_length = payload_length
        self.payload = payload
        self.frame_length = frame_length

def parse_ws_frame(socketframe_bytes):
    fin_bit = (socketframe_bytes[0] >> 7) & 1
    opcode = socketframe_bytes[0] & 0x0F
    mask_bit = (socketframe_bytes[1] >> 7) & 1
    payload_length = socketframe_bytes[1] & 0x7F

    index = 2
    masking_key = b''
    if payload_length == 126:
        payload_length = int.from_bytes(socketframe_bytes[index:index + 2], byteorder='big')
        index += 2
    elif payload_length == 127:
        payload_length = int.from_bytes(socketframe_bytes[index:index + 8], byteorder='big')
        index += 8

    if mask_bit:
        masking_key = socketframe_bytes[index:index + 4]
        index += 4
    payloads = socketframe_bytes[index:index + payload_length]
    frame_length = index + payload_length
    if mask_bit and masking_key:
        unmasked_payload = bytearray()
        for i in range(payload_length):
            unmasked_payload.append(payloads[i] ^ masking_key[i % 4])
        payloads = unmasked_payload

    return WebFrame(fin_bit, opcode, payload_length, payloads, frame_length)


def generate_ws_frame(payload):
    fin_bit = 1
    opcode = 0x1
    payload_length = len(payload)
    frame_header = bytearray()

    frame_header.append((fin_bit << 7) | opcode)

    if payload_length < 126:
        frame_header.append(payload_length)
    elif payload_length <= 0xFFFF:
        frame_header.append(126)
        frame_header.extend(payload_length.to_bytes(2, 'big'))
    else:
        frame_header.append(127)
        frame_header.extend(payload_length.to_bytes(8, 'big'))

    frame_header.extend(payload)

    return bytes(frame_header)



sockets = {}
dms_sockets = {}
frames = []
incall_sockets = {}

def socket_function(request, handler):
    random_id = ''
    res = Response()
    ##########set up database################
    if not drawing_collection.find_one({"strokes": {"$exists": True}}):
        drawing_collection.insert_one({"strokes": []})
    sec_websocket_key = request.headers.get("Sec-WebSocket-Key")
    accept = compute_accept(sec_websocket_key)
    res.headers({"Upgrade": 'websocket'})
    res.headers({"Connection": 'Upgrade'})
    res.headers({"Sec-WebSocket-Accept": accept})
    res.set_status(101, 'Switching Protocols')
    #########WS connection made###################
    handler.request.sendall(res.to_data())
    ###########Sends the drawing history############
    stro = drawing_collection.find_one({"strokes": {"$exists": True}})
    strokes = stro["strokes"]
    response = {
        "messageType": "init_strokes",
        "strokes": strokes
    }
    response_json = json.dumps(response).encode()
    response_frame = generate_ws_frame(response_json)
    handler.request.sendall(response_frame)



    ################stores the connection######################
    auth_token = request.cookies.get('auth_token')
    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
    user = user_collection.find_one({"auth_token": hashed_token})
    ###########id: request###################
    sockets[user['userid']] = handler.request
    #######################Update userlist#########################
    user_ids = list(sockets.keys())
    users_data = user_collection.find({"userid": {"$in": user_ids}})
    user_list = [{"username": user["username"]} for user in users_data]
    response = {"messageType": "active_users_list", "users": user_list}
    response_json = json.dumps(response).encode()
    response_frame = generate_ws_frame(response_json)
    for user_id, sock in list(sockets.items()):
        try:
            sock.sendall(response_frame)
        except:
            del sockets[user_id]

    buffer = b''
    payloads_buffer = b''
    isContinuous = False
    while True:
        try:
            data = handler.request.recv(2048)
            if not data:
                break
            buffer += data


            while True:
                if len(buffer) < 2:
                    break
                frame = parse_ws_frame(buffer)
                if frame is None:
                    break

                while frame.payload_length > len(buffer):
                    chunk = handler.request.recv(2048)
                    if not chunk:
                        return
                    buffer += chunk
                    frame = parse_ws_frame(buffer)
                buffer = buffer[frame.frame_length:]
                if frame.fin_bit == 0:
                    payloads_buffer += frame.payload
                    isContinuous = True
                    continue
                if isContinuous:
                    payloads_buffer += frame.payload
                if frame.opcode == 0x8:
                    ##########Clean up zoom room#######################################################################
                    call_id = incall_sockets[random_id]["callId"]
                    zoom_collection.update_one(
                        {"id": call_id},
                        {"$pull": {"sockets": random_id}}
                    )
                    del incall_sockets[random_id]
                    room = zoom_collection.find_one({"id": call_id})
                    user_left_msg = {
                        "messageType": "user_left",
                        "socketId": random_id
                    }
                    msg_bytes = generate_ws_frame(json.dumps(user_left_msg).encode())
                    for s_id in room["sockets"]:
                        if s_id in incall_sockets:
                            incall_sockets[s_id]["socket"].sendall(msg_bytes)

                    ######################################################################################################
                    del sockets[user['userid']]
                    user_ids = list(sockets.keys())
                    users_data = user_collection.find({"userid": {"$in": user_ids}})
                    user_list = [{"username": user["username"]} for user in users_data]
                    response = {"messageType": "active_users_list", "users": user_list}
                    response_json = json.dumps(response).encode()
                    response_frame = generate_ws_frame(response_json)
                    for user_id, sock in list(sockets.items()):
                        try:
                            sock.sendall(response_frame)
                        except:
                            del sockets[user_id]
                    return

                try:
                    #if continuous read from the payload buffer array
                    if isContinuous:
                        payload_str = payloads_buffer.decode()
                    else:
                        payload_str = frame.payload.decode()
                    msg = json.loads(payload_str)
                    payloads_buffer = b''
                except :
                    continue



                if msg.get("messageType") == "echo_client":
                    response = {
                        "messageType": "echo_server",
                        "text": msg.get("text", "")
                    }
                    response_json = json.dumps(response).encode()
                    response_frame = generate_ws_frame(response_json)
                    handler.request.sendall(response_frame)
                elif msg.get("messageType") == "drawing":
                    response = msg
                    response_json = json.dumps(response).encode()
                    response_frame = generate_ws_frame(response_json)
                    #handler.request.sendall(response_frame)
                    for user_id, sock in list(sockets.items()):
                        try:
                            sock.sendall(response_frame)
                        except:
                            del sockets[user_id]
                    msg.pop("messageType", None)
                    drawing_collection.update_one(
                        {"strokes": {"$exists": True}},
                        {"$push": {"strokes": msg}}
                    )


                #################for dms###############################
                elif msg.get("messageType") == "get_all_users":
                    users = user_collection.find({})
                    user_list = [{"username": user["username"]} for user in users]

                    response = {"messageType": "all_users_list", "users": user_list}
                    response_json = json.dumps(response).encode()
                    response_frame = generate_ws_frame(response_json)
                    handler.request.sendall(response_frame)
                elif msg.get("messageType") == "direct_message":
                    current_user = user["username"]
                    response = {
                        "messageType": "direct_message",
                        "fromUser": current_user,
                        "text": msg.get("text", "")
                    }
                    dm_collection.insert_one({
                        "fromUser": current_user,
                        "toUser": msg.get("targetUser",""),
                        "text": msg.get("text", ""),
                        "timestamp": datetime.now(timezone.utc)
                    })
                    ####send the dm to both clients
                    for user_id, info in list(dms_sockets.items()):
                        user = user_collection.find_one({"userid": user_id})
                        target = info.get("target")

                        if (
                                (user["username"] == current_user and target == msg.get("targetUser"))
                                or
                                (user["username"] == msg.get("targetUser") and target == current_user)
                        ):
                            response_json = json.dumps(response).encode()
                            response_frame = generate_ws_frame(response_json)
                            info["socket"].sendall(response_frame)

                elif msg.get("messageType") == "select_user":
                    current_user = user["username"]
                    target_user = msg.get("targetUser", "")
                    if target_user == current_user:
                        return
                    #store this dms socket

                    dms_sockets[user["userid"]] = {"socket": handler.request, "target": target_user}

                    ##############Getting all the direct message data from the two users only
                    messages = dm_collection.find(
                        {
                            "$or": [
                                {"fromUser": current_user, "toUser": target_user},
                                {"fromUser": target_user, "toUser": current_user}
                            ]
                        }
                    ).sort("timestamp", 1)

                    message_list = []
                    for ms in messages:
                        message_list.append({
                            "messageType": "direct_message",
                            "fromUser": ms["fromUser"],
                            "text": ms["text"]
                        })
                    response = { "messageType": "message_history",
                                 "messages": message_list}
                    response_json = json.dumps(response).encode()
                    response_frame = generate_ws_frame(response_json)
                    handler.request.sendall(response_frame)

                    #####################for zoom##############################
                elif msg.get("messageType") == "get_calls":
                    all_rooms = []
                    room_data = zoom_collection.find({})
                    for room in room_data:
                        all_rooms.append({"id": room["id"], "name": room["name"]})
                    response = {"messageType": "call_list",
                                "calls": all_rooms}
                    response_json = json.dumps(response).encode()
                    response_frame = generate_ws_frame(response_json)
                    handler.request.sendall(response_frame)
                elif msg.get("messageType") == "join_call":
                    # contains: {"messageType":"join_call", "callId":"67e426f9042e96b4cfaa70f2"}
                    # Sent by your server when a user joins a call. Contains the name of the room
                    # return: {"messageType":"call_info", "name":"meeting"}

                    room = zoom_collection.find_one({"id": msg.get("callId")})
                    response = {"messageType": "call_info",
                                "name": room['name']}
                    response_json = json.dumps(response).encode()
                    response_frame = generate_ws_frame(response_json)
                    handler.request.sendall(response_frame)
                    # another return: {"messageType": "existing_participants", "participants": [{"socketId": "febd4d3a-9e61-4a95-8e52-37ba64e2674c", "username": "admin"}, ... ]}
                    user_list = []
                    for socket_id, info in incall_sockets.items():
                        if info.get("callId") == msg.get("callId"):
                            user_list.append({
                                "socketId": str(socket_id),
                                "username": info["username"]
                            })
                    random_id = str(uuid.uuid4())
                    zoom_collection.update_one({"id": msg.get("callId")}, {"$push": {"sockets": str(random_id)}})
                    room = zoom_collection.find_one({"id": msg.get("callId")})
                    incall_sockets[random_id] = {
                        "username": user["username"],
                        "socket": handler.request,
                        "callId": msg.get("callId")
                    }
                    socket = incall_sockets[random_id]["socket"]
                    response = {"messageType": "existing_participants", "participants": user_list}
                    response_json = json.dumps(response).encode()
                    response_frame = generate_ws_frame(response_json)
                    socket.sendall(response_frame)
                    ##########Boardcast to all users in the room############################
                    # Get all the sockets stores in the room db
                    # {"messageType": "user_joined", "socketId": "0a8e1a10-7f20-4797-bd3e-628735f91216", "username": "jesse"}
                    response = {"messageType": "user_joined", "socketId": random_id, "username": user["username"]}
                    for socket_id in room["sockets"]:
                        if socket_id != random_id:
                            frame = generate_ws_frame(json.dumps(response).encode())
                            incall_sockets[socket_id]["socket"].sendall(frame)

                    # messageType - "offer", "answer", and "ice_candidate"
                elif msg.get("messageType") in ["offer", "answer", "ice_candidate"]:
                    target_id = msg.get("socketId")
                    target = incall_sockets[target_id]["socket"]
                    to_sent = msg.copy()
                    to_sent["socketId"] = random_id
                    to_sent["username"] = user["username"]
                    response_json = json.dumps(to_sent).encode()
                    response_frame = generate_ws_frame(response_json)
                    target.sendall(response_frame)


        except Exception as e:
            continue


#AO testing: while connection open
# grab bytes check payload length
# check bytes you have stores extra for later use
# check for header length too
# continouation frame: check finbit or save for later
# only handle one frame per loop
# ao 1 testing: go to front code where is sends the message duplicate it three times, it becomes back to back frame