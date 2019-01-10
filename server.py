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
database = Database.Database('database.json')

def accept_connections():
  while True:
    try:
      client, client_address = SERVER.accept()
      print('%s has connected' % str(client_address))
      threading.Thread(target=handle_client, args=(client,)).start()
    except KeyboardInterrupt:
      break

def handle_client(client):
  while True:
    try: 
      _action = client.recv(BUFSIZ).decode('utf-8')
      action = utils.decodeDict(_action)
      
      print(action)

      res_action = {}

      # OPEN_CONNECTION:
      # -> 1. RECEIVE_USERS
      # -> 2. AUTHENTICATION_FAIL
      if action[constants.TYPE] == constants.OPEN_CONNECTION:
        username = action[constants.PAYLOAD][constants.USERNAME]
        password = action[constants.PAYLOAD][constants.PASSWORD]

        # AUTHENTICATED
        authenticated, is_new_user = database.authenticate(username, password)
        if authenticated:
          clients[username] = client
          users = database.get_users()

          # After authenticated
          # 1. user receives a list of users
          res_action[constants.TYPE] = constants.RECEIVE_USERS
          res_action[constants.PAYLOAD] = {
            constants.USERS: users
          }

          broadcast(utils.encodeDict(res_action), None, username)

          # 2. notify other
          res_action2 = {}
          status = database.get_status(username)[constants.STATUS]
          
          if not is_new_user:
            res_action2[constants.TYPE] = constants.UPDATE_FRIEND_STATUS
            res_action2[constants.PAYLOAD] = {
              constants.USERNAME: username,
              constants.STATUS: status,
              constants.IS_ONLINE: True
            }
            broadcast(utils.encodeDict(res_action2), None, 'all')
          else:
            res_action2[constants.TYPE] = constants.NEW_USER
            res_action2[constants.PAYLOAD] = {
              constants.USERNAME: username
            }
            broadcast(utils.encodeDict(res_action2), None, 'all')
        
        # WRONG PASSWORD
        else:
          res_action[constants.TYPE] = constants.AUTHENTICATION_FAIL
          res_action[constants.PAYLOAD] = {
            constants.MESSAGE: 'Wrong password'
          }
          
          broadcast(utils.encodeDict(res_action), client, None)
          client.close()

      # CLOSE_CONNECTION -> no action sent to client ???
      elif action[constants.TYPE] == constants.CLOSE_CONNECTION:
        username = action[constants.PAYLOAD][constants.USERNAME]

        # update online status to offline if a user's connection is closed
        database.update_online_status(username, False)
        # get user's status from database
        status = database.get_status(username)[constants.STATUS]

        # close client socket
        client.close()
        # delete client from client dictionary
        del clients[username]
        
        # res_action
        res_action[constants.TYPE] = constants.UPDATE_FRIEND_STATUS
        res_action[constants.PAYLOAD] = {
          constants.USERNAME: username,
          constants.STATUS: status,
          constants.IS_ONLINE: False
        }

        broadcast(utils.encodeDict(res_action), None, 'all')

      # INIT_THREAD -> RECEIVE_THREAD_INFO
      elif action[constants.TYPE] == constants.INIT_THREAD:
        sender = action[constants.PAYLOAD][constants.SENDER]
        receiver = action[constants.PAYLOAD][constants.RECEIVER]
        chat_id = database.chat_id_generator(sender, receiver)

        # get all messages of thread
        messages = database.get_messages(chat_id)
        # get user2's status
        friend_status = database.get_status(receiver)

        res_action[constants.TYPE] = constants.RECEIVE_THREAD_INFO
        res_action[constants.PAYLOAD]= {
          constants.MESSAGES: messages,
          constants.FRIEND_STATUS: friend_status
        }

        broadcast(utils.encodeDict(res_action), None, sender)

      # SEND_MSG -> RECEIVE_MSG
      elif action[constants.TYPE] == constants.SEND_MSG:
        sender = action[constants.PAYLOAD][constants.SENDER]
        receiver = action[constants.PAYLOAD][constants.RECEIVER]
        message = action[constants.PAYLOAD][constants.MESSAGE]

        # add message to a thread
        database.add_message(message, sender, receiver)

        res_action[constants.TYPE] = constants.RECEIVE_MSG
        res_action[constants.PAYLOAD] = {
          constants.SENDER: sender,
          constants.MESSAGE: message,
          constants.IS_CHAT_ALL: False
        }

        broadcast(utils.encodeDict(res_action), None, receiver)

      # SEND_MSG_ALL -> RECEIVE_MSG
      elif action[constants.TYPE] == constants.SEND_MSG_ALL:
        sender = action[constants.PAYLOAD][constants.SENDER]
        message = action[constants.PAYLOAD][constants.MESSAGE]

        # add message to a thread named "all"
        database.add_message_all(message, sender)

        res_action[constants.TYPE] = constants.RECEIVE_MSG
        res_action[constants.PAYLOAD] = {
          constants.SENDER: sender,
          constants.MESSAGE: message,
          constants.IS_CHAT_ALL: True
        }

        broadcast(utils.encodeDict(res_action), None, 'all')

      # UPDATE_STATUS -> UPDATE_FRIEND_STATUS
      elif action[constants.TYPE] == constants.UPDATE_STATUS:
        username = action[constants.PAYLOAD][constants.USERNAME]
        status = action[constants.PAYLOAD][constants.STATUS]

        # update user's status
        database.update_status(username, status)

        res_action[constants.TYPE] = constants.UPDATE_FRIEND_STATUS
        res_action[constants.PAYLOAD] = {
          constants.USERNAME: username,
          constants.STATUS: status,
          constants.IS_ONLINE: True
        }

        broadcast(utils.encodeDict(res_action), None, 'all')

    # TODO
    except KeyboardInterrupt:
      break

def broadcast(msg, client, target):
  if client:
    client.send(bytes(msg, 'utf-8'))
  elif target:
    if target == 'all':
      for client in clients.values():
        client.send(bytes(msg, 'utf-8'))
    else:
      client_target = clients[target]
      client_target.send(bytes(msg, 'utf-8'))

if __name__ == '__main__':
  SERVER.listen(4)
  print('Waiting for incoming connections...')
  acceptThread = threading.Thread(target=accept_connections)
  acceptThread.start()
  acceptThread.join()
  SERVER.close()
