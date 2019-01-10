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

        self.username = ''
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

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

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
        username = str(self.usernameEntry.get())
        password = str(self.passwordEntry.get())
        
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
            self.controller.set_username(str(self.usernameEntry.get()))
            self.controller.show_frame(MainPage)
        elif actionType == constants.AUTHENTICATION_FAIL:
            self.errorText.set(actionPayload[constants.MESSAGE])
            

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, controller)
        self.controller = controller
        self.isInitialized = False
        self.currentFriend = ''

        self.usernameText = tk.Text(self, width=50, state=tk.DISABLED)
        tk.Label(self, text='Name').grid(column=0, row=0)
        self.usernameText.grid(column=1, row=0)

        # status
        self.statusEntry = tk.Text(self, width=50, height=4)
        tk.Label(self, text='Status').grid(column=0, row=1)
        self.statusEntry.grid(column=1, row=1)

        # update name and status button
        tk.Button(self, text='Update', command=self.update_status).grid(column=1, row=2)

        # friend list
        tk.Label(self, text='Friend list').grid(column=0, row=3, columnspan=2)
        self.friendList = StringVar(value=[])
        self.friendListBox = tk.Listbox(self, listvariable=self.friendList, height=30)
        self.friendListBox.grid(column=0, row=4, columnspan=2)
        self.friendListBox.bind('<ListboxSelect>', self.select_friend)

        # friend status
        tk.Label(self, text='Friend\'s status').grid(column=0, row=5)
        self.friendStatus = tk.Text(self, width=50, height=4, state=tk.DISABLED)
        self.friendStatus.grid(column=1, row=5)

    def select_friend(self):
        selection = self.friendListBox.curselection()
        if len(selection) == 1:
            index = selection[0]
            self.currentFriend = self.friendList.get()[index]

            initThreadAction = {}
            initThreadAction[constants.TYPE] = constants.INIT_THREAD
            initThreadAction[constants.PAYLOAD] = {
                constants.SENDER: self.controller.get_username(),
                constants.RECEIVER: self.currentFriend
            }

            # TODO: Init thread to ALL

            self.controller.send_action(initThreadAction)
            

    def update_status(self):
        myStatus = str(self.statusEntry.get(1.0, tk.END))
        myUsername = self.controller.get_username()

        updateStatusAction = {}
        updateStatusAction[constants.TYPE] = constants.UPDATE_STATUS
        updateStatusAction[constants.PAYLOAD] = {
            constants.USERNAME: myUsername,
            constants.STATUS: myStatus
        }

        self.controller.send_action(updateStatusAction)

    def process_action(self, action):
        actionType = action[constants.TYPE]
        actionPayload = action[constants.PAYLOAD]
        if actionType == constants.RECEIVE_USERS:
            if not self.isInitialized:
                self.isInitialized = True
                self.usernameText.configure(state=tk.NORMAL)
                self.usernameText.insert(tk.END, self.controller.get_username())
                self.usernameText.configure(state=tk.DISABLED)
            self.friendList.set(actionPayload[constants.USERS])
        elif actionType == constants.RECEIVE_THREAD_INFO:
            isOnline = 'Offline'
            if actionPayload[constants.FRIEND_STATUS][constants.IS_ONLINE]:
                isOnline = 'Online'
            
            self.friendStatus.configure(state=tk.NORMAL)
            self.friendStatus.delete(1.0, tk.END)
            self.friendStatus.insert(tk.END, isOnline + ' - ' + actionPayload[constants.FRIEND_STATUS][constants.STATUS])
            self.friendStatus.configure(state=tk.DISABLED)
        elif actionType == constants.UPDATE_FRIEND_STATUS:
            friendUsername = actionPayload[constants.USERNAME]

            if friendUsername == self.currentFriend:
                isOnline = 'Offline'
                if actionPayload[constants.IS_ONLINE]:
                    isOnline = 'Online'
                self.friendStatus.configure(state=tk.NORMAL)
                self.friendStatus.delete(1.0, tk.END)
                self.friendStatus.insert(tk.END, isOnline + ' - ' + actionPayload[constants.STATUS])
                self.friendStatus.configure(state=tk.DISABLED)