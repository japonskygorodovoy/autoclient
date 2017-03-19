#!/usr/bin/env python3

import json
import pickle
import telethon
import chatwars_utils as utils
from session import Session

CONFIG_PATH = 'config.json'
HISTORY_PATH = 'all_history.pickle'
MAX_HISTORY = 1000000

def prepare_client():
  with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)
  session = Session.try_load_or_create_new(CONFIG['SESSION'])
  client = telethon.TelegramClient(session, CONFIG['API_ID'], CONFIG['API_HASH'])
  client.connect()
  if not client.is_user_authorized():
    print('Not authorized')
    if not CONFIG['PRODUCTION']:
      authorize(client, CONFIG['PHONE_NUMBER'])
    else:
      raise Exception('Unable to authorize on production. Please deliver valid auth token')
  return client

def main():
  ofs_id = 0
  messages = []
  while True:
    try:
      print('Connecting...')
      client = prepare_client()
      dialog = utils.find_dialog(client, utils.CHATWARS_PROPS)
      print('Downloading history')
      while True:
        total, msgs, _ = client.get_message_history(dialog, limit=250, offset_id=ofs_id)
        if len(msgs) == 0 or len(messages) >= MAX_HISTORY:
          break
        ofs_id = msgs[-1].id
        messages.extend(msgs)
        print('Mesages count: %d (of %d), ofs_id = %d' % (len(messages), total, ofs_id))
    except Exception as e:
      print('Telethon fucked up. Reconnecting.', e)
      continue
    break
  print('------')
  print('Total downloaded %d messages' % len(messages))
  with open(HISTORY_PATH, 'wb') as f:
    pickle.dump(messages, f)
  client.disconnect()

if __name__ == '__main__':
  main()
