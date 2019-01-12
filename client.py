#!/usr/bin/env python3
from queue import Queue
from tkinter import *
from tkinter import ttk

import socket
import threading
import constants
import UI

HOST = '127.0.0.1'
PORT = 8000
BUFSIZ = 1024
CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.connect((HOST, PORT))

MSG_CODE_QUIT = '/quit'

def split_action(action):
  actions = []

  start_index = 0
  end_index = 0
  brackets = 0
  for c in action:
    if c == '{':
      brackets = brackets + 1
    if c == '}':
      brackets = brackets - 1
      if brackets == 0:
        actions.append(action[start_index:end_index + 1])
        start_index = end_index + 1
    
    end_index = end_index + 1

  return actions

def receive(outputMsg):
  while True:
    try:
      msg = CLIENT.recv(BUFSIZ).decode('utf-8')
      split_actions = split_action(msg)

      for action in split_actions:
        print(action)
        outputMsg(action)
      
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

  ui = UI.UI(inputQueue)

  def receiveMsg(msg):
    ui.broadcast_action(msg)

  receiveThread = threading.Thread(target=receive, args=(receiveMsg,))
  sendThread = threading.Thread(target=send, args=(inputQueue,))
  receiveThread.start()
  sendThread.start()
  ui.mainloop()

  receiveThread.join()
  sendThread.join()
  CLIENT.close()
