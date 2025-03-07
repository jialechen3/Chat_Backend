#pip install pyotp
#modify extra_credential to return the third element(The 6 digit code)
#=
import hashlib

import pyotp

from util.database import user_collection
from util.response import Response


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



