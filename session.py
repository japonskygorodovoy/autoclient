import telethon
import base64
import pickle

from os.path import isfile as file_exists

class Session(telethon.tl.Session):
  def __init__(self, *args):
    super(Session, self).__init__(*args)

  def save(self):
    if self.session_user_id:
      s = base64.encodebytes(pickle.dumps(self, protocol=0))
      with open('{}.session'.format(self.session_user_id), 'wb') as f:
        f.write(s)

  @staticmethod
  def try_load_or_create_new(session_user_id):
    if session_user_id is None:
      return Session(None)
    else:
      path = '{}.session'.format(session_user_id)
      if file_exists(path):
        with open(path, 'rb') as f:
          s = base64.decodebytes(f.read())
          return pickle.loads(s)
      else:
        return Session(session_user_id)
