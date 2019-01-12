import utils
import constants

class Database:
  def __init__(self, file_name):
    self.db_name = file_name

    with open(self.db_name, 'r') as file:
      db_text = file.read()
      self.database = utils.decodeDict(db_text)
  
  def write_db(self):
    with open(self.db_name, 'w') as file:
      file.write(utils.encodeDict(self.database))

  def chat_id_generator(self, username1, username2):
    if username2 == 'all':
      return username2
    if (username1 > username2):
      return username2 + '-' + username1
    return username1 + '-' + username2

  def get_messages(self, chat_id):
    if chat_id in self.database[constants.CHATS]:
      return self.database[constants.CHATS][chat_id]

    return []

  def get_users(self):
    return list(self.database[constants.USERS].keys())

  def get_status(self, username):
    return self.database[constants.STATUSES][username]

  def add_message(self, message, username1, username2):
    chat_id = self.chat_id_generator(username1, username2)
    message_entry = {
      constants.SENDER: username1,
      constants.RECEIVER: username2,
      constants.MESSAGE: message
    }

    if chat_id in self.database[constants.CHATS]:
      self.database[constants.CHATS][chat_id].append(message_entry)
    else:
      self.database[constants.CHATS][chat_id] = [message_entry]

    # write new db to file
    self.write_db()

  def add_message_all(self, message, username):
    message_entry = {
      constants.SENDER: username,
      constants.MESSAGE: message
    }
    if constants.ALL in self.database[constants.CHATS]:
      self.database[constants.CHATS][constants.ALL].append(message_entry)
    else:
      self.database[constants.CHATS][constants.ALL] = [message_entry]

    # write new db to file
    self.write_db()

  def register(self, username, password):
    self.database[constants.USERS][username] = password
    self.database[constants.STATUSES][username] = {
      constants.IS_ONLINE: True,
      constants.STATUS: '',
      constants.AVATAR: 'avatar.jpg'
    }

    # write new db to file
    self.write_db()

  def update_status(self, username, status, avatar):
    self.database[constants.STATUSES][username][constants.STATUS] = status
    self.database[constants.STATUSES][username][constants.AVATAR] = avatar

    # write new db to file
    self.write_db()

  def update_online_status(self, username, online_status):
    self.database[constants.STATUSES][username][constants.IS_ONLINE] = online_status

    # write new db to file
    self.write_db()

  def authenticate(self, username, password):
    if (username in self.database[constants.USERS]):
      if self.database[constants.USERS][username] == password:
        self.update_online_status(username, True)
        return True, False
      return False, False
    
    self.register(username, password)
    return True, True