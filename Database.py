import constants

class Database:
  def __init__(self, file_name):
    # doc file 
    self.database = {}

  def chat_id_generator(username1, username2):
    if (username1 > username2):
      return username2 + '-' + username1
    return username1 + '-' + username2

  def get_messages(self, chat_id):
    if chat_id in self.database[constants.CHATS]:
      return self.database[constants.CHATS][chat_id]

    return []

  def get_users(self):
    return self.database[constants.USERS].keys()

  def get_status(self, username):
    return self.database[constants.STATUSES][username]

  def add_message(self, message, username1, username2):
    self.database[constants.CHATS][self.chat_id_generator(username1, username2)] = message

  def add_message_all(self, message, username):
    new_entry = {}
    new_entry[constants.SENDER] = username
    new_entry[constants.MESSAGE] = message

    self.database[constants.CHATS][constants.ALL].push(new_entry)

  def register(self, username, password):
    self.database[constants.USERS][username] = password

  def update_status(self, username, status):
    self.database[constants.STATUSES][username][constants.STATUS] = status

  def update_online_status(self, username, online_status):
    self.database[constants.STATUSES][username][constants.IS_ONLINE] = online_status

  def authenticate(self, username, password):
    if (username in self.database[constants.USER]):
      if self.database[constants.USER][username] == password:
        self.update_online_status(username, True)
        return True
      return False
    
    self.register(username, password)
    return True