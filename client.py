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

def receive(outputQueue):
  while True:
    try:
      msg = CLIENT.recv(BUFSIZ).decode('utf-8')
      outputQueue.put(msg)
      if msg == MSG_CODE_QUIT:
        print('Connection to server closed')
        break
    except OSError:
      outputQueue.put(MSG_CODE_QUIT)
      break

def send(inputQueue):
  while True:
    msg = inputQueue.get()
    CLIENT.send(bytes(msg, 'utf-8'))
    if msg == MSG_CODE_QUIT:
      print('Closing pending...')
      break

def ui(inputQueue, outputQueue):
  root = Tk()
  root.title('Chatbox')

  def sendMsg(*args):
    msg = str(chatInput.get())
    inputQueue.put(msg)
    chatInput.set('')

  def receiveMsg():
    while True:
      msg = outputQueue.get()
      if (msg == MSG_CODE_QUIT):
        root.quit()
        break
      chatOutput.set(str(chatOutput.get()) + '\n' + msg)

  # the main frame of the app
  mainframe = ttk.Frame(root, padding='3 3 12 12')
  mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
  mainframe.columnconfigure(0, weight=1)
  mainframe.rowconfigure(0, weight=1)

  # left column (for list of friends + personal info)
  leftCol = ttk.Frame(mainframe)
  leftCol.grid(column=0, row=0, sticky=(N, W, E, S))

  # right column (for chatbox + friend info)
  rightCol = ttk.Frame(mainframe)
  rightCol.grid(column=0, row=1, rowspan=2, sticky=(W, W, E, S))

  # the chat input
  chatInput = StringVar()
  chatEntry = ttk.Entry(rightCol, width=70, textvariable=chatInput)
  chatEntry.grid(column=0, row=2)

  # the button
  ttk.Button(rightCol, text='Send', command=sendMsg).grid(column=1, row=2)

  # the chat display
  chatOutput = StringVar()
  chatDisplay = ttk.Entry(rightCol, width=100, textvariable=chatOutput, state='disabled')
  chatDisplay.grid(column=0, row=1, columnspan=2)

  recvBuffer = threading.Thread(target=receiveMsg)
  root.mainloop()
  recvBuffer.join()
    
if __name__ == '__main__':
  inputQueue = Queue()
  outputQueue = Queue()
  receiveThread = threading.Thread(target=receive, args=(outputQueue,))
  sendThread = threading.Thread(target=send, args=(inputQueue,))
  uiThread = threading.Thread(target=ui, args=(inputQueue, outputQueue))
  receiveThread.start()
  sendThread.start()
  uiThread.start()
  receiveThread.join()
  sendThread.join()
  uiThread.join()
  CLIENT.close()
