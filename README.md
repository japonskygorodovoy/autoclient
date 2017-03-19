### Telegram Automatic client for chatwars.

Автоматический бот, который сам играет в ChatWars.

Написано в режиме "хакатон-стайл", поэтому в коде сплошная ебанина.

Если заметили какие-то ошибеи, хотите что-то улучшить - пожалуйста.
Можно багрепортить, можно пуллреквестить, можно форкать - все что угодно.

Тут все довольно наворочено, есть куча глюков, по любым непоняткам - спрашивайте.

##### Установка и запуск

Установите на вашу систему третий питон (python3) и пакетменеджер pip3.

Для винды вроде как они оба ставятся сразу.

Можно еще в нагрузку virtualenv, но совсем необязательно.
Теперь поставьте библиотеки питоновые:
```
$ pip3 install telethon pytz pymongo
```

Далее нужно получить API\_ID и API\_HASH.
Заходите на [my.telegram.org](http://my.telegram.org), логиньтесь,
открывайте API development tools, получаете нужные токены.

Переименуйте *config.json.template* в *config.json*.
Вбейте в него эти данные и номер телефона аккаунта.
Также укажите ID вашего пользователя.

Запускайте `$ python3 autoclient.py`. При первом запуске он спросит
код подтверждения, при остальных будет читать из файла.

##### Как оно устроено

Фактически это отдельный клиент для телеги, который следит за несколькими чатами
и читает/пишет в них.

Бот сам ходит в квесты - днем в лес, а ночью в пещеры и на караваны.

Бот сам ходит на арену, по рандомной стратегии. Итогда правда там его глючит,
то ли телега присылает сообщения с задержкой, то ли где-то баг. Но в целом норм.

Бот сам ходит тратить деньги в таверну, если указано в конфиге.

Бот сам донатит излишки денег в казну,
чтоб много не просирать на дефах (тоже смотрите конфиг).

Бот сам реагирует на караваны (отсылает **/go**)

Бот сам ходит в атаки по приказу из **RedStatBot** (пытается парсить приказы).
Уходит с арены заблаговременно, если там долго никого нет, а нужно идти в атаку
(полезно ночью), но это не протестировано. Заранее прожимает атаку и ждет
приказа **RedstatBot**a.
Правда местами есть глюки, но обычно норм.

Бот сам форвардит репорты с битв боту Адъютант и свежие профили ему же и RedStatBotу.

Бот контролируется из чата юзера с самим собой - можно отправлять команды
`/status`, `/pause`, `/resume`. Полезно, если бот запущен дома, а случилась какая-то
херня или нужно идти в атаку не по приказу. Еще можно юзать, чтобы купить снаряжение
или торговать ресурсами. Или сделать что-то, чего в боте не предусмотрено.

Бот также при получении сообщения об успешной торговле получает сток и
форвардит боту **RedWings**.

Бот следит за каналом **ChatWarsMarket** и если кто-то кидает вам ответное предложение,
форвардит его в чат юзера с самим собой. Это пока глючит, там что-то с айдишниками -
присыается просто левое сообщение, чтобы была нотификация. Сделано, чтобы
постоянно не листать маркет.

Бот умеет качать перса при левелапе. В зависимости от стратегии в конфиге,
будет качать соответствующую стату. Также от этой стратегии зависит, куда ходит
герой при атаке на замки. При стратегии **defence** будет всегда стоять в дефе.

Бот умеет сам выбирать специализацию и обучение. В конфиге нужно задать список
специализаций, например
```
"SPECIALIZATIONS": ["ESQUIRE", "ATTACKER"]
```
На данный момент известны только **ESQUIRE**, **MASTER**, **ATTACKER**, **DEFENDER**.
Если укажете противоречащие классы, либо при выборе будет неизвестный класс - делать ничего не будет,
но пошлет уведомление об этом в чат SELF\_ID. Выберите как можно скорее, ибо он на этом зацикливается -
пропишите в конфиг и перезапустите клиент.
Если при очередном левелапе есть только "обучение", он тоже сам его выполнит.

##### Ограничения

Как можно понять по тем чатам, за которыми он следит - заточен на красный замок,
в частности на учебку. Но и без этого будет основные функции выполнять.

Бот не умеет в петов пока что, т.к. у меня их нет, я не знаю как с ними взаимодействовать.

Бот сам не закупает снаряжение и не продает ресурсы. Используйте команду паузы,
чтобы делать это с телефона, не останавливая скрипт.

##### P.S.

Приношу извинения авторам игры за этого бота :)
Эта игра меня так сильно не отпускала, что пришлось написать его, чтобы
продолжать нормально жить :(

В какой-то момент я стал сильно занят, вообще забил на игру и не мог добавлять новые фичи сюда.
Таким же образом я проебал введение капчи. Впилил быстрофикс.
Что ж, значит пора заопенсорсить это дело!
