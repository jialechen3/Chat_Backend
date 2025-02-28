
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

specialChars = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}

def extract_credentials(request):
    body = request.body.decode('utf-8')
    #body: query string username&password
    username = None
    password = None

    pairs = body.split('&')
    for pair in pairs:
        key, value = pair.split('=', 1)
        if key == 'username':
            username = value
        elif key == 'password':
            password = decode_(value)


    return [username, password]


def decode_(s):
    str = []
    i = 0
    while i < len(s):
        if s[i] == '%':
            encode = s[i+1]
            encode += s[i+2]
            parse_int = int(encode, 16)
            char = chr(parse_int)
            str.append(char)
            i += 3
        else:
            str.append(s[i])
            i += 1
    return ''.join(str)

def validate_password(password):
    """0.The length of the password is at least 8
    1.The password contains at least 1 lowercase letter
    2.The password contains at least 1 uppercase letter
    3.The password contains at least 1 number
    4.The password contains at least 1 of the 12 special characters listed above
    5.The password does not contain any invalid characters
    (eg. any character that is not an alphanumeric or one of the 12 special characters)
    """
    if (len(password) < 8) or (not password.contains(specialChars)): #0,4
        return False


    return True