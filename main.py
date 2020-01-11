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
                           routing_key=self.nick,
                           queue=nickname)
        
        # Service chat:
        channel.queue_bind(exchange='amq.direct',
                           routing_key='service',
                           queue=nickname)

        # Private service chat:
        channel.queue_bind(exchange='amq.direct',
                           routing_key=self.nick + '_service',
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

        msg = body.decode('utf-8')
        #############
        # TO DELETE:
        #recieve_nick = msg.split(" ")[1].replace(":", "")
        #first_word = msg.split(" ")[2]

        #if "@" in first_word:
        #    self.parse_service(first_word, recieve_nick)
            
        ####################
        color = '2980b9'

        msg_datetime = msg.split(" ")[0]
        sender_nick = msg.split(" ")[1].replace(':', '')
        first_word = msg.split(" ")[2].replace("@","")

        is_service_msg = False
        
        if method.routing_key == 'service':
            color = 'ff0000'
            is_service_msg = True
        if method.routing_key == self.nick:
            color = 'ff00ff'
        if method.routing_key == self.nick + '_service':
            color = 'faaa00'
            is_service_msg = True

        self.root.ids.chat_logs.text += (
                '[b][color={}] {}[/color][/b]\n'.format(color, self.esc_markup(msg))
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
               words[0] == "@i_am_here!":

                routing_key = 'service'
                if len(words) > 1:
                    if "@" in words[1]:     # Если сервис адресован кому-то:
                        routing_key = words[1].replace('@','') + '_service'
            else:
                routing_key = words[0].replace("@", "")   # routing_key = nickname address
            


        message = datetime.datetime.fromtimestamp(time.time()).strftime('%Y.%m.%d_%H:%M:%S')+" "+self.nick+": "+text

            
        self.channel.basic_publish(exchange=exchange,
	                          routing_key=routing_key,
	                          body=message,
	                          properties=pika.BasicProperties(
	                          delivery_mode=2,  # make message persistent
	                          ))

if __name__ == "__main__":
    ChatApp().run();
