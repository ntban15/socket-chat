#!/usr/bin/env python3
from queue import Queue
from tkinter import *
from tkinter import ttk

import socket
import threading

HOST = '127.0.0.1'
PORT = 8000
BUFSIZ = 1024
CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.connect((HOST, PORT))

MSG_CODE_QUIT = '/quit'

def receive(outputMsg):
  while True:
    try:
      msg = CLIENT.recv(BUFSIZ).decode('utf-8')
      outputMsg(msg)
      if msg == MSG_CODE_QUIT:
        print('Connection to server closed')
        break
    except OSError:
      outputMsg(MSG_CODE_QUIT)
      break

def send(inputQueue):
  while True:
    msg = inputQueue.get()
    CLIENT.send(bytes(msg, 'utf-8'))
    if msg == MSG_CODE_QUIT:
      print('Closing pending...')
      break
    
if __name__ == '__main__':
  inputQueue = Queue()

  root = Tk()
  root.title('Chatbox')

  def sendMsg(*args):
    msg = str(chatInput.get())
    inputQueue.put(msg)
    chatInput.set('')

  def receiveMsg(msg):
    if (msg == MSG_CODE_QUIT):
      root.quit()
      return
    chatDisplay.insert(END, msg + '\n')

  # the main frame of the app
  mainframe = ttk.Frame(root, padding='3 3 12 12')
  mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
  mainframe.columnconfigure(0, weight=1)
  mainframe.rowconfigure(0, weight=1)

  # left column (for list of friends + personal info)
  leftCol = ttk.Frame(mainframe)
  leftCol.grid(column=0, row=0, sticky=(N, W, E, S))

  # personal info
  nameInput = StringVar()
  nameEntry = ttk.Entry(leftCol, width=50, textvariable=nameInput)
  ttk.Label(leftCol, text='Name').grid(column=0, row=0)
  nameEntry.grid(column=1, row=0)

  # status
  statusEntry = Text(leftCol, width=50, height=4)
  ttk.Label(leftCol, text='Status').grid(column=0, row=1)
  statusEntry.grid(column=1, row=1)

  # update name and status button
  ttk.Button(leftCol, text='Update').grid(column=1, row=2, sticky=(E,))

  # friend list
  ttk.Label(leftCol, text='Friend list').grid(column=0, row=3, columnspan=2)
  friendList = Listbox(leftCol, height=30)
  friendList.grid(column=0, row=4, columnspan=2, sticky=(E,W))

  # friend status
  ttk.Label(leftCol, text='Friend\'s status').grid(column=0, row=5)
  friendStatus = Text(leftCol, width=50, height=4)
  friendStatus.grid(column=1, row=5)

  # right column (for chatbox + friend info)
  rightCol = ttk.Frame(mainframe)
  rightCol.grid(column=1, row=0, columnspan=2, sticky=(N, W, E, S))

  # the chat input
  chatInput = StringVar()
  chatEntry = ttk.Entry(rightCol, width=70, textvariable=chatInput)
  chatEntry.grid(column=0, row=2)

  # the button
  ttk.Button(rightCol, text='Send', command=sendMsg).grid(column=1, row=2)

  # the chat display
  chatDisplay = Text(rightCol, width=100, height=50)
  chatDisplay.grid(column=0, row=1, columnspan=2, sticky=(N,))

  receiveThread = threading.Thread(target=receive, args=(receiveMsg,))
  sendThread = threading.Thread(target=send, args=(inputQueue,))
  receiveThread.start()
  sendThread.start()
  root.mainloop()

  receiveThread.join()
  sendThread.join()
  CLIENT.close()
