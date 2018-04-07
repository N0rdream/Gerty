# Bot

О программе
----------
Bot представляет собой бота, автоматически отвечающего на сообщения, присланные участниками группы ВК и содержащие определенный хештег. Бот написан на языке Python с использованием веб-фреймворка Django и менеджера очередей Celery.


Установка
-----------
```
$ git clone https://github.com/N0rdream/bot.git
$ cd bot 
```


Зависимости
----------    
Для работы бота требуется версия Python не ниже 3.6.
Установку необходимых зависимостей можно осуществить, выполнив команду:
```
$ pip install -r requirements.txt
```
Кроме того, необходимо установить Postgresql, RabbitMQ, Redis.


Конфигурирование и настройка бота
----------
Настройка бота осуществляется при помощи файла .env. Его необходимо создать в корне папки проекта. Пример содержания файла выглядит следующим образом:
```
SECRET_KEY="django_secret_key"

BOT_DATABASE_NAME="bot"
BOT_DATABASE_USER="postgres"
BOT_DATABASE_PASSWORD="postgres"
BOT_DATABASE_HOST="localhost"
BOT_DATABASE_PORT=5432

CELERY_BROKER_URL="amqp://localhost:5672//"

CELERY_REDIS_HOST="localhost"
CELERY_REDIS_PORT=6379
CELERY_REDIS_DB=0

VK_GROUP_ACCESS_TOKEN="vk_token"
VK_GROUP_SECRET_KEY="vk_secret_key"
VK_GROUP_CONFIRMATION="confirm"

VK_API_VERSION="5.73"

VK_ANSWER_TIMEOUT=1
```
### SECRET_KEY  
Секретный ключ Django.

### BOT_DATABASE_*  
Настройки для подключения к Postgresql.

### CELERY_BROKER_URL  
Адрес для подключения к серверу RabbitMQ.

### CELERY_REDIS_*  
Настройки для подключения к Redis.

### VK_GROUP_ACCESS_TOKEN  
Ключ доступа сообщества. Как получить ключ описано в https://vk.com/dev/access_token?f=2.%20%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0

### VK_GROUP_SECRET_KEY  
Произвольная строка, которая будет передаваться во входящем сообщении в поле 'secret'. Задается при подключении бота к группе ВК (см. ниже). 

### VK_GROUP_CONFIRMATION  
Строка, необходимая для подтверждения работоспособности сервера, гдн находится бот. Задается при подключении бота к группе ВК (см. ниже).

### VK_API_VERSION  
Текущая версия API ВК.

### VK_ANSWER_TIMEOUT  
Временной промежуток (в минутах), в течение которого пользователь не будет получать информацию по уже запрошенному хештегу.


Как подключить бота к группе ВК
----------
Подключение бота к конкретной группе ВК осуществляется при помощи Callback API - https://vk.com/dev/callback_api. В поле "Адрес сервера" необходимо задать https://example.com/bot, где example.com является адресом сервера, где находится бот. Также необходимо отметить галочками типы событий в соответствующей вкладке. Бот настроен на работу с новыми и отредактированными сообщениями.


Коротко о принципе работы
----------
При поступлении нового сообщения или после редактирования старого сервер ВК посылает боту уведомление в формате JSON с информацией о произошедшем событии. Бот парсит тело сообщения, проверяя его на наличие хештега (слово с символом "#"). Если хештег не найден, параметры пришедшего сообщения записываются в Postgresql при помощи задачи handle_message_without_hashtag. Если хештег имеется, тогда вызывается задача handle_message_with_hashtag, которая записывает параметры как в Postgresql, так и в Redis. Данные, накопленные в Redis, обрабатываются каждые четыре секунды celerybeat-задачей send_hashtag_data и отсылаются обратно в группу ВК.


Перед запуском
----------
Для совместной работы с БД выполните следующие команды:
```
$ ./manage.py makemigrations
$ ./manage.py migrate
$ ./manage.py createsuperuser
```
Для сбора статики админки выполнить:
```
$ ./manage.py collectstatic
```


Как запустить
----------
Запуск django посредством gunicorn:
```
$ gunicorn --bind 0.0.0.0:8000 vk_bot_prj.wsgi
```
Запуск celery и celerybeat:
```
$ celery -A vk_bot_prj worker -B
```
Информация для запуска gunicorn в качестве демона: http://docs.gunicorn.org/en/stable/deploy.html.  
Информация для запуска celery и celerybeat в качестве демона: http://docs.celeryproject.org/en/latest/userguide/daemonizing.html.  


Тесты
----------
Для запуска тестов перейдите в корневую директорию проекта и выполните следующую команду:
```
$ pytest
```

После запуска
----------
Заполните через админку (https://example.com/bot) таблицу Hashtags необходимыми данными по хештегам. 






