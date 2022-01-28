"""
Version 1.0.2
Write and receive messages (GUI)

Author:
Nilusink
"""
from core.client import *
from tkinter import ttk
from typing import Dict
import tkinter as tk


def newline_parser(string: str, line_length: int, word_sensitive=False):
    new_string = string
    active = False
    newlines = 1
    correction = int()
    for i in range(len(string)):
        i += correction
        if i % line_length == 0 and i != 0:
            active = word_sensitive
            if not word_sensitive:
                new_string = new_string[:i]+'\n'+new_string[i:]
                newlines += 1

        if string[i] == ' ' and active:
            new_string = new_string[:i]+'\n'+new_string[i:].lstrip(' ')
            newlines += 1
            active = False

    return new_string, newlines


class ChatBox:
    def __init__(self, r, message: str, sent_time: str, sent_by: str, width: int = 1000):
        lines = 1
        if len(message) > int(width / 10):
            message, lines = newline_parser(message, int(width / 10), True)

        height = 40 + 24 * lines

        forTime = sent_time

        r.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(master=r, borderwidth=5, bg='gray', height=height, width=1000)
        self.canvas.create_text(20, 20, fill="black", font="mono 15", text=message, anchor=tk.NW)
        self.canvas.create_text(20, height - 20, fill="black", font="mono 10", text=sent_by,
                                anchor=tk.NW)
        self.canvas.create_text(900, height - 20, fill="black", font="mono 10", text=forTime, anchor=tk.NW)

    def pack(self, *args, **kwargs):
        self.canvas.pack(*args, expand=True, fill='x', anchor=tk.NW, **kwargs)

    def pack_forget(self):
        self.canvas.pack_forget()

    def grid(self, *args, **kwargs):
        self.canvas.grid(*args, **kwargs)

    def grid_forget(self):
        self.canvas.grid_forget()


class Window:
    __done_messages: list = []
    __done_objects: list = []
    __connection: Connection

    def __init__(self, server_secret: str | bytes, client_secret: str | bytes) -> None:
        """
        Create a gui windows for chatting

        :param server_secret: the secret key for the server
        :param client_secret: the secret key for the clients
        """
        # save server information
        self.__server_ip: str
        self.__server_port: int
        self.__server_secret = server_secret
        self.__client_secret = client_secret

        # GUI color config
        self.__colors: Dict[str, str] = {
            "bg": "gray23",
            "fg": "white",
            "error": "red"
        }

        # create GUI
        self.root = tk.Tk()
        self.root.title("SecureMess")
        self.root.config(bg=self["bg"])

        # connection screen
        self.__set_size(200, 150)
        self.login_frame = tk.Frame(self.root, bg=self["bg"])

        self.ip_label = tk.Label(self.login_frame, text="Please enter the Server ip", fg=self["fg"], bg=self["bg"])
        self.ip_entry = ttk.Entry(self.login_frame, width=25)

        self.port_label = tk.Label(self.login_frame, text="Please enter the server port", fg=self["fg"], bg=self["bg"])
        self.port_entry = ttk.Entry(self.login_frame, width=25)
        self.port_entry.insert(0, "3333")

        self.login_label = tk.Label(self.login_frame, text="Please enter your Username", fg=self["fg"], bg=self["bg"])
        self.name_entry = ttk.Entry(self.login_frame, width=25)

        # grid all the stuff
        self.ip_label.grid(row=0, column=0)
        self.port_label.grid(row=2, column=0)
        self.login_label.grid(row=4, column=0)

        self.ip_entry.grid(row=1, column=0)
        self.port_entry.grid(row=3, column=0)
        self.name_entry.grid(row=5, column=0)

        self.ip_entry.bind("<Return>", self.try_login)
        self.port_entry.bind("<Return>", self.try_login)
        self.name_entry.bind("<Return>", self.try_login)

        self.connection_invalid_label = tk.Label(self.login_frame, text="", fg=self["error"], bg=self["bg"])
        self.connection_invalid_label.grid(row=6, column=0)

        # create main chatting frame
        self.main_frame = tk.Frame(self.root, bg=self["bg"])
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        self.scrollbar = tk.Scrollbar(self.main_frame)

        self.messages_frame = tk.Listbox(self.main_frame, yscrollcommand=self.scrollbar.set)

        self.root.bind("<MouseWheel>", self.scroll_chat)

        self.send_message_entry = ttk.Entry(self.main_frame)

        self.scrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.messages_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.send_message_entry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self.send_message_entry.bind("<Return>", self.send_message)

        # place login frame
        self.login_frame.pack()

    def scroll_chat(self, event) -> None:
        self.messages_frame.yview_scroll(-1*int(event.delta/abs(event.delta)), "units")

    @property
    def colors(self) -> dict:
        """
        colors for configuration GUI
        """
        return self.__colors

    def color_config(self, color_type: str, color: str) -> str:
        """
        set one color

        :param color_type: type - bg | fg ...
        :param color: the color to change to
        :return: the old color
        """
        if color_type not in self.colors:
            raise KeyError("Invalid color type")

        # change color
        o_color = self[color_type]
        self.__colors[color_type] = color
        return o_color

    def update_colors(self) -> None:
        """
        updates every color by the colors dict
        """
        # login frame
        self.root.config(bg=self["bg"])
        self.login_frame.configure(bg=self["bg"])
        self.login_label.configure(bg=self["bg"], fg=self["fg"])
        self.connection_invalid_label.configure(bg=self["bg"], fg=self["error"])

        # main frame
        self.main_frame.config(bg=self["bg"])

        self.root.update()

    def __set_size(self, width: int, height: int, set_max: bool = True, set_min: bool = True) -> None:
        """
        set window size

        :param width: width of the window
        :param height: height of the window
        """
        if set_max:
            self.root.maxsize(width=width, height=height)
        else:
            self.root.maxsize(width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())

        if set_min:
            self.root.minsize(width=width, height=height)
        else:
            self.root.minsize(width=1, height=1)

    def run(self) -> None:
        """
        run the tkinter mainloop
        """
        self.root.mainloop()
        self.end()

    def try_login(self, *_tk_trash) -> None:
        """
        try to login with the username from self.name_entry
        """
        name = self.name_entry.get()
        if not name:
            self.connection_invalid_label["text"] = "Please enter a username"
            self.root.after(800, lambda: self.connection_invalid_label.config(text=""))
            return

        try:
            self.__connection = Connection(ip=self.ip_entry.get(), port=int(self.port_entry.get()), username=name, server_secret=self.__server_secret, clients_secret=self.__client_secret)

        except NameError:
            self.connection_invalid_label["text"] = "User already logged in"
            self.root.after(800, lambda: self.connection_invalid_label.config(text=""))
            return

        except ValueError:
            self.connection_invalid_label["text"] = "Invalid Port"
            self.root.after(800, lambda: self.connection_invalid_label.config(text=""))
            return

        except ConnectionRefusedError:
            self.connection_invalid_label["text"] = "Wrong IP / Server (program) down"
            self.root.after(1500, lambda: self.connection_invalid_label.config(text=""))
            return

        except (ConnectionError, TimeoutError):
            self.connection_invalid_label["text"] = "Invalid IP / Server (computer) down"
            self.root.after(1500, lambda: self.connection_invalid_label.config(text=""))
            return

        except InvalidSecret:
            self.connection_invalid_label["text"] = "Server-Secret Wrong!"
            self.root.after(1000, lambda: self.connection_invalid_label.config(text=""))
            return

        # switch to main chat frame
        self.login_frame.pack_forget()
        self.__set_size(300, 500, set_max=False)
        self.main_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
        self.__update_messages()

    def __update_messages(self, *_tk_trash) -> None:
        """
        check if there are new messages
        """
        was_an_update: bool = False
        for message in self.__connection.new_messages:
            if message not in self.__done_messages:
                was_an_update = True
                self.messages_frame.insert(tk.END, f"{message['user']}>> {message['message']}")
                self.__done_messages.append(message)

        if was_an_update:
            self.messages_frame.yview(tk.END)

        self.root.after(200, self.__update_messages)

    def send_message(self, *_tk_trash) -> None:
        """
        send a message from the self.send_message_entry
        """
        self.__connection.send_message(self.send_message_entry.get())
        self.send_message_entry.delete(0, tk.END)

    def end(self) -> None:
        """
        close all windows and end connection
        """
        self.__connection.end()
        with suppress(Exception):
            self.root.destroy()

    def __getitem__(self, item: str):
        if item in self.colors:
            return self.colors[item]

        elif item in self.__dict__:
            return self.__dict__[item]

        raise KeyError("invalid item")


if __name__ == '__main__':
    secrets = json.load(open("config.json", "r"))
    w = Window(secrets["server_secret"], secrets["client_secret"])
    w.run()
