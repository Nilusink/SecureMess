"""
Version 1.0.2
Write and receive messages (terminal only)

Author:
Nilusink
"""
from sys import platform, exit as s_exit
from core.client import Connection
from traceback import format_exc
from core import InvalidSecret
from threading import Thread
from time import sleep
import signal
import json
import os

CONNECTED: bool = False


class Colors:
    """
    for better looks
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def fail(error_msg: str) -> None:
    """
    print a error message in red
    """
    print(f"{Colors.FAIL}{error_msg}{Colors.ENDC}")


def success(success_msg: str) -> None:
    """
    print a success message in green
    """
    print(f"{Colors.OKGREEN}{success_msg}{Colors.ENDC}")


class MessageUpdater:
    def __init__(self, c: Connection, update_delay: float = 0.2) -> None:
        self.__connection = c
        self.update_delay = update_delay
        self.running: bool = True

        # later used variables
        self.__done_messages: list = []

    def run(self) -> None:
        """
        receive messages while self.running
        """
        while self.running:
            for message in self.__connection.new_messages:
                if message not in self.__done_messages:
                    print(f"\r{message['user']}>> {message['message']}", end="\n>> ")
                    self.__done_messages.append(message)

            sleep(self.update_delay)

    def run_thread(self) -> None:
        """
        run self.run in a thread
        """
        Thread(target=self.run).start()


def main() -> int:
    """
    main program, all the code runs here

    """
    global CONNECTED, C, MU
    try:
        print(f"Starting client Headless...")
        # load keys from file
        secrets = json.load(open("config.json", "r"))

        # getting user input and trying to connect to the server
        while not CONNECTED:
            try:
                # get connection data from user
                ip = input(f"\n{Colors.HEADER}Server IP: {Colors.OKCYAN}")
                port = int(input(f"{Colors.HEADER}Server PORT: {Colors.OKCYAN}"))
                username = input(f"{Colors.HEADER}Username: {Colors.OKBLUE}")

                # connect to the server
                C = Connection(ip, port, username, secrets["server_secret"], secrets["client_secret"])

            # catching all the errors
            except ValueError:
                fail("Invalid port. Please enter numbers only!")
                continue

            except NameError:
                fail("User already logged in")
                continue

            except ConnectionRefusedError:
                fail("Wrong IP / Server (program) down")
                continue

            except (ConnectionError, TimeoutError):
                fail("Invalid IP / Server (computer) down")
                continue

            except InvalidSecret:
                fail("Server-Secret Wrong!")
                continue

            CONNECTED = True

        # actual code that runs the program
        success("Successfully connected to server, loading messages...\n")
        MU = MessageUpdater(C)
        MU.run_thread()

        while CONNECTED:
            # get message input
            mes = input("")
            C.send_message(mes)

    except (Exception,):
        print(f"{Colors.FAIL}{format_exc()}\n\nexiting!!{Colors.ENDC}\n")
        return 1

    finally:
        return 0


def end(*signals) -> None:
    """
    called if the program ends (errors and normal exit)
    """
    global CONNECTED
    CONNECTED = False
    if C is not ...:
        C.end()

    if MU is not ...:
        MU.running = False

    print(Colors.ENDC)
    s_exit(signals[0])


if platform == "win32":
    os.system("color")  # only for windows

MU: MessageUpdater = ...
C: Connection = ...

if __name__ == '__main__':
    # in case of termination
    signal.signal(signal.SIGINT, end)
    signal.signal(signal.SIGTERM, end)

    # run main program
    end(main())
