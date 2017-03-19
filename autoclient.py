#!/usr/bin/env python3

'''
Голосовалка "готов к бою"
UpdateEditChannelMessage
upd.message.from_id=289405263
upd.message.to_id.channel_id=1108195835
upd.message.message contains "А ты готов к битве?"
upd.message.reply_markup.rows[0].buttons[0].data='v_ready'
                                           .text='Да,всегда готов'

method: https://core.telegram.org/method/messages.receivedMessages

todo: parse UpdateReadChannelInbox from uchebka
todo: forward stock to redwings
todo: request a new stock when new resources arived
todo: alert about market chat suggestions
todo: reply about actions to addick
todo: fix attack weird waiting
todo: check time when order received
'''

import telethon
import sys
import time
import traceback
import threading
import random
import json
import datetime

from telethon.tl.types.update_new_message             import UpdateNewMessage
from telethon.tl.types.update_edit_channel_message    import UpdateEditChannelMessage
from telethon.tl.types.update_chat_user_typing        import UpdateChatUserTyping
from telethon.tl.types.update_user_status             import UpdateUserStatus
from telethon.tl.types.update_read_history_inbox      import UpdateReadHistoryInbox
from telethon.tl.types.update_channel_pinned_message  import UpdateChannelPinnedMessage

from telethon.tl.functions.messages import ReceivedMessagesRequest
from telethon.tl.functions.messages import ForwardMessageRequest

from chatwars_utils import *
from session import Session
from global_state import GlobalState
from tavern import TavernState
from tamada_module import TamadaModule

# TODO: Remove all of this when publishing!

CONFIG_PATH = 'config.json'

TOTALLY_IGNORED_MESSAGE_TYPES = [
    telethon.tl.types.update_chat_user_typing.UpdateChatUserTyping,
    telethon.tl.types.update_user_typing.UpdateUserTyping,
    telethon.tl.types.update_user_status.UpdateUserStatus,
    telethon.tl.types.update_read_history_inbox.UpdateReadHistoryInbox,
    telethon.tl.types.update_read_history_outbox.UpdateReadHistoryOutbox,
    telethon.tl.types.update_read_channel_inbox.UpdateReadChannelInbox,
    telethon.tl.types.update_read_channel_outbox.UpdateReadChannelOutbox,
    telethon.tl.types.update_delete_channel_messages.UpdateDeleteChannelMessages,
    telethon.tl.types.update_draft_message.UpdateDraftMessage,
]

GLOBAL_STATE = GlobalState()

class ChatWarsAutomator(object):
  def __init__(self, client, config):
    self.client = client
    self.config = config
    self.message_queue = []
    self.message_queue_lock = threading.Lock()
    self.last_message_received = datetime.datetime.now()
    self.intent = 'INIT'
    self.is_waiting = False
    self.wait_started = None
    self.wait_duration = None
    self.status = {}
    self.status_updated = None #timestamp of latest status
    self.latest_buttons = []
    self.last_arena_date = None
    self.order = DEFAULT_ORDER
    self.pinned_order = None
    self.pinned_order_date = None
    self.last_profile_forward_date = None
    self.last_report_forward_date = None
    self.last_sleeping_printed = datetime.datetime.now()

  def UpdateHandler(self, tgupdate):
    self.last_message_received = datetime.datetime.now()
    if hasattr(tgupdate, 'updates'):
      updates = tgupdate.updates
    elif hasattr(tgupdate, 'update'):
      updates = [tgupdate.update]
    elif isinstance(tgupdate, telethon.tl.types.update_short_message.UpdateShortMessage):
      updates = [tgupdate]
    elif isinstance(tgupdate, telethon.tl.types.update_short_chat_message.UpdateShortChatMessage):
      updates = [tgupdate]
    else:
      print('Skipped TGUpdate of class %s: ' % tgupdate.__class__.__name__, tgupdate, dir(tgupdate))
      return
    for upd in updates:
      if any(isinstance(upd, cls) for cls in TOTALLY_IGNORED_MESSAGE_TYPES):
        # 100% ignored to not shit into console
        continue
      if isinstance(upd, telethon.tl.types.update_new_message.UpdateNewMessage):
        message = getattr(upd, 'message', None)
        origin_id = getattr(message, 'from_id', None)
      elif isinstance(upd, telethon.tl.types.update_short_message.UpdateShortMessage):
        message = upd
        origin_id = getattr(message, 'user_id', None)
      elif isinstance(upd, telethon.tl.types.update_edit_message.UpdateEditMessage):
        message = getattr(upd, 'message', None)
        origin_id = getattr(message, 'from_id', None)
      elif isinstance(upd, telethon.tl.types.update_short_chat_message.UpdateShortChatMessage):
        message = upd
        origin_id = getattr(message, 'from_id', None)  # Also field 'chat_id' is present
      elif isinstance(upd, telethon.tl.types.update_new_channel_message.UpdateNewChannelMessage):
        message = getattr(upd, 'message', None)
        origin_id = getattr(getattr(message, 'to_id'), 'channel_id')
      elif isinstance(upd, telethon.tl.types.update_edit_channel_message.UpdateEditChannelMessage):
        message = getattr(upd, 'message', None)
        origin_id = getattr(getattr(message, 'to_id'), 'channel_id')
      elif isinstance(upd, UpdateChannelPinnedMessage):
        print('Handling UpdateChannelPinnedMessage: ', upd)
        self._handle_update_pinned_message(upd)
        continue
      else:
        print('Skipped update class:', upd.__class__.__name__, upd)
        continue
      if not message:
        print('Skipped update without "message" field')
        continue
      if all(origin_id != prop['id'] for prop in ALL_PROPS) and origin_id != self.config['SELF_ID']:
        #print('Skipped message not from chatwars bot: ', message)
        continue
      #print('New message: ', message, dir(message))
      #print('Text: ', message.message)
      #print('Buttons: ', get_buttons(message))
      message.origin_id = origin_id
      with self.message_queue_lock:
        self.message_queue.append(message)

  def analyze_redstatbot_history(self):
    total, messages, _ = self.client.get_message_history(self.redstatbot_dialog, limit=50)
    now = datetime.datetime.now()
    # Find last profile forward date
    for m in messages:
      parsed = RedStatBotParser(m)
      if parsed.msg_type == 'PROFILE_UPDATED':
        self.last_profile_forward_date = parsed.date
        break
    if not self.last_profile_forward_date:
      print('Cannot determine when last time profile was forwarded!')
      self.last_profile_forward_date = now
    print('Last time profile forwarded:',
          (now - self.last_profile_forward_date).total_seconds() / 3600.0,
          'hours ago')

  def loop(self):
    self.chatwars_dialog   = find_dialog(self.client, CHATWARS_PROPS)
    self.market_dialog     = find_dialog(self.client, CHATWARS_MARKET_PROPS)
    self.redcastle_dialog  = find_dialog(self.client, RED_CASTLE_COMMON_PROPS)
    self.redacademy_dialog = find_dialog(self.client, RED_CASTLE_PADAWANS_PROPS)
    self.redstatbot_dialog = find_dialog(self.client, RED_STATBOT_PROPS)
    self.redwings_dialog   = find_dialog(self.client, RED_WINGS_PROPS)
    self.adjutant_dialog   = find_dialog(self.client, RED_ACADEMYBOT_PROPS)
    self.loopback_dialog   = find_dialog(self.client, {'id': self.config['SELF_ID']})
    total, messages, _ = self.client.get_message_history(self.chatwars_dialog, limit=100)
    self.analyze_redstatbot_history()
    appended = False
    for m in messages:
      if getattr(m, 'from_id', None) != CHATWARS_PROPS['id']:
        continue
      if not appended:
        m.origin_id = m.from_id
        self.message_queue.append(m)
        appended = True
      parsed = ChatWarsMessage(m)
      if not parsed.buttons:
        continue
      elif not self.latest_buttons:
        self.latest_buttons = parsed.buttons
      if appended:
        break
    ### Find last report forward date
    now = datetime.datetime.now()
    for m in messages:
      if getattr(m, 'from_id', None) != CHATWARS_PROPS['id']:
        continue
      parsed = ChatWarsMessage(m)
      if parsed.msg_type == 'REPORT':
        self.last_report_forward_date = parsed.date
        break
    if not self.last_report_forward_date:
      print('Cannot determine when last time report was forwarded!')
      self.last_report_forward_date = now - datetime.timedelta(seconds=3600)
    print('Last time report forwarded:',
          (now - self.last_profile_forward_date).total_seconds() / 3600.0,
          'hours ago')
    ### Detecting last arena date
    for m in messages:
      if getattr(m, 'from_id', None) != CHATWARS_PROPS['id']:
        continue
      parsed = ChatWarsMessage(m)
      if parsed.msg_type == 'ARENA_FINISHED':
        self.last_arena_date = parsed.date
        break
    if not self.last_arena_date:
      print('Arena ending not detected by history!')
      self.last_arena_date = now - datetime.timedelta(seconds=55*60)
    print('Considering last arena happened ', (now - self.last_arena_date).total_seconds() / 60.0 ,'minutes ago')
    ### Last Order
    total, redstat_msgs, _ = self.client.get_message_history(self.redstatbot_dialog, limit=50)
    for m in redstat_msgs:
      if getattr(m, 'from_id', None) == RED_STATBOT_PROPS['id']:
        parsed = RedStatBotParser(m)
        if parsed.msg_type != 'ORDER':
          continue
        m.origin_id = getattr(m, 'from_id')
        self.message_queue.append(m)
        break
    else:
      print('Cannot get last order')
    ### Get pinned order
    self._update_pinned_order()
    ### Initiate tavern
    self.tavern_state = TavernState(self.client, self.config['TAVERN_ID'], self.config['NICKNAME'])
    ### Initialize tamada
    self.tamada_module = TamadaModule(self.client, self.config['TAVERN_ID'], ELDER_ACADEMY_PROPS['id'])
    ###
    self.client.add_update_handler(self.UpdateHandler)
    while True:
      msg = None
      if not GLOBAL_STATE.is_paused():
        self._check_wait()
      with self.message_queue_lock:
        if len(self.message_queue):
          msg = self.message_queue[0]
          self.message_queue = self.message_queue[1:]
      if not msg:
        TIMEOUT = 4  # Minutes - if no updates received, then reconnect.
        if (datetime.datetime.now() - self.last_message_received).total_seconds() / 60.0 > TIMEOUT:
           print('No updates from telegram last', TIMEOUT, 'minutes. Seems like update thread dead. Reconnecting.')
           GLOBAL_STATE.inc_metric('TIMEOUT_RECONNECTS')
           return
        time.sleep(5)
        continue
      self._handle_msg(msg)

  # Common pattern in autoclient reaction - ensure button, then press button,
  # then wait for response
  def _ensure_press_wait(self, button, wait):
    self._ensure_button(button)
    self._send_to_chatwars(button)
    self._wait(wait)

  def _send_order(self, order):
    if order['type'] == ORDER_DEFENCE:
      self._send_to_chatwars(BTN_MAINMENU_DEFEND)
    elif order['type'] == ORDER_ATTACK:
      self._send_to_chatwars(BTN_MAINMENU_ATTACK)
    else:
      print('Unknown order type o_O - bug in the code')
    time.sleep(3)
    self._send_to_chatwars(TARGET_TO_BUTTON[order['target']])

  def _update_pinned_order(self):
    pinned_msg = self._get_pinned_message(self.redacademy_dialog)
    if pinned_msg:
      text = getattr(pinned_msg, 'message', None)
      if not text:
        print('No text in pinned message o_O')
      else:
        if any(t in text for t in TARGET_SYMBOLS):
          self.pinned_order = ParseOrder(text)
          self.pinned_order_date = getattr(pinned_msg, 'date', None)
          print('Pinned order: ', self.pinned_order, ' - ', text)
          self._send_order(self.pinned_order)
        else:
          print('Bad pin:', text, ' - Ignored.')
    else:
      print('No pinned msg found in redacademy dialog')

  def _handle_update_pinned_message(self, upd):
    channel_id = getattr(upd, 'channel_id', None)
    if not channel_id:
      print('No channel id in pinned message update')
      return
    if channel_id != RED_CASTLE_PADAWANS_PROPS['id']:
      print('Ignored pinned message update in channel ', channel_id)
    self._update_pinned_order()


  def _handle_msg(self, msg):
    if msg.origin_id != self.config['SELF_ID'] and GLOBAL_STATE.is_paused():
      print('Autoclient paused. Message skipped!')
      return
    handlers_by_origin = {
      CHATWARS_PROPS['id']: self._handle_chatwars_msg,
      CHATWARS_MARKET_PROPS['id']: self._handle_market_msg,
      RED_CASTLE_COMMON_PROPS['id']: self._handle_redcastle_common_msg,
      RED_CASTLE_PADAWANS_PROPS['id']: self._handle_redcastle_academy_msg,
      RED_STATBOT_PROPS['id']: self._handle_redstatbot_msg,
      RED_ACADEMYBOT_PROPS['id']: self._handle_redacademybot_msg,
      TAVERN_PROPS['id']: self._handle_tavern_msg,
      ELDER_ACADEMY_PROPS['id']: self._handle_tamada_msg,
      self.config['SELF_ID']: self._handle_loopback_msg,
    }
    handler = handlers_by_origin.get(msg.origin_id, None)
    if handler:
      handler(msg)
    else:
      print('Unhandled message: cannot route by origin %s ' % msg.origin_id, msg)

  def _handle_market_msg(self, msg):
    parsed = MarketChannelParser(msg)
    if parsed.msg_type == 'EXCHANGE_PAIR':
      nickname = self.status.get('nickname', None)
      #print('Suggestion: ', parsed.params, nickname)
      if nickname in parsed.params['suggestions']:
        # TODO: seems like msg ids are different in common chats and personal chats.
        # Probably there should be another forward method.
        # This one forwards a wrong message
        self._forward_msg(parsed, self.loopback_dialog)
    else:
      pass
      #print('Market:', getattr(msg, 'message', '<no text in this message>'))

  def _handle_tavern_msg(self, msg):
    if self.config["TAVERN"] and self.tavern_state.ready():
      self.tavern_state.handle_message(msg)

  def _handle_tamada_msg(self, msg):
    if self.config["TAMADA"] and self.tamada_module.ready():
      self.tamada_module.handle_message(msg)

  def _handle_loopback_msg(self, msg):
    text = getattr(msg, 'message', None)
    if not text:
      return
    text = text.strip().lower()
    if text in ['/status', '/state', '/stats']:
      self.client.send_message(self.loopback_dialog, GLOBAL_STATE.format_stats())
    elif text in ['/stop', '/pause']:
      GLOBAL_STATE.pause()
      self.client.send_message(self.loopback_dialog, 'Autoclient paused')
    elif text in ['/start', '/resume', '/continue']:
      GLOBAL_STATE.resume()
      self.client.send_message(self.loopback_dialog, 'Autoclient resumed')
      self._send_to_chatwars(BTN_MAINMENU_HERO)

  def _handle_redcastle_common_msg(self, msg):
    print('Red Castle Common:', getattr(msg, 'message', '<no text in this message>'))

  def _handle_redcastle_academy_msg(self, msg):
    text = getattr(msg, 'message', '<no text in this message>')
    t = time_to_nearest_battle()
    if t < 5 and any(t in text for t in TARGET_SYMBOLS):
      print('Checking pinned message - probably order in academy:', text)
    else:
      print('Учебка:', text)

  def _handle_redstatbot_msg(self, msg):  # TODO: filter messages from bot and from me
    date = getattr(msg, 'date', None)
    if not date:
      print('Redstatbot msg without date:', text)
      self._wait(1)
      return
    from_order_to_battle = time_to_nearest_battle() + (datetime.datetime.now() - date).total_seconds() / 60.0
    if from_order_to_battle < 15:
      self._update_pinned_order()
    parsed = RedStatBotParser(msg)
    text = getattr(parsed.orig, 'message', '<no text in this message>')
    if parsed.msg_type == 'ORDER':
      print('Приказы:', text)
      self.order = parsed.props['order']
      if from_order_to_battle > 15:
        print('Redstat order too old - ignored: ', self.order, ' - ', text)
        self._wait(0.1)
        return
      # TODO: check msg date
      if self.pinned_order_date and self.pinned_order:
        print('Ignore currend redstat order (', text, ') - we have pin: ', self.pinned_order)
        # TODO: need to use pinned order instead of redstat
        self._send_order(self.pinned_order)
        self._wait(0.1)
        return
      print('Set current order to: ', self.order, ' - ', text)
      self._send_order(self.order)
      self._wait(1)
    elif parsed.msg_type =='PROFILE_REQUIRED':
      # Then last time forwarded - a week ago
      self.last_profile_forward_date = datetime.datetime.now() - datetime.timedelta(seconds=3600 * 24 * 7) 
    else:
      print('RedStatBot: ', text)

  def _handle_redacademybot_msg(self, msg):
    print('Хуядик:', getattr(msg, 'message', '<no text in this message>'))

  def _confirm_recv(self, msg):
    msg_id = getattr(msg.orig, 'id', None)
    if msg_id:
      self.client.invoke(ReceivedMessagesRequest(msg_id))
    else:
      print('Cannot confirm receipt of message without id:', msg)

  def _check_report_forwarded(self):
    return self._check_forward_by_var(self.last_report_forward_date)

  def _check_profile_forwarded(self):
    return self._check_forward_by_var(self.last_profile_forward_date)

  def _check_forward_by_var(self, forward_date):
    BATTLE_INTERVAL = 3600 * 4
    prev_battle_date = self.status_updated + datetime.timedelta(
          seconds=60*self.status['time_to_battle'] - BATTLE_INTERVAL)

    # prev battle date + 5 mins = valid timestamp for that forward
    prev_forward_valid = prev_battle_date + datetime.timedelta(seconds=300)
    if datetime.datetime.now() < prev_forward_valid:
      return True  # Do not forward in first 5 mins after battle
    elif forward_date > prev_battle_date:
      return True  # Do not forward if already forwarded between last date and now
    else:
      return False

  def _handle_chatwars_msg(self, msg):
    parsed = ChatWarsMessage(msg)
    #self._confirm_recv(parsed)  # Not working in current telethon. Fuck.
    if parsed.buttons:
      self.latest_buttons = parsed.buttons
    print('Message type: ', parsed.msg_type, ' Params: ', parsed.params, ' Buttons: ', parsed.buttons, 'Age minutes:', parsed.age_mins)
    if parsed.msg_type not in ['STATUS', 'QUEST_MENU', 'CASTLE',
                               'INFO1', 'INFO2', 'ARENA_ENTRY', 'TAVERN']:  # Long messages ignored
      print('Message text: ', getattr(msg, 'message', '<no text in this message>'))

    handlers = {
      'CARAVAN_ALERT': self._handler_caravan,
      'STATUS': self._handler_status,
      'QUEST_MENU': self._handler_quest_menu,
      'DEFENCE_CHOICE': self._handler_defence_choice,
      'DEFENCE_READY': self._handler_defence_ready,
      'ATTACK_CHOICE': self._handler_attack_choice,
      'ATTACK_READY': self._handler_attack_ready,
      'FOREST_STARTED': self._handler_quest_started,
      'FOREST_FINISHED': self._handler_forest_finished,
      'CAVE_STARTED':    self._handler_quest_started,
      'CASTLE': self._handler_castle,
      'ARENA_ENTRY': self._handler_arena_entry,
      'ARENA_CONFIRMED': self._handler_arena_confirmed,
      'ARENA_ROUND': self._handler_arena_round,
      'ARENA_CHOICE_DONE': self._handler_arena_choice_done,
      'ARENA_FINISHED': self._handler_arena_finished,
      'ARENA_DELAY': self._handler_arena_delay,
      'ARENA_RATING': self._handler_ignore,
      'PLAYER_BUSY': self._handler_player_busy,
      'REPORT': self._handler_report,
      'PROMO_ACTIVATED': self._handler_ignore,
      'PROMO_MESSAGE': self._handler_ignore,
      'LEVELUP_CHOICE': self._handler_levelup_choice,
      'STAMINA_RESTORED': self._handler_ignore,
      'STAMINA_LIMIT_INCREASED': self._handler_ignore,
      'TECHNICAL_WORKS': self._handler_technical_works,
      'RESOURCES_TRADED': self._handler_resources_traded,
      'STOCK': self._handler_stock,
      'ARENA_AUTOMATIC_CHOICE': self._handler_ignore,  # cannot do anything meaningful here, just wait
      'BATTLE_FINISHED':      self._handler_ignore,
      'COMMAND':              self._handler_ignore,
      'CARAVAN_FAILED1':      self._handler_ignore,
      'CARAVAN_FAILED2':      self._handler_ignore,
      'CARAVAN_TRY_PROTECT':  self._handler_ignore,
      'CARAVAN_CAPTURED':     self._handler_ignore,
      'CARAVAN_STARTED':      self._handler_ignore,
      'CARAVAN_CHALLENGED':   self._handler_ignore,
      'CARAVAN_SUCCESS':      self._handler_ignore,
      'EVENT_INACTUAL':       self._handler_ignore,
      'INFO1':                self._handler_ignore,
      'INFO2':                self._handler_ignore,
      'RENAME_FAILED_LIMIT':  self._handler_ignore,
      'RENAME_FAILED_LENGTH': self._handler_ignore,
      'RENAME_SUCCESS':       self._handler_ignore,
      'PLAYER_INVITED':       self._handler_invitation,
      'ARENA_UNAVAILABLE':    self._handler_ignore,
      'DONATE_SUCCESS':       self._handler_ignore,
      'TAVERN':               self._handler_tavern,
      'TAVERN_STARTED':       self._handler_tavern_started,
      'TAVERN_FINISHED':      self._handler_ignore,
      'TAVERN_CLOSED':        self._handler_ignore,
      'ACADEMY_UNAVAILABLE':  self._handler_ignore,
      'ACADEMY_LEARNING':     self._handler_academy_learning,
      'SPECIALIZATION_CHOICE1':  self._handler_specialization_choice,
      'SPECIALIZATION_CHOICE2':  self._handler_specialization_choice,
      'SPECIALIZATION_LEARNED': self._handler_ignore,
      'CAPTURE': self._handler_capture,
      'TIRED': self._handler_tired,
    }
    if parsed.msg_type in handlers:
      handlers[parsed.msg_type](parsed)
    else:
      GLOBAL_STATE.inc_metric('CHATWARS_UNHANDLED_MESSAGES')
      if BTN_MAINMENU_HERO in parsed.buttons and not self.is_waiting:
        self._send_to_chatwars(BTN_MAINMENU_HERO)
        self._wait(1)
      else:
        print('Unhandled message!', parsed.msg_type, getattr(msg, 'message', '<no text in this message>'), msg)
        self._wait(2)

  def _send_to_chatwars(self, text):
    time.sleep(random.randint(2, 5))
    print('Sending to chatwars: "%s"' % text)
    self.client.send_message(self.chatwars_dialog, text)

  def _handler_caravan(self, msg):
    self._send_to_chatwars(msg.params['cmd'])

  def _handler_capture(self, msg):
    GLOBAL_STATE.pause()
    self.client.send_message(self.loopback_dialog, 'Autoclient paused because of CAPTCHA! Alarm!')
    self._wait(60 * 24)

  def _handler_tired(self, msg):
    self._wait(120)

  def _handler_quest_menu(self, msg):
    if self.intent == 'QUEST':
      if is_chatwars_night():
        btn = random.choice([BTN_QUESTS_CARAVANS, BTN_QUESTS_CAVE])
        print('Night quest mode: going ', btn)
        self._ensure_press_wait(btn, 5)
      else:
        self._ensure_press_wait(BTN_QUESTS_FOREST, 5)
    else:
      self._ensure_press_wait(BTN_QUESTS_BACK, 1)

  def _handler_status(self, msg):
    self.status = msg.params
    self.status_updated = msg.date
    if self.intent == 'INIT':
      self.intent = 'IDLE'
    now = datetime.datetime.now()
    time_to_battle = self.status['time_to_battle'] - msg.age_mins
    '''  # Seems not needed anymore
    if not self.report_valid_until: # Initialization timer
      self.report_sent = True  # Set to true to prevent sending report when autoclient starts
      self.profile_forwarded = True  # Same here with forwarding fresh profile to bots
      self.report_valid_until = msg.date + datetime.timedelta(
          seconds=60*self.status['time_to_battle'] + 300)  # 5 mins after next battle
    if now > self.report_valid_until:
      self.report_sent = False
      self.profile_forwarded = False
      self.report_valid_until = msg.date + datetime.timedelta(
          seconds=60*self.status['time_to_battle'] + 300)  # 5 mins after next battle
    '''
    if msg.age_mins > 20.0 or time_to_battle < 0:  # Very old or inactual status - request a new one
      self._ensure_press_wait(BTN_MAINMENU_HERO, 10)
      self._wait(5)
      return
    # If busy - nothing else could be done, just wait
    if self.status['player_state'] in ['forest', 'tavern', 'cave', 'caravan']:
      self._wait(3)
      return
    if time_to_battle > 15.0:  # Normal mode - go farming
      if self.status['player_state'] == 'arena':  # If busy - nothing else could be done, just wait
        self._wait(8)
        return
      if self.intent == 'WAITING_FOR_REPORT':
        # Handling status msg when waiting for report - means didn't received it.
        # Then fuck it - consider forwarded
        self.last_report_forward_date = datetime.datetime.now()
        self.intent = 'IDLE'
      if self.status['level_up']:
        self._send_to_chatwars(LEVELUP_REQUEST)
        self._wait(2)
      elif self.status['class']:
        self._send_to_chatwars(CLASS_REQUEST)
        self._wait(2)
      elif not self._check_report_forwarded():
        self._send_to_chatwars(REPORT_REQUEST)
        self.intent = 'WAITING_FOR_REPORT'
        self._wait(3)
      elif not self._check_profile_forwarded():
        self._forward_msg(msg, self.adjutant_dialog)
        self._forward_msg(msg, self.redstatbot_dialog)
        self.last_profile_forward_date = datetime.datetime.now()
        self._wait(2)
      elif (self.config.get('DONATE_TO_CASTLE', False) and
            'DONATE_TO_CASTLE_THRESHOLD' in self.config and
            self.status['money'] > self.config['DONATE_TO_CASTLE_THRESHOLD']):
        donate = self.status['money'] - self.config['DONATE_TO_CASTLE_THRESHOLD']
        self._send_to_chatwars(DONATE_REQUEST + ' ' + str(donate))
        self._wait(2)
      elif (msg.params['stamina'] >= 2 and is_chatwars_night()) or (msg.params['stamina'] >=1 and not is_chatwars_night()):
        self.intent = 'QUEST'
        self._ensure_press_wait(BTN_MAINMENU_QUESTS, 10)
      elif self._worth_go_to_arena() and time_to_battle > 20.0:
        self.intent = 'ARENA'
        self._ensure_press_wait(BTN_MAINMENU_CASTLE, 10)
      elif (is_tavern_open() and
            self.config.get('DRINK', False) and
            'DRINK_THRESHOLD' in self.config and
            self.status['money'] > self.config['DRINK_THRESHOLD']):
        self.intent = 'DRINK'
        self._ensure_press_wait(BTN_MAINMENU_CASTLE, 10)
      else:
        wait_for_arena = max(60.0 - (datetime.datetime.now() - self.last_arena_date).total_seconds() / 60.0, 1.0)
        if self.status['level'] < 5 or self.status['money'] < 5:
          wait_for_arena = 240
        wait_duration = min(65, time_to_battle - 14, wait_for_arena)
        print('No available kach - waiting %f mins' % wait_duration)
        self._wait(wait_duration)
    else:  # Battle mode - go to the war
      strategy = self.config.get('STRATEGY', None)
      if strategy not in ['attack', 'defence']:
        print('Using default strategy defence because current configured strategy not known: ', strategy)
        strategy = 'defence'
      order = self._get_order()
      if self.status['player_state'] == 'arena':  # If still on arena - try to leave!
        self.intent = 'LEAVE_ARENA'
        if BTN_ARENA_LEAVE in self.latest_buttons:
          self._send_to_chatwars(BTN_ARENA_LEAVE)
          self._wait(0.5)
        else:
          self._send_to_chatwars(BTN_MAINMENU_CASTLE)
          self._wait(2)
      elif strategy == 'defence' and (self.status['player_state'] != 'defence' or self.status['target'] != HOME_TARGET):
        self.intent = 'DEFENCE'
        self._ensure_press_wait(BTN_MAINMENU_DEFEND, 2)
      elif strategy == 'attack':
        if (self.status['player_state'] != order['type'] or self.status['target'] != order['target']):
          if order['type'] == ORDER_DEFENCE:
            self.intent = 'DEFENCE'
            self._ensure_press_wait(BTN_MAINMENU_DEFEND, 4)
          elif order['type'] == ORDER_ATTACK:
            self.intent = 'ATTACK'
            self._ensure_press_wait(BTN_MAINMENU_ATTACK, 4)
          else:
            print('Unknown order :(')
            self._wait(3)
        elif time_to_battle < 6.0:  # If state is consistent with order - Press attack before battle!
          self.intent = 'WAIT_FOR_ORDER'
          self._ensure_press_wait(BTN_MAINMENU_ATTACK, 7)
        else:
          print('Seems current status matches to order. Just waiting.')
          self._wait(2)
      else:
        self._wait(8)

  def _get_order(self):
    order = self.order
    now = datetime.datetime.now()
    if self.pinned_order_date and (now - self.pinned_order_date).total_seconds() / 60.0 < 60.0 * 4 - time_to_nearest_battle() and self.pinned_order:
      order = self.pinned_order
      print('We have fresh pinned order. Using it: ', order)
    return order

  def _handler_defence_choice(self, msg):
    order = self._get_order()
    target = order['target']
    if order['type'] == 'attack':
      print('Opened defence choice on attack order - go to attack menu immediately!')
      self._send_to_chatwars(BTN_MAINMENU_ATTACK)
      self._wait(1)
      return
    for btn in msg.buttons:
      if target in btn:
        self._send_to_chatwars(btn)
        self._wait(1)
        return
    print('Cannot make a defence choice based on current order', order, '! Making a random one!')
    # Here not use latest_buttons in case of interrupting message we still defend something from current msg
    target = random.choice(msg.buttons)
    print('Defending:', target)
    self._send_to_chatwars(target)
    self._wait(1)

  def _handler_attack_choice(self, msg):
    order = self._get_order()
    if self.intent == 'WAIT_FOR_ORDER':
      print('Do not press button on attack choice - will be pressed from redstatbot handler!')
      self._wait(7)
      return
    if order['type'] == 'defence':
      print('Opened attack choice on defence order - go to defence menu immediately!')
      self._send_to_chatwars(BTN_MAINMENU_DEFEND)
      self._wait(1)
      return
    target = order['target']
    for btn in msg.buttons:
      if target in btn:
        self._send_to_chatwars(btn)
        self._wait(1)
        return
    print('Cannot make an attack choice based on current order', order, '! Making a random one!')
    # Here not use latest_buttons in case of interrupting message we still attack something from current msg
    target = random.choice(msg.buttons)
    print('Attacking:', target)
    self._send_to_chatwars(target)
    self._wait(1)

  def _handler_defence_ready(self, msg):
    self._wait(1.5)

  def _handler_attack_ready(self, msg):
    self._wait(1.5)

  def _handler_quest_started(self, msg):
    self._wait(5.5)

  def _handler_forest_finished(self, msg):
    self.intent = 'IDLE'
    self._ensure_press_wait(BTN_MAINMENU_HERO, 2)

  def _handler_castle(self, msg):
    if self.intent in ['ARENA', 'LEAVE_ARENA']:
      self._ensure_press_wait(BTN_CASTLE_ARENA, 1)
    elif self.intent == 'DRINK':
      self._ensure_press_wait(BTN_CASTLE_TAVERN, 3)
    else:
      self._ensure_press_wait(BTN_CASTLE_BACK, 3)

  def _handler_tavern(self, msg):
    if self.intent == 'DRINK':
      self._ensure_press_wait(BTN_TAVERN_DRINK, 3)
    else:
      self._ensure_press_wait(BTN_TAVERN_BACK, 3)

  def _handler_tavern_started(self, msg):
    self.intent = 'IDLE'
    self._wait(5.5)

  def _handler_arena_entry(self, msg):
    if self.intent == 'ARENA':
      self._ensure_press_wait(BTN_ARENAENTRY_SEARCH, 3)
    elif self.intent == 'LEAVE_ARENA':
      self.intent = 'IDLE'
      self._ensure_press_wait(BTN_ARENA_LEAVE, 2)
    else:
      self._ensure_press_wait(BTN_ARENAENTRY_BACK, 1)

  def _handler_arena_confirmed(self, msg):
    if self.intent != 'ARENA':
      print('You are on arena, but without intent...')
    self._wait(5)

  def _handler_arena_round(self, msg):
    btn = random.choice(self.latest_buttons)
    self._send_to_chatwars(btn)
    self._wait(1)
    if 'outcomes' in msg.params:
      self._save_arena_outcomes(msg)

  def _handler_arena_choice_done(self, msg):
    self._wait(1)

  def _handler_arena_finished(self, msg):
    self.last_arena_date = msg.date
    self.intent = 'IDLE'
    self._ensure_press_wait(BTN_MAINMENU_HERO, 5)

  def _handler_arena_delay(self, msg):
    # Next attempt for arena in 10 minutes
    self.intent = 'IDLE'
    self.last_arena_date = datetime.datetime.now() - datetime.timedelta(seconds=50*60)
    self._wait(1)

  def _handler_player_busy(self, msg):
    self._wait(4)

  def _handler_report(self, msg):
    self._forward_msg(msg, self.adjutant_dialog)
    self.last_report_forward_date = datetime.datetime.now()
    self._wait(0.5)

  def _handler_resources_traded(self, msg):
    self._send_to_chatwars(STOCK_REQUEST)
    self._wait(4)

  def _handler_stock(self, msg):
    self._forward_msg(msg, self.redwings_dialog)
    self._wait(4)

  def _handler_ignore(self, msg):
    print('Message ignored: ', msg.text)
    self._wait(1.5)

  def _handler_levelup_choice(self, msg):
    strategy = self.config.get('STRATEGY', None)
    if strategy == 'attack':
      self._ensure_press_wait(BTN_LEVELUP_ATTACK, 0.5)
    elif strategy == 'defence':
      self._ensure_press_wait(BTN_LEVELUP_DEFENCE, 0.5)
    else:
      print('Cannot do levelup choice with unknown strategy: ', strategy)
      self._wait(120)

  def _handler_technical_works(self, msg):
    self.intent = 'IDLE'
    self._wait(20)

  def _handler_academy_learning(self, msg):
    if BTN_LEARNING in self.latest_buttons:
      self._ensure_press_wait(BTN_LEARNING, 2)
    else:
      self.client.send_message(self.loopback_dialog, 'Important academy decision! Please choose wisely!')
      self._wait(20)

  def _handler_specialization_choice(self, msg):
    btns = [b for b in self.latest_buttons if b in SPEC_CONFIG_MAPPING]
    btns = [b for b in btns if SPEC_CONFIG_MAPPING[b] in self.config['SPECIALIZATIONS']]
    if len(btns) != 1:
      self.client.send_message(self.loopback_dialog, 'Cannot choose specialization! Possible choices: %d' % len(btns))
      self._wait(20)
      return
    btn = btns[0]
    print('Learning a new specialization:', btn)
    self._ensure_press_wait(btn, 2)

  def _handler_invitation(self, msg):
    join_to = []
    for button in msg.buttons:
      if all(t not in button for t in ENEMY_TARGETS):
        join_to.append(button)
    if len(join_to) != 1:
      print('Cannot Determine which castle to join! Please select manually!')
      self._wait(60)
      return
    self._send_to_chatwars(join_to[0])
    self._wait(2)

  def _wait(self, minutes):
    print('Starting wait mode for %.2f mins' % minutes)
    self.is_waiting = True
    self.wait_start = datetime.datetime.now()
    self.wait_duration = minutes

  def _worth_go_to_arena(self):
    if self.status['money'] < 5 or self.status['level'] < 5:
      return False
    if self.last_arena_date == None:  # Not relevant anymore, but just in case...
      return True
    elapsed = (datetime.datetime.now() - self.last_arena_date).total_seconds() / 60.0
    return elapsed > 60

  def _check_wait(self):
    if self.is_waiting:
      now = datetime.datetime.now()
      elapsed = (now - self.wait_start).total_seconds() / 60.0
      if elapsed > self.wait_duration:
        #msg.ensure_button(BTN_MAINMENU_HERO)
        self.is_waiting = False
        self._send_to_chatwars(BTN_MAINMENU_HERO)
      else:
        mins_left = (self.wait_duration - elapsed)
        if mins_left > 5:
          interval = 2 * 60
        else:
          interval = 10
        if (now - self.last_sleeping_printed).total_seconds() > interval:
          print('Sleeping. %.2f mins left' % mins_left)
          self.last_sleeping_printed = now

  def _ensure_button(self, btn):
    if btn in self.latest_buttons:
      return True
    GLOBAL_STATE.inc_metric('ENSURE_BUTTON_FAILURES')
    raise Exception('Cannot find latest button %s in %s' % (btn, self.latest_buttons))

  def _forward_msg(self, msg, dialog):
    if not dialog:
      print('Skipped forwarding msg because dialog not found')
      return
    fwd_id = telethon.helpers.generate_random_long()
    peer = telethon.utils.get_input_peer(dialog)
    msg_id = getattr(msg.orig, 'id', None)
    if msg_id:
      print('Forwarding', msg_id, 'to', peer, msg.orig)
      self.client.invoke(ForwardMessageRequest(peer, msg_id, fwd_id))
      return True
    else:
      print('Cannot forward message: msg id unavailable: ', msg.orig)
      print('Destination dialog: ', dialog)
      return False

  def _save_arena_outcomes(self, msg):
    msg_id = getattr(msg.orig, 'id', None)
    if not msg_id:
      print('Skipped saving arena outcomes: msg has no id!', msg.orig)
    s = repr({'id': msg_id, 'outcomes': msg.params['outcomes']})
    with open(self.config['ARENA_LOG'], 'a') as f:
      f.write(s + '\n')

  def _get_pinned_message(self, dialog):
    if not dialog:
      return None
    peer = telethon.utils.get_input_peer(dialog)
    full = self.client.invoke(telethon.tl.functions.channels.GetFullChannelRequest(peer))
    dialog_id = getattr(dialog, 'id', '<no id o_O>')
    if not full:
      print('Cannot get full channel for dialog', dialog_id)
      return None
    pinned = getattr(getattr(full, 'full_chat', None), 'pinned_msg_id', None)
    if not pinned:
      print('Cannot get pinned message for dialog', dialog_id)
      return None
    msgs = self.client.invoke(telethon.tl.functions.channels.get_messages.GetMessagesRequest(peer, [pinned]))
    if not msgs or len(getattr(msgs, 'messages', [])) != 1:
      print('Error getting pinned message ', pinned, 'in dialog', dialog_id)
      return None
    return msgs.messages[0]
    


def req_input(req_text):
  sys.stdout.write(req_text + '> ')
  return input()

def authorize(client, phone):
  client.send_code_request(phone)
  code = req_input('Auth code')
  client.sign_in(phone, code)

def main():
  with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)
  while True:
    print('Connecting to telegram...')
    session = Session.try_load_or_create_new(CONFIG['SESSION'])
    client = telethon.TelegramClient(session, CONFIG['API_ID'], CONFIG['API_HASH'])
    client.connect()
    if not client.is_user_authorized():
      print('Not authorized')
      if not CONFIG['PRODUCTION']:
        authorize(client, CONFIG['PHONE_NUMBER'])
      else:
        raise Exception('Unable to authorize on production. Please deliver valid auth token')
    try:
      a = ChatWarsAutomator(client, CONFIG)
      a.loop()
    except Exception as e:
      print('Exception during chatwars automation process: ', e)
      traceback.print_exc()
    print('Disconnecting...')
    GLOBAL_STATE.inc_metric('TOTAL_RECONNECTS')
    client.disconnect()
    time.sleep(5)


if __name__ == '__main__':
  main()
