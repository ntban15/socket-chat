# database keys
CHATS = 'chats'
ALL = 'all'
USERS = 'users'
STATUSES = 'statuses'

# dictionary keys
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

class Database:
  def __init__(self, file_name):
    # doc file 
    self.database = {}

  def chat_id_generator(username1, username2):
    if (username1 > username2):
      return username2 + '-' + username1
    return username1 + '-' + username2

  def get_messages(chat_id):
    if chat_id in self.database[CHATS]:
      return self.database[CHATS][chat_id]

    return []

  def get_users():
    return self.database[USERS].keys()

  def get_status(username):
    return self.database[STATUSES][username]

  def register(username, password):
    self.database[USERS][username] = password

  def update_online_status(username):
    self.database[STATUSES][username][IS_ONLINE] = True

  def authenticate(username, password):
    if (username in self.database[USER]):
      if self.database[USER][username] == password:
        self.update_online_status(username)
        return True
      return False
    
    self.register(username, password)
    return True