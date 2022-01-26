"""
server.py
Used for storing messages (encrypted)

Author:
Nilusink
"""
from core import send_long, receive_long, print_traceback, key_func

from cryptography.fernet import Fernet, InvalidToken
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Any, List
from contextlib import suppress
import socket
import json


MESSAGES: list = []


class User:
    running = True

    def __init__(self, client: socket.socket, default_encryption: Callable, username: str) -> None:
        """
        create a new client thread

        :param client: The socket instance of the Client
        """
        self.__client = client
        self.__pool = ThreadPoolExecutor(max_workers=1)

        # create new encryption key for client
        key = key_func(256)
        self.__fer = Fernet(key)
        client.send(default_encryption(json.dumps({"success": True, "key": key.decode()}).encode("utf-32")))

        # start receiving thread
        self.__pool.submit(self.__receive)

        # permanent variables
        self.__username = username

        # mark current client as running
        RUNNING_CLIENTS.append(self)

        print(f"Login: {username}")

    @property
    def username(self) -> str:
        return self.__username

    def encrypt(self, message: str | dict) -> bytes:
        """
        encrypt a str or dictionary with the client secret

        :param message: the message to encrypt
        :return: the encrypted message
        """
        return self.__fer.encrypt(json.dumps(message).encode("utf-32"))

    def decrypt(self, message: bytes) -> str | dict:
        """
        decrypt a str or dictionary with the client secret

        :param message: the message to encrypt
        :return: the encrypted message
        """
        return json.loads(self.__fer.decrypt(message).decode("utf-32"))

    @print_traceback
    def __receive(self) -> None:
        self.__client.settimeout(.5)
        while self.running:
            try:
                bytes_mes = receive_long(self.__client)

            except socket.timeout:
                continue

            except (ConnectionResetError, ConnectionAbortedError):
                self.end(wait=False)
                return

            init_mes: Dict[str, Any] = self.decrypt(bytes_mes)
            # process request
            match init_mes["type"]:
                case "action":
                    match init_mes["action"]:
                        case "end":
                            self.end()

                        case "get_all":
                            self.send({
                                "type": "request_result",
                                "request_type": "get_all",
                                "request_result": MESSAGES
                            })

                case "message":
                    MESSAGES.append({
                        "message": init_mes["message"],
                        "time": init_mes["time"],
                        "user": self.username
                    })
                    RUNNING_CLIENTS.sendall({
                        "type": "message",
                        "message": init_mes["message"],
                        "time": init_mes["time"],
                        "user": self.username
                    })

    def send(self, message: dict) -> None:
        """
        send a message to the client

        :param message: the message to send
        """
        send_long(self.__client, self.encrypt(message))

    def end(self, wait: bool = True) -> None:
        """
        :param wait: decides if to wait for the threads to finish (only set false within the thread itself)
        """
        print(f"Logout: {self.username}")
        with suppress(Exception):
            self.running = False
            self.__pool.shutdown(wait=wait)
            RUNNING_CLIENTS.remove(self)

    def __del__(self) -> None:
        self.end()


class Clients:
    def __init__(self) -> None:
        """
        Collector for multiple clients
        """
        self.__clients: List[User] = []

    def append(self, client: User) -> None:
        """
        append a client to the clients list
        :param client: the client to append
        """
        self.__clients.append(client)

    @print_traceback
    def remove(self, client: User) -> bool:
        """
        remove a client from the clients list
        :param client: the client to remove
        """
        if client in self.__clients:
            self.__clients.remove(client)
            return True
        return False

    @print_traceback
    def sendall(self, message: dict) -> None:
        """
        send to all clients
        :param message: message to send
        """
        for client in self.__clients:
            client.send(message)

    def is_online(self, username: str) -> bool:
        """
        check if a user with the specified username is online

        :param username: the user to search for
        """
        for user in self.__clients:
            if user.username == username:
                return True
        return False

    def end(self) -> None:
        """
        disconnect all clients
        """
        for client in self.__clients.copy():
            client.end()


RUNNING_CLIENTS = Clients()


class Connection:
    protocol_version = "1.0.0"
    accepted_versions = {"1.0.0"}

    def __init__(self, port: int, server_secret: bytes) -> None:
        """
        initialize the server, create socket

        :param port: the port to run on
        :param server_secret: Your custom secret key
        """
        # validation of the secret and creation of the Fernet object
        try:
            self.__fer = Fernet(server_secret)

        except InvalidToken:
            raise ValueError("Client secret not valid")

        # create the socket object
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server.bind(("127.0.0.1", port))
        self.__server.settimeout(.5)
        self.__server.listen()

        # store reused variables
        self.__secret = server_secret
        self.running = True
        self.__pool = None

    @property
    def secret(self) -> bytes:
        return self.__secret

    def receive_clients(self, thread: bool = False) -> None:
        if thread:
            if not self.__pool:
                self.__pool = ThreadPoolExecutor()

            self.__pool.submit(self.receive_clients, thread=False)
            return

        while self.running:
            try:
                client, _address = self.__server.accept()

            except OSError:
                continue

            init_mes = client.recv(2048)
            init_mes = json.loads(self.__fer.decrypt(init_mes).decode("utf-32"))

            # validating version
            if not init_mes["version"] in self.accepted_versions:
                client.send(self.__fer.encrypt(json.dumps({"success": False, "reason": "InvalidVersion"}).encode("utf-32")))
                continue

            if RUNNING_CLIENTS.is_online(init_mes["username"]):
                client.send(self.__fer.encrypt(json.dumps({"success": False, "reason": "UserOnline"}).encode("utf-32")))

            User(client, self.__fer.encrypt, init_mes["username"])

    def end(self) -> None:
        self.running = False
        if self.__pool is not None:
            self.__pool.shutdown(wait=True)

        # shutdown every running client
        RUNNING_CLIENTS.end()
