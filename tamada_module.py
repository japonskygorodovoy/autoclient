import pymongo
import chatwars_utils as utils
import telethon
import datetime
import traceback
import re

from telethon.tl.functions.channels import DeleteMessagesRequest
from telethon.tl.functions.channels import GetMessagesRequest
from telethon.tl.functions.channels import GetParticipantsRequest

from telethon.tl.functions.users    import GetFullUserRequest


from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import InputUser

SAYTEXTBOT_ID = 144248339

ZERO_DATE = datetime.datetime.utcfromtimestamp(0)

TAMADA_FLAGS = ['saytextbot']

GLOBAL_USERS_CACHE = {}

class TamadaModule:
  def __init__(self, client, self_id, channel_id):
    self._self_id = self_id
    self._channel_id = channel_id
    self._client = client
    self._dialog = utils.find_dialog(self._client, {'id': channel_id})
    self._peer   = telethon.utils.get_input_peer(self._dialog)
    self._admins = []
    if self._dialog is not None:
      self._ready = True
    else:
      self._ready = False
      return
    self._peer   = telethon.utils.get_input_peer(self._dialog)
    self._mongo  = pymongo.MongoClient()
    self._db     = self._mongo['autoclient']
    self._states = self._db['states']
    self._update_admins_list()
    self._load_settings()

  def ready(self):
    return self._ready

  def _update_admins_list(self):
    result = self._client.invoke(GetParticipantsRequest(self._peer, ChannelParticipantsAdmins(), 0, 100))
    self._admins = getattr(result, 'participants', [])
    print('Current tamada admins: ', self._admins)

  def _load_settings(self):
    collection = self._db['tamada_settings']
    settings = collection.find_one({'channel_id': self._channel_id})
    if not settings:
      settings = {'channel_id': self._channel_id}
    self._settings = settings
      
  def _save_settings(self):
    collection = self._db['tamada_settings']
    collection.replace_one({'channel_id', self._channel_id}, self._settings, upsert=True)

  def _is_admin_message(self, msg):
    from_id = getattr(msg, 'from_id', None)
    if not from_id:
      return False
    return from_id in [getattr(a, 'user_id') for a in self._admins]
    

  def _get_state(self, user_id):
    state = self._states.find_one({'user_id': user_id, 'channel_id': self._channel_id})
    if not state:
      print('Creating new state for user: ', user_id)
      state = {'user_id': user_id, 'channel_id': self._channel_id}
    def _check_default(prop, value):
      if prop not in state:
        state[prop] = value
    # Here: Init all state fields
    _check_default('last_time_ssal', ZERO_DATE)
    # State fields init end
    return state

  def _get_full_user(self, user_id):
    if user_id in GLOBAL_USERS_CACHE:
      return GLOBAL_USERS_CACHE['user_id']
    try:
      response = self._client.invoke(GetFullUserRequest(InputUser(user_id, 0)))
    except Exception as e:
      return None
      print('Cannot get full user data for user', user_id)
    user = getattr(response, 'user', None)
    if user and getattr(user, 'id', None) == user_id:
      GLOBAL_USERS_CACHE['id'] = user
      return user
    return None

  def _get_message(self, msg_id):
    response = self._client.invoke(GetMessagesRequest(self._peer, [msg_id]))
    messages = getattr(response, 'messages', None)
    if messages and len(messages) == 1:
      return messages[0]
    return None

  def _handle_admin_message(self, msg):
    text = getattr(msg, 'message', None)
    if not text:
      return
    r = re.search('/disable (?P<flag>\d+)', text)
    if r:
      flag = r.group('flag')
      if flag in TAMADA_FLAGS:
        self._settings[flag] = False
        self._save_settings()
      return True
    r = re.search('/enable (?P<flag>\d+)', text)
    if r:
      flag = r.group('flag')
      if flag in TAMADA_FLAGS:
        self._settings[flag] = True
        self._save_settings()
      return True
    # Not handled
    return False

  def handle_message(self, msg):
    try:
      self._unsafe_handle_message(msg)
    except Exception as e:
      print('Could not handle message: ', msg)
      print(e)
      traceback.print_exc()

  def _unsafe_handle_message(self, msg):
    def render_name(user):
      if getattr(user, 'username', None):
        return '@' + user.username
      name = user.first_name
      if getattr(user, 'last_name', None):
        name += ' ' + user.last_name
      return name
      
    print('Tamada:', msg)
    if self._is_admin_message(msg):
      if self._handle_admin_message(msg):
        return
    msg_id = getattr(msg, 'id', None)
    if getattr(msg, 'via_bot_id', None) == SAYTEXTBOT_ID and getattr(self._settings, 'saytextbot', False):
      self._client.invoke(DeleteMessagesRequest(self._peer, [msg_id]))
      return
    text = getattr(msg, 'message', None)
    from_id = getattr(msg, 'from_id', None)
    sender = self._get_full_user(from_id)
    if not sender:
      return
    reply_to_msg_id = getattr(msg, 'reply_to_msg_id', None)
    now = datetime.datetime.now()
    if not text or not from_id or not msg_id:
      return
    if text in ['/possat', '/nassat']:
      if reply_to_msg_id:
        msg = self._get_message(reply_to_msg_id)
        target_id = getattr(msg, 'from_id', None)
        if not target_id:
          return
        target = self._get_full_user(target_id)
        if not target:
          return
        if target_id == from_id:
          self._client.send_message(self._peer, render_name(sender) + ' обоссался!')
        else:
          self._client.send_message(self._peer, render_name(sender) + ' вероломно поссал прямо на ' + render_name(target) + '!')
      else:
        self._client.send_message(self._peer, render_name(sender) + ' поссал прямо при всех! Стыдоба!')
    elif text in ['/ping']:
        self._client.send_message(self._peer, 'Что, ' + render_name(sender) + ', заняться больше нечем?')
