#!/usr/bin/python
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
class UI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for page in (LoginPage, MainPage):

            frame = page(container, self)

            self.frames[page] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)
    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

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