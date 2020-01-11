from kivy.app import App
import kivy
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

import sys
import pickle
import pika
import datetime
import time
import threading
import msvcrt

import json
from datetime import datetime

class RootWidget(ScreenManager):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)


######################
# KIVY APP:

class ChatApp(App):
    def build(self):
        self.host = "127.0.0.1"
        self.nick = "kivy"
        return RootWidget()
    
    def connect(self):
        self.host = self.root.ids.server.text
        self.nick = self.root.ids.nickname.text

        self.channel = self.open_channel(self.nick)
        self.root.current = 'chatroom'

        conuming_thread = threading.Thread(target=self.consuming, name='consuming')
        conuming_thread.start()

        time.sleep(0.5)      # ?Без паузы возникает ошибка pop from an empty deque. нужна проверка потока consuming
        self.send_msg('@зашел_в_чат')

    def send_msg(self):
        pass

    def open_channel(self, nickname):
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost',
                                  credentials=pika.PlainCredentials('guest', 'guest')))
        channel = connection.channel()

        channel.queue_declare(queue=nickname)

        # Public chat:
        channel.queue_bind(exchange='amq.fanout',
                           queue=nickname)

        # Private chat:
        channel.queue_bind(exchange='amq.direct',
                           routing_key=self.nick + "_private",
                           queue=nickname)
        
        # Service chat:
        channel.queue_bind(exchange='amq.direct',
                           routing_key='service',
                           queue=nickname)

        # Private service chat:
        channel.queue_bind(exchange='amq.direct',
                           routing_key=self.nick + '_private_service',
                           queue=nickname)

        return channel

    def consuming(self):
            self.channel.basic_qos(prefetch_count=100)
            self.channel.basic_consume(queue=self.nick, on_message_callback=self.recieve_msg)
            self.channel.start_consuming()

    def esc_markup(self, msg):
        return (msg.replace('&', '&amp;')
                   .replace('[', '&bl;')
                   .replace(']', '&br;'))


    def recieve_msg(self, ch, method, properties, body):

        data = json.loads(body.decode('utf-8'))

        msg = data['msg']

        color = '2980b9'

        msg_datetime = data['datetime']
        sender_nick = data['nick']
        first_word = msg.split(" ")[0].replace("@","")

        msg_age = time.time() - msg_datetime
        if msg_age > 86400:    
            ch.basic_ack(delivery_tag = method.delivery_tag)    # Если сообщению больше суток, то удалить из очереди
        else:
            is_service_msg = False
        
            if method.routing_key == 'service':
                color = 'ff0000'
                is_service_msg = True
            elif method.routing_key.find('_private_service') != -1:
                color = 'faaa00'
                is_service_msg = True
            elif method.routing_key.find('_private') != -1:
                color = 'ff00ff'

            self.root.ids.chat_logs.text += (
                    '{} {}[b][color={}] {}[/color][/b]\n'.format(self.esc_markup(datetime.utcfromtimestamp(msg_datetime).strftime('[%Y.%m.%d_%H:%M:%S]')),
                                                                 sender_nick,
                                                                 color, 
                                                                 self.esc_markup(msg))
            )
            self.root.ids.view.scroll_y = 0

            if first_word == "who_are_here?":
                self.send_msg("@i_am_here! @" + sender_nick)

            if is_service_msg:
                ch.basic_ack(delivery_tag = method.delivery_tag)    # Удалить сообщение из очереди если оно сервисное

    # Returns word and true if msg == service command
    def parse_command(self, word):

        word = word.replace("@", "")

        #if nick != self.nick:
        if word == "who_are_here?":
            #self.send_msg("@i_am_here!")
            return True


    def send_msg(self, text):
        #text = self.root.ids.message.text

        words = text.split(" ")
        exchange = 'amq.fanout'
        routing_key = ''

        # Проверка на сервисное сообщение
        if "@" in words[0]:
            exchange = 'amq.direct'

            if words[0] == "@who_are_here?" or \
               words[0] == "@i_am_here!" or \
               words[0] == '@зашел_в_чат':

                routing_key = 'service'
                if len(words) > 1:
                    if "@" in words[1]:     # Если сервис адресован кому-то:
                        routing_key = words[1].replace('@','') + '_private_service'
            else:
                routing_key = words[0].replace("@", "") + "_private"   # routing_key = nickname address

        message = {'datetime': time.time(), 'nick':self.nick, 'msg':text}

        message = json.dumps(message)
            
        self.channel.basic_publish(exchange=exchange,
	                          routing_key=routing_key,
	                          body=message,
	                          properties=pika.BasicProperties(
	                          delivery_mode=2,  # make message persistent
	                          ))

        # Плохой код, поменять routing:
        if routing_key.find("_private") != -1 and \
             routing_key.find("_private_service") == -1:
            self.channel.basic_publish(exchange=exchange,
                                       routing_key=self.nick + "_private",
	                                   body=message,
	                                   properties=pika.BasicProperties(
	                                   delivery_mode=2,  # make message persistent
	                                   ))


if __name__ == "__main__":
    ChatApp().run();
