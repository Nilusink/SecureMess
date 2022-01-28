"""
client.py
Helper for GUI application, handles server communication

Author:
Nilusink
"""
from core import send_long, receive_long, AuthError, Daytime, print_traceback, InvalidSecret

from cryptography.fernet import Fernet, InvalidToken
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Generator
from contextlib import suppress
from traceback import print_exc
import socket
import struct
import json


# every users sends a message when joining / leaving, customize them here
HELLO_MES: str = "Hello there!"
BYE_MES: str = "Bye!"


class Connection:
    protocol_version = "1.0.0"
    __messages: list = []
    running = True

    def __init__(self, ip: str, port: int, username: str, server_secret: bytes | str, clients_secret: bytes | str) -> None:
        """
        Initialize the connection to a server

        :param ip: The ip of the Server
        :param port: The port the Server runs on
        :param username: username, different for every client (identification for other clients)
        :param server_secret: Your custom secret key
        """
        # validation of the secret and creation of Fernet objects
        try:
            self.fer = Fernet(server_secret)

        except (InvalidToken, ValueError):
            raise InvalidSecret("Server secret not valid")

        try:
            self.__clients_fer = Fernet(clients_secret)

        except (InvalidToken, ValueError):
            raise InvalidSecret("Clients secret not valid")

        # create the socket object
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__server.connect((ip, port))

        except socket.gaierror:
            raise ConnectionError("Invalid ip")

        except ConnectionRefusedError:
            raise ConnectionRefusedError("Server not running on targeted ip")

        # create the initial message and send it to the server
        mes = {
                "username": username,
                "version": self.protocol_version
        }

        self.__server.send(self.fer.encrypt(json.dumps(mes).encode("utf-32")))

        # receive validation message from server
        val = json.loads(self.fer.decrypt(self.__server.recv(2048)).decode("utf-32"))
        if not val["success"]:
            match val["reason"]:
                case "UserOnline":
                    raise NameError("A User with this name is already online, please choose another one")

                case _:
                    raise AuthError(f"Error accessing server: {val['reason']}")

        # create Fernet object with custom key
        self.__fer = Fernet(val["key"].encode())

        # create thread
        self.__pool = ThreadPoolExecutor(max_workers=1)
        self.__pool.submit(self.__receive)

        send_long(self.__server, self.encrypt({
            "type": "action",
            "action": "get_all"
        }))
        self.send_message(HELLO_MES)

    @property
    def new_messages(self) -> Generator:
        """
        yield all new messages
        """
        for element in self.__messages.copy():
            self.__messages.remove(element)
            yield element

    def encrypt(self, message: str | dict) -> bytes:
        """
        encrypt a str or dictionary with the server secret

        :param message: the message to encrypt
        :return: the encrypted message
        """
        return self.__fer.encrypt(json.dumps(message).encode("utf-32"))

    def decrypt(self, message: bytes) -> Any:
        """
        decrypt a str or dictionary with the client server

        :param message: the message to encrypt
        :return: the encrypted message
        """
        return json.loads(self.__fer.decrypt(message).decode("utf-32"))

    def encrypt_client(self, message: str | dict) -> bytes:
        """
        encrypt a str or dictionary with the client secret

        :param message: the message to encrypt
        :return: the encrypted message
        """
        return self.__clients_fer.encrypt(json.dumps(message).encode("utf-32"))

    def decrypt_client(self, message: bytes) -> str | dict:
        """
        decrypt a str or dictionary with the client server

        :param message: the message to encrypt
        :return: the encrypted message
        """
        return json.loads(self.__clients_fer.decrypt(message).decode("utf-32"))

    @print_traceback
    def __receive(self) -> None:
        """
        receive and process incoming messages from the server
        """
        self.__server.settimeout(.5)
        while self.running:
            try:
                byte_mes = receive_long(self.__server)

            except (ConnectionResetError, struct.error, socket.timeout, OSError):
                continue

            except Exception:
                print_exc()
                raise

            message = self.decrypt(byte_mes)
            match message["type"]:
                case "request_result":
                    match message["request_type"]:
                        case "get_all":
                            for mes in message["request_result"]:
                                mes["message"] = self.decrypt_client(mes["message"].encode())
                                self.__messages.append(mes)

                case "message":
                    message["message"] = self.decrypt_client(message['message'].encode())
                    self.__messages.append(message)

    def send_message(self, message: str) -> None:
        """
        send a message to the server

        :param message: the message to send
        """
        mes = {
            "type": "message",
            "message": self.encrypt_client(message).decode(),
            "time": str(Daytime.now())
        }
        send_long(self.__server, self.encrypt(mes))

    def end(self) -> None:
        """
        cuts the connection to the server and end all threads
        """
        with suppress(Exception):
            self.send_message(BYE_MES)
            self.__server.send(self.encrypt({
                "type": "action",
                "action": "end"
            }))
            self.__server.close()

            # threads
            self.running = False
            self.__pool.shutdown(wait=True)

    def __del__(self) -> None:
        self.end()
