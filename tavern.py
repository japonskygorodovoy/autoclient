import re
import chatwars_utils as utils
import datetime
import random
import telethon

TAVERN_OFSYANKA = {
  'id': 368519132,
  'name': 'CWTavernBot',
}

MENU = ['/bunt', '/redpower', '/ave_white', '/ghost', '/mordor', '/chlen']
CMD_DRINK = '/drink'
CMD_THROW = '/throw'

from telethon.tl.functions.messages import SendMessageRequest

class TavernState(object):
  def __init__(self, client, self_id, self_nickname):
    self._client = client
    self._dialog = utils.find_dialog(self._client, utils.TAVERN_PROPS)
    self._peer   = telethon.utils.get_input_peer(self._dialog)
    if not self._dialog:
      self._ready = False
      return
    self._ready = True
    self._self_id = self_id
    self._self_nickname = self_nickname
    _, messages, _ = self._client.get_message_history(self._dialog, limit=150)
    self._last_acion_date = datetime.datetime.now()
    for msg in messages:
      from_id = getattr(msg, 'from_id', None)
      d   = getattr(msg, 'date', None)
      if from_id == self._self_id and d:
        self._last_acion_date = d
        break
    # TODO: restore state by dialog history
    self._drink_received_at = None
    self._drink_requested = False
    self._want_throw = False

  def ready(self):
    return self._ready

  def handle_message(self, msg):
    text = getattr(msg, 'message', None)
    from_id = getattr(msg, 'from_id', None)
    msg_id = getattr(msg, 'id', None)
    now = datetime.datetime.now()
    last_action_elapsed = (now - self._last_acion_date).total_seconds()
    if not text or not from_id or not msg_id:
      return
    # TODO: make night value of 900
    delay = 300.0 if utils.is_chatwars_night() else 240.0
    #print('Tavern:', msg)
    if (re.search('А вот и я! Принесла напитки для посетителей', text) or re.search('вот тебе.*можешь смело', text)) and \
       ('@' + self._self_nickname) in text and from_id == TAVERN_OFSYANKA['id']:
      self._drink_received_at = datetime.datetime.now()
      self._drink_requested = False
      print('Tavern: Drink received.')
    elif self._drink_received_at and (now - self._drink_received_at).total_seconds() > 30.0:
      self._send(CMD_DRINK + '@' + TAVERN_OFSYANKA['name'])
      self._drink_received_at = None
    elif (last_action_elapsed > 35.0 and not self._drink_requested) or last_action_elapsed > delay:
      self._send(random.choice(MENU))
      self._drink_requested = True
    elif (re.search('Слабак что ли', text) or re.search('Как насчет добавки', text)) and ('@' + self._self_nickname) in text:
      self._want_throw = True
    elif self._want_throw:
      if random.random() < 0.09:
        self._reply_to(CMD_THROW, msg_id)
        self._want_throw = False

  def _reply_to(self, text, msg_id):
    new_id = telethon.helpers.generate_random_long()
    self._client.invoke(SendMessageRequest(self._peer, text, new_id, reply_to_msg_id=msg_id))
    self._last_acion_date = datetime.datetime.now()
    
  def _send(self, text):
    print('Sending to tavern:', text)
    self._client.send_message(self._dialog, text)
    self._last_acion_date = datetime.datetime.now()
