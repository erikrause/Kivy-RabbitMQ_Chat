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

""")

class RootWidget(ScreenManager):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

class OldApp(App):

    def callback(self, instance):
        self.layout.add_widget(Button(text=str(10), size_hint_y=None, height=40))

    def build(self):
        fl = FloatLayout()
        fl.add_widget(Button(text = "Отправить",
                             font_size = 20,
                             size_hint = (0.15, 0.10),
                             pos_hint = {'x' : 0.825, 'y' : 0.05}))
        fl.add_widget(TextInput(hint_text = "Введите сообщение",
                                size_hint = (0.775, 0.15),
                                pos_hint = {'x' : 0.025, 'y' : 0.025}))


        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.layout.bind(minimum_height=self.layout.setter('height'))
        print(self.layout.size_hint)
        
        for i in range(10):
            btn = Button(text=str(i), size_hint_y=None, height=40, on_press=self.callback)
            self.layout.add_widget(btn)

        self.layout.add_widget(Button(text=str(10), size_hint_y=None, height=40))
        view = ScrollView(size_hint = (0.95, 0.775),
                                 pos_hint = {'x':0.975, 'y':0.975})
                                 #background_color = [1,1,1,1])
                                 #color = [1,1,1,1]) #debug
        print(view.size_hint)
        
        #view.add_widget(Label(text = 'HELLO!'))
        view = ScrollView(size_hint=(0.95, 0.775),
                          pos_hint = {'x':0.025, 'y':0.20})#, size=(Window.width, Window.height))
        view.add_widget(self.layout)
        fl.add_widget(view)

        return fl   # этот виджет идет в self.root

class ChatApp(App):
    def build(self):
        return RootWidget()
    

if __name__ == "__main__":
    OldApp().run();
    #ChatApp.layout.add_widget(Button(text=str(10), size_hint_y=None, height=40))
