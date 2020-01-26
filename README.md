# Kivy-RabbitMQ_Chat
Для создания пользовательского интерфейса использована библиотека Kivy.

main.py - точка входа.
## Вход в приложение
  - Server -- IP адрес сервера с брокером RabbitMQ (почтовый ящик)
  - Nickname -- имя почтового ящика/отправителя 
  
![alt text](Screenshots/login2.png "Окно входа")

## Окно группового чата
История сообщений группового чата хранится в ScrollWidget. Новые сообщения добавляются снизу, чтобы просмотреть старые сообщения нужно скроллить вверх.
  
![alt text](Screenshots/Test_chat2.png "Окно группового чата")

## Message Routings:
Каждый тип сообщения закрашивается в определенный цвет в зависимости от routing_key.
  - Сервисные сообщения:
    - Публичные (красные):
      - @who_are_here? - получить список пользователей онлайн;
      - @зашел_в_чат - генерируется при входе в чат.
    - Приватные (оранжевые):
      - @i_am_here! - автоматический ответ на @who_are_here?.
  - Приватные сообщения (фиолетовые) - адресуются конкретным потребителям через обменник amq.direct;
  - Публичные сообщения (синие) - рассылаются всем через обменник amq.famout.
  
Сервисные сообщения удаляются из очереди сразу после доставки потребителю. Остальные сообщения удаляются из очереди через 24 часа.
