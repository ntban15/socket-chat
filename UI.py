#!/usr/bin/python
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
import utils
import constants

MSG_CODE_QUIT = '/quit'

class UI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.username = ''
        self.receiver = ''
        self.actionQueue = kwargs['actionQueue']
        self.frames = {}

        for page in (LoginPage, MainPage, ChatPage):

            frame = page(container, self)

            self.frames[page] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)
    def show_frame(self, page):
        frame = self.frames[page]
        if (page == ChatPage):
            frame = page(container, self)
            self.frames[page] = frame
        elif (page == MainPage):
            self.receiver = ''
        frame.tkraise()
    def broadcast_action(self, action):
        for frame in self.frames:
            self.frames[frame].process_action(util.decode(action))
    def send_action(self, action):
        utils.encodeDict(action)
        self.actionQueue.put(action)
    def get_username(self):
        return self.username
    def get_receiver(self):
        return self.receiver

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, controller)
        a = tk.Label(self ,text="username").grid(row=0,column = 0)
        b = tk.Label(self ,text="password").grid(row=1,column=0)
        e = tk.Entry(self).grid(row=0,column=1)
        f = tk.Entry(self,show="*").grid(row=1,column=1)
        c = tk.Button(self, text="LOGIN",command=lambda : self.login(e,f,controller)).grid(row=5,column=0)
    def login(self, username, password, controller):
        controller.show_frame(MainPage)
    def process_action(self, action):
        pass

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
class ChatPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, controller)
        self.controller = controller

        tk.Button(self, text='Back', command=lambda : controller.show_frame(MainPage)).grid(column=1, row=2)
        # the chat input
        chatInput = StringVar()
        chatEntry = tk.Entry(self, width=70, textvariable=chatInput)
        chatEntry.grid(column=0, row=2)

        # the button
        tk.Button(self, text='Send', command=self.sendMsg).grid(column=1, row=2)

        # the chat display
        chatDisplay = tk.Text(self, width=100, height=50)
        
        chatDisplay.grid(column=0, row=1, columnspan=2, sticky=(N,))

        init_action[constants.TYPE] = constants.INIT_THREAD
        init_action[constants.PAYLOAD][constants.SENDER] = controller.get_username()
        init_action[constants.PAYLOAD][constants.RECEIVER] = controller.get_receiver()
        controller.send_action(init_action)
        

    def sendMsg(self):
        msg = str(chatInput.get())
        chatInput.set('')
        action[constants.TYPE] = constants.SEND_MSG_ALL
        action[constants.PAYLOAD][constants.SENDER] = self.controller.get_username()
        action[constants.PAYLOAD][constants.MESSAGE] = msg
        if (self.controller.get_receiver() != 'all'):
            action[constants.PAYLOAD][constants.RECEIVER] = self.controller.get_receiver()
            action[constants.TYPE] = constants.SEND_MSG

        self.controller.send_action(action)
    def receiveMsg(self, msg):
        if (msg == MSG_CODE_QUIT):
            self.controller.quit()
            return
        chatDisplay.insert(END, msg + '\n')
    def process_action(self, action):
        if action[constants.TYPE] == constant.RECEIVE_MSG:
            if (action.payload.message == MSG_CODE_QUIT):
                self.controller.quit()
                return
            elif (not action.payload.is_chat_all and action.payload.sender == self.controller.get_receiver()):
                chatDisplay.insert(END, msg + '\n')
        if action[constants.TYPE] == constant.RECEIVE_THREAD_INFO:
            if (action[constants.PAYLOAD][constants.SENDER] == self.controller.get_username() or action[constants.PAYLOAD][constants.SENDER] == self.controller.get_receiver()):
                for message in action[constants.PAYLOAD][MESSAGES]:
                    chatDisplay.insert(END, message.message + '\n')
        if action[constants.TYPE] == constant.UPDATE_FRIEND_STATUS:
            if (action[constants.PAYLOAD][constants.USERNAME] == self.controller.get_receiver():
                # change UI status
        #  có cần ko?
        # if action.type == constant.CLOSE_CONNECTION:
        #     if (action.payload.username == self.controller.get_receiver():
        #         # change UI online status
        # if action.type == constant.OPEN_CONNECTION:
        #     if (action.payload.username == self.controller.get_receiver():
        #         # change UI online status