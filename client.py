#!/usr/bin/env python3
from queue import Queue
from tkinter import *
from tkinter import ttk

import socket
import threading
import constants
import utils

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

  isChatAll = False
  clientName = ''
  targetName = ''

  def sendMsg(*args):
    msg = str(chatInput.get())
    msgType = constants.SEND_MSG
    if isChatAll:
      msgType = constants.SEND_MSG_ALL

    sendMsgAction = {
      constants.TYPE: msgType,
      constants.PAYLOAD: {
        constants.SENDER: clientName,
        constants.MESSAGE: msg,
        constants.RECEIVER: targetName
      }
    }

    inputQueue.put(utils.encodeDict(sendMsgAction))
    chatInput.set('')

  def receiveMsg(msg):
    msgDict = utils.decodeDict(msg)
    msgType = msgDict[constants.TYPE]
    msgPayload = msgDict[constants.PAYLOAD]
    if (msgType == constants.UPDATE_FRIEND_STATUS):
      pass
    elif (msgType == constants.RECEIVE_THREAD_INFO):
      threadMessages = msgPayload[constants.MESSAGES]
      isFriendOnline = msgPayload[constants.FRIEND_STATUS][constants.IS_ONLINE]
      status = msgPayload[constants.FRIEND_STATUS][constants.STATUS]

      chatDisplay.configure(state=NORMAL)
      for threadMessage in threadMessages:
        chatDisplay.insert(END, threadMessage[constants.SENDER] + ': ' + threadMessage[constants.MESSAGE] + '\n')
      chatDisplay.configure(state=DISABLED)

      onlineState = 'Offline'
      if isFriendOnline:
        onlineState = 'Online'

      friendStatus.configure(state=NORMAL)
      friendStatus.delete(1.0, END)
      friendStatus.insert(END, onlineState + ' - ' + status)
      friendStatus.configure(state=DISABLED)

    elif (msgType == constants.RECEIVE_MSG):
      senderName = msgPayload[constants.SENDER]
      msgContent = msgPayload[constants.MESSAGE]

      chatDisplay.configure(state=NORMAL)
      chatDisplay.insert(END, senderName + ': ' + msgContent + '\n')
      chatDisplay.configure(state=DISABLED)
    elif (msgType == constants.RECEIVE_USERS):
      pass

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
  friendStatus = Text(leftCol, width=50, height=4, state=DISABLED)
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
  chatDisplay.grid(column=0, row=1, columnspan=2, sticky=(N,), state=DISABLED)

  receiveThread = threading.Thread(target=receive, args=(receiveMsg,))
  sendThread = threading.Thread(target=send, args=(inputQueue,))
  receiveThread.start()
  sendThread.start()
  root.mainloop()

  receiveThread.join()
  sendThread.join()
  CLIENT.close()
