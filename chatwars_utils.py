import re
import datetime
import pytz
import time

CHATWARS_PROPS            = {'id': 265204902, 'first_name': 'Chat Wars', 'last_name': None, 'bot': True, 'username': 'ChatWarsBot'}
CHATWARS_MARKET_PROPS     = {'id': 1112398751, 'title': 'Chat Wars Marketplace'}
CHATWARS_TRADEBOT_PROPS   = {'id': 278525885, 'first_name': 'ChatWarsTradeBot', 'last_name': None, 'bot': True, 'username': 'ChatWarsTradeBot'}
CHATWARS_REPORTS_PROPS    = {'id': 1090201075, 'title': 'Chat Wars Reports', 'username': 'chatwarsreports'}
RED_CASTLE_COMMON_PROPS   = {'id': 1062570573, 'title': 'Chat Wars Red'}
RED_CASTLE_PADAWANS_PROPS = {'id': 1108195835}  # , 'title': 'Учебка Красного замка!'}
RED_STATBOT_PROPS         = {'id': 296332261, 'bot': True, 'username': 'RedStatBot'} # 'first_name': 'RedStatBot', 'last_name': None,
RED_ACADEMYBOT_PROPS      = {'id': 289405263, 'bot': True, 'username': 'RedCastleAcademyBot'} # 'first_name': 'Адъютант', 'last_name': None,
RED_WINGS_PROPS           = {'id': 314629547, 'bot': True, 'username': 'RedwingBot'} # 'first_name': 'Redwing', 'last_name': None,
TAVERN_PROPS              = {'id': 1104513622, 'username': 'drinkstardust'}
TEST_CHANNEL_PROPS        = {'id': 1093775502}
ELDER_ACADEMY_PROPS       = {'id': 1071183705}

ALL_PROPS = [CHATWARS_PROPS, CHATWARS_MARKET_PROPS, CHATWARS_TRADEBOT_PROPS, CHATWARS_REPORTS_PROPS,
             RED_CASTLE_COMMON_PROPS, RED_CASTLE_PADAWANS_PROPS, RED_STATBOT_PROPS, RED_ACADEMYBOT_PROPS, RED_WINGS_PROPS,
             TAVERN_PROPS, TEST_CHANNEL_PROPS, ELDER_ACADEMY_PROPS]

BTN_MAINMENU_ATTACK = '\u2694 Атака'
BTN_MAINMENU_DEFEND = '\U0001f6e1 Защита'
BTN_MAINMENU_QUESTS = '\U0001f5fa Квесты'
BTN_MAINMENU_HERO   = '\U0001f3c5Герой'
BTN_MAINMENU_CASTLE = '\U0001f3f0Замок'

BTN_QUESTS_FOREST   = '\U0001f332Лес'
BTN_QUESTS_CARAVANS = '\U0001f42bГРАБИТЬ КОРОВАНЫ'
BTN_QUESTS_CAVE     = '\U0001f578Пещера'
BTN_QUESTS_BACK     = '\u2b05\ufe0fНазад'

BTN_CASTLE_WORKSHOP = '\u2692Мастерская'
BTN_CASTLE_SHOP     = '\U0001f3daЛавка'
BTN_CASTLE_TAVERN   = '\U0001f37aТаверна'
BTN_CASTLE_ARENA    = '\U0001f4efАрена'
BTN_CASTLE_BACK     = '\u2b05\ufe0fНазад'
BTN_CASTLE_ACADEMY  = 'TODO'

BTN_TAVERN_DRINK    = '\U0001f37aВзять кружку эля'
BTN_TAVERN_GAMBLE   = '\U0001f3b2Играть в кости'
BTN_TAVERN_STRANGER = '\U0001f575️Поговорить с незнакомцем'
BTN_TAVERN_BACK     = '\u2b05\ufe0fНазад'

BTN_ARENAENTRY_SEARCH = '\U0001f50eПоиск соперника'
BTN_ARENAENTRY_BACK   = '\u2b05\ufe0fНазад'

BTN_ARENA_LEAVE       = '\u2716\ufe0fОтменить поиск'

BTN_ARENA_ATTACKHEAD  = '\U0001f5e1в голову'
BTN_ARENA_ATTACKBODY  = '\U0001f5e1по корпусу'
BTN_ARENA_ATTACKLEGS  = '\U0001f5e1по ногам'
BTN_ARENA_DEFENDHEAD  = '\U0001f6e1головы'
BTN_ARENA_DEFENDBODY  = '\U0001f6e1корпуса'
BTN_ARENA_DEFENDLEGS  = '\U0001f6e1ног'

BTN_LEVELUP_ATTACK    = '+1 \u2694Атака'
BTN_LEVELUP_DEFENCE   = '+1 \U0001f6e1Защита'

BTN_LEARNING          = '\U0001f4da Обучение'
BTN_SPEC_ESQUIRE      = '\u2694\ufe0f Эсквайр \U0001f6e1'
BTN_SPEC_MASTER       = '\U0001f6e0 Мастер \U0001f4e6'
BTN_SPEC_ATTACKER     = '\u2694\ufe0f Рыцарь'
BTN_SPEC_DEFENDER     = '\U0001f6e1 Страж'
BTN_SPEC_BACK         = '\u2b05\ufe0fНазад'

SPEC_CONFIG_MAPPING = {
  BTN_SPEC_ESQUIRE:  'ESQUIRE', 
  BTN_SPEC_MASTER:   'MASTER', 
  BTN_SPEC_ATTACKER: 'ATTACKER', 
  BTN_SPEC_DEFENDER: 'DEFENDER', 
}

SYMBOL_FOREST       = '\U0001f332'
SYMBOL_MOUNTAIN     = '\u26f0'
SYMBOL_FLAG_YELLOW  = '\U0001f1fb\U0001f1e6'
SYMBOL_FLAG_RED     = '\U0001f1ee\U0001f1f2'
SYMBOL_FLAG_BLACK   = '\U0001f1ec\U0001f1f5'
SYMBOL_FLAG_WHITE   = '\U0001f1e8\U0001f1fe'
SYMBOL_FLAG_BLUE    = '\U0001f1ea\U0001f1fa'

SYMBOL_GOLD         = '\U0001f4b0'

REPORT_REQUEST      = '/report'
LEVELUP_REQUEST     = '/level_up'
STOCK_REQUEST       = '/stock'
DONATE_REQUEST      = '/donate'
CLASS_REQUEST       = '/class'

# Symbols of possible targets
TARGET_SYMBOLS = [SYMBOL_FOREST, SYMBOL_MOUNTAIN, SYMBOL_FLAG_YELLOW, SYMBOL_FLAG_RED, SYMBOL_FLAG_BLACK, SYMBOL_FLAG_WHITE, SYMBOL_FLAG_BLUE]
ENEMY_TARGETS  = [SYMBOL_FLAG_YELLOW, SYMBOL_FLAG_BLACK, SYMBOL_FLAG_WHITE, SYMBOL_FLAG_BLUE]
HOME_TARGET    = SYMBOL_FLAG_RED

ARENA_BUTTONS = [BTN_ARENA_ATTACKHEAD, BTN_ARENA_ATTACKBODY, BTN_ARENA_ATTACKLEGS,
                 BTN_ARENA_DEFENDHEAD, BTN_ARENA_DEFENDBODY, BTN_ARENA_DEFENDLEGS]

TARGET_TO_BUTTON = {
  SYMBOL_FOREST:      SYMBOL_FOREST   + 'Лесной форт',
  SYMBOL_MOUNTAIN:    SYMBOL_MOUNTAIN + 'Горный форт',
  SYMBOL_FLAG_RED:    SYMBOL_FLAG_RED,
  SYMBOL_FLAG_YELLOW: SYMBOL_FLAG_YELLOW,
  SYMBOL_FLAG_BLACK:  SYMBOL_FLAG_BLACK,
  SYMBOL_FLAG_BLUE:   SYMBOL_FLAG_BLUE,
  SYMBOL_FLAG_WHITE:  SYMBOL_FLAG_WHITE,
}

ORDER_DEFENCE = 'defence'
ORDER_ATTACK  = 'attack'

DEFAULT_ORDER = {'type': ORDER_DEFENCE, 'target': SYMBOL_FLAG_RED}

TIMEZONE = pytz.timezone('Europe/Moscow')
BATTLE_HOURS = [0, 4, 8, 12, 16, 20]  # Moscow timezone

# At night we go to caravans and cave.
def is_chatwars_night():
  h = datetime.datetime.now(TIMEZONE).hour
  return h >= 1 and h <= 6

def is_tavern_open():
  h = datetime.datetime.now(TIMEZONE).hour
  return h >= 19 or h <= 6  # Tavern works from 19:00 to 6:59

# Returns time in minutes
def time_to_nearest_battle():
  now = datetime.datetime.now(TIMEZONE)
  ts = dict([((b-now.hour+24) % 24, b) for b in BATTLE_HOURS if b != now.hour])
  hrs_left = min(ts.keys())
  return hrs_left * 60 - now.minute

def find_dialog(client, props):
  ATTEMPTS = 3
  for i in range(ATTEMPTS):  # get_dialogs is unstable method
    try:
      dialogs = client.get_dialogs(count=100)
      for entity in dialogs[1]:
        if all(hasattr(entity, k) and getattr(entity, k) == v for k, v in props.items()):
          return entity
      print('Cannot find dialog with props: %s. Will try to work without it!' % props)
      return None
    except Exception as e:
      if i + 1 != ATTEMPTS:
        print('get_dialogs fucked up!. Error: "' + str(e) + '". Next attempt...')
        time.sleep(2)
      else:
        print('get_dialogs failed', ATTEMPTS, 'times. Fucking up :(')
        raise e

def get_buttons(message):
  if not getattr(message, 'reply_markup', None):
    return []
  result = []
  rows = getattr(message.reply_markup, 'rows', [])
  for row in rows:
    buttons = getattr(row, 'buttons', [])
    for btn in buttons:
      if hasattr(btn, 'text'):
        result.append(btn.text)
  return result

class ChatWarsMessage(object):
  def __init__(self, message):
    self.orig = message
    self.buttons = get_buttons(message)
    self.msg_type = 'UNKNOWN'
    text = getattr(message, 'message', None)
    self.text = text
    self.date = getattr(message, 'date', None)
    self.params = {}
    self.age_mins = (datetime.datetime.now() - self.date).total_seconds() / 60.0
    if not text:
      return
    if not self.date:
      print('Received a message without date!')
      return

    parsers = {
      'STATUS': self._try_parse_status,
      'QUEST_MENU':              self._try_parse_quest_menu,
      'CARAVAN_ALERT':           self._try_parse_caravan_alert,
      'ATTACK_CHOICE':           self._simple_regex_searcher('Смелый вояка! Выбирай врага'),
      'DEFENCE_CHOICE':          self._simple_regex_searcher('Храбрый защитник! Где будем держать оборону?'),
      'DEFENCE_READY':           self._simple_regex_searcher('Ты приготовился к защите. Ближайшее сражение через'),
      'ATTACK_READY':            self._simple_regex_searcher('Ты приготовился к атаке. Ближайшее сражение через'),
      'FOREST_STARTED':          self._simple_regex_searcher('Ты отправился искать приключения в лес. Вернешься через 5 минут.'),
      'FOREST_FINISHED':         self._try_parse_forest_finished,
      'CAVE_STARTED':            self._simple_regex_searcher('Ты отправился искать приключения в пещеру. Вернешься через'),
      'CASTLE':                  self._simple_regex_searcher('Отчет о битве: ', 'Общий отчет:', 'Таверна работает вечером после VII часов.'),
      'ARENA_ENTRY':             self._try_parse_arena_entry,
      'ARENA_CONFIRMED':         self._simple_regex_searcher('Ищем соперника. Пока соперник не найден, ты можешь в любой момент отменить поиск'),
      'ARENA_ROUND':             self._try_parse_arena_round,
      'ARENA_CHOICE_DONE':       self._simple_regex_searcher('Хороший план, посмотрим что из этого выйдет.'),
      'ARENA_FINISHED':          self._try_parse_arena_finished,
      'ARENA_DELAY':             self._try_parse_arena_delay,
      'ARENA_RATING':            self._simple_regex_searcher('самых сильных воинов пяти замков'),
      'PLAYER_BUSY':             self._simple_regex_searcher('Ты сейчас занят другим приключением. Попробуй позже.'),
      'REPORT':                  self._simple_regex_searcher('Твои результаты в бою:'),
      'PROMO_ACTIVATED':         self._simple_regex_searcher('зашел в игру по твоей ссылке', 'к выносливости когда', 'разберётся в игре'),
      'PROMO_MESSAGE':           self._simple_regex_searcher('Присоединяйся к игре Chat Wars! Первая ММОРПГ в Telegram. Заходи по ссылке и получишь'),
      'LEVELUP_CHOICE':          self._simple_regex_searcher('Выбирай, какую характеристику ты хочешь улучшить'),
      'STAMINA_RESTORED':        self._simple_regex_searcher('Выносливость восстановлена: ты полон сил. Вперед на поиски приключений!'),
      'STAMINA_LIMIT_INCREASED': self._simple_regex_searcher('разобрался в игре.', 'Ты получаешь', 'к выносливости.'),
      'TECHNICAL_WORKS':         self._simple_regex_searcher('Технические работы в замке. Попробуй позже.'),
      'RESOURCES_TRADED':        self._simple_regex_searcher('Получено от'),
      'STOCK':                   self._try_parse_stock,
      'ARENA_AUTOMATIC_CHOICE':  self._simple_regex_searcher('Слишком долго! Выбор сделан автоматически.'),
      'BATTLE_FINISHED':         self._simple_regex_searcher('Ветер завывает по окрестным лугам, замки как будто вымерли. '
                                                             'Это воины зашивают раны и латают доспехи'),
      'COMMAND':                 self._try_parse_command,
      'CARAVAN_FAILED1':         self._simple_regex_searcher('Вы упустили', 'он безнаказанно ограбил КОРОВАН'),
      'CARAVAN_FAILED2':         self._simple_regex_searcher('Вы пытались остановить',
                                                             'но он оказался сильнее. Пришлось отступить. Но зато КОРОВАН в безопасности добрался'),
      'CARAVAN_TRY_PROTECT':     self._simple_regex_searcher('Ты встал на защиту КОРОВАНА.'),
      'CARAVAN_CAPTURED':        self._simple_regex_searcher('Вы задержали', 'Получено'),
      'CARAVAN_STARTED':         self._simple_regex_searcher('Ты отправился грабить КОРОВАНЫ. Доберешься до ближайшего'),
      'CARAVAN_CHALLENGED':      self._simple_regex_searcher('Рядом с КОРОВАНОМ вы увидели воина', 'Будем надеяться, что он не заметит вас.'),
      'CARAVAN_SUCCESS':         self._simple_regex_searcher('не обратил на вас внимания. КОРОВАН ваш'),
      'EVENT_INACTUAL':          self._simple_regex_searcher('Слишком поздно, событие не актуально.'),
      'INFO1':                   self._simple_regex_searcher('Жители замка могут присоединиться к тайному чату:',
                                                             'Чтобы поменять имя в игре, напиши боту'),
      'INFO2':                   self._simple_regex_searcher('Общение внутри замка:', 'Чат всех замков:', 'Новости игры:'),
      'RENAME_FAILED_LIMIT':     self._simple_regex_searcher('Дополнительная смена имени стоит', 'по дневному тарифу ЗАГСа.'),
      'RENAME_FAILED_LENGTH':    self._simple_regex_searcher('Британские учёные выяснили, что длина имени рыцаря пропорциональна длине его меча.'),    
      'RENAME_SUCCESS':          self._simple_regex_searcher('Ты сменил имя на', r'Проще чем в жизни, да\? Не надо идти в ЗАГС.'),
      'PLAYER_INVITED':          self._simple_regex_searcher('Тебя пригласил в игру воин', 'Выбери замок, за который ты будешь сражаться'),
      'ARENA_UNAVAILABLE':       self._simple_regex_searcher('Поединки доступны для воинов 5го уровня и выше.'),
      'DONATE_SUCCESS':          self._simple_regex_searcher('Взноc в казну замка сделан успешно.'),
      'TAVERN':                  self._simple_regex_searcher('Ты зашел внутрь и видишь шумную толпу пьяных солдат и обычных жителей замка. '
                                                             'Можешь взять кружку эля и сесть рядом'),
      'TAVERN_STARTED':          self._simple_regex_searcher('Тебе принесли полную до краев кружку свежего эля. '
                                                             'Теперь можно спокойной посидеть и послушать что говорят люди вокруг.'),
      'TAVERN_FINISHED':         self._try_parse_tavern_finished,
      'TAVERN_CLOSED':           self._simple_regex_searcher('Кто ж днем в баре сидит\? Таверна закрыта до вечера. Приходи попозже.'),
      'ACADEMY_UNAVAILABLE':     self._simple_regex_searcher('Освободи свою голову от войны, она пока не готова к знаниям.'),
      'ACADEMY_LEARNING':        self._simple_regex_searcher('Учиться никогда не поздно. Посмотрим, чему мы тебя можем научить.'),
      'SPECIALIZATION_CHOICE1':  self._simple_regex_searcher('Пришло время определиться со своим предназначением, с тем, каким тебя запомнят потомки.'),
      'SPECIALIZATION_CHOICE2':  self._simple_regex_searcher('Как и перед любым воином, перед тобой стоит выбор: '
                                                             'ввергать в бегство врагов или защищать твердыню'),
      'SPECIALIZATION_LEARNED':  self._simple_regex_searcher('Ты стал умнее и опытнее. Теперь у тебя новые навыки'),
      'BUTTON': self._try_parse_button,
      'CAPTURE': self._simple_regex_searcher('На выходе из замка охрана никого не пропускает'),
      'TIRED': self._simple_regex_searcher('Ты слишком устал, возвращайся когда отдохнешь.'),
    }
    def call_parser(item):
      parsed, params = item[1]()
      return (item[0], parsed, params)
    parse_results = [r for r in map(call_parser, parsers.items()) if r[1]]
    if len(parse_results) != 1:
      self.msg_type = 'UNKNOWN'
      self.params = {}
      print('Error while parsing chatwars message: ', self.text)
      print('Possible parsers: [', ','.join([r[0] for r in parse_results]), ']')
      return
    self.msg_type, _, self.params = parse_results[0]

  def _simple_regex_searcher(self, *args):
    def searcher():
      return all(re.search(regex, self.text) for regex in args), {}
    return searcher

  def ensure_button(self, btn):
    if btn in self.buttons:
      return True
    raise Exception('Cannot find button %s in %s' % (btn, self.buttons))

  def _try_parse_status(self):
    params = {}
    lines = self.text.split('\n')
    for line in lines:
      r = re.search(r'Битва пяти замков через (?P<time>.*)!', line)
      if not r:
        continue
      t = r.groupdict()['time']
      for pattern in [r'(?P<hour>\d+)ч (?P<min>\d+) минут', '(?P<hour>\d+)ч', '(?P<min>\d+) минут', 'несколько секунд']:
        r = re.search(pattern, t)
        if not r:
          continue
        fields = r.groupdict()
        params['time_to_battle'] = int(fields.get('hour', 0)) * 60 + int(fields.get('min', 0))
        break
    if 'time_to_battle' not in params:
      return False, {}
    for line in lines:
      r = re.search(HOME_TARGET + r'(?P<nickname>[\w ]+), .* замка', line)
      if not r:
        continue
      params['nickname'] = r.groupdict()['nickname']
    if 'nickname' not in params:
      print('No nickname in status message')
      return False, {}
    for line in lines:
      r = re.search(r'Уровень: (?P<level>\d+)', line)
      if not r:
        continue
      params['level'] = int(r.groupdict()['level'])
    if 'level' not in params:
      print('No level in status message')
      return False, {}
    for line in lines:
      r = re.search(r'Выносливость: (?P<stamina>\d+)/(?P<maxstamina>\d+)', line)
      if not r:
        r = re.search(r'Выносливость: (?P<stamina>\d+) из (?P<maxstamina>\d+)', line)
      if not r:
        continue
      params['stamina']     = int(r.groupdict()['stamina'])
      params['max_stamina'] = int(r.groupdict()['maxstamina'])
    if 'stamina' not in params or 'max_stamina' not in params:
      print('No stamina in status message')
      return False, {}
    for line in lines:
      r = re.search(SYMBOL_GOLD + r'(?P<money>\d+)', line)
      if not r:
        r = re.search(r'Золото: (?P<money>\d+)', line)
      if not r:
        continue
      params['money']     = int(r.groupdict()['money'])
    if 'money' not in params:
      print('No money in status message')
      return False, {}
    for line in lines:
      r = re.search(r'Опыт: (?P<xp>\d+)/(?P<xp_threshold>\d+)', line)
      if not r:
        r = re.search(r'Опыт: (?P<xp>\d+) из (?P<xp_threshold>\d+)', line)
      if not r:
        continue
      params['xp']     = int(r.groupdict()['xp'])
      params['xp_threshold']     = int(r.groupdict()['xp_threshold'])
    if 'xp' not in params:
      print('No xp in status message')
      return False, {}
    for i, line in enumerate(lines):
      r = re.search('Состояние:', line)
      if (not r) or (i+1 == len(lines)):
        continue
      state_line = lines[i+1]
      if re.search('Отдых', state_line):
        params['player_state'] = 'relax'
        params['target'] = 'nothing'
        break
      if re.search('В лесу. Вернешься через', state_line):
        params['player_state'] = 'forest'
        params['target'] = 'nothing'
        break
      if re.search('На арене', state_line):
        params['player_state'] = 'arena'
        params['target'] = 'nothing'
      if re.search('В пещере', state_line):
        params['player_state'] = 'cave'
        params['target'] = 'nothing'
      if re.search('Пьешь в таверне', state_line):
        params['player_state'] = 'tavern'
        params['target'] = 'nothing'
      if re.search('Возишься с КОРОВАНАМИ', state_line):
        params['player_state'] = 'caravan'
        params['target'] = 'nothing'
      # space is importent to distinguish with player attack/defence stats line
      r = re.search('Защита ', state_line) 
      if r:
        params['player_state'] = ORDER_DEFENCE
        for t in TARGET_SYMBOLS:
          if t in state_line:
            params['target'] = t
        break
      r = re.search('Атака на ', state_line)
      if r:
        params['player_state'] = ORDER_ATTACK
        for t in TARGET_SYMBOLS:
          if t in state_line:
            params['target'] = t
        break
    if 'target' not in params or 'player_state' not in params:
      print('No target in status message')
      return False, {}
    params['level_up'] = any(re.search('Поздравляем! Новый уровень!', line) for line in lines) and any(re.search('Жми /level_up', line) for line in lines)
    params['class']    = any(re.search('Определись со специализацией.', line) for line in lines) and any(re.search('Жми /class', line) for line in lines)
    return True, params

  def _try_parse_quest_menu(self):
    # TODO: a bit more precise matching
    return re.search('Доступные квесты:', self.text), {}

  def _try_parse_caravan_alert(self):
    if 'Вы заметили' in self.text and 'Он пытается ограбить КОРОВАН.' in self.text:
      r = re.search(r'Чтобы помешать, нажмите (?P<cmd>/\w+)', self.text)
      if not r:
        return False, {}
      return True, {'cmd': r.groupdict()['cmd']}
    return False, {}

  def _try_parse_forest_finished(self):
    if re.search('Ты заработал: ', self.text) and re.search('опыта', self.text) and re.search('золотых монет.', self.text):
      return True, {}
    if re.search('Вы вернулись из леса. Ничего интересного не произошло.', self.text):
      return True, {}
    if re.search('В лесу ты отдохнул от бесконечных битв и просто набрал грибов и ягод. В замок вернулся уставший, но довольный.', self.text):
      return True, {}
    return False, {}

  def _try_parse_arena_entry(self):
    if re.search('Даже драконы не могут восстановиться менее чем за час. Отдыхай и приходи позже', self.text):
      return False, {}
    if re.search('Твои вены наполняет адреналин, как только ты переступаешь ворота арены. '
        'Дышать тяжело. Пыльныйвоздух пропитан густым приторным запахом крови. '
        'В этом месте нельзя оказаться случайно, и еслиты тут, значит тебе нечего терять. '
        'Надеюсь, ты достаточно хорошо заточил клинок.', self.text):
      return True, {}
    if re.search('Ты переступаешь ворота арены. Тебя наполняет адреналин, дышать тяжело. '
                 'Пыльный воздух пропитан густым приторным запахом крови. Здесь нельзя оказаться случайно: если ты тут', self.text):
      return True, {}
    return False, {}

  def _try_parse_arena_round(self):
    is_first_msg = re.search('Соперник найден. С вами будет драться воин', self.text)  # First msg does not contain outcomes
    is_large_msg = re.search('выбери точку атаки и точку защиты. У тебя 30 секунд.', self.text)
    if is_large_msg or re.search('Хорошо! Осталось определиться с защитой!', self.text) or re.search('Отлично! Выбери место удара.', self.text):
      for btn in self.buttons:
        if btn not in ARENA_BUTTONS:
          print('Detected arena round mesage but with unknown button: "%s"', btn)
          return False, {}
      params = {}
      if is_large_msg and not is_first_msg:
        self._fill_arena_outcomes(params)
        if len(params['outcomes']) != 2:
          print('Could not parse 2 outcomes in large arena round message! parsed only', len(params['outcomes']), '   ', self.text)
          del params['outcomes']
      return True, params
    return False, {}

  def _try_parse_arena_finished(self):
    if not all(re.search(pattern, self.text) for pattern in ['Победил воин', 'Таблица победителей обновлена', 'Получено:']):
      return False, {}
    params = {}
    self._fill_arena_outcomes(params)
    if len(params['outcomes']) != 2:
      print('Could not parse 2 outcomes in arena final message! parsed only', len(params['outcomes']), self.text)
      del params['outcomes']
    return True, {}

  def _fill_arena_outcomes(self, params):
    # Try to find any outcomes of this round
    params['outcomes'] = []
    for line in self.text.split('\n'):
      r = re.search('(?P<nickname>\w+) нанес \w+ удар (?P<target>\w+ \w+)', line)
      if not r:
        continue
      ru_target = r.groupdict()['target']
      target_mapping = {
        'в голову': 'HEAD',
        'по корпусу': 'BODY',
        'по ногам': 'LEGS',
      }
      target = target_mapping.get(ru_target, None)
      if not target:
        print('Cannot parse target', ru_target, 'in arena outcome:', line)
        continue
      nickname = r.groupdict()['nickname']
      fail_patterns = ['оказался проворнее', 'вовремя пресечен',
                       'не достиг цели', 'своевременно угадал движение',
                       'вовремя поставил блок', 'оказался быстрее и ушел',
                       'вмиг отскочил', 'поставил непробиваемую защиту',
                       'заранее знал место удара и остановил его']
      if re.search('-\d+$', line):
        success = True
      elif any(re.search(pattern, line) for pattern in fail_patterns):
        success = False
      else:
        print('Cannot parse arena outcome:', line)
        continue
      params['outcomes'].append({'nickname': nickname, 'target': target, 'success': success})

  def _try_parse_arena_delay(self):
    if re.search('Казна замка', self.text) or re.search('Отчет о битве:', self.text) or re.search('Общий отчет:', self.text):
      return False, {}
    if re.search('Сражаться можно не чаще чем один раз в час. Приходи позже.', self.text):
      return True, {}
    if re.search('Даже драконы не могут восстановиться менее чем за час. Отдыхай и приходи позже', self.text):
      return True, {}
    return False, {}

  # Just to collect different tavern outcomes
  def _try_parse_tavern_finished(self):
    detected = (
      re.search('Ты не добился в этой жизни ничего. Мальчик принёс тебе водочки.', self.text) or
      re.search('похоже самый населенный сейчас. В таверне, куда не глянь — всюду выходцы оттуда. И выпить то не с кем.', self.text) or
      re.search('В таверне вы подслушали разговор каких-то заезжих конторских служащих, из которого вы узнали, что самый богатый', self.text) or
      re.search('Сегодня вы были полным раздолбаем. Вы напились в сопли и не смогли ничего разведать в таверне. '
                'Дома вас ждала кровать и похмелье.', self.text) or
      re.search('За соседним столом в таверне вы услышали смешную шутку', self.text) or
      re.search('Старный моряк рассказывал трактирщику, как они чистили пудру, когда он', self.text)
    )
    return detected, {}

  def _try_parse_stock(self):
    # TODO: parse stock total price
    return re.search('Содержимое склада ', self.text), {}

  def _try_parse_command(self):
    s = self.text.strip()
    if re.match('^/[a-z_0-9]+$', s):
      return True, {'cmd': s}
    return False, {}

  def _try_parse_button(self):
    btns = [BTN_MAINMENU_ATTACK, BTN_MAINMENU_DEFEND, BTN_MAINMENU_QUESTS,
            BTN_MAINMENU_HERO, BTN_MAINMENU_CASTLE,
            BTN_ARENA_ATTACKHEAD, BTN_ARENA_ATTACKBODY, BTN_ARENA_ATTACKLEGS,
            BTN_ARENA_DEFENDHEAD, BTN_ARENA_DEFENDBODY, BTN_ARENA_DEFENDLEGS,
            BTN_LEVELUP_ATTACK, BTN_LEVELUP_DEFENCE,
            BTN_QUESTS_FOREST, BTN_QUESTS_CARAVANS, BTN_QUESTS_CAVE, BTN_QUESTS_BACK,
            BTN_TAVERN_DRINK, BTN_ARENAENTRY_SEARCH, BTN_CASTLE_TAVERN, BTN_CASTLE_ARENA,
    ] + list(TARGET_TO_BUTTON.values())
    return self.text in btns, {}


# Return: {'type': ORDER_ATTACK, 'target': TARGET_SYMBOL}
def ParseOrder(text):
  order = {}
  for t in ENEMY_TARGETS:
    if t in text:
      return {'type': ORDER_ATTACK, 'target': t}
  if HOME_TARGET in text:
    return {'type': ORDER_DEFENCE, 'target': HOME_TARGET}
  if re.search('атак', text) or re.search('Атак', text):
    order['type'] = ORDER_ATTACK
  elif re.search('защит', text) or re.search('Защит', text) or re.search('Деф', text) or re.search('деф', text):  # TODO: make case insensitive checks
    order['type'] = ORDER_DEFENCE
  else:
    return DEFAULT_ORDER
  for t in TARGET_SYMBOLS:
    if t in text:
      order['target'] = t
      return order
  return DEFAULT_ORDER

class RedStatBotParser(object):
  def __init__(self, message):
    self.props = {}
    self.orig = message
    self.date = getattr(message, 'date', None)
    if not self.date:
      print('Received a redstatbot message without date!')
      self.msg_type = 'UNKNOWN'
      return
    text = getattr(message, 'message', None)
    if self._try_parse_profile_required(text):
      self.msg_type = 'PROFILE_REQUIRED'
    elif self._try_parse_profile_updated(text):
      self.msg_type = 'PROFILE_UPDATED'
    elif self._try_parse_profile_forward(text):
      self.msg_type = 'PROFILE_FORWARD'
    elif self._try_parse_new_stats_required(text):
      self.msg_type = 'NEW_STATS_REQUIRED'
    elif self._try_parse_order(text):
      self.msg_type = 'ORDER'
    else:
      self.msg_type = 'UNKNOWN'

  def _try_parse_order(self, text):
    self.props = {}
    if any(flag in text for flag in TARGET_SYMBOLS):
      self.props['order'] = ParseOrder(text)
      return True
    return False

  def _try_parse_profile_required(self, text):
    self.props = {}
    return re.search('Добро пожаловать! Скинь мне форвардом свой профиль', text)

  def _try_parse_profile_updated(self, text):
    self.props = {}
    return re.search('Спасибо, я обновил твой профиль', text)

  def _try_parse_profile_forward(self, text):
    self.props = {}
    return re.search('Состояние', text) and re.search('Экипировка', text)

  def _try_parse_new_stats_required(self, text):
    self.props = {}
    return re.search('Извини, это старое сообщение. Скинь более новую стату', text)


class AdDickBotParser(object):
  def __init__(self, message):
    self.props = {}
    self.orig = message
    self.date = getattr(message, 'date', None)
    if not self.date:
      print('Received an AdDick message without date!')
      self.msg_type = 'UNKNOWN'
      return
    self.text = getattr(message, 'message', None)
    if self._try_parse_report_received():
      self.msg_type = 'REPORT_RECEIVED'
    else:
      self.msg_type = 'UNKNOWN'

  def _try_parse_report_received(self):
    self.props = {}
    return re.search('Данные о твоих подвигах записаны!', self.text)


class MarketChannelParser(object):
  def __init__(self, message):
    self.props = {}
    self.msg_type = 'UNKNOWN'
    self.orig = message
    self.date = getattr(message, 'date', None)
    if not self.date:
      print('Received market channel message without date!')
      return
    self.text = getattr(message, 'message', None)
    if not self.text:
      print('Receivedmarket channel message without text.')
      return
    parsers = {
      'EXCHANGE_PAIR': self._parse_exchange_pair,
    }
    def call_parser(item):
      parsed, params = item[1]()
      return (item[0], parsed, params)
    parse_results = [r for r in map(call_parser, parsers.items()) if r[1]]
    if len(parse_results) != 1:
      #print('Error while parsing market message: ', self.text)
      #print('Possible parsers: [', ','.join([r[0] for r in parse_results]), ']')
      return
    self.msg_type, _, self.params = parse_results[0]

  def _parse_exchange_pair(self):
    params = {'suggestions': {}}
    current_suggestion = None
    for line in self.text.split('\n'):
      l = line.strip()
      r = re.search(r'(?P<nickname>[\w ]+) воин .* предлагает:', l)
      if r:
        current_suggestion = {}
        params['suggestions'][r.groupdict()['nickname']] = current_suggestion
        continue
      if current_suggestion is None:
        continue
      r = re.search('(?P<resname>[\w ]+) x (?P<quantity>\d+)$', l)
      if r:
        res = self._get_resource(r.groupdict()['resname'])
        if not res:
          continue
        res['quantity'] = int(r.groupdict()['quantity'])
        current_suggestion[res['key']] = res
    if len(params['suggestions'].keys()) != 2:
      return False, {}
    return True, params

  def _get_resource(self, name):
    def R(key, price, real_price):
      return {'key': key, 'price': price, 'real_price': real_price}
    table = {
      'Философский камень': R('PHIL_STONE',   15,  20),
      'Алюминиевая руда':   R('ALUM_ORE',     15,  15),
      'Адамантитовая руда': R('ADAN_ORE',     20,  20),
      'Мифриловая руда':    R('MYTH_ORE',     15,  15),
      'Серебряная руда':    R('SILVER_ORE',    6,  12),
      'Железная руда':      R('IRON_ORE',      4,  10),
      'Сапфир':             R('SAPPHIRE',     40,  40),
      'Стальная нить':      R('STEEL_STRING', 12,  25),
      'Кость животного':    R('BONE',          3,   8),
      'Шкура животного':    R('SKIN',          3,   3),
      'Уголь':              R('COAL',          3,   3),
      'Сундучок':           R('BOX',           1, 150),
      'Ветки':              R('BRANCHES',      2,  20),
      'Растворитель':       R('SOLVENT',      60,  60),
      'Костяная пудра':     R('STONE_DUST',   16,  20),
      'Плотная ткань':      R('FIBRE',         4,   4),
      'Порошок':            R('DUST',          4,  20),
      'Нитки':              R('STRINGS',       2,   4),
      'Древесный уголь':    R('WOOD_COAL',     3,   3),
      'Зерно':              R('GRAIN',         1,  40),
      'Сено':               R('HAY',           1,  40),
      'Комбикорм':          R('COMBO_FOOD',    1,  40),
      'Кроличья лапка':     R('RABBIT_FOOT',   1, 200),
      'Рубин':              R('ROOBEEN',      80,  80),
      'Загуститель':        R('GOOSTER',     100, 100),
    }
    res = table.get(name, None)
    if not res:
      print('Unknown resource!', name)
      return None
    res['name'] = name
    return res
