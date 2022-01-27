"""
Version 1.0.0
handle client messages and requests

Author:
Nilusink
"""
from core.server import Connection
import signal
import json
import sys

secret = json.load(open("config.json", "r"))["server_secret"]
serv = Connection(port=3333, server_secret=secret)


def term_func(*sign) -> None:
    """
    called when terminating / ending the server
    """
    print("shutting down server...")
    serv.end()
    sys.exit(sign[0])


# set signals to trigger term_func
signals = [signal.SIGINT, signal.SIGTERM]
for s in signals:
    signal.signal(s, term_func)

# run server
try:
    serv.receive_clients()

except KeyboardInterrupt:
    term_func()
