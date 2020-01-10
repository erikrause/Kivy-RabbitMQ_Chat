from kivy.app import App
import kivy
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


class ChatApp(App):
    def build(self):
        fl = FloatLayout()
        fl.add_widget(Button(text = "Отправить",
                             font_size = 23,
                             size_hint = (0.25, 0.25),
                             pos_hint = {'x':0.725, 'y':0.025}))
        return fl

if __name__ == "__main__":
    ChatApp().run();
