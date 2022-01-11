"""
Beta 0.0.1
handle client messages and requests

Author:
Nilusink
"""
from core.server import Connection
import json
import sys

secret = json.load(open("config.json", "r"))["server_secret"]
s = Connection(port=3333, server_secret=secret)
try:
    s.receive_clients()

except KeyboardInterrupt:
    s.end()
    sys.exit(0)
