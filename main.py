from kivy.app import App
import kivy
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

import sys
import pickle
import pika
import datetime
import time
import threading
import msvcrt

Builder.load_string("""
#:import C kivy.utils.get_color_from_hex
<ChatLabel@Label>:
    color: C('#101010')
    text_size: (self.width, None)
    halign: 'left'
    valign: 'top'
    padding: (0, 0)  # fixed in Kivy 1.8.1
    size_hint: (1, None)
    height: self.texture_size[1]
    markup: True

<ScrollView>:
    canvas.before:
        Color:
            rgb: 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<RootWidget>:
    Screen:
        name: 'login'

        BoxLayout:
            orientation: 'vertical'

            GridLayout:
                rows: 2
                cols: 2
                spacing: 10
                row_default_height: 90
                row_force_default: True

                Label:
                    text: 'Server:'
                    halign: 'left'
                    size_hint: (0.4, 1)

                TextInput:
                    id: server
                    text: app.host

                Label:
                    text: 'Nickname:'
                    halign: 'left'
                    size_hint: (0.4, 1)

                TextInput:
                    id: nickname
                    text: app.nick
            
            Button:
                font_size: 30
                height: 90
                size_hint: (1, None)

                text: 'Connect'
                on_press: app.connect()


    Screen:
        name: 'chatroom'

        FloatLayout:
            Button:
                text: 'Отправить'
                font_size: 20
                size_hint: (0.15, 0.10)
                pos_hint: {'x' : 0.825, 'y' : 0.05}
                on_press: app.send_msg()

            TextInput:
                id: message
                hint_text: "Введите сообщение"
                size_hint: (0.775, 0.15)
                pos_hint: {'x' : 0.025, 'y' : 0.025}
                on_text_validate: app.send_msg()
            
            ScrollView:
                size_hint: (0.95, 0.775)
                pos_hint: {'x':0.025, 'y':0.20}

                ChatLabel:
                    id: chat_logs
                    text: ''
                    background_color: [1,1,1,1]
""")

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
#############################
# RABBITMQ:

    def esc_markup(self, msg):    #??????
        return (msg.replace('&', '&amp;')
                .replace('[', '&bl;')
                .replace(']', '&br;'))

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

    def recieve_msg(self, ch, method, properties, body):

            self.root.ids.chat_logs.text += (
            '[b][color=2980b9] {}[/color][/b]\n'.format(body.decode('utf-8'))
            )

    def send_msg(self):
        text = self.root.ids.message.text
        message = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')+" "+self.nick+": "+text
            
        self.channel.basic_publish(exchange='amq.fanout',
	                          routing_key='',
	                          body=message,
	                          properties=pika.BasicProperties(
	                          delivery_mode=2,  # make message persistent
	                          ))

if __name__ == "__main__":
    ChatApp().run();
