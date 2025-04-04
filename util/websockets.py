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
    #fin bit
    #is the bit count from left to right or right to left
    # ex. | FIN | RSV1 | RSV2 | RSV3 |  OPCODE  |
    #     |  1  |  0   |  0   |  0   |  0001    |
    fin_bit = (socketframe_bytes[0] >> 7) & 1

    opcode = socketframe_bytes & 0x0F
    mask_bit = (socketframe_bytes[1] >> 7) & 1
    #check length is <126
    #01111111
    payload_length = socketframe_bytes[1] & 0x7F
    masking_key = b''
    index = 0
    masking_index = 4
    if payload_length < 126:
        #check bytes to skip in order to get to masking key/payload
        if mask_bit:
            index += 2
            masking_key = socketframe_bytes[index:index+masking_index]
            index += masking_index
            masked_payload = socketframe_bytes[index:index + payload_length]
        else:
            index += 2
            payloads = socketframe_bytes[index:payload_length]
            return WebFrame(fin_bit, opcode, payload_length, payloads)
    elif payload_length >= 126 & payload_length<=0xFFFF:
        if mask_bit:
            index += 4
            masking_key = socketframe_bytes[index:index+masking_index]
            index += masking_index
            masked_payload = socketframe_bytes[index:index + payload_length]
        else:
            index += 4
            payloads = socketframe_bytes[index:payload_length]
            return WebFrame(fin_bit, opcode, payload_length, payloads)
    else:
        if mask_bit:
            index += 10
            masking_key = socketframe_bytes[index:index + masking_index]
            index += masking_index
            masked_payload = socketframe_bytes[index:index + payload_length]
        else:
            index += 10
            payloads = socketframe_bytes[index:payload_length]
            return WebFrame(fin_bit, opcode, payload_length, payloads)

    #if we reach here, we have payload lefts with a masking_key
    payloads = []
    for i in range(payload_length):
        payloads.append(bytes(masked_payload[i] ^ masking_key[i % 4]))

    return WebFrame(fin_bit, opcode, payload_length, payloads)


def generate_ws_frame(payload):
    fin_bit = 1
    opcode = 0x1
    payload_length = len(payload)
    frame_header = bytearray()

    frame_header.append((fin_bit << 7) | (0 << 4) | (0 << 3) | (0 << 2) | opcode)

    if payload_length < 126:
        frame_header.append(payload_length)
    elif payload_length >= 126 & payload_length<=0xFFFF:
        frame_header.append(126)
        frame_header.extend(payload_length.to_bytes(2))
    else:
        frame_header.append(127)
        frame_header.extend(payload_length.to_bytes(8))

    frame_header.extend(payload)

    return bytes(frame_header)