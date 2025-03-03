from dotenv import dotenv_values
import requests
config = dotenv_values(".env")
print(config)
#scope: repo

requests.post("string", params=params)