"""
Beta 0.0.1
Write and receive messages

Author:
Nilusink
"""
from core.client import *

secrets = json.load(open("config.json", "r"))
server_secret = secrets["server_secret"]
client_secret = secrets["client_secret"]

c = Connection("127.0.0.1", 3333, "Niclas", server_secret, client_secret)
while True:
    mes = input(">> ")
    if mes:
        c.send_message(mes)
