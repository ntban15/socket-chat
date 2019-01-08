#!usr/bin/env python3

import socket
import threading
import Database
import json

clients = {}
MSG_CODE_FORCE_QUIT = 'MSG_CODE_FORCE_QUIT'
HOST = '127.0.0.1'
PORT = 8000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)

# database
database = Database('database.json')

# client action types
INIT_THREAD = 'INIT_THREAD'
SEND_MSG = 'SEND_MSG'
SEND_MSG_ALL = 'SEND_MSG_ALL'
CLOSE_CONNECTION = 'CLOSE_CONNECTION'
OPEN_CONNECTION = 'OPEN_CONNECTION'
UPDATE_STATUS = 'UPDATE_STATUS'

# server action types
UPDATE_FRIEND_STATUS = 'UPDATE_FRIEND_STATUS'
RECEIVE_THREAD_INFO = 'RECEIVE_THREAD_INFO'
RECEIVE_MSG = 'RECEIVE_MSG'
RECEIVE_USERS = 'RECEIVE_USERS'
AUTHENTICATION_FAIL = 'AUTHENTICATION_FAIL'

# database keys
CHATS = 'chats'
ALL = 'all'
USERS = 'users'
STATUSES = 'statuses'

# dictionary keys
TYPE = 'type'
PAYLOAD = 'payload'

SENDER = 'sender'
RECEIVER = 'receiver'
USERNAME = 'username'
PASSWORD = 'password'
STATUS = 'status'
IS_ONLINE = 'is_online'
SENDER = 'sender'
RECEIVER = 'receiver'
MESSAGE = 'message'
IS_CHAT_ALL = 'is_chat_all'

def accept_connections():
  while True:
    try:
      client, client_address = SERVER.accept()
      print('%s has connected' % str(client_address))
      threading.Thread(target=handle_client, args=(client,)).start()
    except KeyboardInterrupt:
      break

def handle_client(client):
  # client.send(bytes('Welcome to my chat app. What is your name?', 'utf-8'))
  # name = client.recv(BUFSIZ).decode('utf-8')
  # client.send(bytes('Type /quit if you want to exit the chat app', 'utf-8'))
  # clients[client] = name

  while True:
    try: 
      action = client.recv(BUFSIZ)
      res_action = {}
      if action[TYPE] == OPEN_CONNECTION:
        username = action[PAYLOAD][USERNAME]
        password = action[PAYLOAD][PASSWORD]

        if database.authenticate(username, password):
          clients[username] = client
          users = database.get_users()

          res_action[TYPE] = RECEIVE_USERS
          res_action[PAYLOAD][USERS] = users

          broadcast(json.dumps(res_action), username=username)
        else:
          res_action[TYPE] = AUTHENTICATION_FAIL
          res_action[PAYLOAD][MESSAGE] = 'Wrong password'
          broadcast(json.dumps(res_action), client=client)
          client.close()


      elif action[TYPE] == INIT_THREAD:
        user1 = action[PAYLOAD][SENDER]
        user2 = action[PAYLOAD][RECEIVER]
        chat_id = database.chat_id_generator(user1, user2)

        messages = database.get_messages(chat_id)
        friend_status = database.get_status(user2)




    

      # msg = client.recv(BUFSIZ)
      # if msg != bytes('/quit', 'utf-8'):
      #   broadcast(name + ': ' + msg.decode('utf-8'))
      # else:
      #   client.send(msg)
      #   client.close()
      #   del clients[client]
      #   broadcast('%s has leaved the room' % str(name))
      #   break
    except KeyboardInterrupt:
      broadcast(MSG_CODE_FORCE_QUIT)
      break

def broadcast(msg):
  for client in clients:
    client.send(bytes(msg, 'utf-8'))

if __name__ == '__main__':
  SERVER.listen(4)
  print('Waiting for incoming connections...')
  acceptThread = threading.Thread(target=accept_connections)
  acceptThread.start()
  acceptThread.join()
  SERVER.close()
