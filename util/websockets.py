import base64
import hashlib



def compute_accept(websocket):
    specific_key = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    to_compute = websocket + specific_key
    hashed = hashlib.sha1(to_compute.encode()).digest()
    accept_key = base64.b64encode(hashed).decode()
    return accept_key

class WebFrame:
    def __init__(self, fin_bit, opcode, payload_length, payload):
        self.fin_bit = fin_bit
        self.opcode = opcode
        self.payload_length = payload_length
        self.payload = payload


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

    if mask_bit and masking_key:
        unmasked_payload = bytearray()
        for i in range(payload_length):
            unmasked_payload.append(payloads[i] ^ masking_key[i % 4])
        payloads = unmasked_payload

    return WebFrame(fin_bit, opcode, payload_length, payloads)


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
#to get websocket handshake request, get the websocket key from request.headers
#computer acept the key
#set the response header and status code(101) like the slides
#handler.send
#have a loop to check alive(while True:) frame = handler.request.recv(2048)
#parse the frame
#if payload got not equal to length, buffer
#store socket authen user sockets[user_id] = handler.request, after the handler.send
#for socket in sockets: try/except

#def make_connection(request, handler):

