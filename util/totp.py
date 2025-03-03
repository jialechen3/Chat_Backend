#pip install pyotp
#modify extra_credential to return the third element(The 6 digit code)
#=
import pyotp
secret = pyotp.random_base32()
print(secret)
totp = pyotp.TOTP(secret)
print(totp.now())
code = input()
print ("IsValid", totp.verify(code))