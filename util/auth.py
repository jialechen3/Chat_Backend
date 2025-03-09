
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
import html

specialChars = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}

def extract_credentials(request):
    body = request.body.decode('utf-8')

    username = None
    password = None
    code = None
    pairs = body.split('&')
    check_pairs = []
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            check_pairs.append((key, value))

    if len(check_pairs) == 2:
        for check_pair in check_pairs:
            key, value = check_pair
            if key == 'username':
                username = value
            elif key == 'password':
                password = decode_(value)
        return [username, password]
    elif len(check_pairs) == 3:
        for check_pair in check_pairs:
            key, value = check_pair
            if key == 'username':
                username = value
            elif key == 'password':
                password = decode_(value)
            elif key == 'totpCode':
                code = value
        result = [username, password, code]
        return result


def decode_(s):
    str = ''
    i = 0
    while i < len(s):
        if s[i] == '%':
            encode = s[i+1]
            encode += s[i+2]
            parse_int = int(encode, 16)
            char = chr(parse_int)
            str+= char
            i += 3
        else:
            str+=(s[i])
            i += 1

    return str

def validate_password(password:str):
    """0.The length of the password is at least 8
    1.The password contains at least 1 lowercase letter
    2.The password contains at least 1 uppercase letter
    3.The password contains at least 1 number
    4.The password contains at least 1 of the 12 special characters listed above
    5.The password does not contain any invalid characters
    (eg. any character that is not an alphanumeric or one of the 12 special characters)
    """
    if len(password) < 8 : #0,4
        return False

    lowercase = False
    uppercase = False
    number = False
    special_inRange = False
    for c in password:
        if c.islower():
            lowercase = True
        elif c.isupper():
            uppercase = True
        elif c.isdigit():
            number = True
        elif c in specialChars:
            special_inRange = True
        else:
            return False

    return lowercase and uppercase and number and special_inRange