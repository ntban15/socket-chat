#!usr/bin/env python3

import socket
import threading

import Database
import constants
import utils

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

      # OPEN_CONNECTION:
      # -> 1. RECEIVE_USERS
      # -> 2. AUTHENTICATION_FAIL
      if action[constants.TYPE] == constants.OPEN_CONNECTION:
        username = action[constants.PAYLOAD][constants.USERNAME]
        password = action[constants.PAYLOAD][constants.PASSWORD]

        # AUTHENTICATED
        if database.authenticate(username, password):
          clients[username] = client
          users = database.get_users()

          # After authenticated, user receives a list of users
          res_action[constants.TYPE] = constants.RECEIVE_USERS
          res_action[constants.PAYLOAD][constants.USERS] = users

          broadcast(utils.encodeDict(res_action), username=username)
        
        # WRONG PASSWORD
        else:
          res_action[constants.TYPE] = constants.AUTHENTICATION_FAIL
          res_action[constants.PAYLOAD][constants.MESSAGE] = 'Wrong password'
          
          broadcast(utils.encodeDict(res_action), client=client)
          client.close()

      # CLOSE_CONNECTION -> no action sent to client ???
      elif action[constants.TYPE] == constants.CLOSE_CONNECTION:
        username = action[constants.PAYLOAD][constants.USERNAME]

        # update online status to offline if a user's connection is closed
        database.update_online_status(username, False)

        # close client socket
        client.close()
        # delete client from client dictionary
        del clients[username]

        # target là gì ??? all in clients ???
        broadcast('%s has leaved the room' % str(username))

      # INIT_THREAD -> RECEIVE_THREAD_INFO
      elif action[constants.TYPE] == constants.INIT_THREAD:
        sender = action[constants.PAYLOAD][constants.SENDER]
        receiver = action[constants.PAYLOAD][constants.RECEIVER]
        chat_id = database.chat_id_generator(sender, receiver)

        # get all messages of thread
        messages = database.get_messages(chat_id)
        # get user2's status
        friend_status = database.get_status(user2)

        res_action[constants.TYPE] = constants.RECEIVE_THREAD_INFO
        res_action[constants.PAYLOAD][constants.MESSAGES] = messages
        res_action[constants.PAYLOAD][constants.FRIEND_STATUS] = friend_status

        broadcast(utils.encodeDict(res_action), target=sender)

      # SEND_MSG -> RECEIVE_MSG
      elif action[constants.TYPE] == constants.SEND_MSG:
        sender = action[constants.PAYLOAD][constants.SENDER]
        receiver = action[constants.PAYLOAD][constants.RECEIVER]
        message = action[constants.PAYLOAD][constants.MESSAGE]

        # add message to a thread
        database.add_message(message, sender, receiver)

        res_action[constants.TYPE] = constants.RECEIVE_MSG
        res_action[constants.PAYLOAD][constants.SENDER] = sender
        res_action[constants.PAYLOAD][constants.MESSAGE] = message
        res_action[constants.PAYLOAD][constants.IS_CHAT_ALL] = False

        broadcast(utils.encodeDict(res_action), target=receiver)

      # SEND_MSG_ALL -> RECEIVE_MSG
      elif action[constants.TYPE] == constants.SEND_MSG_ALL:
        sender = action[constants.PAYLOAD][constants.SENDER]
        message = action[constants.PAYLOAD][constants.MESSAGE]

        # add message to a thread named "all"
        database.add_message_all(message, sender, receiver)

        res_action[constants.TYPE] = constants.RECEIVE_MSG
        res_action[constants.PAYLOAD][constants.SENDER] = sender
        res_action[constants.PAYLOAD][constants.MESSAGE] = message
        res_action[constants.PAYLOAD][constants.IS_CHAT_ALL] = True

        # target là gì ??? all in clients ???
        broadcast(utils.encodeDict(res_action))

      # UPDATE_STATUS -> UPDATE_FRIEND_STATUS
      elif action[constants.TYPE] == constants.UPDATE_STATUS
        username = action[constants.PAYLOAD][constants.USERNAME]
        status = action[constants.PAYLOAD][constants.STATUS]

        # update user's status
        database.update_status(username, status)

        res_action[constants.TYPE] = constants.UPDATE_FRIEND_STATUS
        res_action[constants.PAYLOAD][username] = username
        res_action[constants.PAYLOAD][constants.STATUS] = status

        # target là gì ??? all in clients ???
        broadcast(utils.encodeDict(res_action))

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
