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

Builder.load_string("""
<RootWidget>:
    Screen:
        name: 'chatroom'

        FloatLayout:
            Button:
                text: 'Отправить'
                font_size: 20
                size_hint: (0.15, 0.10)
                pos_hint: {'x' : 0.825, 'y' : 0.05}

            TextInput:
                hint_text: "Введите сообщение"
                size_hint: (0.775, 0.15)
                pos_hint: {'x' : 0.025, 'y' : 0.025}
            
            ScrollView:
                size_hint: (0.95, 0.775)
                pos_hint: {'x':0.025, 'y':0.20}

                GridLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height  #<<<<<<<<<<<<<<<<<<<<
                    row_default_height: 60
                    cols:1

                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
                    Button:
""")

class RootWidget(ScreenManager):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)



class ChatApp(App):
    def build(self):
        return RootWidget()
    

if __name__ == "__main__":
    ChatApp().run();
    #ChatApp.layout.add_widget(Button(text=str(10), size_hint_y=None, height=40))
