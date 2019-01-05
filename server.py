#!usr/bin/env python3

import socket
import threading

clients = {}
HOST = '127.0.0.1'
PORT = 8000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)

def accept_connections():
  while True:
    client, client_address = SERVER.accept()
    print('%s has connected' % str(client_address))
    threading.Thread(target=handle_client, args=(client,)).start()

def handle_client(client):
  client.send(bytes('Welcome to my chat app. What is your name?', 'utf-8'))
  name = client.recv(BUFSIZ).decode('utf-8')
  client.send(bytes('Type /quit if you want to exit the chat app', 'utf-8'))
  clients[client] = name
  while True:
    msg = client.recv(BUFSIZ)
    if msg != bytes('/quit', 'utf-8'):
      broadcast(name + ': ' + msg.decode('utf-8'))
    else:
      client.send(msg)
      client.close()
      del clients[client]
      broadcast('%s has leaved the room' % str(name))
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
