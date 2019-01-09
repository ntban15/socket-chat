#!/usr/bin/python
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
import utils
import constants

class UI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.actionQueue = kwargs['actionQueue']
        self.frames = {}

        for page in (LoginPage, MainPage):

            frame = page(container, self)

            self.frames[page] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)
    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
    def broadcast_action(self, action):
        decodedAction = utils.decodeDict(action)
        for frame in self.frames:
            self.frames[frame].process_action(decodedAction)
    def send_action(self, action):
        self.actionQueue.put(utils.encodeDict(action))

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, controller)
        self.controller = controller

        # Username
        tk.Label(self, text="Username").grid(row=0, column=0)
        self.usernameEntry = StringVar()
        tk.Entry(self, textvariable=self.usernameEntry).grid(row=0, column=1)

        # Password
        tk.Label(self, text="Password").grid(row=1, column=0)
        self.passwordEntry = StringVar()
        tk.Entry(self, show="*", textvariable=self.passwordEntry).grid(row=1, column=1)

        # Error text
        self.errorText = StringVar()
        tk.Label(self, textvariable=self.errorText).grid(row=2, column=0)

        # Login button
        tk.Button(self, text="LOGIN", command=self.login).grid(row=5, column=0)

    def login(self):
        self.errorText.set('')
        username = self.usernameEntry.get()
        password = self.passwordEntry.get()
        
        loginAction = {}
        loginAction[constants.TYPE] = constants.OPEN_CONNECTION
        loginAction[constants.PAYLOAD] = {
            constants.USERNAME: username,
            constants.PASSWORD: password
        }

        self.controller.send_action(loginAction)
        
    def process_action(self, action):
        actionType = action[constants.TYPE]
        actionPayload = action[constants.PAYLOAD]
        if actionType == constants.RECEIVE_USERS:
            self.controller.show_frame(MainPage)
        elif actionType == constants.AUTHENTICATION_FAIL:
            self.errorText.set(actionPayload[constants.MESSAGE])
            

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, controller)
        nameInput = StringVar()
        nameEntry = tk.Entry(self, width=50, textvariable=nameInput)
        tk.Label(self, text='Name').grid(column=0, row=0)
        nameEntry.grid(column=1, row=0)

        # status
        statusEntry = tk.Text(self, width=50, height=4)
        tk.Label(self, text='Status').grid(column=0, row=1)
        statusEntry.grid(column=1, row=1)

        # update name and status button
        tk.Button(self, text='Update').grid(column=1, row=2)

        # friend list
        tk.Label(self, text='Friend list').grid(column=0, row=3, columnspan=2)
        friendList = tk.Listbox(self, height=30)
        friendList.grid(column=0, row=4, columnspan=2)

        # friend status
        tk.Label(self, text='Friend\'s status').grid(column=0, row=5)
        friendStatus = tk.Text(self, width=50, height=4)
        friendStatus.grid(column=1, row=5)

    def process_action(self, action):
        pass