# -*- coding:utf-8 -*-

BOT_HREF = 'https://t.me/Sugawara_Kou'  # ссылка на бота
RootUsers = []  # рутовые пользователь (организаторы)

# настройка uvicorn
UvicornHost = '0.0.0.0'  # хост на котором находиться веб сервер
UvicornPort = 8000  # порт на котором будет запущен веб сервер
UvicornReload = True  # перезапуск веб сервера при изменении кода
UvicornLogsOff = False  # отключение логов uvicorn и использование собственных логов
UvicornWorkers = 10  # количество потоков


# параметры для подключения к базе данных
DatabaseName = ''  # Имя
DatabaseUser = ''  # Пользователь
DatabasePassword = ''  # Пароль
DatabaseHost = ''  # IP-Адрес
DatabasePort = ''  # Порт