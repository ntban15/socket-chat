#!/usr/bin/python
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from tkinter import filedialog
from PIL import ImageTk, Image
import utils
import constants

class UI(tk.Tk):
    def __init__(self, actionQueue, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.username = ''
        self.actionQueue = actionQueue
        self.frames = {}
        self.receiver = ''
        self.avatar = 'avatar.jpg'

        for page in (LoginPage, MainPage, ChatPage):

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

    def set_receiver(self, username):
        self.receiver = username

    def get_receiver(self):
        return self.receiver

    def get_avatar(self):
        return self.avatar

    def set_avatar(self, new_avatar):
        self.avatar = new_avatar

    def quit(self):
        pass

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

        self.usernameText = tk.Text(self, width=20, height=2, state=tk.DISABLED)
        tk.Label(self, text='Name').grid(column=0, row=0)
        self.usernameText.grid(column=1, row=0)
        

        # friend avatar
        img = ImageTk.PhotoImage(Image.open(self.controller.avatar).resize((200, 200), Image.ANTIALIAS))
        self.myAvatar = tk.Label(self, width=200, height=200, image=img)
        self.myAvatar.image = img
        self.myAvatar.grid(column=1, row=2)
        tk.Button(self, text='Change Avatar', command=self.change_avatar).grid(column=1, row=4)

        # status
        self.statusEntry = tk.Text(self, width=20, height=4)
        tk.Label(self, text='Status').grid(column=0, row=1)
        self.statusEntry.grid(column=1, row=1)

        # update name and status button
        tk.Button(self, text='Update', command=self.update_status).grid(column=1, row=3)

        # friend list
        tk.Label(self, text='Friend list').grid(column=0, row=5, columnspan=2)
        self.friendList = tk.Listbox(self, height=30)
        self.friendList.grid(column=0, row=6, columnspan=2)
        self.friendList.bind('<<ListboxSelect>>', self.select_friend)
        self.friendList.insert(tk.END, ('all',))
    
    def init_status(self, new_status):
        self.statusEntry.delete(1.0, tk.END)
        self.statusEntry = tk.Text(self, width=20, height=4)
        self.statusEntry.insert(tk.END, new_status)
        self.statusEntry.grid(column=1, row=1)

    def change_avatar(self):
        avatar = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        self.display_avatar(avatar)
        self.controller.set_avatar(avatar)
        self.update_status(avatar)
        
        
    def display_avatar(avatar_name):
        img = ImageTk.PhotoImage(Image.open(avatar_name).resize((200, 200), Image.ANTIALIAS))
        self.myAvatar = tk.Label(self, width=200, height=200, image=img)
        self.myAvatar.image = img


    def select_friend(self, event):
        selection = self.friendList.curselection()
        if len(selection) == 1:
            index = selection[0]
            self.controller.set_receiver(self.friendList.get(index)[0])

            initThreadAction = {}
            initThreadAction[constants.TYPE] = constants.INIT_THREAD
            initThreadAction[constants.PAYLOAD] = {
                constants.SENDER: self.controller.get_username(),
                constants.RECEIVER: self.controller.get_receiver()
            }

            # TODO: Init thread to ALL

            self.controller.send_action(initThreadAction)
            self.controller.show_frame(ChatPage)
            
    def filter_friend_list(self, friendname):
        return friendname != self.controller.get_username()

    def update_status(self):
        myStatus = str(self.statusEntry.get(1.0, tk.END))
        myUsername = self.controller.get_username()
        myAvatar = self.controller.get_avatar()

        updateStatusAction = {}
        updateStatusAction[constants.TYPE] = constants.UPDATE_STATUS
        updateStatusAction[constants.PAYLOAD] = {
            constants.USERNAME: myUsername,
            constants.STATUS: myStatus,
            constants.AVATAR: myAvatar
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
            
            filteredFriendList = filter(self.filter_friend_list, actionPayload[constants.USERS])
            for friend in list(filteredFriendList):
                self.friendList.insert(0, (friend,))

        if actionType == constants.NEW_USER:
            newUserName = actionPayload[constants.USERNAME]
            if newUserName != self.controller.get_username():
                self.friendList.insert(tk.END, (newUserName,))
        if actionType == constants.UPDATE_MY_STATUS:
            new_status = actionPayload[constants.STATUS]
            new_avatar = actionPayload[constants.AVATAR]
            self.init_status(new_status)
            self.controller.set_avatar(new_avatar)
            self.display_avatar(new_avatar)

class ChatPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, controller)
        self.controller = controller

        # back button
        tk.Button(self, text='Back', command=self.back).grid(column=1, row=7)
        
        # friend name
        self.friendName = StringVar()
        tk.Label(self, text='Friend name: ').grid(column=0, row=0)
        tk.Label(self, textvariable=self.friendName).grid(column=1, row=0)

        # friend status
        self.friendStatus = tk.Text(self, width=30, height=10, state=tk.DISABLED)
        self.friendStatus.grid(column=1, row=2, sticky=(tk.N,))

        # friend avatar
        img = ImageTk.PhotoImage(Image.open('avatar.jpg').resize((200, 200), Image.ANTIALIAS))
        self.friendAvatar = tk.Label(self, width=200, height=200, image=img)
        self.friendAvatar.image = img
        self.friendAvatar.grid(column=1, row=3)
        

        # the chat input
        self.chatInput = StringVar()
        chatEntry = tk.Entry(self, width=50, textvariable=self.chatInput)
        chatEntry.grid(column=0, row=5)

        # the button
        tk.Button(self, text='Send', command=self.sendMsg).grid(column=0, row=7)

        # the chat display
        self.chatDisplay = tk.Text(self, width=50, height=20, state=tk.DISABLED)
        self.chatDisplay.grid(column=0, row=2, columnspan=1, rowspan=2, sticky=(tk.NW,))
        
    def display_avatar(avatar_name):
        img = ImageTk.PhotoImage(Image.open(avatar_name).resize((200, 200), Image.ANTIALIAS))
        self.friendAvatar = tk.Label(self, width=200, height=200, image=img)
        self.friendAvatar.image = img

    def back(self):
        self.chatDisplay.configure(state=tk.NORMAL)
        self.chatDisplay.delete(1.0, tk.END)
        self.chatDisplay.configure(state=tk.DISABLED)
        self.controller.show_frame(MainPage)
        self.controller.set_receiver('')
        # self.controller.set_avatar('avatar.jpg')

    def sendMsg(self):
        msg = str(self.chatInput.get())
        self.chatInput.set('')

        self.chatDisplay.configure(state=tk.NORMAL)
        self.chatDisplay.insert(tk.END, self.controller.get_username() + ': ' + msg + '\n')
        self.chatDisplay.configure(state=tk.DISABLED)

        action = {
            constants.TYPE: constants.SEND_MSG_ALL,
            constants.PAYLOAD: {
                constants.SENDER: self.controller.get_username(),
                constants.MESSAGE: msg
            }
        }

        if (self.controller.get_receiver() != 'all'):
            action[constants.PAYLOAD][constants.RECEIVER] = self.controller.get_receiver()
            action[constants.TYPE] = constants.SEND_MSG

        self.controller.send_action(action)

    def process_action(self, action):
        if action[constants.TYPE] == constants.RECEIVE_MSG:
            senderName = action[constants.PAYLOAD][constants.SENDER]
            msg = action[constants.PAYLOAD][constants.MESSAGE]

            # Case dang chat cho 1 thg dang bat tab all => hien lun tin nhan o tab all, 
            # Case dang chat cho mot thang dang o main => bi duplicate 
            # Case dang chat cho all => bi duplicate tin nhan vi vua insert luc gui va insert luc nhan
            if ((not action[constants.PAYLOAD][constants.IS_CHAT_ALL] and senderName == self.controller.get_receiver()) or 
            (action[constants.PAYLOAD][constants.IS_CHAT_ALL] and self.controller.get_receiver() == 'all' and senderName != self.controller.get_username())):
                self.chatDisplay.configure(state=tk.NORMAL)
                self.chatDisplay.insert(tk.END, senderName + ': ' + msg + '\n')
                self.chatDisplay.configure(state=tk.DISABLED)


        elif action[constants.TYPE] == constants.RECEIVE_THREAD_INFO:
            self.friendName.set(self.controller.get_receiver())

            for message in action[constants.PAYLOAD][constants.MESSAGES]:
                self.chatDisplay.configure(state=tk.NORMAL)
                self.chatDisplay.insert(tk.END, message[constants.SENDER] + ': ' + message[constants.MESSAGE] + '\n')
                self.chatDisplay.configure(state=tk.DISABLED)

            isOnline = 'Offline'
            if action[constants.PAYLOAD][constants.FRIEND_STATUS][constants.IS_ONLINE]:
                isOnline = 'Online'
            
            self.friendStatus.configure(state=tk.NORMAL)
            self.friendStatus.delete(1.0, tk.END)
            self.friendStatus.insert(tk.END, isOnline + ' - ' + action[constants.PAYLOAD][constants.FRIEND_STATUS][constants.STATUS])
            self.friendStatus.configure(state=tk.DISABLED)
            self.display_avatar(action[constants.PAYLOAD][constants.FRIEND_STATUS][constants.AVATAR])

        elif action[constants.TYPE] == constants.UPDATE_FRIEND_STATUS:
            if (action[constants.PAYLOAD][constants.USERNAME] == self.controller.get_receiver()):
                isOnline = 'Offline'
                if action[constants.PAYLOAD][constants.IS_ONLINE]:
                    isOnline = 'Online'
                self.friendStatus.configure(state=tk.NORMAL)
                self.friendStatus.delete(1.0, tk.END)
                self.friendStatus.insert(tk.END, isOnline + ' - ' + action[constants.PAYLOAD][constants.STATUS])
                self.friendStatus.configure(state=tk.DISABLED)
                self.display_avatar(action[constants.PAYLOAD][constants.AVATAR])
