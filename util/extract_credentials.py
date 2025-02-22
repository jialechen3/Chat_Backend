
#parse the %
'''
123@gmail.com --> 123%40gmail.com   decode this in order
html escape

not do this
password hash
hashlib.sha256(password.encode().hexdigest())
do this with salt


bycrypt lib
result=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
result_id = result.inserted_id
insert hashed password


check password
user = findone({"id"}:bson.objectID(result_id)})
isVerified = bcrypt.checkpw("Password123".encode,user["password"].encode())

'''
def extract_credentials(request):

    body = request.body.decode('utf-8')

    username = None
    password = None

    pairs = body.split('&')
    for pair in pairs:
        key, value = pair.split('=', 1)
        if key == 'username':
            username = value  #username is not percent-encoded
        elif key == 'password':

            password = decode_percent_encoded(value)


    return [username, password]


def decode_percent_encoded(s):
    result = []
    i = 0
    while i < len(s):
        if s[i] == '%':
            # Decode the percent-encoded character
            hex_code = s[i+1:i+3]
            char = chr(int(hex_code, 16))
            result.append(char)
            i += 3
        else:
            # Append the character as-is
            result.append(s[i])
            i += 1
    return ''.join(result)