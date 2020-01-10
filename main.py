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
        channel.queue_bind(exchange='amq.fanout', queue=nickname)
        

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

        recieve_nick = msg.split(" ")[1].replace(":", "")
        first_word = msg.split(" ")[2]

        if "@" in first_word:
            self.parse(first_word, recieve_nick)

        self.root.ids.chat_logs.text += (
                '[b][color=2980b9] {}[/color][/b]\n'.format(self.esc_markup(msg))
        )
        self.root.ids.view.scroll_y = 0

    def parse(self, word, nick):

        word = word.replace("@", "")

        if nick != self.nick:
            if word == "who_are_here?":
                self.send_msg("@i_am_here!")


    def send_msg(self, text):
        #text = self.root.ids.message.text
        message = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')+" "+self.nick+": "+text
            
        self.channel.basic_publish(exchange='amq.fanout',
	                          routing_key='',
	                          body=message,
	                          properties=pika.BasicProperties(
	                          delivery_mode=2,  # make message persistent
	                          ))

if __name__ == "__main__":
    ChatApp().run();
