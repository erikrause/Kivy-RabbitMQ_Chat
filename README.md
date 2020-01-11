# Kivy-RabbitMQ_Chat
Для создания пользовательского интерфейса использована библиотека Kivy.

main.py - точка входа.
## Вход в приложение
  - Server -- IP адрес сервера с брокером RabbitMQ (почтовый ящик)
  - Nickname -- имя почтового ящика/отправителя 
  
![alt text](Screenshots/login2.png "Окно входа")

## Окно группового чата
История сообщений группового чата хранится в ScrollWidget. Новые сообщения добавляются снизу, чтобы просмотреть старые сообщения нужно скроллить вверх.
![alt text](Screenshots/Test_chat.png "Окно группового чата")